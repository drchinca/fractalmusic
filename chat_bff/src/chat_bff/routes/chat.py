"""POST /api/chat — the whole pipeline in one place.

The route owns: question validation → retrieval → prompt → LLM →
parse → validate → maybe regenerate → final response. No module-level
singletons; every dependency comes through ``Depends(get_services)``
and is overridable in tests via ``app.dependency_overrides``.
"""

import asyncio
import time
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request

from chat_bff import prompts
from chat_bff.citations import parse_answer, validate_answer
from chat_bff.citations.validator import ValidationOutcome, ValidationVerdict
from chat_bff.models import SCOPE, ChatRequest, ChatResponse, Citation, LLMChoice
from chat_bff.protocols import LLM, RetrievedChunk
from chat_bff.services import ChatServices

router = APIRouter()
log = structlog.get_logger("chat_bff.chat")


def get_services(request: Request) -> ChatServices:
    """FastAPI dependency. Tests override this via app.dependency_overrides."""
    services = getattr(request.app.state, "services", None)
    if services is None:
        raise RuntimeError("ChatServices not attached to app.state — wire create_app correctly.")
    return services


def _pick_llm(services: ChatServices, choice: LLMChoice) -> LLM:
    return services.llm_claude if choice == LLMChoice.CLAUDE else services.llm_ollama


def _chunk_to_payload(c: RetrievedChunk) -> dict:
    return {
        "book_hash": c.book_hash,
        "book_title": c.book_title,
        "chapter_idx": c.chapter_idx,
        "section_idx": c.section_idx,
        "paragraph_idx": c.paragraph_idx,
        "page_start": c.page_start,
        "text": c.text,
    }


def _chunks_as_unverified_citations(chunks: tuple[RetrievedChunk, ...]) -> tuple[Citation, ...]:
    """Surface what we retrieved so the FE can render 'here's what I
    found' even when the LLM didn't ground in it."""
    return tuple(
        Citation(
            book_hash=c.book_hash,
            book_title=c.book_title,
            chapter_idx=c.chapter_idx,
            section_idx=c.section_idx,
            paragraph_idx=c.paragraph_idx,
            page_start=c.page_start,
            snippet=c.text[:2000],
            verified=False,
        )
        for c in chunks
    )


def _build_verified_citations(
    *,
    outcome: ValidationOutcome,
    chunks_by_key: dict[tuple[str, int, int, int], RetrievedChunk],
) -> tuple[Citation, ...]:
    """Hydrate verified ParsedCitation tuples into Citation responses."""
    out: list[Citation] = []
    for cite in outcome.verified:
        chunk = chunks_by_key[(cite.book_hash, cite.chapter_idx, cite.section_idx, cite.paragraph_idx)]
        out.append(
            Citation(
                book_hash=chunk.book_hash,
                book_title=chunk.book_title,
                chapter_idx=chunk.chapter_idx,
                section_idx=chunk.section_idx,
                paragraph_idx=chunk.paragraph_idx,
                page_start=chunk.page_start,
                snippet=chunk.text[:2000],
                verified=True,
            )
        )
    return tuple(out)


def _retrieved_in_scope(chunks: tuple[RetrievedChunk, ...]) -> tuple[RetrievedChunk, ...]:
    """I-1 enforcement at the boundary: drop anything outside the two books."""
    return tuple(c for c in chunks if c.book_hash in SCOPE)


async def _call_llm(llm: LLM, *, system: str, user: str, timeout_s: float) -> str:
    return await asyncio.wait_for(llm.complete(system=system, user=user), timeout=timeout_s)


@router.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    services: Annotated[ChatServices, Depends(get_services)],
) -> ChatResponse:
    started = time.monotonic()

    # 1. Retrieval, scope-filtered.
    raw = await services.retriever.search(
        question=request.question, k=services.settings.retrieval_k
    )
    chunks = _retrieved_in_scope(raw)

    if not chunks:
        log.info("chat.no_evidence")
        return ChatResponse(
            llm=request.llm,
            answer=None,
            citations=(),
            reason="no_evidence_in_corpus",
            elapsed_ms=int((time.monotonic() - started) * 1000),
        )

    chunks_by_key = {
        (c.book_hash, c.chapter_idx, c.section_idx, c.paragraph_idx): c for c in chunks
    }
    retrieved_lookup = {k: v.text for k, v in chunks_by_key.items()}

    # 2. Build prompt.
    prompt = prompts.load("citation_strict")
    payloads = [_chunk_to_payload(c) for c in chunks]
    user_msg = prompts.render(
        prompt.template,
        passages=prompts.format_passages(payloads),
        question=request.question,
    )
    llm = _pick_llm(services, request.llm)

    # 3. LLM call → parse → validate, with one regeneration on failure.
    outcome: ValidationOutcome | None = None
    answer_text: str | None = None
    attempts = 1 + services.settings.max_regenerations
    last_failure_reason: str | None = None

    for attempt in range(attempts):
        try:
            answer_text = await _call_llm(
                llm,
                system="You are a careful reader of music-theory books.",
                user=user_msg if attempt == 0 else (
                    user_msg + "\n\nYour previous answer was rejected. "
                    "Cite ONLY the passages above, by their exact book_hash and tuple, "
                    "and ground every fact-bearing sentence in a passage that actually supports it."
                ),
                timeout_s=services.settings.request_timeout_s,
            )
        except TimeoutError as e:
            log.warning("chat.timeout")
            raise HTTPException(status_code=504, detail="upstream_llm_timeout") from e
        except Exception as e:
            log.exception("chat.upstream_llm_failed")
            raise HTTPException(status_code=502, detail="upstream_llm_unavailable") from e

        claims = parse_answer(answer_text)
        outcome = await validate_answer(
            claims=claims,
            retrieved=retrieved_lookup,
            similarity=services.similarity,
            threshold=services.settings.fidelity_threshold,
        )
        if outcome.verdict == ValidationVerdict.OK:
            log.info("chat.success", attempt=attempt + 1, citations=len(outcome.verified))
            break
        last_failure_reason = outcome.verdict.value
        log.info("chat.regenerating", attempt=attempt + 1, reason=last_failure_reason)

    elapsed_ms = int((time.monotonic() - started) * 1000)

    if outcome is None or outcome.verdict != ValidationVerdict.OK:
        # Validation never converged. Surface the retrieval as unverified
        # citations so the FE can show "here's what I found".
        return ChatResponse(
            llm=request.llm,
            answer=None,
            citations=_chunks_as_unverified_citations(chunks),
            reason=last_failure_reason or "citation_validation_failed",
            elapsed_ms=elapsed_ms,
        )

    return ChatResponse(
        llm=request.llm,
        answer=answer_text,
        citations=_build_verified_citations(outcome=outcome, chunks_by_key=chunks_by_key),
        reason=None,
        elapsed_ms=elapsed_ms,
    )
