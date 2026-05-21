from __future__ import annotations

from pathlib import Path

import pytest

from jktz.reporting import CheckFailed
from jktz.validation import filenames


def test_passes_with_uppercase_basename_and_extension(tmp_path: Path) -> None:
    (tmp_path / "VALID.SRV").write_text("")
    filenames.check(root=tmp_path)


def test_fails_on_lowercase_extension(tmp_path: Path) -> None:
    (tmp_path / "ANY.srv").write_text("")
    with pytest.raises(CheckFailed, match="SRV filename format"):
        filenames.check(root=tmp_path)


def test_fails_on_lowercase_basename_letter(tmp_path: Path) -> None:
    (tmp_path / "MixedCase.SRV").write_text("")
    with pytest.raises(CheckFailed, match="SRV filename format"):
        filenames.check(root=tmp_path)


def test_ignores_raw_subtree(tmp_path: Path) -> None:
    raw = tmp_path / "Some_Cave" / "_RAW"
    raw.mkdir(parents=True)
    (raw / "original_lower.srv").write_text("")
    (raw / "MixedCase.SRV").write_text("")
    filenames.check(root=tmp_path)


def test_basename_with_digits_and_underscores_is_valid(tmp_path: Path) -> None:
    (tmp_path / "TC1601_A1.SRV").write_text("")
    filenames.check(root=tmp_path)
