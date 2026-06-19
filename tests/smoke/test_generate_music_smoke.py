"""Smoke tests that prove the generator can produce music artifacts."""

from pathlib import Path

import numpy as np
import pytest
import soundfile as sf
from fractalmusic.generate import (
    GenerationRequest,
    JsonCorpus,
    StubExpert,
    research_loop,
    to_strudel_payload,
)
from fractalmusic.generate.realize import freq_for
from fractalmusic.render import RenderConfig, render_wav


@pytest.mark.smoke
@pytest.mark.parametrize(
    ("tonic", "mode", "flavor"),
    [
        ("A", "Eólico", "free"),
        ("D", "Penta 2", "penta-walk"),
        ("E", "Frigio", "carta-progression"),
    ],
)
def test_generate_music_smoke_writes_wav_and_strudel(
    tmp_path: Path,
    tonic: str,
    mode: str,
    flavor: str,
) -> None:
    request = GenerationRequest(
        tonic=tonic,
        mode=mode,
        length_events=4,
        flavor=flavor,
    )
    result = research_loop(
        request=request,
        expert=StubExpert(),
        corpus=JsonCorpus(root=tmp_path / "patterns"),
    )

    wav_path = render_wav(
        result.events,
        out_path=tmp_path / f"{tonic}-{mode}-{flavor}.wav",
        config=RenderConfig(
            sample_rate=22050,
            bpm=result.web_payload["bpm"],
            reverb_wet=0.08,
        ),
        tonic_freq_hz=freq_for(note=result.pattern.tonic, octave=3),
    )

    audio, sample_rate = sf.read(wav_path, dtype="float32")
    peak = float(np.max(np.abs(audio)))

    assert wav_path.exists()
    assert wav_path.stat().st_size > 44
    assert sample_rate == 22050
    assert audio.ndim == 1
    assert audio.size > sample_rate
    assert peak > 0.05

    payload = to_strudel_payload(
        pattern=result.pattern,
        events=result.events,
        score=result.score,
        bpm=result.web_payload["bpm"],
        book_guidance=[
            {
                "book_hash": result.pattern.provenance.book_hash,
                "book_title": result.pattern.provenance.book_title,
                "chapter_idx": 0,
                "section_idx": 0,
                "paragraph_idx": 0,
                "page_start": result.pattern.provenance.page or 0,
                "snippet": result.pattern.provenance.quote or result.pattern.provenance.book_title,
                "strudel_use": "Smoke test: preserve the fractal sequence as live-code layers.",
            }
        ],
    )

    assert payload["pattern_name"] == result.pattern.name
    assert payload["total_beats"] == 4.0
    assert payload["generated_from"]["events"][0]["freq_hz"] > 0
    assert payload["book_guidance"]
    assert "setcps(" in payload["code"]
    assert "stack(" in payload["code"]
    assert 'note("' in payload["code"]
    assert "// book 1:" in payload["code"]
