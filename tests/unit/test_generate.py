"""Contract + unit tests for fractalmusic.generate."""

import json
from pathlib import Path

import pytest
from fractalmusic.generate import (
    GenerationRequest,
    JsonCorpus,
    Pattern,
    Provenance,
    StubExpert,
    realize,
    research_loop,
    score,
    to_midi,
    to_strudel_code,
    to_strudel_payload,
    to_web_payload,
)
from fractalmusic.generate.types import CandidateTrace, GenerationTrace
from fractalmusic.generate.loop import _adapt_length
from fractalmusic.generate.realize import _midi_number
from fractalmusic.wheel import Wheel

PROV = Provenance(book_hash="b202598c", book_title="El Sistema Fractal")


def _pattern(
    *,
    tonic: str = "A",
    mode: str = "Eólico",
    degrees: tuple[int, ...] = (1, 2, 3, 4, 5, 4, 3, 1),
    rhythm: tuple[float, ...] | None = None,
    name: str = "free:A-Eólico",
) -> Pattern:
    rhythm = rhythm or tuple(1.0 for _ in degrees)
    return Pattern(
        name=name,
        tonic=tonic,
        mode=mode,
        degrees=degrees,
        rhythm=rhythm,
        provenance=PROV,
    )


# --- Contract tests ----------------------------------------------------------


def test_generation_request_validates_inputs():
    GenerationRequest(tonic="A", mode="Eólico", length_events=8)
    with pytest.raises(ValueError):
        GenerationRequest(tonic="H", mode="Eólico", length_events=8)
    with pytest.raises(ValueError):
        GenerationRequest(tonic="A", mode="Klingon", length_events=8)
    with pytest.raises(ValueError):
        GenerationRequest(tonic="A", mode="Eólico", length_events=2)
    with pytest.raises(ValueError, match="flavor"):
        GenerationRequest(tonic="A", mode="Eólico", length_events=8, flavor="jazz-hands")


def test_pattern_rejects_unknown_tonic():
    with pytest.raises(ValueError, match="tonic"):
        Pattern(
            name="bad",
            tonic="H",
            mode="Eólico",
            degrees=(1, 2, 3, 4),
            rhythm=(1.0, 1.0, 1.0, 1.0),
            provenance=PROV,
        )


def test_pattern_rejects_unknown_mode():
    with pytest.raises(ValueError, match="mode"):
        Pattern(
            name="bad",
            tonic="A",
            mode="Klingon",
            degrees=(1, 2, 3, 4),
            rhythm=(1.0, 1.0, 1.0, 1.0),
            provenance=PROV,
        )


def test_pattern_rejects_empty_degrees():
    with pytest.raises(ValueError, match="non-empty"):
        Pattern(name="bad", tonic="A", mode="Eólico", degrees=(), rhythm=(), provenance=PROV)


def test_pattern_rejects_mismatched_rhythm_length():
    with pytest.raises(ValueError, match="rhythm length"):
        Pattern(
            name="bad",
            tonic="A",
            mode="Eólico",
            degrees=(1, 2, 3, 4),
            rhythm=(1.0, 1.0),
            provenance=PROV,
        )


def test_pattern_rejects_out_of_range_degrees_for_penta():
    with pytest.raises(ValueError, match="degrees"):
        Pattern(
            name="bad",
            tonic="A",
            mode="PentaI",
            degrees=(1, 2, 6),
            rhythm=(1.0, 1.0, 1.0),
            provenance=PROV,
        )


def test_pattern_requires_provenance_book_fields():
    with pytest.raises(ValueError, match="Provenance"):
        Pattern(
            name="bad",
            tonic="A",
            mode="Eólico",
            degrees=(1, 2),
            rhythm=(1.0, 1.0),
            provenance=Provenance(book_hash="", book_title="x"),
        )


# --- Realize -----------------------------------------------------------------


