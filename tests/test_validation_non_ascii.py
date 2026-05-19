from __future__ import annotations

from pathlib import Path

import pytest

from jktz.reporting import CheckFailed
from jktz.validation import non_ascii


def test_passes_with_pure_ascii(tmp_path: Path) -> None:
    (tmp_path / "OK.SRV").write_text("#prefix Marmurowa\n0\t1\t4.61\t293\t2\n")
    non_ascii.check(root=tmp_path)


def test_fails_on_non_ascii_byte_in_content(tmp_path: Path) -> None:
    bad = tmp_path / "BAD.SRV"
    # CP1250 byte 0xb9 = 'ą' — a Polish diacritic that must be ASCII-folded.
    bad.write_bytes(b"#prefix Mietusia\xb9\n")
    with pytest.raises(CheckFailed, match=r"byte 0xb9"):
        non_ascii.check(root=tmp_path)


def test_allows_tab_and_cr(tmp_path: Path) -> None:
    (tmp_path / "OK.SRV").write_bytes(b"0\t1\t4.61\t293\t2\r\n")
    non_ascii.check(root=tmp_path)


def test_ignores_raw_subtree(tmp_path: Path) -> None:
    raw = tmp_path / "Cave" / "_RAW"
    raw.mkdir(parents=True)
    (raw / "ORIG.SRV").write_bytes(b"raw with diacritics: \xb9\xea\n")
    non_ascii.check(root=tmp_path)
