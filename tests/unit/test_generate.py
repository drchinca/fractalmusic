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
from fractalmusic.wheel import Wheel

PROV = Provenance(book_hash="b202598c", book_title="El Sistema Fractal")


def _pattern(
    *,
    tonic: str = "A",
    mode: str = "Eólico",
    degrees: tuple[int, ...] = (1, 2, 3, 4, 5, 4, 3, 1),
    rhythm: tuple[float, ...] | None = None,
) -> Pattern:
    rhythm = rhythm or tuple(1.0 for _ in degrees)
    return Pattern(
        name="test",
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


def test_pattern_rejects_out_of_range_degrees_for_penta():
    with pytest.raises(ValueError, match="degrees"):
        Pattern(
            name="bad",
            tonic="A",
            mode="Penta 1",
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
        mode="Penta 1",
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
    pattern = _pattern()
    s = score(events=realize(pattern), pattern=pattern)
    assert s.band in {"strong", "tentative", "exploratory"}


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
    assert payload["code"].startswith("// Fractal Music: test")
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
    request = GenerationRequest(tonic="A", mode="Eólico", length_events=8)
    corpus = JsonCorpus(root=tmp_path / "patterns")
    result = research_loop(request=request, expert=StubExpert(), corpus=corpus)
    if result.score.total >= 0.75:
        assert any((tmp_path / "patterns").iterdir())


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
