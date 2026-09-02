"""Unit tests — the degenerate/edge-case branches of scoring.py.

These were previously uncovered entirely (not just weakly asserted): the
empty-events case, the off-mode breach message, and the single-note /
zero-length pattern edge cases in the rhythm and fractal-shape heuristics.
"""

from fractalmusic.generate import Event, Pattern, Provenance, realize, score

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
        name="test", tonic=tonic, mode=mode, degrees=degrees, rhythm=rhythm, provenance=PROV
    )


def _event(note: str) -> Event:
    return Event(
        note=note,  # type: ignore[arg-type]
        octave=4,
        beat=0.0,
        duration=1.0,
        time_sec=0.0,
        freq_hz=440.0,
        role_hour=9,
        carta_glyph="⋮",
    )


def test_score_with_no_events_yields_zero_membership_and_breach():
    s = score(events=(), pattern=_pattern())
    assert s.mode_membership == 0.0
    assert s.breaches == ("no events",)


def test_score_reports_off_mode_breach_count():
    # C# is not in A Eólico's scale (A B C D E F G).
    events = (_event("A"), _event("C#"), _event("C"))
    s = score(events=events, pattern=_pattern())
    assert s.mode_membership < 1.0
    assert s.breaches == ("mode-tone violation: 1/3 off-mode",)


def test_rhythmic_coherence_zero_total_scores_zero():
    pattern = _pattern(degrees=(1, 2), rhythm=(0.0, 0.0))
    s = score(events=(_event("A"), _event("B")), pattern=pattern)
    assert s.rhythmic_coherence == 0.0


def test_rhythmic_coherence_sub_one_total_scores_half():
    pattern = _pattern(degrees=(1,), rhythm=(0.5,))
    s = score(events=(_event("A"),), pattern=pattern)
    assert s.rhythmic_coherence == 0.5


def test_fractal_shape_single_degree_scores_half():
    pattern = _pattern(degrees=(1,), rhythm=(1.0,))
    s = score(events=(_event("A"),), pattern=pattern)
    assert s.fractal_shape == 0.5


def test_score_total_matches_the_weighted_formula():
    # 0.55*membership + 0.20*rhythm + 0.25*fractal. Pins the exact weighting —
    # sub-score assertions and the tautological `band in {strong, tentative,
    # exploratory}` check (every band is a member of that set) can't catch a
    # swapped weight, since it doesn't move any individual sub-score.
    pattern = _pattern()
    s = score(events=realize(pattern), pattern=pattern)
    expected = round(
        0.55 * s.mode_membership + 0.20 * s.rhythmic_coherence + 0.25 * s.fractal_shape, 4
    )
    assert s.total == expected
    assert s.total == 0.9266
