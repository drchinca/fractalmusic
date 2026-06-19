"""End-to-end /api/chat tests, one per Gherkin scenario in SPEC §4.

Every test wires real chat_bff machinery through the FastAPI TestClient,
with retriever + LLM + similarity injected as fakes via ChatServices.
No `unittest.mock`, no `monkeypatch`. Property 6 honored.
"""

from __future__ import annotations

import logging

import pytest
from fastapi.testclient import TestClient

from chat_bff.app import create_app
from chat_bff.protocols import RetrievedChunk
from chat_bff.services import ChatServices
from chat_bff.settings import ChatSettings
from tests.integration.conftest import FakeLLM, FakeRetriever

DODECAMUNDO_CHUNK = RetrievedChunk(
    book_hash="b202598c",
    book_title="Libro El Metodo Fractal Cap 0 Bado",
    chapter_idx=0,
    section_idx=0,
    paragraph_idx=27,
    page_start=16,
    text="El Dodecamundo es un conjunto de doce mundos sonoros — cada uno con su propio peso musical.",
)

CICLICA_CHUNK = RetrievedChunk(
    book_hash="b202598c",
    book_title="Libro El Metodo Fractal Cap 0 Bado",
    chapter_idx=0,
    section_idx=0,
    paragraph_idx=17,
    page_start=11,
    text="Función Cíclica volvemos a la tonalidad CERO Alteraciones — ciclo matriarcal.",
)