def test_realize_notes_are_in_mode_for_a_eolico():
    pattern = _pattern()
    events = realize(pattern)
    scale = set(Wheel("A").mode_for("A").scale_notes())
    assert all(e.note in scale for e in events)
    assert len(events) == len(pattern.degrees)


def test_realize_prebakes_time_sec_and_freq_hz():
    events = realize(_pattern())
    assert events[0].time_sec == 0.0
    assert events[1].time_sec > 0
    assert all(e.freq_hz > 0 for e in events)
    # A4 ≈ 440 Hz baseline holds somewhere in an A-Eólico walk
    assert any(
        abs(e.freq_hz - 440.0) < 0.01
        or abs(e.freq_hz - 220.0) < 0.01
        or abs(e.freq_hz - 880.0) < 0.01
        for e in events
    )


def test_realize_attaches_role_hour_and_carta_glyph():
    events = realize(_pattern())
    assert all(1 <= e.role_hour <= 12 for e in events)
    assert all(e.carta_glyph for e in events)


def test_realize_penta_uses_penta_scale():
    pattern = _pattern(
        tonic="A",
        mode="PentaI",
        degrees=(1, 2, 3, 4, 5, 1),
    )
    events = realize(pattern)
    scale = set(Wheel("A").penta("I"))
    assert all(e.note in scale for e in events)


# --- Score -------------------------------------------------------------------


def test_score_full_in_mode_yields_high_membership():
    pattern = _pattern()
    s = score(events=realize(pattern), pattern=pattern)
    assert s.mode_membership == 1.0
    assert s.breaches == ()


def test_score_band_brackets():
    # Was previously a tautology: `band` can only ever return one of these
    # three strings, so membership in the full set can never fail. Pin the
    # actual threshold behavior instead.
    pattern = _pattern()
    s = score(events=realize(pattern), pattern=pattern)
    assert s.total >= 0.85  # this pattern's total (0.9266) is "strong"
    assert s.band == "strong"


# --- Web payload + MIDI ------------------------------------------------------


def test_to_web_payload_shape():
    pattern = _pattern()
    events = realize(pattern)
    s = score(events=events, pattern=pattern)
    payload = to_web_payload(pattern=pattern, events=events, score=s)
    assert payload["schema_version"] == 1
    assert payload["requires_user_gesture"] is True
    assert payload["key_label"] == "A Eólico"
    assert payload["events"][0]["time_sec"] == 0.0
    assert "freq_hz" in payload["events"][0]
    assert payload["confidence"]["band"] in {"strong", "tentative", "exploratory"}
    assert payload["provenance"]["book_title"] == "El Sistema Fractal"


def test_to_strudel_code_uses_realized_events_and_cycle_timing():
    pattern = _pattern()
    events = realize(pattern)
    s = score(events=events, pattern=pattern)
    code = to_strudel_code(pattern=pattern, events=events, score=s)
    notes = " ".join(f"{e.note.lower()}{e.octave}" for e in events)

    assert "setcps(96 / 60 / 8)" in code
    assert f'note("{notes}")' in code
    assert "// key: A Eólico" in code
    assert "// source: El Sistema Fractal" in code
    assert "free_text" not in code


def test_to_strudel_payload_wraps_existing_web_payload():
    pattern = _pattern()
    events = realize(pattern)
    s = score(events=events, pattern=pattern)
    web_payload = to_web_payload(pattern=pattern, events=events, score=s)
    payload = to_strudel_payload(
        pattern=pattern,
        events=events,
        score=s,
        web_payload=web_payload,
    )

    assert payload["schema_version"] == 1
    assert payload["generated_from"] is web_payload
    assert payload["pattern_name"] == pattern.name
    assert payload["code"].startswith(f"// Fractal Music: {pattern.name}")
    assert payload["book_guidance"] == []
    assert payload["warnings"] == []


