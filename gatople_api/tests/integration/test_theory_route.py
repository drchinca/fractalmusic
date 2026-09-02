"""Integration tests for /api/theory/* — pure fractalmusic.geometry math,
no fakes needed since there's no external service in this path at all.

Every request is tonic + mode + degree + quality — never a bare note
letter, per Cardinal Invariant #2 (function lives on the wheel, not on
the note)."""

from __future__ import annotations

from fastapi.testclient import TestClient
from fractalmusic.generate import JsonCorpus, StubExpert

from gatople_api.app import create_app
from gatople_api.llm_expert import LLMExpert
from gatople_api.services import GatopleServices
from gatople_api.settings import ChatSettings
from tests.integration.conftest import FakeLLM, FakeRetriever


def _client(tmp_path) -> TestClient:
    settings = ChatSettings(
        anthropic_api_key="test-key-not-real",
        corpus_root=tmp_path / "patterns",
    )
    fake_claude = FakeLLM(name="claude")
    services = GatopleServices(
        retriever=FakeRetriever(),
        llm_claude=fake_claude,
        llm_ollama=FakeLLM(name="ollama"),
        similarity=lambda _a, _b: _always_high(),
        settings=settings,
        expert=StubExpert(),
        llm_expert=LLMExpert(llm=fake_claude),
        corpus=JsonCorpus(root=settings.corpus_root),
    )
    return TestClient(create_app(services=services))


async def _always_high() -> float:
    return 0.9


def test_chord_options_returns_the_closed_sets(tmp_path) -> None:
    client = _client(tmp_path)

    response = client.get("/api/theory/chord-options")

    assert response.status_code == 200
    body = response.json()
    assert body["modes"] == [
        "Eólico",
        "Locrio",
        "Jónico",
        "Dórico",
        "Frigio",
        "Lidio",
        "Mixolidio",
        "PentaI",
        "PentaII",
        "PentaIII",
        "PentaIV",
        "PentaV",
    ]
    assert set(body["qualities"]) == {
        "major",
        "minor",
        "augmented",
        "diminished",
        "maj7",
        "min7",
        "dom7",
        "m7b5",
        "dim7",
    }


def test_augmented_triad_geometry_is_a_regular_polygon(tmp_path) -> None:
    # The headline example: degree I of Jónico under tonic A is C (the C
    # major scale starts on C — book Ch. 4 trivia) — C augmented forms a
    # perfect equilateral triangle centered on the wheel.
    client = _client(tmp_path)

    response = client.get(
        "/api/theory/chord",
        params={"tonic": "A", "mode": "Jónico", "degree": 1, "quality": "augmented"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["root"] == "C"
    assert body["symbol"] == "Caug"
    assert body["notes"] == ["C", "E", "G#"]
    assert body["polygon"]["is_regular"] is True
    assert len(body["polygon"]["vertices"]) == 3
    cx, cy = body["polygon"]["centroid"]
    assert abs(cx) < 1e-6
    assert abs(cy) < 1e-6
    assert len(body["coordinates_3d"]) == 3
    # The edge-consonance / geometry correspondence: an equilateral
    # triangle's edges are all the same interval, so all the same
    # Pythagorean-ratio consonance too.
    assert len(set(body["edge_consonance"])) == 1


def test_same_degree_resolves_a_different_note_under_a_different_tonic(tmp_path) -> None:
    # A degree has no fixed identity independent of its tonic: the same
    # (mode, degree) resolves to a different absolute root note under a
    # different tonic. But the polygon's SHAPE and POSITION are anchored
    # to the wheel's own relative coordinate frame, not to absolute note
    # names — since both "which degree" and "which chord shape" are
    # resolved relative to the same tonic, the vertices come out identical
    # even though the underlying notes differ. That invariance is itself
    # the point of Cardinal Invariant #2: the geometry lives on the wheel.
    client = _client(tmp_path)

    at_a = client.get(
        "/api/theory/chord",
        params={"tonic": "A", "mode": "Jónico", "degree": 1, "quality": "augmented"},
    ).json()
    at_d = client.get(
        "/api/theory/chord",
        params={"tonic": "D", "mode": "Jónico", "degree": 1, "quality": "augmented"},
    ).json()

    assert at_a["root"] != at_d["root"]
    assert at_a["polygon"]["is_regular"] is True
    assert at_d["polygon"]["is_regular"] is True
    assert at_a["polygon"]["vertices"] == at_d["polygon"]["vertices"]


def test_maj7_chord_is_not_a_regular_polygon(tmp_path) -> None:
    client = _client(tmp_path)

    response = client.get(
        "/api/theory/chord",
        params={"tonic": "A", "mode": "Jónico", "degree": 1, "quality": "maj7"},
    )

    body = response.json()
    assert body["notes"] == ["C", "E", "G", "B"]
    assert body["polygon"]["is_regular"] is False
    # Real harmonic tension, not a flat classical label: the edges are not
    # all the same interval, so not all the same consonance either.
    assert len(set(body["edge_consonance"])) > 1


def test_unknown_quality_returns_422(tmp_path) -> None:
    client = _client(tmp_path)

    response = client.get(
        "/api/theory/chord",
        params={"tonic": "A", "mode": "Jónico", "degree": 1, "quality": "made-up"},
    )

    assert response.status_code == 422


def test_unknown_mode_returns_422(tmp_path) -> None:
    client = _client(tmp_path)

    response = client.get(
        "/api/theory/chord",
        params={"tonic": "A", "mode": "made-up-mode", "degree": 1, "quality": "major"},
    )

    assert response.status_code == 422


def test_degree_out_of_range_for_penta_mode_returns_422(tmp_path) -> None:
    client = _client(tmp_path)

    response = client.get(
        "/api/theory/chord",
        params={"tonic": "A", "mode": "PentaI", "degree": 6, "quality": "major"},
    )

    assert response.status_code == 422
