"""GET /api/theory/chord-options — the closed sets (modes, qualities) the FE
renders as the chord picker's dropdowns.

GET /api/theory/chord — a chord's geometry (2D polygon on the Gátople wheel
+ 3D dodecahedron coordinates), resolved from a scale DEGREE, never a bare
note letter. A note has no fixed identity in this system — degree III of
Dórico under tonic F# is a different note than under tonic A. Every input
here is tonic + mode + degree + quality; the actual note names only ever
appear in the response, as a resolved *result*, never as something the
caller picks (Cardinal Invariant #2 — function lives on the wheel, not on
the note). Pure fractalmusic.geometry/wheel math — no LLM, no corpus, no
external services, deterministic and fast.
"""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from fractalmusic.geometry import CHORD_QUALITIES, Chord
from pydantic import BaseModel

from gatople_api.routes.generate import MODE_ORDER

router = APIRouter()


class ChordOptionsResponse(BaseModel):
    modes: list[str]
    qualities: list[str]


@router.get("/api/theory/chord-options")
def chord_options() -> ChordOptionsResponse:
    return ChordOptionsResponse(modes=list(MODE_ORDER), qualities=list(CHORD_QUALITIES))


class Polygon2DPayload(BaseModel):
    vertices: list[list[float]]
    centroid: list[float]
    perimeter: float
    is_regular: bool


class ChordGeometryResponse(BaseModel):
    tonic: str
    mode: str
    degree: int
    quality: str
    root: str
    symbol: str
    notes: list[str]
    glyphs: list[str]
    polygon: Polygon2DPayload
    coordinates_3d: list[list[float]]
    # Pythagorean-ratio consonance per polygon edge, in vertex order — the
    # book's own etno-matemática tension math, not a classical-theory label.
    edge_consonance: list[float]


@router.get("/api/theory/chord")
def chord_geometry(
    tonic: Annotated[str, Query(min_length=1, max_length=2)],
    mode: Annotated[str, Query(min_length=1, max_length=20)],
    degree: Annotated[int, Query(ge=1, le=7)],
    quality: Annotated[str, Query(min_length=1, max_length=20)],
) -> ChordGeometryResponse:
    if mode not in MODE_ORDER:
        raise HTTPException(status_code=422, detail=f"unknown mode: {mode!r}")
    if quality not in CHORD_QUALITIES:
        raise HTTPException(status_code=422, detail=f"unknown chord quality: {quality!r}")

    try:
        chord = Chord.from_degree(tonic=tonic, mode=mode, degree=degree, quality=quality)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    polygon = chord.polygon_2d(tonic=tonic)

    return ChordGeometryResponse(
        tonic=tonic,
        mode=mode,
        degree=degree,
        quality=chord.quality,
        root=chord.root,
        symbol=chord.symbol,
        notes=list(chord.notes),
        glyphs=list(chord.glyphs),
        polygon=Polygon2DPayload(
            vertices=[list(v) for v in polygon.vertices],
            centroid=list(polygon.centroid),
            perimeter=polygon.perimeter,
            is_regular=polygon.is_regular,
        ),
        coordinates_3d=[list(c) for c in chord.coordinates_3d()],
        edge_consonance=list(chord.edge_consonance()),
    )
