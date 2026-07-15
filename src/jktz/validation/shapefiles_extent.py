from __future__ import annotations

from pathlib import Path

import pyogrio
import pyproj

from jktz.reporting import CheckFailed
from jktz.validation.constants import (
    TATRA_LAT_MAX,
    TATRA_LAT_MIN,
    TATRA_LON_MAX,
    TATRA_LON_MIN,
)

# Survex compiles to UTM zone 34N (EPSG:32634); we reproject to geographic
# WGS84 (EPSG:4326) and compare to the Tatra Mountains bounding box.
_UTM34N_TO_WGS84 = pyproj.Transformer.from_crs("EPSG:32634", "EPSG:4326", always_xy=True)


def _wgs84_bbox_of_shapefile(shp: Path) -> tuple[float, float, float, float] | None:
    """Return (lon_min, lat_min, lon_max, lat_max) or None for empty shapefiles."""
    info = pyogrio.read_info(shp)
    # pyogrio reports total_bounds=(0,0,0,0) for empty layers - use the feature
    # count as the real "is empty" signal instead.
    if int(info.get("features", 0)) == 0:
        return None
    bounds = info.get("total_bounds")
    if bounds is None or any(b is None for b in bounds):
        return None
    xmin, ymin, xmax, ymax = bounds
    # The shapefile extent is an axis-aligned rectangle in UTM, but after
    # reprojection to WGS84 it is no longer axis-aligned. Transform all four
    # corners and take the bounding box of the result before checking it
    # against the Tatras envelope.
    xs = [xmin, xmax, xmin, xmax]
    ys = [ymin, ymin, ymax, ymax]
    lons, lats = _UTM34N_TO_WGS84.transform(xs, ys)
    return min(lons), min(lats), max(lons), max(lats)


def check(outdir: Path, version: str) -> None:
    """Every shapefile's extent (reprojected to WGS84) must lie inside the Tatras."""
    candidates: list[Path] = [outdir / f"JKTZ-{version}-all.shp"]
    candidates.extend(sorted((outdir / "caves").glob("*.shp")))

    errors: list[str] = []
    for shp in candidates:
        if not shp.is_file():
            continue
        bbox = _wgs84_bbox_of_shapefile(shp)
        if bbox is None:
            # Empty shapefile - reported separately by empty_shapefiles.check.
            continue
        lon_min, lat_min, lon_max, lat_max = bbox
        if lon_min < TATRA_LON_MIN or lon_max > TATRA_LON_MAX:
            errors.append(
                f"    {shp.as_posix()}: lon {lon_min:.6f} .. {lon_max:.6f} "
                f"outside [{TATRA_LON_MIN:.2f}, {TATRA_LON_MAX:.2f}]"
            )
        if lat_min < TATRA_LAT_MIN or lat_max > TATRA_LAT_MAX:
            errors.append(
                f"    {shp.as_posix()}: lat {lat_min:.6f} .. {lat_max:.6f} "
                f"outside [{TATRA_LAT_MIN:.2f}, {TATRA_LAT_MAX:.2f}]"
            )

    if errors:
        raise CheckFailed(
            "\n".join(errors)
            + "\n\nERROR: Shapefiles have features outside the Tatra Mountains extent."
        )
