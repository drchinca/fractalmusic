"""LLMExpert — fake-LLM-backed unit tests. No real network calls; the one
real-behavior round trip lives in tests/eval (see test-behavior-real.md)."""

from __future__ import annotations

from dataclasses import dataclass, field

from fractalmusic.generate.types import GenerationRequest

from gatople_api.llm_expert import LLMExpert


@dataclass
class FakeLLM:
    """Returns a queue of pre-primed responses, one per call."""

    _responses: list[str] = field(default_factory=list)
    call_count: int = 0

    def set_responses(self, *texts: str) -> None:
        self._responses = list(texts)

    async def complete(self, *, system: str, user: str) -> str:
        self.call_count += 1
        return self._responses.pop(0)


def _request(free_text: str | None) -> GenerationRequest:
    return GenerationRequest(
        tonic="A",
        mode="Eólico",
        length_events=16,
        flavor="free",
        free_text=free_text,
    )


def test_valid_json_produces_a_valid_pattern() -> None:
    """Well-formed LLM output constructs a Pattern honoring the LLM's choices,
    with honest (never book-faked) provenance."""
    llm = FakeLLM()
    llm.set_responses(
        '{"tonic": "D", "mode": "Jónico", "degrees": [1, 3, 5, 1], "rhythm": [1.0, 1.0, 1.0, 1.0]}'
    )
    expert = LLMExpert(llm=llm)

    pattern = expert.query(_request("uplifting pop with trumpets"))

    assert pattern.tonic == "D"
    assert pattern.mode == "Jónico"
    assert pattern.degrees == (1, 3, 5, 1)
    assert pattern.provenance.book_hash == "llm-composed"
    assert llm.call_count == 1


def test_no_free_text_skips_the_llm_entirely() -> None:
    """No description -> nothing for the LLM to compose from; falls
    straight to StubExpert without ever calling complete()."""
    llm = FakeLLM()
    expert = LLMExpert(llm=llm)

    pattern = expert.query(_request(None))

    assert pattern.provenance.book_hash != "llm-composed"
    assert llm.call_count == 0


def test_malformed_json_falls_back_to_stub_after_retry() -> None:
    """Garbage on both attempts -> graceful degradation to StubExpert,
    never a 500 (pluggable-scalable.md PS-14)."""
    llm = FakeLLM()
    llm.set_responses("not json at all", "still not json")
    expert = LLMExpert(llm=llm)

    pattern = expert.query(_request("a moody minor waltz"))

    assert pattern.provenance.book_hash != "llm-composed"
    assert llm.call_count == 2


def test_out_of_range_degree_falls_back_to_stub() -> None:
    """Degree 6 is invalid for a 5-degree Penta mode -> rejected, retried,
    still invalid -> falls back rather than constructing a broken Pattern."""
    llm = FakeLLM()
    bad = '{"tonic": "A", "mode": "PentaI", "degrees": [1, 6, 2, 3], "rhythm": [1.0, 1.0, 1.0, 1.0]}'
    llm.set_responses(bad, bad)
    expert = LLMExpert(llm=llm)

    pattern = expert.query(_request("a five-note folk riff"))

    assert pattern.provenance.book_hash != "llm-composed"
    assert llm.call_count == 2


def test_unknown_tonic_falls_back_to_stub() -> None:
    """The LLM must only choose from the closed NOTE_NAMES set."""
    llm = FakeLLM()
    bad = '{"tonic": "H", "mode": "Eólico", "degrees": [1, 2, 3], "rhythm": [1.0, 1.0, 1.0]}'
    llm.set_responses(bad, bad)
    expert = LLMExpert(llm=llm)

    pattern = expert.query(_request("something in H minor"))

    assert pattern.provenance.book_hash != "llm-composed"
    assert llm.call_count == 2


def test_mismatched_degrees_and_rhythm_length_falls_back() -> None:
    """Pattern.__post_init__ itself rejects mismatched lengths; LLMExpert
    must catch that and fall back rather than letting it raise to the route."""
    llm = FakeLLM()
    bad = '{"tonic": "A", "mode": "Eólico", "degrees": [1, 2, 3, 4], "rhythm": [1.0, 1.0]}'
    llm.set_responses(bad, bad)
    expert = LLMExpert(llm=llm)

    pattern = expert.query(_request("a short broken phrase"))

    assert pattern.provenance.book_hash != "llm-composed"
    assert llm.call_count == 2


def test_second_attempt_succeeds_after_first_fails() -> None:
    """Retry-once actually works: bad then good -> the good Pattern wins."""
    llm = FakeLLM()
    llm.set_responses(
        "garbage",
        '{"tonic": "G", "mode": "Mixolidio", "degrees": [1, 4, 5, 1], "rhythm": [1.0, 1.0, 1.0, 1.0]}',
    )
    expert = LLMExpert(llm=llm)

    pattern = expert.query(_request("a bright anthemic riff"))

    assert pattern.tonic == "G"
    assert pattern.mode == "Mixolidio"
    assert llm.call_count == 2
