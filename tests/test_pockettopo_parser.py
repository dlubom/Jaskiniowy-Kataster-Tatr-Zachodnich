"""Adversarial and boundary cases; native P01 oracles are tested separately."""

from __future__ import annotations

import io
import struct
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from jktz.pockettopo import (
    ParseError,
    ParseLimits,
    Polygon,
    StationId,
    XSection,
    parse_bytes,
    read_top,
)


def _int(fmt: str, *values: int) -> bytes:
    return struct.pack("<" + fmt, *values)


def _string(value: str) -> bytes:
    raw = value.encode("utf-8")
    length = len(raw)
    prefix = bytearray()
    while length >= 128:
        prefix.append((length & 127) | 128)
        length >>= 7
    prefix.append(length)
    return bytes(prefix) + raw


def _mapping(x: int = 0, y: int = 0, scale: int = 500) -> bytes:
    return _int("iii", x, y, scale)


def _trip(ticks: int = 0, comment: str = "", declination: int = 0) -> bytes:
    return _int("q", ticks) + _string(comment) + _int("h", declination)


def _shot(
    from_id: int = -2147483647,
    to_id: int = -2147483648,
    distance: int = 0,
    azimuth: int = 0,
    inclination: int = 0,
    flags: int = 0,
    roll: int = 0,
    trip: int = -1,
    comment: str = "",
) -> bytes:
    body = _int("iiihhBBh", from_id, to_id, distance, azimuth, inclination, flags, roll, trip)
    return body + (_string(comment) if flags & 2 else b"")


def _reference(
    station: int = -2147483647, east: int = 0, north: int = 0, altitude: int = 0, comment: str = ""
) -> bytes:
    return _int("iqqi", station, east, north, altitude) + _string(comment)


def _polygon(points: tuple[tuple[int, int], ...] = (), color: int = 1) -> bytes:
    return (
        b"\x01" + _int("i", len(points)) + b"".join(_int("ii", *p) for p in points) + bytes([color])
    )


def _xsection(direction: int = -1) -> bytes:
    return b"\x03" + _int("iiii", -1, 2, -2147483648, direction)


def _file(
    trips: tuple[bytes, ...] = (),
    shots: tuple[bytes, ...] = (),
    references: tuple[bytes, ...] = (),
    overview: bytes | None = None,
    outline: bytes = b"",
    sideview: bytes = b"",
    trailer: bytes = b"",
) -> bytes:
    tables = b"".join(
        _int("i", len(table)) + b"".join(table) for table in (trips, shots, references)
    )
    return (
        b"Top\x03"
        + tables
        + (_mapping() if overview is None else overview)
        + _mapping()
        + outline
        + b"\x00"
        + _mapping()
        + sideview
        + b"\x00"
        + trailer
    )


def _error(data: bytes, code: str, offset: int, context: str, **kwargs) -> None:
    with pytest.raises(ParseError) as caught:
        parse_bytes(data, **kwargs)
    error = caught.value
    assert isinstance(error, ValueError)
    assert (error.code, error.offset, error.context) == (code, offset, context)
    assert str(error) == f"{code} at byte {offset} ({context})"


def test_empty_file_and_immutable_model() -> None:
    parsed = parse_bytes(_file())
    assert parsed.trips == parsed.shots == parsed.references == ()
    assert parsed.outline.elements == parsed.sideview.elements == ()
    assert parsed.overview.origin.x == parsed.overview.origin.y == 0
    assert parsed.overview.scale == 500
    assert parsed.ending == "eof"
    with pytest.raises(FrozenInstanceError):
        parsed.ending = "changed"
    with pytest.raises(FrozenInstanceError):
        parsed.overview.origin.x = 1


@pytest.mark.parametrize(
    ("raw", "kind", "text"),
    [
        (-2147483648, "undefined", None),
        (-2147483647, "plain", "0"),
        (-2147483646, "plain", "1"),
        (-1, "plain", "2147483646"),
        (0, "major.minor", "0.0"),
        (1, "major.minor", "0.1"),
        (65535, "major.minor", "0.65535"),
        (65536, "major.minor", "1.0"),
        (2147483647, "major.minor", "32767.65535"),
    ],
)
def test_station_id_preserves_kind_and_full_integer_range(raw: int, kind: str, text: str) -> None:
    station = parse_bytes(_file(shots=(_shot(from_id=raw, to_id=raw),))).shots[0].from_id
    assert station == StationId(raw)
    assert (station.raw, station.kind, station.text) == (raw, kind, text)
    with pytest.raises(FrozenInstanceError):
        station.raw = 0


