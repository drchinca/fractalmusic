"""Production wiring. Builds a real GatopleServices from cemaf + meridian.

This is the only module that touches concrete adapters. The rest of the
package depends only on the protocols in gatople_api.protocols, so this is
also the only place to swap implementations later.
"""

from __future__ import annotations

import math
import os
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from cemaf.llm.anthropic import AnthropicLLMClient
from cemaf.llm.bedrock_cli import BedrockCliLLMClient
from cemaf.llm.openai_compat import OpenAICompatClient
from cemaf.llm.protocols import Message, MessageRole
from fastapi import FastAPI
from fractalmusic.generate import JsonCorpus, StubExpert
from meridian_library.embedders.ollama import OllamaEmbedder
from meridian_library.embedders.protocol import EmbeddingClient
from meridian_library.index.bm25_store import LibraryBM25Store
from meridian_library.index.book_catalog import SQLiteBookCatalog
from meridian_library.index.hybrid import LibraryHybridIndex
from meridian_library.index.vector_store import LibraryVectorStore

from gatople_api.models import in_scope, short_hash
from gatople_api.protocols import LLM, RetrievedChunk
from gatople_api.services import GatopleServices
from gatople_api.settings import ChatSettings

# ---------- LLM adapters: cemaf protocol → our flat .complete() ----------


@dataclass(frozen=True, slots=True)
class CemafLLMAdapter:
    """Wraps any cemaf LLMClient and exposes the gatople_api.protocols.LLM
    shape (one user message in, one assistant string out)."""

    name: str
    client: object  # cemaf LLMClient — duck-typed by .complete(messages=...)

    async def complete(self, *, system: str, user: str) -> str:
        result = await self.client.complete(  # type: ignore[attr-defined]
            messages=[
                Message(role=MessageRole.SYSTEM, content=system),
                Message(role=MessageRole.USER, content=user),
            ],
        )
        if not result.success:
            raise RuntimeError(f"{self.name} LLM error: {result.error}")
        return str(result.message.content)


# ---------- Retriever: hybrid index → in-scope RetrievedChunk tuple ----------


@dataclass
class MeridianRetriever:
    """Adapts the meridian LibraryHybridIndex to gatople_api's Retriever.

    Scope filter is applied here so the route only ever sees in-corpus chunks.
    """

    hybrid: LibraryHybridIndex
    catalog: SQLiteBookCatalog

    async def search(self, *, question: str, k: int) -> tuple[RetrievedChunk, ...]:
        # Over-fetch then filter to scope, in case some hits land outside
        # the two fractal books.
        chunks = await self.hybrid.search(query=question, k=k * 2)
        titles = {b.hash: b.title for b in self.catalog.list_books()}
        out: list[RetrievedChunk] = []
        for c in chunks:
            if not in_scope(c.book_hash):
                continue
            # Normalize to the friendly 8-char prefix everywhere downstream
            # (citation parser, prompt, FE chips). The full sha256 is only
            # meaningful inside meridian.
            out.append(
                RetrievedChunk(
                    book_hash=short_hash(c.book_hash),
                    book_title=titles.get(c.book_hash, short_hash(c.book_hash)),
                    chapter_idx=c.chapter_idx,
                    section_idx=c.section_idx,
                    paragraph_idx=c.paragraph_idx,
                    page_start=c.page_start,
                    text=c.text,
                )
            )
            if len(out) >= k:
                break
        return tuple(out)


# ---------- Similarity: cosine over nomic-embed ----------


def _cosine(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def make_similarity(embedder: EmbeddingClient) -> Callable[[str, str], Awaitable[float]]:
    async def score(claim: str, snippet: str) -> float:
        vectors = await embedder.embed(texts=(claim, snippet))
        return _cosine(vectors[0], vectors[1])

    return score


# ---------- Composition root ----------


def build_services(settings: ChatSettings | None = None) -> GatopleServices:
    """Wire production GatopleServices. Run once at app startup."""
    settings = settings or ChatSettings()

    bm25 = LibraryBM25Store(index_dir=settings.index_dir)
    embedder = OllamaEmbedder(
        base_url=settings.ollama_base_url,
        model=settings.embed_model,
    )
    vector = LibraryVectorStore(index_dir=settings.index_dir, embedder=embedder)
    hybrid = LibraryHybridIndex(bm25=bm25, vector=vector)
    catalog = SQLiteBookCatalog(index_dir=settings.index_dir)

    retriever = MeridianRetriever(hybrid=hybrid, catalog=catalog)

    ollama_llm: LLM = CemafLLMAdapter(
        name="ollama",
        client=OpenAICompatClient(
            base_url=f"{settings.ollama_base_url}/v1",
            model=settings.ollama_model,
        ),
    )

    if settings.anthropic_api_key:
        claude_llm: LLM = CemafLLMAdapter(
            name="claude",
            client=AnthropicLLMClient(
                api_key=settings.anthropic_api_key,
                model=settings.anthropic_model,
            ),
        )
    elif os.environ.get("AWS_BEARER_TOKEN_BEDROCK") or os.environ.get("AWS_PROFILE"):
        # No direct Anthropic key, but a Bedrock-capable AWS session is
        # present in the environment (bearer token or an SSO profile) —
        # route Claude through Bedrock instead of silently degrading to
        # Ollama. Same LLM protocol, same CemafLLMAdapter wrapping.
        claude_llm = CemafLLMAdapter(
            name="claude-bedrock",
            client=BedrockCliLLMClient(
                model=settings.bedrock_model,
                region=settings.bedrock_region,
                profile=os.environ.get("AWS_PROFILE"),
            ),
        )
    else:
        # Neither a direct key nor a Bedrock session — fall back to the
        # local Ollama model so the toggle still works in offline dev.
        # The user sees the same UI; the BFF just routes both choices to
        # Ollama.
        claude_llm = ollama_llm

    return GatopleServices(
        retriever=retriever,
        llm_claude=claude_llm,
        llm_ollama=ollama_llm,
        similarity=make_similarity(embedder),
        settings=settings,
        expert=StubExpert(),
        corpus=JsonCorpus(root=settings.corpus_root),
    )


# ---------- ASGI entry point for `uvicorn gatople_api.bootstrap:app_factory --factory` ----------


def app_factory() -> FastAPI:
    """Build a FastAPI app for `uvicorn gatople_api.bootstrap:app_factory --factory`."""
    from gatople_api.app import create_app

    return create_app(
        services=build_services(),
        cors_origins=(
            "http://localhost:5174",
            "http://127.0.0.1:5174",
        ),  # vite dev server
    )
