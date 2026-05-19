from __future__ import annotations

from pathlib import Path

import pytest

from jktz.reporting import CheckFailed
from jktz.validation import unattached


def test_passes_when_log_has_no_unattached_message(tmp_path: Path) -> None:
    log = tmp_path / "cavern.txt"
    log.write_text("cavern compile OK\n\n")
    unattached.check(log_path=log)


def test_fails_on_fixed_point_message(tmp_path: Path) -> None:
    log = tmp_path / "cavern.txt"
    log.write_text(
        "warning: station X12 is not attached to a fixed point\n"
        "  see survey FOO\n"
        "\n"
        "compile complete\n"
    )
    with pytest.raises(CheckFailed, match="not attached to a fixed point"):
        unattached.check(log_path=log)


def test_fails_on_control_point_message(tmp_path: Path) -> None:
    log = tmp_path / "cavern.txt"
    log.write_text("warning: not attached to a control point\n\n")
    with pytest.raises(CheckFailed):
        unattached.check(log_path=log)
