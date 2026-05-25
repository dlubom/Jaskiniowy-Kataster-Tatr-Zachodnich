from __future__ import annotations

from pathlib import Path

import pytest

from jktz.reporting import CheckFailed
from jktz.validation import cavern_warnings


def test_passes_when_log_has_no_warning(tmp_path: Path) -> None:
    log = tmp_path / "cavern.txt"
    log.write_text(
        "Survex 1.4.21\n"
        "Survey contains 10 survey stations, joined by 9 legs.\n"
        "There were 0 warning(s).\n"
    )
    cavern_warnings.check(log_path=log)


def test_fails_on_linux_warning_line(tmp_path: Path) -> None:
    log = tmp_path / "cavern.txt"
    log.write_text(
        "Poligony/Cave/CAVE.srv:12:18: warning: Compass reading given on plumbed leg\n"
        " 12 13 17.05 90.0 259.0\n"
        "                  ^~~~~\n"
    )

    with pytest.raises(CheckFailed) as excinfo:
        cavern_warnings.check(log_path=log)

    assert "CAVE.srv:12:18: warning: Compass reading given on plumbed leg" in str(excinfo.value)


def test_fails_on_windows_warning_line(tmp_path: Path) -> None:
    log = tmp_path / "cavern.txt"
    log.write_bytes(
        b"C:\\project\\Poligony\\Cave\\CAVE.srv:6: warning: No survey date specified\r\n"
    )

    with pytest.raises(CheckFailed) as excinfo:
        cavern_warnings.check(log_path=log)

    assert "C:\\project\\Poligony\\Cave\\CAVE.srv:6: warning:" in str(excinfo.value)


def test_fails_on_nonzero_warning_summary(tmp_path: Path) -> None:
    log = tmp_path / "cavern.txt"
    log.write_text("Survey contains 10 survey stations.\nThere were 2 warning(s).\n")

    with pytest.raises(CheckFailed, match=r"There were 2 warning\(s\)"):
        cavern_warnings.check(log_path=log)
