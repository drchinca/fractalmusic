"""The spinning Gátople — a tonic-aware view over the 12 roles.

The Gátople is two concentric discs (per the canonical paper toy):

* the **outer disc** is the function/role layer — at each clock position sits a
  fixed (glyph, color, family, quality, scale pattern). It never moves.
* the **inner disc** is the note layer — it rotates freely under the outer.
  The note that lands under a given role glyph depends on the **tonic**.

The default tonic is ``A`` (La menor / Eólico horizon), which reproduces the
book's "matriarchal" setting; module-level helpers in :mod:`modes`,
:mod:`scales`, and :mod:`dodecamundo` are this default. Use :class:`Wheel`
when you want to spin — e.g. ``Wheel(tonic="F")`` puts F under ``⋮`` and
turns the whole system into F Eólico.
"""

from dataclasses import dataclass
from typing import Final

from fractalmusic.modes import (
    ALL_MODES,
    CHROMATIC_ORDER,
    PENTA_ROOTS,
    Mode,
    _clock_hour,
)


def _note_index(note: str) -> int:
    """Chromatic index of a note name (handles flat enharmonics)."""
    if note in CHROMATIC_ORDER:
        return CHROMATIC_ORDER.index(note)
    enharmonics = {"Bb": "A#", "Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#"}
    if note in enharmonics:
        return CHROMATIC_ORDER.index(enharmonics[note])
    raise ValueError(f"unknown note: {note!r}")


# Canonical roles, ordered by their default-tonic note (A-tonic). The role at
# each position carries glyph/color/family/quality/pattern — these are fixed to
# the OUTER disc and never move when the wheel spins.
_DEFAULT_TONIC: Final[str] = "A"


@dataclass(frozen=True)
class Role:
    """One of the 12 fixed positions on the outer disc.

    The role's glyph, color, clock_hour, family, quality, and scale-step pattern
    are immutable; only the *note* that fills the role changes when the wheel
    spins. The role identity is its position relative to the tonic (0..11).
    """

    position: int  # 0..11, the chromatic offset from the tonic
    mode_name: str
    glyph: str
    family: str
    quality: str
    clock_hour: int
    scale_steps: tuple[int, ...]


def _build_roles() -> tuple[Role, ...]:
    """Roles indexed by chromatic offset from the (default A-) tonic."""
    by_note: dict[str, Mode] = {m.note: m for m in ALL_MODES}
    roles: list[Role] = []
    for offset, default_note in enumerate(CHROMATIC_ORDER):
        mode = by_note[default_note]
        # The mode's note_order — turn the spelling into pure semitone steps so
        # the role can be transposed to any tonic without re-spelling.
        spelling = mode.note_order
        spelling_idx = [_note_index(n) for n in spelling]
        steps = tuple(
            (spelling_idx[(i + 1) % len(spelling_idx)] - spelling_idx[i]) % 12
            for i in range(len(spelling_idx))
        )
        roles.append(
            Role(
                position=offset,
                mode_name=mode.mode_name,
                glyph=mode.glyph,
                family=mode.family,
                quality=mode.quality,
                clock_hour=mode.clock_hour,
                scale_steps=steps,
            )
        )
    return tuple(roles)


ROLES: Final[tuple[Role, ...]] = _build_roles()


@dataclass(frozen=True)
class WheelMode:
    """A role bound to a specific note via a given tonic."""

    note: str
    role: Role

    @property
    def mode_name(self) -> str:
        return self.role.mode_name

    @property
    def glyph(self) -> str:
        return self.role.glyph

    @property
    def family(self) -> str:
        return self.role.family

    @property
    def quality(self) -> str:
        return self.role.quality

    @property
    def clock_hour(self) -> int:
        return self.role.clock_hour

    def scale_notes(self) -> tuple[str, ...]:
        """The mode's scale, spelled from its own note using the role's steps."""
        idx = _note_index(self.note)
        notes: list[str] = [self.note]
        for step in self.role.scale_steps[:-1]:
            idx = (idx + step) % 12
            notes.append(CHROMATIC_ORDER[idx])
        return tuple(notes)


