from __future__ import annotations

from pathlib import Path

import pytest

from jktz.reporting import CheckFailed
from jktz.validation import coordinates


def _write_otwory(tmp_path: Path, body: str) -> Path:
    p = tmp_path / "OTWORY.SRV"
    p.write_text(body, encoding="utf-8")
    return p


def test_passes_with_in_extent_fix(tmp_path: Path) -> None:
    p = _write_otwory(tmp_path, "#fix\tCave:0\tE19.9000\tN49.2500\t1500m\n")
    coordinates.check(otwory_path=p)


def test_fails_on_lon_outside_extent(tmp_path: Path) -> None:
    p = _write_otwory(tmp_path, "#fix\tCave:0\tE21.0\tN49.25\t1500m\n")
    with pytest.raises(CheckFailed, match="lon 21.000000 outside"):
        coordinates.check(otwory_path=p)


def test_fails_on_lat_outside_extent(tmp_path: Path) -> None:
    p = _write_otwory(tmp_path, "#fix\tCave:0\tE19.9\tN50.0\t1500m\n")
    with pytest.raises(CheckFailed, match="lat 50.000000 outside"):
        coordinates.check(otwory_path=p)


def test_fails_on_elevation_outside_extent(tmp_path: Path) -> None:
    p = _write_otwory(tmp_path, "#fix\tCave:0\tE19.9\tN49.25\t100m\n")
    with pytest.raises(CheckFailed, match=r"elevation 100\.00 m outside"):
        coordinates.check(otwory_path=p)


def test_fails_on_missing_longitude(tmp_path: Path) -> None:
    p = _write_otwory(tmp_path, "#fix\tCave:0\tN49.25\t1500m\n")
    with pytest.raises(CheckFailed, match="missing longitude"):
        coordinates.check(otwory_path=p)


def test_ignores_non_fix_lines(tmp_path: Path) -> None:
    body = ";this is a comment\n#flag\tCave:0\t/ENTRANCE\n#fix\tCave:0\tE19.9\tN49.25\t1500m\n"
    p = _write_otwory(tmp_path, body)
    coordinates.check(otwory_path=p)
