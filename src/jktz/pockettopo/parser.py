"""Strict PocketTopo v3 reader. No export, correction or source-file writes.

The schema is recorded in doc/pockettopo/FORMAT_V3.md. Resource limits are
operational limits, not claims about the binary format or survey validity.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, fields
from pathlib import Path

from jktz.pockettopo.model import (
    Drawing,
    Mapping,
    Point,
    Polygon,
    Reference,
    Shot,
    StationId,
    TopFile,
    Trip,
    XSection,
)


class ParseError(ValueError):
    """Failure at a zero-based byte offset with a stable field context and code."""

    def __init__(self, code: str, offset: int, context: str):
        self.code = code
        self.offset = offset
        self.context = context
        super().__init__(f"{code} at byte {offset} ({context})")


@dataclass(frozen=True)
class ParseLimits:
    """Bound input bytes, individual tables/strings and total drawing objects."""

    max_bytes: int = 64 * 1024 * 1024
    max_records: int = 1_000_000
    max_string_bytes: int = 1024 * 1024
    max_points: int = 2_000_000
    max_elements: int = 100_000

    def __post_init__(self) -> None:
        for field in fields(self):
            value = getattr(self, field.name)
            if type(value) is not int or value < 0:
                raise ValueError(f"{field.name} must be a nonnegative integer")


DEFAULT_LIMITS = ParseLimits()


class _Reader:
    def __init__(self, data: bytes, limits: ParseLimits):
        self.data = data
        self.limits = limits
        self.offset = 0
        self.points_left = limits.max_points
        self.elements_left = limits.max_elements

    def take(self, size: int, context: str) -> bytes:
        end = self.offset + size
        if end > len(self.data):
            raise ParseError("truncated", self.offset, context)
        result = self.data[self.offset : end]
        self.offset = end
        return result

    def number(self, fmt: str, context: str) -> int:
        return struct.unpack("<" + fmt, self.take(struct.calcsize("<" + fmt), context))[0]

    def bounded(self, fmt: str, low: int, high: int, context: str) -> int:
        start = self.offset
        value = self.number(fmt, context)
        if not low <= value <= high:
            raise ParseError("out_of_range", start, context)
        return value

    def count(self, limit: int, minimum_bytes: int, context: str) -> int:
        start = self.offset
        value = self.number("i", context)
        if value < 0:
            raise ParseError("negative_count", start, context)
        if value > limit:
            raise ParseError("resource_limit", start, context)
        if value * minimum_bytes > len(self.data) - self.offset:
            raise ParseError("truncated", start, context)
        return value

    def string_length(self, context: str) -> int:
        start = self.offset
        value = 0
        shift = 0
        while True:
            byte = self.number("B", context)
            # .NET's length is a nonnegative Int32: only 3 payload bits in byte 5.
            if shift == 28 and byte > 7:
                raise ParseError("string_length_overflow", start, context)
            value |= (byte & 127) << shift
            if byte < 128:
                return value
            shift += 7

    def string(self, context: str) -> str:
        start = self.offset
        length = self.string_length(context + ".length")
        if length > self.limits.max_string_bytes:
            raise ParseError("resource_limit", start, context)
        start = self.offset
        raw = self.take(length, context)
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ParseError("invalid_utf8", start + error.start, context) from error

    def station(self, context: str) -> StationId:
        return StationId(self.number("i", context))

    def point(self, context: str) -> Point:
        return Point(self.number("i", context + ".x"), self.number("i", context + ".y"))

    def mapping(self, context: str) -> Mapping:
        return Mapping(
            self.point(context + ".origin"),
            self.bounded("i", 10, 50000, context + ".scale"),
        )

    def trip(self, context: str) -> Trip:
        return Trip(
            self.number("q", context + ".ticks"),
            self.string(context + ".comment"),
            self.number("h", context + ".declination_raw"),
        )

    def shot(self, context: str, trip_count: int) -> Shot:
        from_id = self.station(context + ".from_id")
        to_id = self.station(context + ".to_id")
        distance = self.number("i", context + ".distance_mm")
        azimuth = self.number("h", context + ".azimuth_raw")
        inclination = self.number("h", context + ".inclination_raw")
        start = self.offset
        flags = self.number("B", context + ".flags")
        if flags & ~3:
            raise ParseError("unknown_flags", start, context + ".flags")
        roll = self.number("B", context + ".roll_raw")
        trip_index = self.bounded("h", -1, trip_count - 1, context + ".trip_index")
        comment = self.string(context + ".comment") if flags & 2 else None
        return Shot(
            from_id, to_id, distance, azimuth, inclination, flags, roll, trip_index, comment
        )

    def reference(self, context: str) -> Reference:
        return Reference(
            self.station(context + ".station"),
            self.number("q", context + ".east_mm"),
            self.number("q", context + ".north_mm"),
            self.number("i", context + ".altitude_mm"),
            self.string(context + ".comment"),
        )

    def polygon(self, context: str) -> Polygon:
        count = self.count(self.points_left, 8, context + ".point_count")
        self.points_left -= count
        points = tuple(self.point(f"{context}.points[{index}]") for index in range(count))
        return Polygon(points, self.bounded("B", 1, 7, context + ".color"))

    def xsection(self, context: str) -> XSection:
        return XSection(
            self.point(context + ".position"),
            self.station(context + ".station"),
            self.bounded("i", -1, 2147483647, context + ".direction"),
        )

    def drawing(self, context: str) -> Drawing:
        mapping = self.mapping(context + ".mapping")
        elements = []
        while True:
            field = f"{context}.elements[{len(elements)}]"
            start = self.offset
            kind = self.number("B", field + ".kind")
            if kind == 0:
                return Drawing(mapping, tuple(elements))
            if kind not in (1, 3):
                raise ParseError("unknown_element", start, field + ".kind")
            if self.elements_left == 0:
                raise ParseError("resource_limit", start, field)
            self.elements_left -= 1
            elements.append(self.polygon(field) if kind == 1 else self.xsection(field))

    def ending(self) -> str:
        suffix = self.data[self.offset :]
        if suffix == b"":
            return "eof"
        if suffix == b"\x00\x00\x00\x00":
            return "zero_trailer"
        raise ParseError("invalid_trailer", self.offset, "ending")


def parse_bytes(data: bytes, *, limits: ParseLimits = DEFAULT_LIMITS) -> TopFile:
    """Parse a complete v3 input or raise ParseError; never return partial data."""
    if len(data) > limits.max_bytes:
        raise ParseError("resource_limit", 0, "file")
    reader = _Reader(data, limits)
    if reader.take(3, "header.magic") != b"Top":
        raise ParseError("invalid_magic", 0, "header.magic")
    if reader.number("B", "header.version") != 3:
        raise ParseError("unsupported_version", 3, "header.version")
    trip_count = reader.count(limits.max_records, 11, "trips.count")
    trips = tuple(reader.trip(f"trips[{index}]") for index in range(trip_count))
    shot_count = reader.count(limits.max_records, 20, "shots.count")
    shots = tuple(reader.shot(f"shots[{index}]", trip_count) for index in range(shot_count))
    ref_count = reader.count(limits.max_records, 25, "references.count")
    references = tuple(reader.reference(f"references[{index}]") for index in range(ref_count))
    return TopFile(
        trips,
        shots,
        references,
        reader.mapping("overview"),
        reader.drawing("outline"),
        reader.drawing("sideview"),
        reader.ending(),
    )


def read_top(path: str | Path, *, limits: ParseLimits = DEFAULT_LIMITS) -> TopFile:
    """Read at most the byte budget plus one; propagate filesystem failures."""
    with Path(path).open("rb") as source:
        data = source.read(limits.max_bytes + 1)
    return parse_bytes(data, limits=limits)