def test_to_strudel_code_includes_book_guidance_comments():
    pattern = _pattern()
    events = realize(pattern)
    s = score(events=events, pattern=pattern)
    code = to_strudel_code(
        pattern=pattern,
        events=events,
        score=s,
        book_guidance=[
            {
                "book_hash": "b202598c",
                "book_title": "El Sistema Fractal",
                "chapter_idx": 4,
                "section_idx": 1,
                "paragraph_idx": 7,
                "page_start": 42,
                "snippet": "La rueda ordena los modos.",
                "strudel_use": "Mantener el ciclo como drone y capas.",
            }
        ],
    )

    assert "// book 1: b202598c p.42 El Sistema Fractal" in code
    assert "// strudel use 1: Mantener el ciclo como drone y capas." in code


def test_to_strudel_code_sanitizes_metadata_comments():
    pattern = Pattern(
        name="test\nhush()",
        tonic="A",
        mode="Eólico",
        degrees=(1, 2, 3, 4),
        rhythm=(1.0, 0.5, 1.5, 1.0),
        provenance=Provenance(
            book_hash="b202598c",
            book_title='Book\nnote("c4").play()',
            chapter='Ch\nstack(note("d4"))',
        ),
    )
    events = realize(pattern)
    s = score(events=events, pattern=pattern)
    code = to_strudel_code(pattern=pattern, events=events, score=s)

    assert "// Fractal Music: test hush()" in code
    assert '// source: Book note("c4").play()' in code
    assert "\nhush()" not in code
    assert '\nnote("c4").play()' not in code
    assert "// warning: rhythm_quantized_to_event_sequence" in code


def test_to_strudel_code_rejects_empty_events():
    pattern = _pattern()
    with pytest.raises(ValueError, match="at least one Event"):
        to_strudel_code(pattern=pattern, events=(), score=score(events=(), pattern=pattern))


def test_to_strudel_code_includes_page_comment_when_provenance_has_one():
    pattern = Pattern(
        name="test",
        tonic="A",
        mode="Eólico",
        degrees=(1, 2, 3, 4),
        rhythm=(1.0, 1.0, 1.0, 1.0),
        provenance=Provenance(book_hash="b202598c", book_title="El Sistema Fractal", page=26),
    )
    events = realize(pattern)
    s = score(events=events, pattern=pattern)
    code = to_strudel_code(pattern=pattern, events=events, score=s)
    assert "// page: 26" in code


def test_to_midi_writes_a_file(tmp_path: Path):
    pattern = _pattern()
    events = realize(pattern)
    out = to_midi(events=events, path=tmp_path / "out.mid")
    assert out.exists() and out.stat().st_size > 0


# --- Loop --------------------------------------------------------------------


def test_research_loop_produces_in_mode_result(tmp_path: Path):
    request = GenerationRequest(tonic="A", mode="Eólico", length_events=8)
    corpus = JsonCorpus(root=tmp_path / "patterns")
    result = research_loop(request=request, expert=StubExpert(), corpus=corpus)
    scale = set(Wheel("A").mode_for("A").scale_notes())
    assert all(e.note in scale for e in result.events)
    assert result.score.total > 0


def test_research_loop_persists_winners(tmp_path: Path):
    # Was previously conditional (`if score >= 0.75: assert ...`), so it
    # passed trivially whenever the score happened to fall short — neither
    # branch of the persistence gate was ever deliberately forced. This
    # request+StubExpert combination deterministically scores 0.9189.
    request = GenerationRequest(tonic="A", mode="Eólico", length_events=8)
    corpus = JsonCorpus(root=tmp_path / "patterns")
    result = research_loop(request=request, expert=StubExpert(), corpus=corpus)
    assert result.score.total >= 0.75
    assert any((tmp_path / "patterns").iterdir())


class _FlatLowScoreExpert:
    """Deliberately bad candidate: same degree repeated, ragged rhythm."""

    def query(self, request: GenerationRequest) -> Pattern:
        return Pattern(
            name="flat",
            tonic=request.tonic,
            mode=request.mode,
            degrees=(1, 1, 1, 1),
            rhythm=(1.0, 0.5, 1.0, 0.5),
            provenance=Provenance(book_hash="b202598c", book_title="El Sistema Fractal"),
        )


