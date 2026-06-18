"""Unicode glyph vocabulary for the Dodecamundo (Sistema Fractal de Patricio Torres).

Canonical bindings from *El Sistema Fractal* (Torres, 2024), Ch. 8 "Música de
Colores" and Ch. 4 "Explorando la esfera de los sonidos". Each of the 7 natural
notes carries the glyph of its Greek mode; the 5 black keys are the pentatonic
"stars" labelled with roman numerals.

The 7 natural-note glyphs (Ch. 8):
  A Eólico    ⋮  "los dos puntos de la división matemática" (rest / relaxation)
  B Locrio    △  "la primera figura geométrica natural, el triángulo"
  C Jónico    □  "el cuadrado" (verticality, the major)
  D Dórico    +  "la cruz" (first Cero Pitágoras, instability)
  E Frigio    ♀  koppa ϙ — the key that closes the circle
  F Lidio     ↑  "una flecha exclusiva hacia arriba"
  G Mixolidio ↓  "una flecha inclusiva hacia abajo" (compression)
"""

from typing import Final

# --- The 7 mode glyphs, one per natural note ---
EOLICO: Final[str] = "⋮"  # A — vertical ellipsis (division dots)
LOCRIO: Final[str] = "△"  # B — white up-pointing triangle
JONICO: Final[str] = "□"  # C — white square
DORICO: Final[str] = "+"  # D — plus / cross
FRIGIO: Final[str] = "♀"  # E — female sign (stands in for koppa ϙ)
LIDIO: Final[str] = "↑"  # F — up arrow
MIXOLIDIO: Final[str] = "↓"  # G — down arrow

# --- The pentatonic / black-key marker (the 5 penta stars) ---
BLACK_STAR: Final[str] = "★"
