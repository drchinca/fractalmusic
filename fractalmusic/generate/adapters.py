"""MIDI + WebAudio JSON + Strudel adapters. Pure functions over Events."""

from pathlib import Path
from typing import Final

from fractalmusic.generate.realize import DEFAULT_BPM, _midi_number
from fractalmusic.generate.types import (
    Event,
    Pattern,
    Score,
    StrudelBookGuidancePayload,
    StrudelPayload,
    WebPayload,
)

WEB_PAYLOAD_SCHEMA_VERSION: Final[int] = 1
STRUDEL_PAYLOAD_SCHEMA_VERSION: Final[int] = 1
DEFAULT_VELOCITY: Final[int] = 96


class MidiUnavailable(RuntimeError):  # noqa: N818 — public name kept for stability
    """Raised when `mido` is not installed but to_midi was called."""


def to_midi(
    events: tuple[Event, ...],
    path: Path,
    *,
    bpm: int = DEFAULT_BPM,
) -> Path:
    try:
        import mido  # local import — keeps mido optional
    except ImportError as error:
        raise MidiUnavailable("mido not installed; pip install 'fractalmusic[midi]'") from error

    ticks_per_beat = 480
    midi_file = mido.MidiFile(ticks_per_beat=ticks_per_beat)
    track = mido.MidiTrack()
    midi_file.tracks.append(track)
    track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm)))

    cursor_tick = 0
    for event in events:
        on_tick = int(event.beat * ticks_per_beat)
        off_tick = int((event.beat + event.duration) * ticks_per_beat)
        midi_num = _midi_number(note=event.note, octave=event.octave)
        track.append(
            mido.Message(
                "note_on",
                note=midi_num,
                velocity=DEFAULT_VELOCITY,
                time=max(0, on_tick - cursor_tick),
            )
        )
        cursor_tick = on_tick
        track.append(
            mido.Message(
                "note_off",
                note=midi_num,
                velocity=0,
                time=max(0, off_tick - cursor_tick),
            )
        )
        cursor_tick = off_tick

    path.parent.mkdir(parents=True, exist_ok=True)
    midi_file.save(str(path))
    return path


def to_web_payload(
    pattern: Pattern,
    events: tuple[Event, ...],
    score: Score,
    *,
    bpm: int = DEFAULT_BPM,
    audio_url: str | None = None,
) -> WebPayload:
    total_beats = max((e.beat + e.duration for e in events), default=0.0)
    return WebPayload(
        schema_version=WEB_PAYLOAD_SCHEMA_VERSION,
        pattern_name=pattern.name,
        bpm=bpm,
        tonic=pattern.tonic,
        mode=pattern.mode,
        key_label=f"{pattern.tonic} {pattern.mode}",
        total_beats=round(total_beats, 4),
        requires_user_gesture=True,
        confidence={"score": score.total, "band": score.band},
        events=[
            {
                "note": e.note,
                "octave": e.octave,
                "beat": e.beat,
                "duration": e.duration,
                "time_sec": round(e.time_sec, 4),
                "freq_hz": e.freq_hz,
                "role_hour": e.role_hour,
                "carta_glyph": e.carta_glyph,
            }
            for e in events
        ],
        provenance={
            "book_hash": pattern.provenance.book_hash,
            "book_title": pattern.provenance.book_title,
            "chapter": pattern.provenance.chapter,
            "page": pattern.provenance.page,
            "quote": pattern.provenance.quote,
        },
        audio_url=audio_url,
    )


def _total_beats(events: tuple[Event, ...]) -> float:
    return round(max((e.beat + e.duration for e in events), default=0.0), 4)


def _fmt_number(value: float | int) -> str:
    if isinstance(value, int) or float(value).is_integer():
        return str(int(value))
    return f"{value:.4f}".rstrip("0").rstrip(".")


def _comment_text(value: str, *, limit: int = 120) -> str:
    normalized = " ".join(value.replace("\r", " ").replace("\n", " ").split())
    return normalized[:limit]


