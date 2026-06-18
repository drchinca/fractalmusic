"""Showcase — print the Dodecamundo, scales, color wheel, and combinations.

Run as a module to see the Sistema Fractal rendered in the terminal:

    python -m fractalmusic.showcase
"""

from fractalmusic.cartas import carta, spell
from fractalmusic.colors import ansi_bg
from fractalmusic.dodecamundo import DODECAMUNDO, heptatonic_worlds, pentatonic_worlds
from fractalmusic.gatople import cero_pitagoras, clock_hour, interval_angle
from fractalmusic.scales import PENTA_MODES, microstructures, mode_scale, penta

RULE = "─" * 60


def _header(title: str) -> str:
    return f"\n{RULE}\n  {title}\n{RULE}"


def show_dodecamundo() -> str:
    """The 12 cartas as colored cards."""
    lines = [_header("EL DODECAMUNDO — 12 cartas (A-origin)")]
    for w in DODECAMUNDO:
        family = "penta ★" if w.is_pentatonic else "hepta"
        lines.append(f"{carta(w)}  {w.mode.mode_name:<10} {family:<8} {w.clock_hour:>2}h")
    return "\n".join(lines)


def show_color_wheel() -> str:
    """The 12-hue chromatic wheel as colored swatches."""
    lines = [_header("THE COLOR WHEEL (12 hues, A → G#)")]
    row = " ".join(ansi_bg(w.color_hex, f" {w.note:<2} ") for w in DODECAMUNDO)
    lines.append(row)
    return "\n".join(lines)


def show_heptatonic_modes() -> str:
    """The 7 Greek modes spelled in notes and glyphs."""
    lines = [_header("THE 7 GREEK MODES (white keys)")]
    for w in heptatonic_worlds():
        scale = mode_scale(w.note)
        notes = " ".join(f"{n:<2}" for n in scale.notes)
        glyphs = spell(list(scale.notes))
        lines.append(
            f"{w.glyph} {scale.name:<10} {w.mode.quality:<11} {notes}   {glyphs}"
        )
    return "\n".join(lines)


def show_pentatonic_modes() -> str:
    """The 5 Penta modes (the ancestral stars)."""
    lines = [_header("THE 5 PENTA MODES (black keys / stars)")]
    roots = {"I": "C#", "II": "D#", "III": "F#", "IV": "G#", "V": "A#"}
    for roman, root in roots.items():
        scale = penta(root, mode=roman)
        notes = " ".join(f"{n:<2}" for n in scale.notes)
        lines.append(f"★ {scale.name:<9} {notes}   no-semitone={not scale.has_semitone}")
    return "\n".join(lines)


def show_gatople_clock() -> str:
    """Each world's clock hour and angle from A."""
    lines = [_header("THE GÁTOPLE CLOCK (hour & angle from A)")]
    for w in DODECAMUNDO:
        lines.append(
            f"{w.glyph} {w.note:<3} {w.mode.mode_name:<10} "
            f"{clock_hour(w.note):>2} o'clock   {interval_angle('A', w.note):>5.0f}°"
        )
    return "\n".join(lines)


def show_combinations() -> str:
    """Sample chords/scales written in Fractal glyphs."""
    lines = [_header("COMBINATIONS — music written in glyphs")]
    samples: list[tuple[str, list[str]]] = [
        ("A minor triad", ["A", "C", "E"]),
        ("C major triad", ["C", "E", "G"]),
        ("Cero Pitágoras (A)", cero_pitagoras("A")),
        ("A blues-ish", ["A", "C", "D", "D#", "E", "G"]),
        ("Penta 1 (C#)", list(penta("C#", mode="I").notes)),
    ]
    for name, notes in samples:
        lines.append(f"{name:<22} {' '.join(f'{n:<2}' for n in notes):<22} {spell(notes)}")
    return "\n".join(lines)


def show_stats() -> str:
    """The 5 + 7 = 12 → 60 microstructures summary."""
    lines = [_header("THE NUMBERS")]
    lines.append(f"  {len(pentatonic_worlds())} penta + {len(heptatonic_worlds())} hepta = {len(DODECAMUNDO)} worlds")
    lines.append(f"  {len(PENTA_MODES)} penta modes × 12 roots = {len(microstructures())} microstructures")
    return "\n".join(lines)


def main() -> None:
    """Print the full showcase."""
    print(show_dodecamundo())
    print(show_color_wheel())
    print(show_heptatonic_modes())
    print(show_pentatonic_modes())
    print(show_gatople_clock())
    print(show_combinations())
    print(show_stats())


if __name__ == "__main__":
    main()
