"""Test doubles + fixtures. No mocks, no monkeypatch — every fake is a
real class implementing the production protocol, swapped at the
ChatServices boundary."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

import pytest
from fastapi.testclient import TestClient

from chat_bff.app import create_app
from chat_bff.protocols import RetrievedChunk
from chat_bff.services import ChatServices
from chat_bff.settings import ChatSettings


@dataclass
class FakeRetriever:
    chunks_by_question: dict[str, tuple[RetrievedChunk, ...]] = field(default_factory=dict)
    default: tuple[RetrievedChunk, ...] = ()

    async def search(self, *, question: str, k: int) -> tuple[RetrievedChunk, ...]:
        return self.chunks_by_question.get(question, self.default)[:k]


@dataclass
class FakeLLM:
    """Returns a queue of pre-primed responses, one per call.

    Use ``set_responses(...)`` to load the queue. ``call_count`` exposes
    how many times complete() was invoked. ``sleep_s`` lets us simulate
    a slow LLM for the timeout scenario."""

    name: str = "fake"
    sleep_s: float = 0.0
    _responses: list[str] = field(default_factory=list)
    call_count: int = 0
    last_user: str = ""
    raise_on_call: Exception | None = None

    def set_responses(self, *texts: str) -> None:
        self._responses = list(texts)

    async def complete(self, *, system: str, user: str) -> str:
        self.call_count += 1
        self.last_user = user
        if self.raise_on_call is not None:
            raise self.raise_on_call
        if self.sleep_s:
            await asyncio.sleep(self.sleep_s)
        if not self._responses:
            return "(no response primed) [b202598c·ch0§0¶17 p.11]."
        return self._responses.pop(0)


@pytest.fixture
def fake_retriever() -> FakeRetriever:
    return FakeRetriever()


@pytest.fixture
def fake_claude() -> FakeLLM:
    return FakeLLM(name="claude")


@pytest.fixture
def fake_ollama() -> FakeLLM:
    return FakeLLM(name="ollama")


@pytest.fixture
def settings() -> ChatSettings:
    # Override env so tests don't depend on the user's local config.
    return ChatSettings(
        anthropic_api_key="test-key-not-real",
        request_timeout_s=2.0,
        retrieval_k=8,
        fidelity_threshold=0.55,
        max_regenerations=1,
    )


@pytest.fixture
def services(
    fake_retriever: FakeRetriever,
    fake_claude: FakeLLM,
    fake_ollama: FakeLLM,
    settings: ChatSettings,
) -> ChatServices:
    async def always_high(_claim: str, _snippet: str) -> float:
        return 0.9

    from fractalmusic.generate import JsonCorpus, StubExpert

    return ChatServices(
        retriever=fake_retriever,
        llm_claude=fake_claude,
        llm_ollama=fake_ollama,
        similarity=always_high,
        settings=settings,
        expert=StubExpert(),
        corpus=JsonCorpus(root=settings.corpus_root),
    )


@pytest.fixture
def client(services: ChatServices) -> TestClient:
    app = create_app(services=services)
    return TestClient(app)