@dataclass(frozen=True)
class Wheel:
    """A Gátople wheel rotated so ``tonic`` sits under the Eólico (⋮) glyph.

    Default tonic is ``A``; pass any chromatic note to spin. Methods return the
    note→mode bindings for that rotation.
    """

    tonic: str = _DEFAULT_TONIC

    @property
    def tonic_index(self) -> int:
        return _note_index(self.tonic)

    def note_at_position(self, position: int) -> str:
        """The note that fills the role at chromatic offset ``position`` (0..11)."""
        return CHROMATIC_ORDER[(self.tonic_index + position) % 12]

    def mode_for(self, note: str) -> WheelMode:
        """The mode-role currently bound to ``note`` under this rotation."""
        position = (_note_index(note) - self.tonic_index) % 12
        return WheelMode(note=note, role=ROLES[position])

    def all_modes(self) -> tuple[WheelMode, ...]:
        """The 12 (note, role) bindings under this rotation."""
        return tuple(
            WheelMode(note=self.note_at_position(p), role=ROLES[p])
            for p in range(12)
        )

    def penta(self, roman: str) -> tuple[str, ...]:
        """The Penta-mode (I..V) scale notes under this rotation."""
        roman_to_pos: Final[dict[str, int]] = {
            r: _note_index(n) - _note_index(_DEFAULT_TONIC)
            for r, n in PENTA_ROOTS
        }
        try:
            position = roman_to_pos[roman] % 12
        except KeyError as error:
            raise ValueError(f"unknown penta roman: {roman!r}") from error
        note = self.note_at_position(position)
        return WheelMode(note=note, role=ROLES[position]).scale_notes()


def spin(tonic: str) -> Wheel:
    """Convenience constructor: ``fm.spin('F')`` → ``Wheel(tonic='F')``."""
    return Wheel(tonic=tonic)


def is_valid_pattern(interval_pattern: list[int], starting_note: str) -> bool:
    """Validate (interval_pattern, starting_note) for ``generate_scale``.

    A valid pattern is a list of ints in 1..4 with at least 5 entries (the
    pentatonic floor). The starting note must be a chromatic name we recognise.
    Raises :class:`ValueError` on invalid input.
    """
    if not isinstance(interval_pattern, list) or len(interval_pattern) < 5:
        raise ValueError("interval_pattern must be a list of at least 5 ints")
    if not all(isinstance(step, int) and 1 <= step <= 4 for step in interval_pattern):
        raise ValueError("each interval step must be an int in 1..4")
    if not isinstance(starting_note, str):
        raise ValueError("starting_note must be a string")
    try:
        _note_index(starting_note)
    except ValueError as error:
        raise ValueError(f"unknown starting_note: {starting_note!r}") from error
    return True


def generate_scale(interval_pattern: list[int], starting_note: str) -> list[str]:
    """Generate a scale from a step pattern (1=½ tone, 2=tone, 3=tone½, …).

    Walks the chromatic circle from ``starting_note``, summing ``interval_pattern``
    semitone-by-semitone and emitting the note that lands at each step.
    """
    is_valid_pattern(interval_pattern, starting_note)
    current = _note_index(starting_note)
    out: list[str] = [CHROMATIC_ORDER[current]]
    for step in interval_pattern:
        current = (current + step) % 12
        out.append(CHROMATIC_ORDER[current])
    return out


def generate_twelve_outputs(
    underlying_structure: list[list[int]],
    dynamic_circular: list[str],
    starting_note: str,
) -> list[list[str]]:
    """Generate the 12 scales of the spinning Gátople from a step structure.

    For each rotation of the wheel (12 total), produce a scale from the
    corresponding row of ``underlying_structure``. ``dynamic_circular`` is the
    note ring (any 12-note ordering — typically chromatic A-order or a
    transposition); ``starting_note`` is the rotation anchor.
    """
    if len(underlying_structure) != 12:
        raise ValueError("underlying_structure must have exactly 12 rows")
    if len(dynamic_circular) != 12:
        raise ValueError("dynamic_circular must have exactly 12 notes")
    if starting_note not in dynamic_circular:
        raise ValueError(f"starting_note {starting_note!r} not in dynamic_circular")

    start = dynamic_circular.index(starting_note)
    return [
        generate_scale(underlying_structure[i], dynamic_circular[(start + i) % 12])
        for i in range(12)
    ]


def clock_hour_for(note: str, *, tonic: str = _DEFAULT_TONIC) -> int:
    """The clock hour of ``note`` when the wheel is spun to ``tonic``.

    The hour is a property of the **role** (outer disc), so it depends on
    *which role* the note currently fills under the rotation — not on the note
    itself. With ``tonic='A'`` this matches the book's canonical hours.
    """
    if tonic == _DEFAULT_TONIC:
        return _clock_hour(note)
    position = (_note_index(note) - _note_index(tonic)) % 12
    return ROLES[position].clock_hour
