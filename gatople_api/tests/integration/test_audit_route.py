"""Integration tests for the real CEMAF audit trail wired around
/api/generate* — a real EventBusAuditLog/InMemoryAuditTrail, not a fake,
since the whole point is proving the actual CEMAF subsystem records and
serves back what research_loop actually did."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from fractalmusic.generate import JsonCorpus, StubExpert

from gatople_api.app import create_app
from gatople_api.audit import build_audit_system
from gatople_api.llm_expert import LLMExpert
from gatople_api.services import GatopleServices
from gatople_api.settings import ChatSettings
from tests.integration.conftest import FakeLLM, FakeRetriever


async def _always_high(_claim: str, _snippet: str) -> float:
    return 0.9


def _client(tmp_path: Path) -> TestClient:
    settings = ChatSettings(
        anthropic_api_key="test-key-not-real",
        corpus_root=tmp_path / "patterns",
        audio_cache_dir=tmp_path / "generated",
        audio_cache_url="/generated",
    )
    audit_log, audit_trail = build_audit_system()
    fake_claude = FakeLLM(name="claude")
    services = GatopleServices(
        retriever=FakeRetriever(),
        llm_claude=fake_claude,
        llm_ollama=FakeLLM(name="ollama"),
        similarity=_always_high,
        settings=settings,
        expert=StubExpert(),
        llm_expert=LLMExpert(llm=fake_claude),
        corpus=JsonCorpus(root=settings.corpus_root),
        audit_log=audit_log,
        audit_trail=audit_trail,
    )
    return TestClient(create_app(services=services))


def test_generate_writes_a_real_queryable_audit_trail(tmp_path: Path) -> None:
    client = _client(tmp_path)

    response = client.post(
        "/api/generate",
        json={"tonic": "A", "mode": "Eólico", "length": 8, "flavor": "free"},
    )
    assert response.status_code == 200
    audio_url = response.json()["audio_url"]
    run_id = audio_url.removeprefix("/generated/").removesuffix(".wav")

    trail = client.get(f"/api/audit/{run_id}")

    assert trail.status_code == 200
    body = trail.json()
    assert body["run_id"] == run_id
    # 5 candidates (N_CANDIDATES, all from StubExpert since corpus starts
    # empty) + 1 summary entry.
    assert len(body["entries"]) == 6
    eval_entries = [e for e in body["entries"] if e["type"] == "eval.result"]
    summary_entries = [e for e in body["entries"] if e["type"] == "dag.completed"]
    assert len(eval_entries) == 5
    assert len(summary_entries) == 1
    assert all(e["source"] == "expert" for e in eval_entries)
    assert summary_entries[0]["payload"]["winner_source"] == "expert"
    # This is the actual point: a real score value per candidate, not a
    # placeholder.
    assert all(isinstance(e["payload"]["score"], (int, float)) for e in eval_entries)


def test_audit_trail_shows_corpus_winner_after_a_pattern_is_seeded(tmp_path: Path) -> None:
    # Same request body twice -> same content-addressed cache key -> same
    # run_id, so the timeline accumulates entries from BOTH requests (in
    # timestamp order, per InMemoryAuditTrail.get_run_timeline). The first
    # request's winner is necessarily "expert" (nothing in corpus yet);
    # the second's must be "corpus" (the first request's winner, now
    # persisted, scores high enough to beat 4 fresh expert candidates).
    client = _client(tmp_path)
    body = {"tonic": "A", "mode": "Eólico", "length": 8, "flavor": "free"}

    first = client.post("/api/generate", json=body)
    assert first.status_code == 200
    second = client.post("/api/generate", json=body)
    assert second.status_code == 200

    run_id = second.json()["audio_url"].removeprefix("/generated/").removesuffix(".wav")
    trail = client.get(f"/api/audit/{run_id}").json()

    summaries = [e for e in trail["entries"] if e["type"] == "dag.completed"]
    assert len(summaries) == 2
    assert summaries[0]["payload"]["winner_source"] == "expert"
    assert summaries[1]["payload"]["winner_source"] == "corpus"
    corpus_entries = [e for e in trail["entries"] if e["type"] == "eval.result" and e["source"] == "corpus"]
    assert len(corpus_entries) == 1
    assert corpus_entries[0]["payload"]["won"] is True


def test_unknown_run_id_returns_404(tmp_path: Path) -> None:
    client = _client(tmp_path)

    response = client.get("/api/audit/not-a-real-run-id")

    assert response.status_code == 404


def test_audit_unavailable_when_not_wired(tmp_path: Path) -> None:
    settings = ChatSettings(
        anthropic_api_key="test-key-not-real",
        corpus_root=tmp_path / "patterns",
    )
    fake_claude = FakeLLM(name="claude")
    services = GatopleServices(
        retriever=FakeRetriever(),
        llm_claude=fake_claude,
        llm_ollama=FakeLLM(name="ollama"),
        similarity=_always_high,
        settings=settings,
        expert=StubExpert(),
        llm_expert=LLMExpert(llm=fake_claude),
        corpus=JsonCorpus(root=settings.corpus_root),
    )
    client = TestClient(create_app(services=services))

    response = client.get("/api/audit/anything")

    assert response.status_code == 503
