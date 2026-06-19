# fractalmusic Project Instructions

> Patricio Torres's **Sistema Fractal** as a typed Python layer over [pytheory](https://pytheory.org), with a TypeScript/React companion app under `web/`. Source of truth: *El Sistema Fractal* (2024) and *2025 Fractal Music World*.

## Project Rules (override the global BrightHive defaults)

This is a **personal music-theory project**, single developer, no team, no Jira, no BrightHive context. The global rules at `~/.claude/CLAUDE.md` are calibrated for enterprise multi-person workflows; the rules below override them for work in this repo.

### What's dropped

- **No Jira, no tickets, no epics.** Don't run `/create-jira-ticket`. Don't reference BH-*. Don't add story points.
- **No team reviewers.** PRs are assigned to `drchinca`. No `--add-reviewer`. The PR template's "Assignees + Reviewers" rule does not apply.
- **No multi-agent review on every code change.** Use the project agent roster below, and only when the work warrants it (specs, non-trivial features, security-adjacent code). Routine fixes don't need 4 reviewers.
- **No OTel observability contract section in specs** unless the feature actually ships telemetry (this app doesn't yet).
- **No BrightHive-grade SDD ceremony.** See lean spec template below.

### Lean spec template (5 sections, not 9)

When a feature warrants a spec (LLM behavior, cross-service contract, new public surface), use this shape — total length usually under 200 lines. Specs live at `docs/specs/SPEC-{slug}.md`.

```
1. Context           — problem, who, why now (≤ 1 paragraph + optional mermaid)
2. Interface         — Pydantic models, HTTP shapes, type contracts
3. Invariants        — what must always hold (max 5; if you need more, split the feature)
4. Acceptance        — Gherkin scenarios (max 8; the headline behaviors)
5. Out of scope      — explicit non-goals
```

Dropped from the global template: §6 Dependencies (put in README), §7 Correctness Properties (collapse into §3 invariants), §8 Eval Criteria (only when LLM behavior is the feature, and then inline a small "how we know it works" subsection — not a full evaluator table), §9 Observability Contract.

When in doubt: **fewer sections, fewer invariants, fewer scenarios.** The simplifier agent reviews specs and will cut what doesn't earn its place.

### Project agent roster

| Agent | Role | When to invoke |
|---|---|---|
| `react-frontend-expert` | React 19 + TS + Vite review | UI work in `web/` |
| `ux-designer` | Voice of the everyday musician (not a dev) | Any user-facing change — flags jargon, pedagogy gaps, mobile/touch UX |
| `senior-python` | Python core + BFF review | Non-trivial Python changes |
| `simplifier` | Lean-keeper. Reads specs/PRs through "does this earn its place in a 1-dev music app?" | Every spec; every PR over ~200 lines; whenever ceremony creeps in |

Multi-agent review for a feature spec = these four agents in parallel, **not** the global Solutions Architect → Senior Python → QA → Junior Dev sequence. Routine code changes need none.

### Commit / branch / PR

- Branches off `develop` (created in v1 release). `master` only on explicit user say-so.
- Conventional commits, no AI attribution. (Same as global.)
- PR size cap is **soft, not hard**, here: prefer ≤500 lines but a coherent feature milestone can land in one squash PR. Acknowledge the deviation in the PR body when over.
- Draft PR after first commit on a branch — same as global. This rule earns its place even on a 1-dev project (gives CI a green/red signal early).
- Squash-merge into `develop`.

### Testability

The global `testable-code.md` rule (no `patch()`, DI everywhere) applies. It earns its place even on a 1-dev project — singletons rot fast.

### When to escalate to the global rules

If a feature genuinely needs SLOs, observability, or a calibrated eval set, write that section *and* mark it as such. The lean template is a default, not a ceiling.

## Cardinal Invariants

These are non-negotiable. Code that violates them is wrong, even if tests pass.

1. **A-origin everywhere.** `A` (La menor / Eólico) is the matriarchal tonic. Module-level helpers in `modes`, `scales`, `dodecamundo` are the A-tonic readings. Tonic shifts happen *only* through `Wheel(tonic=...)`. Index 0 = A (matches pytheory's native order; index 3 = C).
2. **Function lives on the wheel, not on the note.** A note like `D` has no fixed identity — it is whichever role sits under it when the inner disc lands at the chosen tonic. Code that hard-codes "D is Dorian" is wrong; code that asks `Wheel("A").mode_for("D")` is right.
3. **Two-disc model is load-bearing.** Outer disc = roles `(glyph, color, clock-position, scale-pattern)` — *never moves*. Inner disc = 12 notes — *rotates freely*. Pedagogy is geometric, not nominal. Any abstraction that collapses these into a single layer breaks the system.
4. **Pentatonic-first.** Scales are derived from pentatonic skeletons, not bolted on as a subset of heptatonic. The 5 penta roots (`PENTA_ROOTS`) and the 7 Greek modes are co-equal members of the 12-role wheel.
5. **The 12 cartas are canonical.** Each carta = `(glyph, color, default-tonic note, mode)`. They are the source of truth for role identity. Painted deck order matters; do not renumber.
6. **BE owns logic, FE only renders.** All music-theory, generation, scoring, and learning logic lives in the Python core. The web app consumes JSON snapshots and plays/draws them — it never re-derives wheel logic, never scores, never picks notes. New behavior → add it to Python and re-emit JSON. If you find yourself writing theory code in `web/src/`, stop and move it to `fractalmusic/`.

## Architecture Overview

fractalmusic has a Python core (the system) and a web companion (a teaching surface). Both consume the same A-origin model — the web app is a renderer, never a re-implementation.

```
┌─────────────────────────────────────────────────────────────┐
│                    PYTHON CORE (the system)                  │
│                                                              │
│   fractalmusic/                                              │
│   ├─ symbols.py     12 role glyphs (⋮ ★ △ ■ + ♀ ...)         │
│   ├─ colors.py      role → hex color (book-canonical)        │
│   ├─ modes.py       Mode dataclass, ALL_MODES, _clock_hour   │
│   ├─ dodecamundo.py 12 NoteWorlds (5 penta + 7 heptatonic)   │
│   ├─ scales.py      pentatonic-first scale construction      │
│   ├─ cartas.py      12-card deck, piano_stickers, spell      │
│   ├─ formulas.py    PHI, chessboard_grains, consonance       │
│   ├─ wheel.py       Wheel(tonic) — the spinning Gátople      │
│   ├─ gatople.py     clock-face data builder                  │
│   ├─ svg.py         render wheel/cards/scales to SVG         │
│   ├─ gallery.py     CLI: render all 12 wheels                │
│   └─ showcase.py    CLI entry: print system summary          │
│                                                              │
│   ↓ depends on                                               │
│   pytheory (Tones, intervals, mode names)                    │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼ consumed by
┌─────────────────────────────────────────────────────────────┐
│                  WEB COMPANION (web/)                        │
│   Vite + React + TS. Reads JSON snapshots emitted by         │
│   scripts/build_gatople_data.py and                          │
│   scripts/build_progressions_data.py.                        │
│   The web app NEVER re-derives wheel logic — it renders.     │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼ retrieves expert knowledge from
┌─────────────────────────────────────────────────────────────┐
│              FRACTAL EXPERT (CEMAF + meridian)               │
│   ~/.meridian/library — books indexed:                       │
│     [f39cb7c5] Fractal Music World 2025                      │
│     [b202598c] El Metodo Fractal Cap 0 (Bado)                │
│   meridian_library.CemafBM25VectorStore                       │
│   → CEMAF Researcher / Librarian agent                        │
│   See `docs/agents/fractal-expert.md` for the wiring.         │
└─────────────────────────────────────────────────────────────┘
```

**Entry points**:
- Library: `import fractalmusic as fm; fm.Wheel("A").mode_for("D")`
- CLI: `fractalmusic` (showcase), `fractalmusic-gallery` (12 SVGs)
- Web: `cd web && npm run dev`
- Expert agent: `meridian-research "..." --source library --library-index ~/.meridian/library --book f39cb7c5 --book b202598c --hybrid`

## Module Map

### Core (the system)

| Module | Purpose | Key Symbols |
|---|---|---|
| `symbols` | 12 role glyphs in canonical order | `GLYPHS`, `glyph_at_hour` |
| `colors` | Book-canonical role colors | `ROLE_COLORS`, hex constants |
| `modes` | Mode dataclass, all 12 modes, clock-hour mapping | `Mode`, `ALL_MODES`, `CHROMATIC_ORDER`, `PENTA_ROOTS`, `_clock_hour` |
| `dodecamundo` | 12 NoteWorlds — penta + heptatonic | `DODECAMUNDO`, `NoteWorld`, `world`, `heptatonic_worlds`, `pentatonic_worlds` |
| `scales` | Pentatonic-first scale construction | scale-from-mode helpers |
| `cartas` | 12-card deck (canonical order) | `carta`, `deck`, `piano_stickers`, `spell` |
| `formulas` | Etno-matemática constants & ratios | `PHI`, `chessboard_grains`, `consonance` |
| `wheel` | The spinning Gátople | `Wheel(tonic).mode_for(note)`, role-at-hour, note-at-role |
| `gatople` | Clock-face data builder for renderers | `build_clock(...)` |
| `svg` | Pure-Python SVG of wheel/cards/scales | render functions |
| `gallery` | CLI: render all 12 wheels to disk | `main` |
| `showcase` | CLI: print system summary | `main` |

### Web (`web/`)

Vite + React 19 + TypeScript app. Static JSON consumed by components:
- `web/public/gatople-data.json` — emitted by `scripts/build_gatople_data.py`
- `web/public/progressions-data.json` — emitted by `scripts/build_progressions_data.py`
- `web/src/` — renders the wheel, the picker, the compose tabs (in-key / book progressions)

**Greenfield rule applies**: web code targets latest React. No legacy class components, no IE shims.

### Tests

| Layer | Path | Purpose |
|---|---|---|
| Unit | `tests/unit/` | Per-module pure-Python tests |
| Integration | `tests/integration/` | Cross-module wiring (wheel ↔ modes ↔ cartas) |
| UAT | `tests/uat/` | Book-canonical scenario tests — these are the spec |

## Testing Discipline

**Three levels, no exceptions.**

1. **Contract tests (TDD)** — define the interface in `modes.py` / `wheel.py` first, write 2-3 contract tests before implementing.
2. **Unit tests** — each module in isolation.
3. **Integration tests** — every cross-module seam. If `Wheel.mode_for(note)` consumes `ALL_MODES` from `modes`, there is an integration test that wires real `ALL_MODES` through real `Wheel`.

### Required Integration Tests (book-anchored)

| Feature | Integration Test |
|---|---|
| Wheel rotation matches book | `Wheel("F").mode_for("D")` → "Frigio" (book §Wheel example) |
| A-tonic default holds across modules | `world("A")`, `mode_for("A")`, `carta(1)` all return the Eólico/⋮/red triple |
| Pentatonic-first | The 5 penta worlds are members of `DODECAMUNDO` with the same shape as the 7 Greek; no separate "penta path" |
| Carta ↔ wheel parity | For each carta `n`, its `(glyph, color, mode)` matches `Wheel("A").role_at_hour(n)` |
| SVG renderer is pure | `svg.render_wheel(...)` is deterministic — same input → byte-identical SVG |
| Web data export round-trip | `build_gatople_data.py` output → loaded in TS → renders the same wheel the Python `gallery` produces |

### UAT Scenarios

Live in `tests/uat/`. These are **the spec** — they encode book examples (chord progressions, mode shifts, carta spellings). Failing UAT = either book misread or implementation drift; never silently patch.

## Pattern Reference

### Greenfield-First

No legacy compat. No fallback paths. No "kept for old behavior" code. Modern Python (3.11+), modern React. If you see a deprecated pattern, kill it.

### Data Conventions

- All value objects: `@dataclass(frozen=True, slots=True)`
- Constants: `Final[...]` with `UPPER_SNAKE_CASE`
- IDs/labels: `Literal[...]` types where the set is closed (mode names, glyph chars)
- Module-level singletons (`DODECAMUNDO`, `ALL_MODES`, `PENTA_ROOTS`) — OK because they are pure data, not behavior with hidden deps. Wheel construction stays a function, not a singleton.

### No Hardcoded Strings

Mode names, glyph chars, role colors — all promoted to constants in `modes`, `symbols`, `colors`. Never inline `"Eólico"` or `"⋮"` in a second module. Use the constant.

### Imports

- Direct imports only; no `if TYPE_CHECKING:`.
- Public API is `fractalmusic.__init__`'s explicit re-exports — anything not re-exported is internal.

### Function Arguments

- All parameters typed.
- Pass by name on call sites (`Wheel(tonic="A")`, not `Wheel("A")` in library code — the README/docstrings can stay positional for readability).

### Docstrings

One-liner. Type hints carry the rest. No parameter lists.

## CEMAF + Meridian Integration (the fractal expert)

The system the user is building also feeds back into itself: agents become experts on the Sistema Fractal by retrieving from the indexed corpus.

### Wiring (already in place)

```
~/.meridian/library/                     # SQLite + BM25 + nomic-embed vectors
  ├─ books: f39cb7c5 (Fractal Music World 2025)
  │         b202598c (El Metodo Fractal Cap 0)
  └─ usage: meridian-library search ... --hybrid

meridian_library.CemafBM25VectorStore    # implements cemaf.retrieval.protocols.VectorStore
  ↓
cemaf.agents.Researcher / Librarian      # standard CEMAF agents, scope retrieval to fractal book hashes
  ↓
DAGExecutor                              # answer questions, cite chunks (book + chapter + page)
```

### Constraint

The expert agent **cites by chunk** — book hash, chapter index, paragraph, page. Answers without `(book_hash, page)` provenance are rejected. This matches CEMAF's citation discipline (`citation/tracker.py`) and meridian's chunk metadata.

### Scope rule

Retrieval is filtered to the two fractal book hashes by default. Cross-book reasoning (e.g. fractal ↔ pytheory ↔ etno-matemática) is opt-in: pass extra `--book` hashes explicitly. No silent corpus-wide bleed.

### What the expert is NOT

- Not a code generator. The Python core is human-authored against the book. The agent answers *questions about the system* and surfaces *book passages*; it does not write `wheel.py`.
- Not a pedagogy substitute. The wheel is geometric. The agent narrates; the cartas teach.

## Git Workflow

- Branch naming: `<user>/<scope>/<short-desc>` (current: `drchinca/functional-surface-v1`).
- Conventional commits: `feat(compose): ...`, `fix(gatople): ...` — match recent history.
- No AI attribution in commits.
- PR size ≤ 500 lines preferred, ≤ 900 hard cap.
- Never merge to `master` without explicit user say-so.

## Anti-Patterns

- **Re-deriving the wheel in JS/TS.** The web app is a renderer over JSON snapshots. If you need new behavior, add it to the Python core and re-emit.
- **Hard-coding "D is Dorian".** Use `Wheel(...).mode_for(...)` — function is on the wheel.
- **Silent A-origin shift.** If a function changes tonic, it must take `tonic=` as a named arg or operate through a `Wheel`. Never imply tonic from caller context.
- **Splitting penta from hepta.** Both are members of the 12-role wheel. Branching on `mode.is_penta` to take a different code path is almost always wrong.
- **"Fractal expert" without citations.** Any agent answer about the system must point to a chunk in the indexed books.

## Glossary

| Term | Meaning |
|---|---|
| **A-origin** | Matriarchal default: tonic = A, index 0 = A, Eólico horizon |
| **Gátople** | The two-disc spinner clock — outer roles, inner notes |
| **Dodecamundo** | The 12 note-worlds (5 penta + 7 heptatonic) on the wheel |
| **Carta** | One of the 12 canonical hand-painted cards: `(glyph, color, default-note, mode)` |
| **Role** | A fixed clock-position with `(glyph, color, scale-pattern)` — outer disc |
| **Spin** | Rotate the inner disc to put a chosen note under `⋮` (Eólico position) |
| **Penta-first** | Scales derived from the 5 penta skeletons; heptatonic is the same wheel, not a superset |
| **Etno-matemática** | The PHI / chessboard / consonance ratios in `formulas.py` — book-sourced |

## References

- Book: *El Sistema Fractal* (Patricio Torres, 2024) — `[b202598c]` in `~/.meridian/library`
- Book: *2025 Fractal Music World* — `[f39cb7c5]` in `~/.meridian/library`
- Method intro: `./QUE_ES_FRACTALWORLD.md`
- Upstream: `pytheory` (Tones, intervals)
- Sibling: `iccha_context_multi_agent/cemaf` (agent framework), `iccha_context_multi_agent/meridian_library` (retrieval)