def _book_guidance_comments(
    book_guidance: list[StrudelBookGuidancePayload] | None,
) -> list[str]:
    if not book_guidance:
        return []
    comments: list[str] = []
    for idx, item in enumerate(book_guidance[:3], start=1):
        comments.append(
            "// book "
            f"{idx}: {_comment_text(item['book_hash'], limit=16)} "
            f"p.{item['page_start']} "
            f"{_comment_text(item['book_title'], limit=64)}"
        )
        comments.append(f"// strudel use {idx}: {_comment_text(item['strudel_use'], limit=180)}")
    return comments


def _strudel_note(event: Event) -> str:
    return f"{event.note.lower()}{event.octave}"


def _strudel_warnings(events: tuple[Event, ...]) -> list[str]:
    warnings: list[str] = []
    ordered = sorted(events, key=lambda e: e.beat)
    one_beat_durations = all(abs(e.duration - 1.0) < 0.0001 for e in ordered)
    one_beat_steps = all(
        abs(next_event.beat - event.beat - 1.0) < 0.0001
        for event, next_event in zip(ordered, ordered[1:], strict=False)
    )
    if not (one_beat_durations and one_beat_steps):
        warnings.append("rhythm_quantized_to_event_sequence")
    return warnings


def to_strudel_code(
    pattern: Pattern,
    events: tuple[Event, ...],
    score: Score,
    *,
    bpm: int = DEFAULT_BPM,
    book_guidance: list[StrudelBookGuidancePayload] | None = None,
) -> str:
    if not events:
        raise ValueError("to_strudel_code requires at least one Event")

    ordered = tuple(sorted(events, key=lambda e: e.beat))
    total_beats = _total_beats(ordered)
    notes = " ".join(_strudel_note(event) for event in ordered)
    glyphs = " ".join(event.carta_glyph for event in ordered)
    roles = " ".join(str(event.role_hour) for event in ordered)
    tonic_drone = f"{pattern.tonic.lower()}2"

    comments = [
        f"// Fractal Music: {_comment_text(pattern.name)}",
        f"// key: {_comment_text(f'{pattern.tonic} {pattern.mode}')}",
        f"// confidence: {score.band} {_fmt_number(score.total)}",
        f"// roles: {_comment_text(roles)}",
        f"// glyphs: {_comment_text(glyphs)}",
        f"// source: {_comment_text(pattern.provenance.book_title)}",
    ]
    if pattern.provenance.chapter is not None:
        comments.append(f"// chapter: {_comment_text(pattern.provenance.chapter)}")
    if pattern.provenance.page is not None:
        comments.append(f"// page: {pattern.provenance.page}")
    comments.extend(_book_guidance_comments(book_guidance))
    comments.extend(f"// warning: {warning}" for warning in _strudel_warnings(ordered))

    return "\n".join(
        [
            *comments,
            f"setcps({bpm} / 60 / {_fmt_number(total_beats)})",
            "",
            "stack(",
            f'  note("{notes}")',
            '    .sound("triangle")',
            "    .gain(.22),",
            f'  note("{tonic_drone}")',
            '    .sound("sine")',
            f"    .slow({_fmt_number(total_beats)})",
            "    .gain(.08)",
            ")",
        ]
    )


def to_strudel_payload(
    pattern: Pattern,
    events: tuple[Event, ...],
    score: Score,
    *,
    bpm: int = DEFAULT_BPM,
    web_payload: WebPayload | None = None,
    book_guidance: list[StrudelBookGuidancePayload] | None = None,
) -> StrudelPayload:
    generated_from = web_payload or to_web_payload(
        pattern=pattern,
        events=events,
        score=score,
        bpm=bpm,
    )
    return StrudelPayload(
        schema_version=STRUDEL_PAYLOAD_SCHEMA_VERSION,
        pattern_name=pattern.name,
        bpm=bpm,
        total_beats=generated_from["total_beats"],
        code=to_strudel_code(
            pattern=pattern,
            events=events,
            score=score,
            bpm=bpm,
            book_guidance=book_guidance,
        ),
        generated_from=generated_from,
        book_guidance=book_guidance or [],
        warnings=_strudel_warnings(events),
    )
