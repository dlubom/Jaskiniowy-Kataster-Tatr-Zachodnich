"""Coordinate parsing and conversion helpers."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional, Tuple, cast

from pyproj import CRS, Geod, Transformer


@dataclass(frozen=True)
class Epsg2180Point:
    northing: float
    easting: float
    z: Optional[float] = None


@dataclass(frozen=True)
class Wgs84Point:
    lat: float
    lon: float
    z: Optional[float] = None


def parse_float(value: object) -> Optional[float]:
    if value is None:
        return None
    text = str(value).strip().replace(" ", "").replace(",", ".")
    if not text:
        return None
    return float(text)


def format_float(value: Optional[float], digits: int = 8) -> str:
    if value is None:
        return ""
    text = f"{value:.{digits}f}".rstrip("0").rstrip(".")
    return "0" if text == "-0" else text


@lru_cache(maxsize=1)
def _to_wgs84() -> Transformer:
    return Transformer.from_crs(2180, 4326, always_xy=True)


@lru_cache(maxsize=1)
def _to_epsg2180() -> Transformer:
    return Transformer.from_crs(4326, 2180, always_xy=True)


@lru_cache(maxsize=1)
def _geod() -> Geod:
    return Geod(ellps="WGS84")


def epsg2180_to_wgs84(point: Epsg2180Point) -> Wgs84Point:
    lon, lat = _to_wgs84().transform(point.easting, point.northing)
    return Wgs84Point(lat=lat, lon=lon, z=point.z)


def wgs84_to_epsg2180(point: Wgs84Point) -> Epsg2180Point:
    easting, northing = _to_epsg2180().transform(point.lon, point.lat)
    return Epsg2180Point(northing=northing, easting=easting, z=point.z)


def distance_m(first: Wgs84Point, second: Wgs84Point) -> float:
    _az1, _az2, distance = _geod().inv(first.lon, first.lat, second.lon, second.lat)
    return abs(distance)


def epsg2180_prj() -> str:
    return CRS.from_epsg(2180).to_wkt("WKT1_ESRI")


def read_epsg2180(coords: dict[str, object]) -> Optional[Epsg2180Point]:
    epsg_raw = coords.get("epsg2180") if isinstance(coords, dict) else None
    if not isinstance(epsg_raw, Mapping):
        return None
    epsg = cast(Mapping[str, object], epsg_raw)
    northing = parse_float(epsg.get("northing"))
    easting = parse_float(epsg.get("easting"))
    if northing is None or easting is None:
        return None
    return Epsg2180Point(northing=northing, easting=easting, z=parse_float(epsg.get("z")))


def read_wgs84(coords: dict[str, object]) -> Optional[Wgs84Point]:
    wgs84_raw = coords.get("wgs84") if isinstance(coords, dict) else None
    if not isinstance(wgs84_raw, Mapping):
        return None
    wgs84 = cast(Mapping[str, object], wgs84_raw)
    lat = parse_float(wgs84.get("lat"))
    lon = parse_float(wgs84.get("lon"))
    if lat is None or lon is None:
        return None
    return Wgs84Point(lat=lat, lon=lon, z=None)


def ensure_both(
    epsg2180: Optional[Epsg2180Point],
    wgs84: Optional[Wgs84Point],
) -> Tuple[Optional[Epsg2180Point], Optional[Wgs84Point]]:
    if epsg2180 is None and wgs84 is not None:
        epsg2180 = wgs84_to_epsg2180(wgs84)
    if wgs84 is None and epsg2180 is not None:
        wgs84 = epsg2180_to_wgs84(epsg2180)
    return epsg2180, wgs84
