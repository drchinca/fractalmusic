"""Etno-matemática — Fibonacci/Phi chords, Pythagorean ratios, and potenciación.

The book builds chords with the Fibonacci series (Ch. 5, "para clasificar
escalas") and analyzes harmony via Pythagorean ratios. Ch. 5's chessboard tale
teaches geometric potenciación (powers of the square). These helpers expose
those "fórmulas" over the Dodecamundo.
"""

from typing import Final

from fractalmusic.dodecamundo import DODECAMUNDO, NoteWorld, world

PHI: Final[float] = 1.618033988749895

# Just-intonation ratios for the 12 chromatic intervals (Pythagorean-leaning).
PYTHAGOREAN_RATIOS: Final[tuple[tuple[int, int], ...]] = (
    (1, 1),
    (16, 15),
    (9, 8),
    (6, 5),
    (5, 4),
    (4, 3),
    (45, 32),
    (3, 2),
    (8, 5),
    (5, 3),
    (16, 9),
    (15, 8),
)


def fibonacci(count: int) -> list[int]:
    """First ``count`` Fibonacci numbers starting 1, 2, 3, 5, 8, ... (book's form)."""
    series = [1, 2]
    while len(series) < count:
        series.append(series[-1] + series[-2])
    return series[:count]


def fibonacci_chord(root: str = "A", *, voices: int = 3) -> tuple[NoteWorld, ...]:
    """Stack a chord by Fibonacci semitone offsets from a root (mod 12)."""
    base = world(root).index
    offsets = fibonacci(voices)
    return tuple(DODECAMUNDO[(base + offset - 1) % 12] for offset in offsets)


def chessboard_grains(square: int) -> int:
    """Grains on a chessboard square under the book's geometric doubling (2**n).

    Ch. 5: 1, 2, 4, 16, 256, 65536 ... — the king's ruinous wager. The book uses
    the self-squaring sequence g(n) = g(n-1)**2 for the famous squares; here we
    return the classic doubling 2**(square-1) for the standard tale, exposing the
    potenciación principle (square 64 ≈ 9.2e18).
    """
    if not 1 <= square <= 64:
        raise ValueError("square must be in 1..64")
    return int(2 ** (square - 1))


def interval_ratio(from_note: str, to_note: str) -> tuple[int, int]:
    """Pythagorean frequency ratio between two worlds."""
    semitones = (world(to_note).index - world(from_note).index) % 12
    return PYTHAGOREAN_RATIOS[semitones]


def consonance(from_note: str, to_note: str) -> float:
    """Rough consonance score (1.0 = unison/octave); simpler ratios score higher."""
    numerator, denominator = interval_ratio(from_note, to_note)
    return float(round(1.0 / (numerator * denominator) ** 0.5, 4))
