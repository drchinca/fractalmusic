"""The 12 cartas — rendering worlds as colored, glyphed cards.

Renders each NoteWorld as a terminal card (truecolor background + glyph + mode +
number) and lays out the full Dodecamundo deck. Also produces sticker maps for
placing the cartas on a piano or fretboard ("tabla periódica de sonidos", Ch. 10).
"""

from fractalmusic.colors import ansi_bg
from fractalmusic.dodecamundo import DODECAMUNDO, NoteWorld, world


def carta(world_obj: NoteWorld) -> str:
    """Render a single world as a one-line colored card."""
    label = world_obj.roman if world_obj.is_pentatonic else world_obj.note
    face = f" {world_obj.glyph} {label:<3} {world_obj.number:>2} "
    return ansi_bg(world_obj.color_hex, face)


def deck() -> str:
    """Render all 12 cartas in chromatic (A-origin) order."""
    return "\n".join(carta(w) for w in DODECAMUNDO)


def piano_stickers() -> str:
    """Map each world's glyph onto its piano key (white naturals, black stars)."""
    lines: list[str] = []
    for w in DODECAMUNDO:
        kind = "black" if w.is_pentatonic else "white"
        label = w.roman or w.mode.mode_name
        lines.append(f"{w.note:<3} {kind:<5} {w.glyph} {label}".rstrip())
    return "\n".join(lines)


def spell(notes: list[str]) -> str:
    """Spell a list of notes as a glyph row (a scale or chord 'written' in symbols)."""
    return " ".join(world(note).glyph for note in notes)