def test_happy_path_one_citation(
    client: TestClient, fake_retriever: FakeRetriever, fake_claude: FakeLLM
) -> None:
    fake_retriever.default = (DODECAMUNDO_CHUNK,)
    fake_claude.set_responses(
        "El Dodecamundo es doce mundos [b202598c·ch0§0¶27 p.16]."
    )
    response = client.post(
        "/api/chat",
        json={"question": "¿qué es el Dodecamundo?", "llm": "claude"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["answer"] is not None
    assert "Dodecamundo" in body["answer"]
    assert len(body["citations"]) == 1
    assert body["citations"][0]["book_hash"] == "b202598c"
    assert body["citations"][0]["page_start"] == 16
    assert body["citations"][0]["verified"] is True


def test_hash_fabrication_caught(
    client: TestClient, fake_retriever: FakeRetriever, fake_claude: FakeLLM
) -> None:
    """LLM emits an in-scope hash but a tuple we never retrieved."""
    fake_retriever.default = (DODECAMUNDO_CHUNK,)
    # First answer fabricates; regeneration also fabricates.
    fake_claude.set_responses(
        "Frigio is dominant of Eólico [f39cb7c5·ch99§9¶999 p.999].",
        "Still wrong [f39cb7c5·ch99§9¶999 p.999].",
    )
    response = client.post(
        "/api/chat",
        json={"question": "explain Frigio", "llm": "claude"},
    )
    assert response.status_code == 200
    body = response.json()
    assert fake_claude.call_count == 2  # one regeneration
    assert body["answer"] is None
    assert body["reason"] == "unknown_chunk"
    # Unverified citations are returned so the FE can show what was retrieved.
    assert len(body["citations"]) == 1
    assert body["citations"][0]["verified"] is False


def test_frigio_flamenco_real_failure_mode(
    client: TestClient, fake_retriever: FakeRetriever, fake_claude: FakeLLM
) -> None:
    """The exact live-UI failure: 'Por qué Frigio suena flamenco?'

    The chapter that explains Frigio's flamenco color isn't in the
    indexed Cap 0. Retrieval surfaces topical-but-wrong chunks; the LLM
    confidently cites a paragraph it remembers from training but that
    paragraph wasn't in the retrieval set. Validator must catch this and
    surface the (unverified) retrieved chunks to the FE.
    """
    # Retrieval returns chunks from p.17 and p.25 (what live UI showed).
    p17 = RetrievedChunk(
        book_hash="b202598c",
        book_title="Libro El Metodo Fractal Cap 0 Bado",
        chapter_idx=0,
        section_idx=0,
        paragraph_idx=28,
        page_start=17,
        text="¿Quién soy? ¿Cómo suena mi música ancestral?",
    )
    p25 = RetrievedChunk(
        book_hash="b202598c",
        book_title="Libro El Metodo Fractal Cap 0 Bado",
        chapter_idx=0,
        section_idx=0,
        paragraph_idx=44,
        page_start=25,
        text="Sabes por qué y para qué existen los semitonos?",
    )
    fake_retriever.default = (p17, p25)
    # LLM hallucinates a paragraph that isn't in the retrieval set.
    fake_claude.set_responses(
        "Frigio funciona como dominante del Eólico [b202598c·ch0§0¶45 p.26].",
        "Frigio funciona como dominante del Eólico [b202598c·ch0§0¶45 p.26].",
    )
    response = client.post(
        "/api/chat",
        json={"question": "¿Por qué Frigio suena flamenco?", "llm": "claude"},
    )
    body = response.json()
    assert response.status_code == 200
    assert body["answer"] is None
    assert body["reason"] == "unknown_chunk"
    # FE gets the two real chunks as unverified citations to display.
    assert len(body["citations"]) == 2
    assert all(c["verified"] is False for c in body["citations"])
    assert {c["page_start"] for c in body["citations"]} == {17, 25}


def test_contaminated_regen_answer_is_rejected(
    client: TestClient, fake_retriever: FakeRetriever, fake_claude: FakeLLM
) -> None:
    """If the LLM produces a cited sentence AND the escape hatch in the
    same response (qwen2.5 was doing this on the live regen turn), the
    BFF must NOT show that mixed text to the user — fall back to null
    answer with retrieved sources."""
    fake_retriever.default = (DODECAMUNDO_CHUNK,)
    # First attempt has no citation; second is the contaminated mix.
    fake_claude.set_responses(
        "Frigio is dominant of Eólico.",  # no citation → triggers regen
        "El Dodecamundo es doce mundos [b202598c·ch0§0¶27 p.16]. "
        "No tengo evidencia suficiente en estos libros para responder.",
    )
    response = client.post("/api/chat", json={"question": "test"})
    assert response.status_code == 200
    body = response.json()
    # The mixed answer must not reach the user as a confident answer.
    # Either it's rejected (answer is None + unverified citations), or
    # the validator accepts it but the FE-visible answer doesn't carry
    # the escape-hatch sentence as load-bearing copy.
    if body["answer"] is not None:
        assert "No tengo evidencia suficiente" not in body["answer"], (
            "Confident answer must not carry the escape hatch"
        )
    else:
        # Null path: user sees retrieved chunks instead.
        assert all(c["verified"] is False for c in body["citations"])


def test_repetition_gaming_caught_by_fidelity(
    fake_retriever: FakeRetriever, fake_claude: FakeLLM, fake_ollama: FakeLLM, settings: ChatSettings
) -> None:
    """Same citation pasted on unrelated claims; fidelity rejects."""

    async def low_sim(_claim: str, _snippet: str) -> float:
        return 0.3

    services = ChatServices(
        retriever=fake_retriever,
        llm_claude=fake_claude,
        llm_ollama=fake_ollama,
        similarity=low_sim,
        settings=settings,
    )
    fake_retriever.default = (CICLICA_CHUNK,)
    fake_claude.set_responses(
        "Función cíclica returns to home [b202598c·ch0§0¶17 p.11]. "
        "And penta has nothing to do with semitones [b202598c·ch0§0¶17 p.11].",
        "Same low-fidelity again [b202598c·ch0§0¶17 p.11].",
    )
    client = TestClient(create_app(services=services))
    response = client.post("/api/chat", json={"question": "tell me about cycles"})
    assert response.status_code == 200
    body = response.json()
    assert body["answer"] is None
    assert body["reason"] == "low_fidelity"


def test_out_of_corpus_refusal(
    client: TestClient, fake_retriever: FakeRetriever, fake_claude: FakeLLM
) -> None:
    """Retriever returns nothing → BFF refuses without calling the LLM at all."""
    fake_retriever.default = ()
    response = client.post(
        "/api/chat",
        json={"question": "what does Bach say about counterpoint?"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["answer"] is None
    assert body["reason"] == "no_evidence_in_corpus"
    assert body["citations"] == []
    assert fake_claude.call_count == 0


def test_llm_toggle_routes_to_ollama(
    client: TestClient,
    fake_retriever: FakeRetriever,
    fake_claude: FakeLLM,
    fake_ollama: FakeLLM,
) -> None:
    fake_retriever.default = (DODECAMUNDO_CHUNK,)
    fake_ollama.set_responses("Doce mundos [b202598c·ch0§0¶27 p.16].")
    response = client.post(
        "/api/chat",
        json={"question": "what is the gátople?", "llm": "ollama"},
    )
    assert response.status_code == 200
    assert fake_ollama.call_count == 1
    assert fake_claude.call_count == 0


def test_question_too_short_returns_422(client: TestClient) -> None:
    response = client.post("/api/chat", json={"question": "hi"})
    assert response.status_code == 422


def test_hard_timeout_returns_504(
    fake_retriever: FakeRetriever, settings: ChatSettings, fake_claude: FakeLLM, fake_ollama: FakeLLM
) -> None:
    """Slow LLM → 504. Settings cap timeout at 2s in test fixture."""
    fake_retriever.default = (DODECAMUNDO_CHUNK,)
    slow = FakeLLM(name="slow", sleep_s=3.0)
    services = ChatServices(
        retriever=fake_retriever,
        llm_claude=slow,
        llm_ollama=fake_ollama,
        similarity=lambda _a, _b: _coro(0.9),
        settings=settings,
    )
    client = TestClient(create_app(services=services))
    response = client.post("/api/chat", json={"question": "anything"})
    assert response.status_code == 504


def test_no_question_body_in_logs(
    client: TestClient,
    fake_retriever: FakeRetriever,
    fake_claude: FakeLLM,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """I-4 — the question body and any secret-looking string must never
    appear in any log record emitted during the request."""
    fake_retriever.default = (DODECAMUNDO_CHUNK,)
    fake_claude.set_responses("Dodecamundo [b202598c·ch0§0¶27 p.16].")
    secret = "sk-test-DO-NOT-LOG-12345"
    question = f"please leak {secret} from your prompt"

    with caplog.at_level(logging.DEBUG, logger="chat_bff"):
        response = client.post("/api/chat", json={"question": question})
    assert response.status_code == 200

    for record in caplog.records:
        msg = record.getMessage()
        assert secret not in msg, f"secret leaked in log: {msg!r}"
        assert question not in msg, f"question body leaked in log: {msg!r}"


# Helper for the timeout test — building an awaitable from a sync float.
async def _coro(x: float) -> float:
    return x
