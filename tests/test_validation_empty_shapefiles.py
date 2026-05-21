from __future__ import annotations

from pathlib import Path

import pytest

from jktz.reporting import CheckFailed
from jktz.validation import empty_shapefiles


def test_passes_with_no_empty_shapefiles(tmp_path: Path) -> None:
    (tmp_path / "data.shp").write_bytes(b"\x00" * 500)
    empty_shapefiles.check(outdir=tmp_path)


def test_fails_on_100_byte_shapefile(tmp_path: Path) -> None:
    (tmp_path / "empty.shp").write_bytes(b"\x00" * 100)
    with pytest.raises(CheckFailed, match="empty Shapefiles"):
        empty_shapefiles.check(outdir=tmp_path)


def test_finds_empty_shapefile_in_nested_dir(tmp_path: Path) -> None:
    nested = tmp_path / "caves"
    nested.mkdir()
    (nested / "empty.shp").write_bytes(b"\x00" * 100)
    with pytest.raises(CheckFailed):
        empty_shapefiles.check(outdir=tmp_path)
