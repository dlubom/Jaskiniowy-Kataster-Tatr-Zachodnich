from __future__ import annotations

from pathlib import Path

import pytest

from jktz.reporting import CheckFailed
from jktz.validation import decimal_format


def test_passes_with_dot_decimals(tmp_path: Path) -> None:
    (tmp_path / "OK.SRV").write_text("0\t1\t4.61\t293\t2\n1\t2\t2.06\t303\t7\n")
    decimal_format.check(root=tmp_path)


def test_fails_on_comma_decimal_in_measurement(tmp_path: Path) -> None:
    (tmp_path / "BAD.SRV").write_text("0\t1\t4,61\t293\t2\n")
    with pytest.raises(CheckFailed, match="decimal comma found"):
        decimal_format.check(root=tmp_path)


def test_ignores_comma_inside_comment(tmp_path: Path) -> None:
    (tmp_path / "OK.SRV").write_text("0\t1\t4.61\t293\t2  ; up to 1,5m wide bedding\n")
    decimal_format.check(root=tmp_path)


def test_ignores_comma_inside_lrud_block(tmp_path: Path) -> None:
    (tmp_path / "OK.SRV").write_text("0\t1\t4.61\t293\t2  <1,2,3,4>\n")
    decimal_format.check(root=tmp_path)


def test_ignores_raw_subtree(tmp_path: Path) -> None:
    raw = tmp_path / "Cave" / "_RAW"
    raw.mkdir(parents=True)
    (raw / "ORIG.SRV").write_text("0\t1\t4,61\t293\t2\n")
    decimal_format.check(root=tmp_path)
