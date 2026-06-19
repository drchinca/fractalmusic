from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from chat_bff.app import create_app
from chat_bff.protocols import RetrievedChunk
from chat_bff.services import ChatServices
from chat_bff.settings import ChatSettings
from tests.integration.conftest import FakeLLM, FakeRetriever


async def _always_high(_claim: str, _snippet: str) -> float:
    return 0.9


def test_generate_strudel_route_returns_code(
    tmp_path: Path,
    fake_retriever: FakeRetriever,
    fake_claude: FakeLLM,
    fake_ollama: FakeLLM,
) -> None:
    from fractalmusic.generate import JsonCorpus, StubExpert

    settings = ChatSettings(
        anthropic_api_key="test-key-not-real",
        corpus_root=tmp_path / "patterns",
        audio_cache_dir=tmp_path / "generated",
        audio_cache_url="/generated",
    )
    services = ChatServices(
        retriever=fake_retriever,
        llm_claude=fake_claude,
        llm_ollama=fake_ollama,
        similarity=_always_high,
        settings=settings,
        expert=StubExpert(),
        corpus=JsonCorpus(root=settings.corpus_root),
    )
    fake_retriever.default = (
        RetrievedChunk(
            book_hash="b202598c",
            book_title="El Sistema Fractal",
            chapter_idx=4,
            section_idx=1,
            paragraph_idx=7,
            page_start=42,
            text="La rueda ordena modos, funciones y ciclos para sostener el centro.",
        ),
    )
    client = TestClient(create_app(services=services))

    response = client.post(
        "/api/generate/strudel",
        json={"tonic": "A", "mode": "Eólico", "length": 4, "flavor": "free"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["schema_version"] == 1
    assert body["pattern_name"] == "free:A-Eólico"
    assert body["code"].startswith("// Fractal Music: free:A-Eólico")
    assert "setcps(96 / 60 / 4)" in body["code"]
    assert body["generated_from"]["events"][0]["note"] == "A"
    assert body["generated_from"]["audio_url"].startswith("/generated/")
    assert body["book_guidance"][0]["book_hash"] == "b202598c"
    assert body["book_guidance"][0]["page_start"] == 42
    assert "Strudel" in body["book_guidance"][0]["strudel_use"]
    assert "// book 1: b202598c p.42 El Sistema Fractal" in body["code"]
    assert body["warnings"] == []

    wav_name = body["generated_from"]["audio_url"].removeprefix("/generated/")
    assert (settings.audio_cache_dir / wav_name).exists()


def test_generate_strudel_route_falls_back_when_book_chunks_are_weak(
    tmp_path: Path,
    fake_retriever: FakeRetriever,
    fake_claude: FakeLLM,
    fake_ollama: FakeLLM,
) -> None:
    from fractalmusic.generate import JsonCorpus, StubExpert

    settings = ChatSettings(
        anthropic_api_key="test-key-not-real",
        corpus_root=tmp_path / "patterns",
        audio_cache_dir=tmp_path / "generated",
        audio_cache_url="/generated",
    )
    services = ChatServices(
        retriever=fake_retriever,
        llm_claude=fake_claude,
        llm_ollama=fake_ollama,
        similarity=_always_high,
        settings=settings,
        expert=StubExpert(),
        corpus=JsonCorpus(root=settings.corpus_root),
    )
    fake_retriever.default = (
        RetrievedChunk(
            book_hash="f39cb7c5",
            book_title="Fractal Music World",
            chapter_idx=0,
            section_idx=0,
            paragraph_idx=14,
            page_start=21,
            text="Resultados de redes sociales, feria, negocios, Instagram y LinkedIn.",
        ),
    )
    client = TestClient(create_app(services=services))

    response = client.post(
        "/api/generate/strudel",
        json={"tonic": "A", "mode": "Eólico", "length": 4, "flavor": "free"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["book_guidance"][0]["book_hash"] == "b202598c"
    assert body["book_guidance"][0]["book_title"] == "El Sistema Fractal (Patricio Torres, 2024)"
    assert "Strudel orquesta timbre" in body["book_guidance"][0]["strudel_use"]