@pytest.mark.parametrize(
    "ticks", [-9223372036854775808, -1, 0, 639259776000000009, 9223372036854775807]
)
@pytest.mark.parametrize("declination", [-32768, -32767, -1, 0, 1, 32767])
def test_ticks_and_declination_remain_signed_integers(ticks: int, declination: int) -> None:
    trip = parse_bytes(_file(trips=(_trip(ticks, "", declination),))).trips[0]
    assert trip.ticks == ticks
    assert type(trip.ticks) is int
    assert trip.comment == ""
    assert trip.declination_raw == declination
    assert trip.declination_mode == ("auto" if declination == -32768 else "explicit")


@pytest.mark.parametrize("value", [-2147483648, -1, 0, 2147483647])
@pytest.mark.parametrize("angle", [-32768, -16384, -1, 0, 16384, 32767])
def test_raw_distance_angles_and_coordinates_are_not_normalized(value: int, angle: int) -> None:
    parsed = parse_bytes(
        _file(
            shots=(_shot(distance=value, azimuth=angle, inclination=angle, roll=255),),
            overview=_mapping(value, -1),
            outline=_polygon(((value, value),)),
        )
    )
    shot = parsed.shots[0]
    assert (shot.distance_mm, shot.azimuth_raw, shot.inclination_raw, shot.roll_raw) == (
        value,
        angle,
        angle,
        255,
    )
    assert (parsed.overview.origin.x, parsed.overview.origin.y) == (value, -1)
    point = parsed.outline.elements[0].points[0]
    assert (point.x, point.y) == (value, value)


@pytest.mark.parametrize("east", [-9223372036854775808, 0, 9223372036854775807])
@pytest.mark.parametrize("altitude", [-2147483648, 0, 2147483647])
def test_reference_keeps_signed_int64_and_no_crs(east: int, altitude: int) -> None:
    ref = parse_bytes(
        _file(references=(_reference(0, east, east, altitude, "x\x00ą"),))
    ).references[0]
    assert ref.station.raw == 0
    assert (ref.east_mm, ref.north_mm, ref.altitude_mm, ref.comment) == (
        east,
        east,
        altitude,
        "x\x00ą",
    )


@pytest.mark.parametrize("flags", [0, 1, 2, 3])
@pytest.mark.parametrize("trip", [-1, 0, 1])
def test_flags_comments_and_trip_index_are_preserved(flags: int, trip: int) -> None:
    parsed = parse_bytes(_file(trips=(_trip(1), _trip(2)), shots=(_shot(flags=flags, trip=trip),)))
    shot = parsed.shots[0]
    assert shot.trip_index == trip
    assert shot.flags == flags
    assert shot.flipped is bool(flags & 1)
    assert shot.comment == ("" if flags & 2 else None)
    assert shot.roll_raw == 0


@pytest.mark.parametrize("flags", [4, 8, 16, 32, 64, 128, 255])
def test_unknown_shot_flag_bits_are_rejected(flags: int) -> None:
    _error(_file(shots=(_shot(flags=flags),)), "unknown_flags", 28, "shots[0].flags")


@pytest.mark.parametrize(
    ("trips", "trip"), [((), 0), ((), -2), ((_trip(),), 1), ((_trip(),), 32767)]
)
def test_trip_index_must_reference_an_existing_trip_or_minus_one(trips: tuple, trip: int) -> None:
    _error(
        _file(trips=trips, shots=(_shot(trip=trip),)),
        "out_of_range",
        30 + sum(map(len, trips)),
        "shots[0].trip_index",
    )


@pytest.mark.parametrize("scale", [10, 50000])
def test_mapping_scale_boundaries(scale: int) -> None:
    assert parse_bytes(_file(overview=_mapping(scale=scale))).overview.scale == scale


