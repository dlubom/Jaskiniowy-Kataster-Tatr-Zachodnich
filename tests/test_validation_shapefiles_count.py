from __future__ import annotations

from pathlib import Path

import pytest

from jktz.reporting import CheckFailed
from jktz.validation import shapefiles_count

# Inside-Tatras UTM 34N coordinates - exact values don't matter for count tests,
# only the number of features per shapefile does.
_P1 = (570000.0, 5460000.0)
_P2 = (572000.0, 5461000.0)
_P3 = (574000.0, 5462000.0)


def _layout(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Return (outdir, all_shp_path, caves_dir)."""
    outdir = tmp_path
    caves_dir = outdir / "caves"
    caves_dir.mkdir()
    return outdir, outdir / "JKTZ-v1-all.shp", caves_dir


def test_passes_when_per_cave_sum_equals_whole(tmp_path: Path, make_point_shapefile) -> None:
    outdir, all_shp, caves_dir = _layout(tmp_path)
    make_point_shapefile(all_shp, [_P1, _P2, _P3])
    make_point_shapefile(caves_dir / "CaveA.shp", [_P1, _P2])
    make_point_shapefile(caves_dir / "CaveB.shp", [_P3])
    shapefiles_count.check(outdir=outdir, version="v1")


def test_fails_on_count_mismatch(tmp_path: Path, make_point_shapefile) -> None:
    outdir, all_shp, caves_dir = _layout(tmp_path)
    make_point_shapefile(all_shp, [_P1, _P2, _P3])
    make_point_shapefile(caves_dir / "CaveA.shp", [_P1])
    make_point_shapefile(caves_dir / "CaveB.shp", [_P2])
    with pytest.raises(CheckFailed, match="Feature count mismatch") as exc:
        shapefiles_count.check(outdir=outdir, version="v1")
    msg = str(exc.value)
    assert "Whole-project (JKTZ-v1-all.shp): 3" in msg
    assert "Sum of per-cave shapefiles:" in msg
    assert "CaveA: 1" in msg
    assert "CaveB: 1" in msg


def test_passes_with_zero_caves_and_zero_features(tmp_path: Path, make_point_shapefile) -> None:
    # Edge case - if all_shp has 0 features and no caves dir entries exist,
    # both totals are 0 and the check passes.
    outdir, all_shp, _ = _layout(tmp_path)
    make_point_shapefile(all_shp, [])
    shapefiles_count.check(outdir=outdir, version="v1")