def test_research_loop_does_not_persist_below_threshold_scores(tmp_path: Path):
    request = GenerationRequest(tonic="A", mode="Eólico", length_events=4)
    corpus = JsonCorpus(root=tmp_path / "patterns")
    result = research_loop(request=request, expert=_FlatLowScoreExpert(), corpus=corpus)
    assert result.score.total == 0.65
    assert list((tmp_path / "patterns").iterdir()) == []


class _ExactThresholdExpert:
    """Every candidate scores exactly SCORE_THRESHOLD (0.75) — the boundary."""

    def query(self, request: GenerationRequest) -> Pattern:
        n = request.length_events
        return Pattern(
            name="boundary",
            tonic=request.tonic,
            mode=request.mode,
            degrees=(1,) * n,
            rhythm=(1.0,) * n,
            provenance=Provenance(book_hash="b202598c", book_title="El Sistema Fractal"),
        )


def test_research_loop_persists_at_exact_threshold_boundary(tmp_path: Path):
    # SCORE_THRESHOLD is a >= gate, not >: a pattern scoring exactly 0.75
    # must still persist. Neither existing test lands exactly on 0.75.
    request = GenerationRequest(tonic="A", mode="Eólico", length_events=8)
    corpus = JsonCorpus(root=tmp_path / "patterns")
    result = research_loop(request=request, expert=_ExactThresholdExpert(), corpus=corpus)
    assert result.score.total == 0.75
    assert any((tmp_path / "patterns").iterdir())


class _VaryingQualityExpert:
    """Returns a mix of candidates so best-of-N has something to select."""

    def __init__(self) -> None:
        self._calls = 0

    def query(self, request: GenerationRequest) -> Pattern:
        self._calls += 1
        prov = Provenance(book_hash="b202598c", book_title="El Sistema Fractal")
        if self._calls == 3:
            # the one genuinely good candidate, buried in the middle.
            return Pattern(
                name="rich",
                tonic=request.tonic,
                mode=request.mode,
                degrees=(1, 2, 3, 4, 5, 4, 3, 1),
                rhythm=(1.0,) * 8,
                provenance=prov,
            )
        return Pattern(
            name="flat",
            tonic=request.tonic,
            mode=request.mode,
            degrees=(1,) * 8,
            rhythm=(1.0,) * 8,
            provenance=prov,
        )


def test_research_loop_selects_the_highest_scoring_candidate(tmp_path: Path):
    # Every existing StubExpert/_FlatLowScoreExpert-based test returns the
    # SAME pattern on all 5 candidate calls, so best-of-N never actually had
    # anything to choose between — min-selection and max-selection are
    # indistinguishable when every candidate is identical. This forces real
    # variance: candidate 3 of 5 is the only high scorer.
    request = GenerationRequest(tonic="A", mode="Eólico", length_events=8)
    corpus = JsonCorpus(root=tmp_path / "patterns")
    result = research_loop(request=request, expert=_VaryingQualityExpert(), corpus=corpus)
    assert result.pattern.name == "rich"
    assert result.score.total == 0.9266