@pytest.mark.parametrize("scale", [-2147483648, 9, 50001, 2147483647])
def test_mapping_scale_out_of_range(scale: int) -> None:
    _error(_file(overview=_mapping(scale=scale)), "out_of_range", 24, "overview.scale")


@pytest.mark.parametrize("color", [1, 2, 3, 4, 5, 6, 7])
def test_polygons_preserve_empty_singleton_open_paths_and_order(color: int) -> None:
    points = ((1, 2), (3, 4), (5, 6))
    parsed = parse_bytes(
        _file(outline=_polygon((), color) + _polygon(((7, 8),), color) + _polygon(points, color))
    )
    elements = parsed.outline.elements
    assert all(
        isinstance(p, Polygon) and p.kind == "polygon" and p.color == color for p in elements
    )
    assert [tuple((p.x, p.y) for p in element.points) for element in elements] == [
        (),
        ((7, 8),),
        points,
    ]


@pytest.mark.parametrize("color", [0, 8, 255])
def test_unknown_polygon_color_is_rejected(color: int) -> None:
    _error(_file(outline=_polygon(color=color)), "out_of_range", 45, "outline.elements[0].color")


@pytest.mark.parametrize("direction", [-1, 0, 65535, 65536, 2147483647])
def test_xsection_preserves_position_station_and_uninterpreted_direction(direction: int) -> None:
    element = parse_bytes(_file(sideview=_xsection(direction))).sideview.elements[0]
    assert isinstance(element, XSection)
    assert element.kind == "xsection"
    assert (element.position.x, element.position.y, element.station.raw, element.direction) == (
        -1,
        2,
        -2147483648,
        direction,
    )


@pytest.mark.parametrize("direction", [-2, -2147483648])
def test_invalid_negative_xsection_direction(direction: int) -> None:
    _error(_file(outline=_xsection(direction)), "out_of_range", 53, "outline.elements[0].direction")


@pytest.mark.parametrize("kind", [2, 4, 127, 255])
def test_unknown_drawing_element_is_never_skipped(kind: int) -> None:
    _error(_file(outline=bytes([kind])), "unknown_element", 40, "outline.elements[0].kind")


@pytest.mark.parametrize("text", ["", "x" * 127, "ą" * 64, "x" * 16383, "ą" * 8192, "x" * 2097152])
def test_string_length_counts_utf8_bytes_across_varint_boundaries(text: str) -> None:
    parsed = parse_bytes(
        _file(trips=(_trip(comment=text),)), limits=ParseLimits(max_string_bytes=len(text.encode()))
    )
    assert parsed.trips[0].comment == text


@pytest.mark.parametrize("prefix", [b"\x80\x80\x80\x80\x00", b"\x80\x00"])
def test_nonminimal_varint_is_legal_and_consumed_in_full(prefix: bytes) -> None:
    trip = _int("q", 7) + prefix + _int("h", -1)
    parsed = parse_bytes(_file(trips=(trip,)))
    assert (parsed.trips[0].ticks, parsed.trips[0].comment, parsed.trips[0].declination_raw) == (
        7,
        "",
        -1,
    )


@pytest.mark.parametrize("last", [8, 15, 127, 128, 255])
def test_overflowing_string_length_is_rejected_before_payload(last: int) -> None:
    trip = _int("q", 0) + b"\xff\xff\xff\xff" + bytes([last]) + _int("h", 0)
    _error(_file(trips=(trip,)), "string_length_overflow", 16, "trips[0].comment.length")


def test_largest_int32_string_length_is_valid_varint_but_exceeds_resource_limit() -> None:
    trip = _int("q", 0) + b"\xff\xff\xff\xff\x07" + _int("h", 0)
    _error(_file(trips=(trip,)), "resource_limit", 16, "trips[0].comment")


@pytest.mark.parametrize(
    "raw", [b"\xff", b"\xc0\xaf", b"\xed\xa0\x80", b"\xf4\x90\x80\x80", b"a\xc2"]
)
def test_invalid_utf8_is_not_replaced(raw: bytes) -> None:
    trip = _int("q", 0) + bytes([len(raw)]) + raw + _int("h", 0)
    _error(
        _file(trips=(trip,)),
        "invalid_utf8",
        17 + (1 if raw.startswith(b"a") else 0),
        "trips[0].comment",
    )


