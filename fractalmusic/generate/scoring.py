"""Score realized events against the pattern's claimed mode + fractal shape."""

from fractalmusic.formulas import PHI
from fractalmusic.generate.realize import _scale_for_mode
from fractalmusic.generate.types import Event, Pattern, Score
from fractalmusic.wheel import Wheel

MODE_WEIGHT: float = 0.55
RHYTHM_WEIGHT: float = 0.20
FRACTAL_WEIGHT: float = 0.25


def _mode_membership(events: tuple[Event, ...], pattern: Pattern) -> tuple[float, list[str]]:
    if not events:
        return 0.0, ["no events"]
    wheel = Wheel(tonic=pattern.tonic)
    scale = set(_scale_for_mode(wheel=wheel, mode=pattern.mode))
    in_mode = sum(1 for e in events if e.note in scale)
    ratio = in_mode / len(events)
    breaches: list[str] = []
    if ratio < 1.0:
        breaches.append(f"mode-tone violation: {len(events) - in_mode}/{len(events)} off-mode")
    return ratio, breaches


def _rhythmic_coherence(pattern: Pattern) -> float:
    """Reward rhythms whose total length is a power-of-2 number of beats."""
    total = sum(pattern.rhythm)
    if total <= 0:
        return 0.0
    int_total = int(total)
    if int_total < 1:
        return 0.5
    nearest_pow2 = 1 << max(0, int_total.bit_length() - 1)
    delta = abs(total - nearest_pow2) / nearest_pow2
    return max(0.0, 1.0 - delta)


def _fractal_shape(pattern: Pattern) -> float:
    """Reward degree-walks whose mean step approximates a PHI-like ratio.

    Crude proxy for "fractal" — penalizes flat repeats and large random jumps.
    """
    if len(pattern.degrees) < 2:
        return 0.5
    steps = [abs(b - a) for a, b in zip(pattern.degrees[:-1], pattern.degrees[1:], strict=True)]
    avg_step = sum(steps) / len(steps)
    target = PHI  # ~1.618
    delta = abs(avg_step - target) / target
    return max(0.0, 1.0 - min(delta, 1.0))


def score(events: tuple[Event, ...], pattern: Pattern) -> Score:
    """Soft-score events against the pattern. Total in [0,1]."""
    membership, mode_breaches = _mode_membership(events=events, pattern=pattern)
    rhythm = _rhythmic_coherence(pattern=pattern)
    fractal = _fractal_shape(pattern=pattern)
    total = MODE_WEIGHT * membership + RHYTHM_WEIGHT * rhythm + FRACTAL_WEIGHT * fractal
    return Score(
        total=round(total, 4),
        mode_membership=round(membership, 4),
        rhythmic_coherence=round(rhythm, 4),
        fractal_shape=round(fractal, 4),
        breaches=tuple(mode_breaches),
    )
