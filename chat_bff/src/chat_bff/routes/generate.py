"""POST /api/generate — runs the fractalmusic research loop, renders the
result to a real WAV the FE plays. BE owns all theory AND all synthesis;
FE never computes a note and never synthesizes a sample.

GET /api/generate/options — emits the closed sets (tonics, modes, flavors)
so the FE doesn't re-derive them.
"""

import hashlib
import json
from typing import Annotated, Literal

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request
from fractalmusic.generate import (
    Flavor,
    GenerationRequest,
    GenerationResult,
    StrudelBookGuidancePayload,
    StrudelPayload,
    WebPayload,
    research_loop,
)
from fractalmusic.generate.adapters import to_strudel_payload, to_web_payload
from fractalmusic.generate.realize import freq_for
from fractalmusic.generate.types import FLAVORS, MODE_NAMES, NOTE_NAMES
from fractalmusic.render import RenderConfig, render_wav
from pydantic import BaseModel, ConfigDict, Field

from chat_bff.models import in_scope, short_hash
from chat_bff.protocols import RetrievedChunk
from chat_bff.services import ChatServices

_DRONE_OCTAVE: int = 3
_STRUDEL_GUIDANCE_K: int = 3
_MIN_THEORY_SCORE: int = 2
_THEORY_TERMS: tuple[str, ...] = (
    "rueda",
    "modo",
    "modos",
    "gatople",
    "gátople",
    "funcion",
    "función",
    "ciclo",
    "cíclica",
    "pentat",
    "carta",
    "cartas",
    "dodecamundo",
    "cadencia",
    "escala",
    "matriz",
    "símbolo",
    "simbolo",
)
_NON_THEORY_TERMS: tuple[str, ...] = (
    "facebook",
    "feria",
    "instagram",
    "linkedin",
    "negocios",
    "resultados",
    "sociedad anónima",
    "sociedad anonima",
    "ticktoc",
    "tiktok",
)

router = APIRouter()
log = structlog.get_logger("chat_bff.generate")


def get_services(request: Request) -> ChatServices:
    services = getattr(request.app.state, "services", None)
    if services is None:
        raise RuntimeError("ChatServices not attached to app.state — wire create_app correctly.")
    return services


_NOTE_ORDER: tuple[str, ...] = (
    "A",
    "A#",
    "B",
    "C",
    "C#",
    "D",
    "D#",
    "E",
    "F",
    "F#",
    "G",
    "G#",
)
_MODE_ORDER: tuple[str, ...] = (
    "Eólico",
    "Locrio",
    "Jónico",
    "Dórico",
    "Frigio",
    "Lidio",
    "Mixolidio",
    "Penta 1",
    "Penta 2",
    "Penta 3",
    "Penta 4",
    "Penta 5",
)
_FLAVOR_ORDER: tuple[Flavor, ...] = ("free", "penta-walk", "carta-progression")