def test_truncated_string_payload_and_varint_report_field_offset() -> None:
    # Padding satisfies the fixed lower bound of Trip before entering the string.
    _error(
        b"Top\x03" + _int("i", 1) + _int("q", 0) + b"\x80\x80\x80",
        "truncated",
        19,
        "trips[0].comment.length",
    )
    _error(
        b"Top\x03" + _int("i", 1) + _int("q", 0) + b"\x03ab", "truncated", 17, "trips[0].comment"
    )


@pytest.mark.parametrize(
    ("data", "code", "offset", "context"),
    [
        (b"", "truncated", 0, "header.magic"),
        (b"Top", "truncated", 3, "header.version"),
        (b"TOP\x03", "invalid_magic", 0, "header.magic"),
        (b"Top\x00", "unsupported_version", 3, "header.version"),
        (b"Top\x04", "unsupported_version", 3, "header.version"),
        (b"Top\x03", "truncated", 4, "trips.count"),
    ],
)
def test_header_failures(data: bytes, code: str, offset: int, context: str) -> None:
    _error(data, code, offset, context)


@pytest.mark.parametrize(
    ("offset", "context"),
    [
        (4, "trips.count"),
        (8, "shots.count"),
        (12, "references.count"),
        (41, "outline.elements[0].point_count"),
    ],
)
def test_negative_counts_are_rejected(offset: int, context: str) -> None:
    data = _file(outline=_polygon())
    data = data[:offset] + _int("i", -1) + data[offset + 4 :]
    _error(data, "negative_count", offset, context)


@pytest.mark.parametrize(
    ("offset", "context"),
    [
        (4, "trips.count"),
        (8, "shots.count"),
        (12, "references.count"),
        (41, "outline.elements[0].point_count"),
    ],
)
def test_count_cannot_exceed_remaining_bytes(offset: int, context: str) -> None:
    data = _file(outline=_polygon())
    data = data[:offset] + _int("i", 100) + data[offset + 4 :]
    _error(data, "truncated", offset, context)


@pytest.mark.parametrize(("trailer", "ending"), [(b"", "eof"), (b"\x00" * 4, "zero_trailer")])
def test_exact_accepted_endings(trailer: bytes, ending: str) -> None:
    assert parse_bytes(_file(trailer=trailer)).ending == ending


@pytest.mark.parametrize(
    "trailer", [b"\x00", b"\x00\x00", b"\x00" * 3, b"\x00" * 5, b"\x00\x00\x00\x01", b"other"]
)
def test_all_other_trailers_are_rejected(trailer: bytes) -> None:
    _error(_file(trailer=trailer), "invalid_trailer", 54, "ending")


def test_missing_drawing_terminator_is_not_accepted_as_eof() -> None:
    _error(_file()[:-1], "truncated", 53, "sideview.elements[0].kind")


def test_default_limits_are_explicit_operational_budgets() -> None:
    limits = ParseLimits()
    assert (
        limits.max_bytes,
        limits.max_records,
        limits.max_string_bytes,
        limits.max_points,
        limits.max_elements,
    ) == (67108864, 1000000, 1048576, 2000000, 100000)


@pytest.mark.parametrize(
    "field", ["max_bytes", "max_records", "max_string_bytes", "max_points", "max_elements"]
)
@pytest.mark.parametrize("invalid", [-1, 1.5, True, None])
def test_limits_require_nonnegative_integers(field: str, invalid) -> None:
    with pytest.raises(ValueError, match=f"^{field} must be a nonnegative integer$"):
        ParseLimits(**{field: invalid})


def test_resource_budgets_include_boundary_and_reject_next_record() -> None:
    data = _file(trips=(_trip(),), shots=(_shot(),), references=(_reference(),))
    assert len(parse_bytes(data, limits=ParseLimits(max_records=1)).shots) == 1
    _error(data, "resource_limit", 4, "trips.count", limits=ParseLimits(max_records=0))
    _error(
        _file(shots=(_shot(),)),
        "resource_limit",
        8,
        "shots.count",
        limits=ParseLimits(max_records=0),
    )
    _error(
        _file(references=(_reference(),)),
        "resource_limit",
        12,
        "references.count",
        limits=ParseLimits(max_records=0),
    )


