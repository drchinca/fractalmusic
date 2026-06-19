# Fractal Expert Agent

> A CEMAF agent that becomes an expert on the Sistema Fractal by retrieving from the indexed book corpus via meridian_library. Cites by `(book_hash, chapter, paragraph, page)` — answers without provenance are rejected.

## What this is

A scoped retrieval agent. Not a code generator, not a teacher, not a chatbot — it answers questions about Patricio Torres's system using passages from the two indexed books, with citations that point back to specific chunks.

## Source corpus (already indexed)

```
~/.meridian/library/
  catalog.db, bm25.pkl, vectors.pkl  (nomic-embed-text 768-d)

  [f39cb7c5]  2025 Fractal Music World         9.4 MB
  [b202598c]  Libro El Metodo Fractal Cap 0    1.9 MB
```

Both are BM25 + dense-vector indexed. Hybrid retrieval (RRF, k=60) works for synonym matches (e.g. "letting go" → "renunciation"). Verified hits: `dodecamundo`, `gatople`, `modos griegos`, `Sistema Fractal`.

## Pipeline

```
Question
   │
   ▼
LibraryRetriever (meridian_research.retrievers.library)
   │  index_dir = ~/.meridian/library
   │  force_hybrid = True
   │  shelf filter = [f39cb7c5, b202598c]   # fractal scope
   ▼
List[Evidence]   # source=LIBRARY, snippet ≤ 2000 chars, stable id
   │
   ▼
CEMAF Researcher (or Librarian) agent
   │  receives Evidence as ContextSource
   │  answers via LLMClient (Anthropic / Ollama)
   │  every claim → cites Evidence.id
   ▼
Result
   │  answer text
   │  citations: List[(book_hash, chapter, paragraph, page)]
```

## Two ways to use it

### A. CLI (zero wiring)

```bash
cd iccha_context_multi_agent/meridian_research
uv run meridian-research "explain the dodecamundo and how it relates to the gatople" \
  --source library \
  --library-index ~/.meridian/library \
  --book f39cb7c5 --book b202598c \
  --hybrid
```

This is the fastest path. Use it for ad-hoc lookups and to validate the corpus before wiring anything heavier.

### B. CEMAF agent in code

```python
from pathlib import Path
from cemaf.bootstrap import create_executor
from cemaf.agents import AgentRegistry
from cemaf.agents.context_agents import Researcher
from cemaf.retrieval.protocols import VectorStore
from meridian_library.index.cemaf_adapter import CemafBM25VectorStore

# 1. The retrieval substrate — speaks CEMAF's VectorStore protocol
fractal_store: VectorStore = CemafBM25VectorStore(
    index_dir=Path.home() / ".meridian" / "library",
    book_filter=("f39cb7c5", "b202598c"),  # scope to fractal corpus
)

# 2. The agent — uses fractal_store as its retrieval source
registry = AgentRegistry()
registry.register("fractal_expert", Researcher(vector_store=fractal_store))

# 3. Composition root — DAGExecutor wires everything
executor = create_executor(agent_registry=registry)

# 4. Run a question through a one-node DAG
# (See cemaf docs for full DAG construction; this agent slots into any
#  pipeline that consumes a Researcher.)
```

The `CemafBM25VectorStore` adapter satisfies `cemaf.retrieval.protocols.VectorStore` at runtime — `isinstance(store, VectorStore)` returns True. Phase 3 swap to `cemaf.retrieval.PgVectorStore` requires zero changes to consumer code.

## Citation contract

Every answer the agent produces must surface, per claim:

```python
@dataclass(frozen=True, slots=True)
class FractalCitation:
    book_hash: str            # f39cb7c5 | b202598c
    chapter_idx: int
    section_idx: int
    paragraph_idx: int
    page_start: int
    snippet: str              # ≤ 2000 chars
```

This metadata lives on `Evidence.metadata` already (set by `meridian_library.index.cemaf_adapter`). The agent's job is to *not drop it* on the way to the answer.

**Reject** any answer where:
- A factual claim has no citation, OR
- A citation points to a chunk outside the scoped book hashes, OR
- The snippet doesn't actually support the claim (use `cemaf.evals.semantic` to verify).

## Scope rule (don't bleed)

Default scope is the two fractal books. Cross-source reasoning is opt-in:

```python
# Default — fractal only
CemafBM25VectorStore(index_dir=..., book_filter=("f39cb7c5", "b202598c"))

# Opt-in — fractal + music theory shelf
CemafBM25VectorStore(
    index_dir=...,
    book_filter=("f39cb7c5", "b202598c", *MUSIC_THEORY_BOOK_HASHES),
)
```

Silent corpus-wide retrieval is a bug. The agent's value is *narrow expertise*, not *general world knowledge*.

## Eval criteria

Before this agent ships, three goldens must pass:

| Eval | Pass condition |
|---|---|
| **Citation membership** | 100% of answer citations resolve to chunks inside `(f39cb7c5, b202598c)` |
| **Semantic recall** | Asked "what is the Dodecamundo?", answer cites `[b202598c] ch0 §0 ¶27 p.16` (verified live hit) |
| **Refusal on out-of-scope** | Asked "what does Bach say about counterpoint?", answer is "no fractal-corpus evidence" — not a hallucinated stretch |

These live (or will live) in `tests/uat/test_fractal_expert.py`.

## What this agent is NOT

- Not a code generator. The Python core is human-authored against the book.
- Not a teacher. The wheel is geometric; cartas teach. The agent narrates passages.
- Not a chat companion. It answers system questions with citations or refuses.

## Re-ingest / maintenance

If the books are revised:

```bash
cd iccha_context_multi_agent/meridian_library
uv run meridian-library ingest ~/library_of_kuri/Personal-Works-by-Kuri/Metodo-Fractal \
  --index-dir ~/.meridian/library --embed --verbose
# Idempotent — content-hashed, only changed books re-embed.
```

If the chunker changes (e.g. new heading heuristics for Spanish), use `--reindex` to wipe and rebuild.

## References

- `iccha_context_multi_agent/meridian_library/README.md` — index format, CLI, hybrid retrieval
- `iccha_context_multi_agent/meridian_library/docs/specs/SPEC-meridian-library.md` — invariants
- `iccha_context_multi_agent/cemaf/CLAUDE.md` — agent framework, RuntimeServices, Researcher pattern
- `iccha_context_multi_agent/meridian_research/src/meridian_research/retrievers/library.py` — the retrieval adapter pattern
