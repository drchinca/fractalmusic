"""Unit tests — the CLI entry points run end-to-end."""

import json
import sys

import fractalmusic.gallery as gallery_mod
from fractalmusic.gallery import main as gallery_main
from fractalmusic.generate.cli import main as generate_main
from fractalmusic.showcase import main as showcase_main


def test_showcase_main_prints(capsys):
    showcase_main()
    out = capsys.readouterr().out
    assert "EL DODECAMUNDO" in out
    assert "60 microstructures" in out


def test_gallery_main_writes_to_arg_dir(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(gallery_mod.sys, "argv", ["fractalmusic-gallery", str(tmp_path)])
    gallery_main()
    out = capsys.readouterr().out
    assert "wrote:" in out
    assert (tmp_path / "deck.svg").exists()


def test_gallery_main_uses_default_dir(monkeypatch):
    seen: list[object] = []

    def fake_write(target):
        seen.append(target)
        return []

    monkeypatch.setattr(gallery_mod.sys, "argv", ["fractalmusic-gallery"])
    monkeypatch.setattr(gallery_mod, "write_gallery", fake_write)
    gallery_main()
    assert seen == [gallery_mod._DEFAULT_DIR]


def test_generate_cli_writes_midi_and_json(tmp_path, monkeypatch, capsys):
    corpus_dir = tmp_path / "patterns"
    out_dir = tmp_path / "generated"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "fractalmusic-generate",
            "--tonic",
            "A",
            "--mode",
            "Eólico",
            "--length",
            "4",
            "--flavor",
            "free",
            "--corpus",
            str(corpus_dir),
            "--out",
            str(out_dir),
            "--bpm",
            "96",
        ],
    )

    generate_main()

    out = capsys.readouterr().out
    assert "score=" in out
    assert "band=" in out
    assert "events=4" in out

    json_path = out_dir / "A-Eólico-free.json"
    midi_path = out_dir / "A-Eólico-free.mid"
    assert json_path.exists()
    assert midi_path.exists()
    assert midi_path.stat().st_size > 0

    payload = json.loads(json_path.read_text())
    assert payload["tonic"] == "A"
    assert payload["mode"] == "Eólico"
    assert len(payload["events"]) == 4
    assert corpus_dir.exists()  # JsonCorpus created its root dir


def test_generate_cli_defaults_bpm_and_flavor(tmp_path, monkeypatch, capsys):
    out_dir = tmp_path / "generated"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "fractalmusic-generate",
            "--tonic",
            "C#",
            "--mode",
            "PentaI",
            "--corpus",
            str(tmp_path / "patterns"),
            "--out",
            str(out_dir),
        ],
    )

    generate_main()

    payload = json.loads((out_dir / "C#-PentaI-free.json").read_text())
    assert payload["bpm"] == 96  # default --bpm
    assert len(payload["events"]) == 16  # default --length