def test_file_size_limit_is_inclusive() -> None:
    data = _file()
    assert parse_bytes(data, limits=ParseLimits(max_bytes=len(data))).ending == "eof"
    _error(data, "resource_limit", 0, "file", limits=ParseLimits(max_bytes=len(data) - 1))


def test_string_limit_is_measured_in_bytes() -> None:
    data = _file(trips=(_trip(comment="ą"),))
    assert parse_bytes(data, limits=ParseLimits(max_string_bytes=2)).trips[0].comment == "ą"
    _error(data, "resource_limit", 16, "trips[0].comment", limits=ParseLimits(max_string_bytes=1))


def test_total_points_budget_spans_polygons_and_both_drawings() -> None:
    data = _file(outline=_polygon(((1, 2),)), sideview=_polygon(((3, 4),)))
    assert len(parse_bytes(data, limits=ParseLimits(max_points=2)).sideview.elements[0].points) == 1
    _error(
        data,
        "resource_limit",
        68,
        "sideview.elements[0].point_count",
        limits=ParseLimits(max_points=1),
    )
    _error(
        data,
        "resource_limit",
        41,
        "outline.elements[0].point_count",
        limits=ParseLimits(max_points=0),
    )


def test_total_elements_budget_spans_both_drawings_and_accepts_terminator() -> None:
    data = _file(outline=_polygon() + _xsection(), sideview=_polygon())
    assert len(parse_bytes(data, limits=ParseLimits(max_elements=3)).sideview.elements) == 1
    _error(data, "resource_limit", 46, "outline.elements[1]", limits=ParseLimits(max_elements=1))
    _error(data, "resource_limit", 76, "sideview.elements[0]", limits=ParseLimits(max_elements=2))
    empty_limits = replace(
        ParseLimits(), max_elements=0, max_points=0, max_records=0, max_string_bytes=0
    )
    assert parse_bytes(_file(), limits=empty_limits).outline.elements == ()


def test_read_top_never_writes_input_and_honors_byte_limit(tmp_path: Path) -> None:
    path = tmp_path / "source.top"
    original = _file(trailer=b"\x00" * 4)
    path.write_bytes(original)
    assert read_top(str(path)).ending == "zero_trailer"
    with pytest.raises(ParseError) as caught:
        read_top(path, limits=ParseLimits(max_bytes=54))
    assert (caught.value.code, caught.value.offset, caught.value.context) == (
        "resource_limit",
        0,
        "file",
    )
    assert path.read_bytes() == original
    assert list(tmp_path.iterdir()) == [path]
    with pytest.raises(FileNotFoundError):
        read_top(tmp_path / "missing.top")


@pytest.mark.parametrize("table", ["shots", "references"])
def test_dense_minimum_size_tables_accept_every_record(table: str) -> None:
    record = _shot() if table == "shots" else _reference()
    parsed = parse_bytes(_file(**{table: (record,) * 50}))
    records = getattr(parsed, table)
    assert len(records) == 50
    assert all(record == records[0] for record in records)
    assert parsed.outline.elements == parsed.sideview.elements == ()
    assert parsed.ending == "eof"


def test_read_top_bounds_io_before_parsing(monkeypatch: pytest.MonkeyPatch) -> None:
    read_sizes = []

    class ObservedSource(io.BytesIO):
        def read(self, size: int = -1) -> bytes:
            read_sizes.append(size)
            return super().read(size)

    source = ObservedSource(_file(trailer=b"\x00" * 100))
    monkeypatch.setattr(Path, "open", lambda self, mode: source)
    with pytest.raises(ParseError) as caught:
        read_top(Path("source.top"), limits=ParseLimits(max_bytes=54))
    assert read_sizes == [55]
    assert source.closed
    assert (caught.value.code, caught.value.offset, caught.value.context) == (
        "resource_limit",
        0,
        "file",
    )
