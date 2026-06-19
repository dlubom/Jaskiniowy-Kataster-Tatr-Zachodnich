from __future__ import annotations

from pathlib import Path

import pytest

from jktz.reporting import CheckFailed
from jktz.validation import directives


def test_passes_with_only_allowed_directives(tmp_path: Path) -> None:
    (tmp_path / "OK.SRV").write_text("#prefix Cave\n#fix Cave:0 E19.9 N49.25 1500m\n")
    directives.check(root=tmp_path)


def test_fails_on_pound_left_angle_directive(tmp_path: Path) -> None:
    (tmp_path / "BAD.SRV").write_text("#<bogus\n0\t1\t1.0\t90\t0\n")
    with pytest.raises(CheckFailed, match="Invalid #< directive"):
        directives.check(root=tmp_path)


def test_ignores_raw_subtree(tmp_path: Path) -> None:
    source = tmp_path / "Cave" / "_RAW" / "01" / "SOURCE.SRV"
    source.parent.mkdir(parents=True)
    source.write_text("#<source syntax\n")

    directives.check(root=tmp_path)