def test_research_loop_never_lets_a_persisted_pattern_cross_flavors(tmp_path: Path):
    # Caught live on :5174: JsonCorpus.find()/append() keyed only on
    # tonic/mode, never flavor, so a pattern persisted under one flavor
    # could win best-of-N for a request made under a completely different
    # flavor — the FE's Estilo selector silently did nothing once any
    # pattern for that tonic/mode had ever been persisted. Confirmed via
    # the live API: a "penta-walk" and a "carta-progression" request both
    # came back with pattern_name "free:A-Eólico" — the persisted "free"
    # winner, not a pattern reflecting the flavor actually requested.
    corpus = JsonCorpus(root=tmp_path / "patterns")
    free_request = GenerationRequest(tonic="A", mode="Eólico", length_events=8, flavor="free")
    free_result = research_loop(request=free_request, expert=StubExpert(), corpus=corpus)
    assert free_result.score.total >= 0.75
    assert any((tmp_path / "patterns").iterdir())

    carta_request = GenerationRequest(
        tonic="A", mode="Eólico", length_events=8, flavor="carta-progression"
    )
    carta_result = research_loop(request=carta_request, expert=StubExpert(), corpus=corpus)
    assert carta_result.pattern.name.startswith("carta-progression:")
    assert carta_result.pattern.degrees == (1, 4, 5, 1, 1, 4, 5, 1)


class _CountingExpert:
    """Tracks call count; always returns the same deliberately mediocre
    (but valid) candidate so it can be told apart from a corpus seed."""

    def __init__(self) -> None:
        self.calls = 0

    def query(self, request: GenerationRequest) -> Pattern:
        self.calls += 1
        return Pattern(
            name="from-expert",
            tonic=request.tonic,
            mode=request.mode,
            degrees=(1, 3, 5, 1),
            rhythm=(1.0, 1.0, 1.0, 1.0),
            provenance=Provenance(book_hash="llm-composed", book_title="Generado por IA"),
        )


def test_research_loop_with_free_text_bypasses_corpus_best_of_n(tmp_path: Path):
    # A free-text description has no relationship to whatever patterns
    # happen to be pre-seeded in the corpus for the same tonic/mode — DE-
    # SCRIBE always sends the fixed defaults A/Eólico regardless of what
    # was typed, so corpus.find() would return the SAME candidates for
    # every description. Before this fix, best-of-N let a high-scoring
    # seeded corpus pattern silently outscore and replace the LLM's actual
    # composition — the user's description was discarded whenever a
    # curated pattern happened to score higher on raw musical-rule metrics.
    request = GenerationRequest(tonic="A", mode="Eólico", length_events=8)
    corpus = JsonCorpus(root=tmp_path / "patterns")

    # Seed the corpus with a high-scoring "A_Eólico" pattern first — this
    # is exactly the shape research_loop's non-free-text path persists.
    research_loop(request=request, expert=StubExpert(), corpus=corpus)
    assert any((tmp_path / "patterns").iterdir())

    described_request = GenerationRequest(
        tonic="A", mode="Eólico", length_events=8, free_text="a slow melancholy waltz"
    )
    expert = _CountingExpert()
    result = research_loop(request=described_request, expert=expert, corpus=corpus)

    assert result.pattern.name == "from-expert"
    assert expert.calls == 1


def test_research_loop_with_free_text_still_returns_a_real_trace(tmp_path: Path):
    # The reconciliation point between the free-text bypass and the audit
    # trail: a free-text composition must be exactly as auditable as a
    # best-of-N one, not a blind spot — a lone "expert" candidate that
    # always won, not a missing trace field.
    corpus = JsonCorpus(root=tmp_path / "patterns")
    described_request = GenerationRequest(
        tonic="A", mode="Eólico", length_events=8, free_text="a bright morning fanfare"
    )
    result = research_loop(request=described_request, expert=_CountingExpert(), corpus=corpus)

    assert result.trace.winner_source == "expert"
    assert len(result.trace.candidates) == 1
    only = result.trace.candidates[0]
    assert only.source == "expert"
    assert only.won is True
    assert only.pattern_name == "from-expert"
    assert only.score_total == result.score.total


