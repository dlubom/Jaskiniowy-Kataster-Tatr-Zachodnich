"""Immutable source records; units and signed bit patterns remain unchanged."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Union


# Keep raw-value interpretation in ordinary functions: mutmut 3.8 does not
# instrument @property methods. Properties expose these tested transformations.
def _station_kind(raw: int) -> str:
    if raw == -2147483648:
        return "undefined"
    return "plain" if raw < 0 else "major.minor"


def _station_text(raw: int) -> str | None:
    if raw == -2147483648:
        return None
    if raw < 0:
        return str(raw + 2147483647)
    return f"{raw >> 16}.{raw & 65535}"


def _declination_mode(raw: int) -> str:
    return "auto" if raw == -32768 else "explicit"


def _is_flipped(flags: int) -> bool:
    return bool(flags & 1)


@dataclass(frozen=True)
class StationId:
    raw: int

    @property
    def kind(self) -> str:
        return _station_kind(self.raw)

    @property
    def text(self) -> str | None:
        return _station_text(self.raw)


@dataclass(frozen=True)
class Trip:
    ticks: int
    comment: str
    declination_raw: int

    @property
    def declination_mode(self) -> str:
        return _declination_mode(self.declination_raw)


@dataclass(frozen=True)
class Shot:
    from_id: StationId
    to_id: StationId
    distance_mm: int
    azimuth_raw: int
    inclination_raw: int
    flags: int
    roll_raw: int
    trip_index: int
    comment: str | None

    @property
    def flipped(self) -> bool:
        return _is_flipped(self.flags)


@dataclass(frozen=True)
class Reference:
    station: StationId
    east_mm: int
    north_mm: int
    altitude_mm: int
    comment: str


@dataclass(frozen=True)
class Point:
    x: int
    y: int


@dataclass(frozen=True)
class Mapping:
    origin: Point
    scale: int


@dataclass(frozen=True)
class Polygon:
    kind: ClassVar[str] = "polygon"
    points: tuple[Point, ...]
    color: int


@dataclass(frozen=True)
class XSection:
    kind: ClassVar[str] = "xsection"
    position: Point
    station: StationId
    direction: int


Element = Union[Polygon, XSection]


@dataclass(frozen=True)
class Drawing:
    mapping: Mapping
    elements: tuple[Element, ...]


@dataclass(frozen=True)
class TopFile:
    trips: tuple[Trip, ...]
    shots: tuple[Shot, ...]
    references: tuple[Reference, ...]
    overview: Mapping
    outline: Drawing
    sideview: Drawing
    ending: str
