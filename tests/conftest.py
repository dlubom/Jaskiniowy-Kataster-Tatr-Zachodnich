from __future__ import annotations

import struct
from collections.abc import Callable, Sequence
from pathlib import Path

import numpy as np
import pyogrio.raw
import pytest


def _point_wkb(x: float, y: float) -> bytes:
    # 2D POINT WKB, little-endian: byte_order(1B) + type(4B) + X(8B) + Y(8B).
    return struct.pack("<BIdd", 1, 1, x, y)


@pytest.fixture
def make_point_shapefile() -> Callable[..., None]:
    """Factory fixture that writes a tiny ESRI Shapefile.

    Lets tests build pyogrio-readable shapefiles without geopandas/shapely.
    Usage: ``make_point_shapefile(path, [(x, y), ...], crs="EPSG:32634")``.
    """

    def _make(
        path: Path,
        points: Sequence[tuple[float, float]],
        crs: str = "EPSG:32634",
    ) -> None:
        geometries = np.array([_point_wkb(x, y) for x, y in points], dtype=object)
        pyogrio.raw.write(
            str(path),
            geometry=geometries,
            field_data=[],
            fields=[],
            geometry_type="Point",
            crs=crs,
        )

    return _make
