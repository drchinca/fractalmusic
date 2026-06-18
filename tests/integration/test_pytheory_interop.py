"""Integration tests — fractalmusic worlds round-trip through pytheory."""

from fractalmusic.dodecamundo import DODECAMUNDO, world
from fractalmusic.scales import mode_scale, penta
from pytheory import Tone


def test_every_world_yields_a_valid_pytheory_tone():
    for w in DODECAMUNDO:
        tone = w.tone(octave=4)
        assert isinstance(tone, Tone)
        assert tone.exists


def test_world_index_matches_pytheory_western_order():
    # pytheory western is A-indexed; our worlds must line up 1:1.
    from pytheory.systems import SYSTEMS

    western = [names[0] for names in SYSTEMS["western"].tone_names]
    assert [w.note for w in DODECAMUNDO] == western


def test_pentatonic_tones_have_distinct_positive_frequencies():
    tones = [world(n).tone(octave=4) for n in penta("A", mode="I").notes]
    freqs = [t.frequency for t in tones]
    assert all(f > 0 for f in freqs)
    assert len(set(freqs)) == 5  # five distinct pitches


def test_eolico_scale_is_seven_distinct_naturals():
    notes = mode_scale("A").notes
    tones = [world(n).tone(octave=4) for n in notes]
    assert len(tones) == 7
    assert len({t.frequency for t in tones}) == 7  # all distinct pitches


def test_fractal_pentatonic_matches_pytheory_intervals():
    # A-minor-pentatonic worlds → semitone deltas should be 3,2,2,3(,2 wrap).
    indices = [world(n).index for n in penta("A", mode="I").notes]
    deltas = [(b - a) % 12 for a, b in zip(indices, indices[1:], strict=False)]
    assert deltas == [2, 3, 2, 2]  # A→B→D→E→F# within the octave