def test_trace_records_every_candidate_and_exactly_one_winner(tmp_path: Path):
    # The audit record's basic contract: N_CANDIDATES entries in, exactly
    # one marked won, and it's the actual returned pattern.
    request = GenerationRequest(tonic="A", mode="Eólico", length_events=8)
    corpus = JsonCorpus(root=tmp_path / "patterns")
    result = research_loop(request=request, expert=_VaryingQualityExpert(), corpus=corpus)

    assert isinstance(result.trace, GenerationTrace)
    assert len(result.trace.candidates) == 5
    winners = [c for c in result.trace.candidates if c.won]
    assert len(winners) == 1
    assert winners[0].pattern_name == result.pattern.name
    assert winners[0].score_total == result.score.total
    assert all(isinstance(c, CandidateTrace) for c in result.trace.candidates)


def test_trace_attributes_source_correctly_when_corpus_pattern_wins(tmp_path: Path):
    # This is the exact shape of the two real bugs caught live this
    # session: a corpus-seeded pattern silently outscoring a fresh
    # expert candidate. Before the trace existed, telling which one
    # actually won required re-deriving it by hand from the response.
    # Now it's a direct field.
    request = GenerationRequest(tonic="A", mode="Eólico", length_events=8)
    corpus = JsonCorpus(root=tmp_path / "patterns")
    research_loop(request=request, expert=StubExpert(), corpus=corpus)  # seeds a strong corpus entry

    result = research_loop(request=request, expert=_FlatLowScoreExpert(), corpus=corpus)

    assert result.trace.winner_source == "corpus"
    corpus_candidates = [c for c in result.trace.candidates if c.source == "corpus"]
    expert_candidates = [c for c in result.trace.candidates if c.source == "expert"]
    assert len(corpus_candidates) == 1
    assert len(expert_candidates) == 4
    assert corpus_candidates[0].won is True
    assert all(not c.won for c in expert_candidates)


def test_trace_attributes_source_correctly_when_expert_candidate_wins(tmp_path: Path):
    # No corpus seed at all -> every candidate must come from the expert,
    # and the trace must say so.
    request = GenerationRequest(tonic="D", mode="Dórico", length_events=8)
    corpus = JsonCorpus(root=tmp_path / "patterns")
    result = research_loop(request=request, expert=_VaryingQualityExpert(), corpus=corpus)

    assert result.trace.winner_source == "expert"
    assert all(c.source == "expert" for c in result.trace.candidates)


def test_adapt_length_is_a_noop_when_length_already_matches():
    pattern = _pattern(degrees=(1, 2, 3, 4), rhythm=(1.0, 1.0, 1.0, 1.0))
    assert _adapt_length(pattern, 4) is pattern


def test_adapt_length_stretches_by_cycling_degrees_and_rhythm():
    pattern = _pattern(degrees=(1, 2, 3, 4), rhythm=(1.0, 1.0, 1.0, 1.0))
    stretched = _adapt_length(pattern, 8)
    assert stretched.degrees == (1, 2, 3, 4, 1, 2, 3, 4)
    assert stretched.rhythm == (1.0,) * 8


def test_midi_number_rejects_unknown_note():
    with pytest.raises(ValueError, match="unknown note"):
        _midi_number(note="H", octave=4)


def test_adapt_length_truncates_to_the_requested_length():
    pattern = _pattern(degrees=(1, 2, 3, 4, 5, 6), rhythm=(1.0, 2.0, 1.0, 1.0, 1.0, 1.0))
    truncated = _adapt_length(pattern, 4)
    assert truncated.degrees == (1, 2, 3, 4)
    assert truncated.rhythm == (1.0, 2.0, 1.0, 1.0)


def test_corpus_round_trip(tmp_path: Path):
    pattern = _pattern()
    corpus = JsonCorpus(root=tmp_path / "patterns")
    s = score(events=realize(pattern), pattern=pattern)
    corpus.append(pattern, s)
    request = GenerationRequest(tonic="A", mode="Eólico", length_events=8)
    found = corpus.find(request)
    assert len(found) == 1
    assert found[0].name == pattern.name


def test_pattern_dict_round_trip():
    pattern = _pattern()
    rebuilt = Pattern.from_dict(json.loads(json.dumps(pattern.to_dict())))
    assert rebuilt == pattern
