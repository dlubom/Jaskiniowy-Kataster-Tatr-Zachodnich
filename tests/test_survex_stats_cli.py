from __future__ import annotations

from pathlib import Path

from jktz.cli import survex_stats
from jktz.exports.tools import ExternalToolError


def test_survex_stats_runs_cavern_from_source_directory(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "survey" / "main.svx"
    source.parent.mkdir()
    source.write_text("*begin main\n*end main\n", encoding="utf-8")
    calls: list[tuple[list[str], Path | None]] = []

    def fake_cavern(args: list[str], cwd: Path | None = None, log_to=None) -> None:
        calls.append((args, cwd))

    monkeypatch.setattr(survex_stats.tools, "cavern", fake_cavern)

    assert survex_stats.main([str(source)]) == 0
    assert calls[0][0][:2] == ["--no-auxiliary-files", "-o"]
    assert calls[0][0][-1] == "main.svx"
    assert calls[0][1] == source.parent


def test_survex_stats_reports_missing_source(tmp_path: Path, capsys) -> None:
    missing = tmp_path / "missing.svx"

    assert survex_stats.main([str(missing)]) == 1
    assert f"ERROR: file not found: {missing}" in capsys.readouterr().err


def test_survex_stats_reports_missing_or_failed_cavern(tmp_path: Path, monkeypatch, capsys) -> None:
    source = tmp_path / "main.wpj"
    source.write_text(".BOOK Main\n", encoding="utf-8")

    def fail(*args, **kwargs) -> None:
        raise ExternalToolError("cavern unavailable")

    monkeypatch.setattr(survex_stats.tools, "cavern", fail)

    assert survex_stats.main([str(source)]) == 1
    assert "ERROR: cavern unavailable" in capsys.readouterr().err
