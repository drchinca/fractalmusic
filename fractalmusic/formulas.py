"""Etno-matemática — Fibonacci/Phi chords, Pythagorean ratios, and potenciación.

The book builds chords with the Fibonacci series (Ch. 5, "para clasificar
escalas") and analyzes harmony via Pythagorean ratios. Ch. 5's chessboard tale
teaches geometric potenciación (powers of the square). These helpers expose
those "fórmulas" over the Dodecamundo.
"""

from typing import Final

from fractalmusic.dodecamundo import DODECAMUNDO, NoteWorld, world

PHI: Final[float] = 1.618033988749895

# 5-limit just-intonation frequency ratios for the 12 chromatic intervals.
# True Pythagorean ratios use only powers of 3/2 (e.g. 256/243 for the minor
# second); these are 5-limit just intervals, which the book uses for harmonic
# analysis. The two systems agree on the unison, octave, fifth, and fourth.
JUST_RATIOS: Final[tuple[tuple[int, int], ...]] = (
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
# Back-compat alias — older callers expected this name. Prefer JUST_RATIOS.
PYTHAGOREAN_RATIOS: Final[tuple[tuple[int, int], ...]] = JUST_RATIOS


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
    """Grains on a chessboard square under the classic doubling (``2**(n-1)``).

    The standard wheat-and-chessboard tale: 1, 2, 4, 8, 16, ... — square 64 is
    ``2**63`` ≈ 9.22e18. Use :func:`self_squaring_grains` for the self-squaring
    variant the book recites in Ch. 5.
    """
    if not 1 <= square <= 64:
        raise ValueError("square must be in 1..64")
    return int(2 ** (square - 1))


def self_squaring_grains(step: int) -> int:
    """The self-squaring sequence the book recites in Ch. 5: ``2 ** (2 ** (n-1))``.

    Yields 2, 4, 16, 256, 65 536, 4 294 967 296, 1.84e19, 3.4e38, ... — the
    book's "potenciación" variant where each step squares the previous. Python
    ints are unbounded, so any positive ``step`` is valid; ``step >= 9`` produces
    numbers larger than int64 but Python handles them natively.
    """
    if step < 1:
        raise ValueError("step must be >= 1")
    return int(2 ** (2 ** (step - 1)))


def interval_ratio(from_note: str, to_note: str) -> tuple[int, int]:
    """Pythagorean frequency ratio between two worlds."""
    semitones = (world(to_note).index - world(from_note).index) % 12
    return PYTHAGOREAN_RATIOS[semitones]


def consonance(from_note: str, to_note: str) -> float:
    """Rough consonance score (1.0 = unison/octave); simpler ratios score higher."""
    numerator, denominator = interval_ratio(from_note, to_note)
    return float(round(1.0 / (numerator * denominator) ** 0.5, 4))
