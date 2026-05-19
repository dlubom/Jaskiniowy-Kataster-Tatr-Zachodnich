from __future__ import annotations

from pathlib import Path

import pytest

from jktz.reporting import CheckFailed
from jktz.validation import prefixes


def test_passes_with_dot_free_prefix(tmp_path: Path) -> None:
    (tmp_path / "OK.SRV").write_text("#prefix Marmurowa\n#prefix2 WielkaSniezna\n")
    prefixes.check(root=tmp_path)


def test_fails_on_prefix_with_dot(tmp_path: Path) -> None:
    (tmp_path / "BAD.SRV").write_text("#prefix Cave.Section\n")
    with pytest.raises(CheckFailed, match=r"#prefix directives must not contain '\.'"):
        prefixes.check(root=tmp_path)


def test_fails_on_prefix2_with_dot(tmp_path: Path) -> None:
    (tmp_path / "BAD.SRV").write_text("#prefix2 System.Sub\n")
    with pytest.raises(CheckFailed):
        prefixes.check(root=tmp_path)


def test_ignores_raw_subtree(tmp_path: Path) -> None:
    raw = tmp_path / "Cave" / "_RAW"
    raw.mkdir(parents=True)
    (raw / "ORIG.SRV").write_text("#prefix Original.With.Dots\n")
    prefixes.check(root=tmp_path)
