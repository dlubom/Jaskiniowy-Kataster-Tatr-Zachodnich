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


@pytest.mark.parametrize("lrud", ["<1,2,3,4>", "*1,2,3,4*", "<1,2,3,4> <4,3,2,1>"])
def test_ignores_comma_inside_lrud_block(tmp_path: Path, lrud: str) -> None:
    (tmp_path / "OK.SRV").write_text(f"0 {lrud}\n0\t1\t4.61\t293\t2  {lrud}\n")
    decimal_format.check(root=tmp_path)


def test_asterisk_station_and_trailing_lrud_do_not_hide_a_decimal_comma(tmp_path):
    (tmp_path / "BAD.SRV").write_text("A *8 4,61 90 0 * 1,2,3,4 *\n")
    with pytest.raises(CheckFailed, match="decimal comma found"):
        decimal_format.check(root=tmp_path)


def test_ignores_raw_subtree(tmp_path: Path) -> None:
    raw = tmp_path / "Cave" / "_RAW"
    raw.mkdir(parents=True)
    (raw / "ORIG.SRV").write_text("0\t1\t4,61\t293\t2\n")
    decimal_format.check(root=tmp_path)


def test_ignores_metadata_and_disabled_shots_but_checks_following_active_shots(tmp_path):
    path = tmp_path / "CAVE.SRV"
    text = '#[\nPROCESSING "poprawiono 1,5 na 1.5"\n#]\n#[\n0 1 1,5 90 0\n#]\n'
    path.write_text(text + "0 1 1.5 90 0\n")
    decimal_format.check(root=tmp_path)

    path.write_text(text + "0 1 1,5 90 0\n")
    with pytest.raises(CheckFailed, match=r"CAVE.SRV:7"):
        decimal_format.check(root=tmp_path)
