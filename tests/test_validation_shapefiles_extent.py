from __future__ import annotations

from pathlib import Path

import pyproj
import pytest

from jktz.reporting import CheckFailed
from jktz.validation import shapefiles_extent

_WGS84_TO_UTM34N = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32634", always_xy=True)


def _utm(lon: float, lat: float) -> tuple[float, float]:
    """Convert WGS84 lon/lat to UTM 34N easting/northing for fixture inputs."""
    e, n = _WGS84_TO_UTM34N.transform(lon, lat)
    return e, n


# Two points well inside the Tatras WGS84 bounds (19.80-20.10 / 49.20-49.30).
_INSIDE_A = _utm(19.85, 49.22)
_INSIDE_B = _utm(20.05, 49.28)

# Two points clearly outside (west of the Tatras + south of them).
_OUTSIDE_LON = _utm(16.5, 49.25)  # lon=16.5 is far west of TATRA_LON_MIN=19.80
_OUTSIDE_LAT = _utm(19.95, 45.0)  # lat=45 is far south of TATRA_LAT_MIN=49.20


def _layout(tmp_path: Path) -> tuple[Path, Path, Path]:
    outdir = tmp_path
    caves_dir = outdir / "caves"
    caves_dir.mkdir()
    return outdir, outdir / "JKTZ-v1-all.shp", caves_dir


def test_passes_when_all_extents_inside_tatras(tmp_path: Path, make_point_shapefile) -> None:
    outdir, all_shp, caves_dir = _layout(tmp_path)
    make_point_shapefile(all_shp, [_INSIDE_A, _INSIDE_B])
    make_point_shapefile(caves_dir / "InsideCave.shp", [_INSIDE_A])
    shapefiles_extent.check(outdir=outdir, version="v1")


def test_fails_when_a_cave_extends_too_far_west(tmp_path: Path, make_point_shapefile, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("staging").mkdir()
    outdir, all_shp, caves_dir = _layout(Path("staging"))
    make_point_shapefile(all_shp, [_INSIDE_A, _INSIDE_B])
    make_point_shapefile(caves_dir / "BadCave.shp", [_OUTSIDE_LON])
    outdir = outdir.rename("new!exports")
    Path("exports").mkdir()
    _, old_all, old_caves = _layout(Path("exports"))
    make_point_shapefile(old_all, [_INSIDE_A, _INSIDE_B])
    make_point_shapefile(old_caves / "BadCave.shp", [_INSIDE_A])
    with pytest.raises(CheckFailed, match=r"lon .* outside"):
        shapefiles_extent.check(outdir=outdir, version="v1")


def test_fails_when_latitude_outside(tmp_path: Path, make_point_shapefile) -> None:
    outdir, all_shp, caves_dir = _layout(tmp_path)
    make_point_shapefile(all_shp, [_INSIDE_A, _INSIDE_B])
    make_point_shapefile(caves_dir / "BadCave.shp", [_OUTSIDE_LAT])
    with pytest.raises(CheckFailed, match=r"lat .* outside"):
        shapefiles_extent.check(outdir=outdir, version="v1")


def test_skips_empty_shapefile(tmp_path: Path, make_point_shapefile) -> None:
    # Empty shapefiles have no total_bounds; this check should silently skip
    # them and rely on empty_shapefiles.check to catch the empty case.
    outdir, all_shp, caves_dir = _layout(tmp_path)
    make_point_shapefile(all_shp, [_INSIDE_A])
    make_point_shapefile(caves_dir / "Empty.shp", [])
    shapefiles_extent.check(outdir=outdir, version="v1")


def test_rejects_valid_coordinates_with_the_wrong_declared_crs(tmp_path, make_point_shapefile):
    outdir, all_shp, caves_dir = _layout(tmp_path)
    make_point_shapefile(all_shp, [_INSIDE_A])
    make_point_shapefile(caves_dir / "Cave.shp", [_INSIDE_A], crs="EPSG:32633")

    with pytest.raises(CheckFailed, match=r"Cave\.shp.*32633.*32634"):
        shapefiles_extent.check(outdir, "v1")


@pytest.mark.parametrize("extension", [".dbf", ".prj", ".shx"])
def test_rejects_incomplete_shapefile(tmp_path, make_point_shapefile, extension):
    outdir, all_shp, _ = _layout(tmp_path)
    make_point_shapefile(all_shp, [_INSIDE_A])
    all_shp.with_suffix(extension).unlink()

    with pytest.raises(CheckFailed, match=rf"JKTZ-v1-all.*\{extension}"):
        shapefiles_extent.check(outdir, "v1")