class GenerateBody(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    tonic: Annotated[str, Field(min_length=1, max_length=2)]
    mode: Annotated[str, Field(min_length=1, max_length=20)]
    length: Annotated[int, Field(ge=4, le=64)] = 16
    flavor: Literal["free", "penta-walk", "carta-progression"] = "free"


@router.get("/api/generate/options")
def generate_options() -> dict[str, list[str]]:
    return {
        "tonics": [n for n in _NOTE_ORDER if n in NOTE_NAMES],
        "modes": [m for m in _MODE_ORDER if m in MODE_NAMES],
        "flavors": [f for f in _FLAVOR_ORDER if f in FLAVORS],
    }


def _cache_key(*, tonic: str, mode: str, length: int, flavor: str, pattern_name: str) -> str:
    raw = f"{tonic}|{mode}|{length}|{flavor}|{pattern_name}".encode()
    return hashlib.sha256(raw).hexdigest()[:16]


def _generation_request(body: GenerateBody) -> GenerationRequest:
    return GenerationRequest(
        tonic=body.tonic,
        mode=body.mode,
        length_events=body.length,
        flavor=body.flavor,
    )


def _compact_text(value: str, *, limit: int = 520) -> str:
    normalized = " ".join(value.replace("\r", " ").replace("\n", " ").split())
    return normalized[:limit]


def _guidance_query(body: GenerateBody, result: GenerationResult) -> str:
    flavor_focus = {
        "free": "rueda de modos, ciclo, función modal, centro tonal, drone",
        "penta-walk": "pentatonía, caminar grados, escala sin error, ciclo",
        "carta-progression": "cartas, cadencia, función armónica, resolución",
    }[body.flavor]
    roles = " ".join(str(event.role_hour) for event in result.events[:16])
    glyphs = " ".join(event.carta_glyph for event in result.events[:16])
    return (
        "Cómo usar los libros fractales para live coding en Strudel: "
        f"{body.tonic} {body.mode}, estilo {body.flavor}. "
        f"Buscar evidencia sobre {flavor_focus}. "
        f"Roles generados: {roles}. Cartas generadas: {glyphs}."
    )


def _strudel_use_for_chunk(
    *,
    body: GenerateBody,
    result: GenerationResult,
    chunk: RetrievedChunk,
    index: int,
) -> str:
    text = chunk.text.lower()
    if body.flavor == "carta-progression" or "carta" in text or "cadencia" in text:
        return (
            "Mapear las cartas y funciones como capas Strudel: melodía arriba, "
            "bajo/drone como centro, beats marcando resolución del ciclo."
        )
    if body.flavor == "penta-walk" or body.mode.startswith("Penta") or "penta" in text:
        return (
            "Mantener el loop dentro del camino pentatónico y usar variaciones "
            "de speed, delay y hats sin romper la escala."
        )
    if index == 0:
        return (
            f"Conservar {result.pattern.tonic} {result.pattern.mode} como regla modal; "
            "Strudel orquesta timbre, repetición, filtro y espacio sin recalcular notas."
        )
    return (
        "Usar el pasaje como referencia de forma: repetir, densificar o soltar "
        "capas mientras la secuencia fractal sigue siendo la fuente."
    )


def _fallback_book_guidance(
    *,
    body: GenerateBody,
    result: GenerationResult,
) -> list[StrudelBookGuidancePayload]:
    provenance = result.pattern.provenance
    quote = provenance.quote or (
        f"{result.pattern.tonic} {result.pattern.mode} desde la rueda fractal."
    )
    return [
        {
            "book_hash": short_hash(provenance.book_hash),
            "book_title": provenance.book_title,
            "chapter_idx": 0,
            "section_idx": 0,
            "paragraph_idx": 0,
            "page_start": provenance.page or 0,
            "snippet": _compact_text(quote),
            "strudel_use": _strudel_use_for_chunk(
                body=body,
                result=result,
                chunk=RetrievedChunk(
                    book_hash=provenance.book_hash,
                    book_title=provenance.book_title,
                    chapter_idx=0,
                    section_idx=0,
                    paragraph_idx=0,
                    page_start=provenance.page or 0,
                    text=quote,
                ),
                index=0,
            ),
        }
    ]


def _guidance_relevance_score(chunk: RetrievedChunk, body: GenerateBody) -> int:
    text = chunk.text.lower()
    score = sum(1 for term in _THEORY_TERMS if term in text)
    score -= sum(2 for term in _NON_THEORY_TERMS if term in text)
    score += 2 if body.mode.lower() in text else 0
    if body.flavor == "penta-walk":
        score += 2 if "penta" in text else 0
    if body.flavor == "carta-progression":
        score += 2 if "carta" in text or "cadencia" in text else 0
    return score


def _chunk_to_strudel_guidance(
    *,
    body: GenerateBody,
    result: GenerationResult,
    chunk: RetrievedChunk,
    index: int,
) -> StrudelBookGuidancePayload:
    return {
        "book_hash": short_hash(chunk.book_hash),
        "book_title": chunk.book_title,
        "chapter_idx": chunk.chapter_idx,
        "section_idx": chunk.section_idx,
        "paragraph_idx": chunk.paragraph_idx,
        "page_start": chunk.page_start,
        "snippet": _compact_text(chunk.text),
        "strudel_use": _strudel_use_for_chunk(
            body=body,
            result=result,
            chunk=chunk,
            index=index,
        ),
    }


async def _book_guidance_for_strudel(
    *,
    body: GenerateBody,
    result: GenerationResult,
    services: ChatServices,
) -> list[StrudelBookGuidancePayload]:
    try:
        chunks = await services.retriever.search(
            question=_guidance_query(body=body, result=result),
            k=max(services.settings.retrieval_k, _STRUDEL_GUIDANCE_K * 2),
        )
    except Exception as error:
        log.warning("generate.strudel_guidance_failed", error=str(error))
        return []

    scoped = tuple(chunk for chunk in chunks if in_scope(chunk.book_hash))
    ranked = sorted(
        enumerate(scoped),
        key=lambda item: (_guidance_relevance_score(item[1], body), -item[0]),
        reverse=True,
    )
    selected = tuple(
        chunk
        for _, chunk in ranked
        if _guidance_relevance_score(chunk, body) >= _MIN_THEORY_SCORE
    )[:_STRUDEL_GUIDANCE_K]
    if not selected:
        return _fallback_book_guidance(body=body, result=result)
    return [
        _chunk_to_strudel_guidance(
            body=body,
            result=result,
            chunk=chunk,
            index=index,
        )
        for index, chunk in enumerate(selected)
    ]


def _research(body: GenerateBody, services: ChatServices) -> GenerationResult:
    try:
        request = _generation_request(body)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    try:
        return research_loop(
            request=request,
            expert=services.expert,
            corpus=services.corpus,
        )
    except (OSError, json.JSONDecodeError) as error:
        log.exception("generate.corpus_io_failed")
        raise HTTPException(status_code=500, detail="corpus_io_failed") from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


def _render_web_payload(
    body: GenerateBody,
    services: ChatServices,
) -> tuple[GenerationResult, WebPayload]:
    result = _research(body=body, services=services)
    settings = services.settings
    cache_dir = settings.audio_cache_dir
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = _cache_key(
        tonic=body.tonic,
        mode=body.mode,
        length=body.length,
        flavor=body.flavor,
        pattern_name=result.pattern.name,
    )
    wav_path = cache_dir / f"{key}.wav"

    if not wav_path.exists():
        tonic_freq = freq_for(note=result.pattern.tonic, octave=_DRONE_OCTAVE)
        try:
            render_wav(
                result.events,
                out_path=wav_path,
                config=RenderConfig(
                    bpm=result.web_payload["bpm"],
                    sf2_path=settings.soundfont_path,
                    ir_path=settings.reverb_ir_path,
                ),
                tonic_freq_hz=tonic_freq,
            )
            log.info("generate.rendered", key=key, bytes=wav_path.stat().st_size)
        except Exception as error:
            log.exception("generate.render_failed")
            raise HTTPException(status_code=500, detail=f"render_failed: {error}") from error

    audio_url = f"{settings.audio_cache_url}/{key}.wav"
    payload = to_web_payload(
        pattern=result.pattern,
        events=result.events,
        score=result.score,
        bpm=result.web_payload["bpm"],
        audio_url=audio_url,
    )

    log.info(
        "generate.success",
        score=result.score.total,
        band=result.score.band,
        events=len(result.events),
        audio_url=audio_url,
    )
    return result, payload


@router.post("/api/generate")
def generate(
    body: GenerateBody,
    services: Annotated[ChatServices, Depends(get_services)],
) -> WebPayload:
    _, payload = _render_web_payload(body=body, services=services)
    return payload


@router.post("/api/generate/strudel")
async def generate_strudel(
    body: GenerateBody,
    services: Annotated[ChatServices, Depends(get_services)],
) -> StrudelPayload:
    result, web_payload = _render_web_payload(body=body, services=services)
    book_guidance = await _book_guidance_for_strudel(
        body=body,
        result=result,
        services=services,
    )
    return to_strudel_payload(
        pattern=result.pattern,
        events=result.events,
        score=result.score,
        bpm=result.web_payload["bpm"],
        web_payload=web_payload,
        book_guidance=book_guidance,
    )
