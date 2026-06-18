"""Unit tests — the CLI entry points run end-to-end."""

import fractalmusic.gallery as gallery_mod
from fractalmusic.gallery import main as gallery_main
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
