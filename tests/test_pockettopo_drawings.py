"""SVG semantics and pinned raster execution, independent XML/PNG readers."""

from __future__ import annotations

import hashlib
import json
import os
import struct
import subprocess
import zlib
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from jktz.pockettopo.drawing_svg import DrawingSettings, make_svg, validate_settings
from jktz.pockettopo.drawings import (
    DrawingExport,
    RenderingError,
    _png,
    _renderer_version,
    _run,
    _validate_png,
    export_drawings,
)
from jktz.pockettopo.model import Drawing, Mapping, Point, Polygon, StationId, XSection
from jktz.pockettopo.parser import ParseError, ParseLimits, parse_bytes
from jktz.pockettopo.report import ProcessingPlan, RepeatConfirmation

EVIDENCE = Path(__file__).resolve().parents[1] / "doc/pockettopo/evidence"
NS = {"s": "http://www.w3.org/2000/svg"}
VARIANTS = {"plan-sketch", "plan-measurements", "side-sketch", "side-measurements"}


def _native(name):
    return next((EVIDENCE / "p01/cases" / name).glob("*.top")).read_bytes()


def _geometry():
    return {"survey": [], "splays": [], "stations": [], "xsections": []}


def _drawing(points=None):
    if points is None:
        points = (Point(0, 0), Point(1000, -1000))
    return Drawing(Mapping(Point(-123, 456), 500), (Polygon(points, 1),))


def _xml(svg):
    return ET.fromstring(svg)


def _layer(root, layer):
    return root.find(f"s:g[@id='{layer}']", NS)


@pytest.mark.parametrize("name", ["api-cardinal", "api-drawings", "api-references", "gui-colors"])
def test_four_variants_source_semantics_and_determinism(name):
    data = _native(name)
    model = parse_bytes(data)
    result = export_drawings(data)
    assert isinstance(result, DrawingExport)
    assert result.pngs == {}
    assert set(result.svgs) == VARIANTS
    assert result.svgs == export_drawings(data).svgs
    assert result.report["stage"] == "P05"
    assert result.source_document["provenance"] == result.report["provenance"]
    assert result.report["provenance"]["algorithm_version"] == "p05-1"
    assert result.report["completeness"]["conversion_complete"] is False
    assert result.report["completeness"]["atomic_package_created"] is False
    assert result.report["drawings"]["renderer"]["status"] == "not_requested"
    assert not any("Sketches, CLI" in row for row in result.report["limitations"])
    for name, svg in result.svgs.items():
        root = _xml(svg)
        metadata = json.loads(root.find("s:metadata", NS).text)
        assert metadata == result.report["drawings"]["artifacts"][name]
        drawing = model.outline if name.startswith("plan") else model.sideview
        assert metadata["mapping"] == {
            "origin": {"x": drawing.mapping.origin.x, "y": drawing.mapping.origin.y},
            "scale": drawing.mapping.scale,
        }
        assert metadata["mapping_applied_to_geometry"] is False
        assert root.findall(".//s:text", NS) == []
        assert root.findall(".//s:image", NS) == []
        assert root.findall(".//s:use", NS) == []
        assert {group.attrib["id"] for group in root.findall("s:g", NS)} == {
            "sketch",
            "survey",
            "splays",
            "stations",
            "xsections",
        }
        sketch = _layer(root, "sketch")
        rows = [row for row in sketch if "data-element-index" in row.attrib]
        expected = [
            (i, element)
            for i, element in enumerate(drawing.elements)
            if isinstance(element, Polygon)
        ]
        assert [int(row.attrib["data-element-index"]) for row in rows] == [i for i, _ in expected]
        for row, (_, polygon) in zip(rows, expected):
            assert int(row.attrib["data-color-index"]) == polygon.color
            if len(polygon.points) == 1:
                assert row.tag.endswith("circle")
                assert (int(row.attrib["cx"]), int(row.attrib["cy"])) == (
                    polygon.points[0].x,
                    polygon.points[0].y,
                )
                assert float(row.attrib["r"]) > 0
            else:
                assert row.tag.endswith("polyline")
                assert row.attrib["points"] == " ".join(f"{p.x},{p.y}" for p in polygon.points)
        if name.endswith("sketch"):
            assert all(
                len(_layer(root, layer)) == 0
                for layer in ("survey", "splays", "stations", "xsections")
            )


def test_empty_polygon_and_xsection_only_are_visibly_marked_without_invented_outline():
    drawing = Drawing(
        Mapping(Point(1, 2), 500),
        (Polygon((), 7), XSection(Point(100, 200), StationId(-2147483647), -1)),
    )
    svg, metadata = make_svg(drawing, _geometry(), "plan", False, DrawingSettings())
    root = _xml(svg)
    assert root.attrib["data-sketch-status"] == "empty"
    assert metadata["sketch_vertices"] == 0
    assert metadata["xsections"][0]["position"] == {"x": 100, "y": 200}
    assert _layer(root, "sketch").find("s:polyline", NS).attrib["points"] == ""
    assert _layer(root, "sketch").find("s:g", NS).attrib["aria-label"] == "EMPTY SKETCH"


def test_palette_and_overlap_order_are_native_exact():
    root = _xml(export_drawings(_native("gui-colors")).svgs["plan-sketch"])
    palette = ("#000000", "#b0b0b0", "#a52a2a", "#0000ff", "#ff0000", "#00c000", "#ffa500")
    rows = list(_layer(root, "sketch"))
    assert len(rows) == 9
    assert rows[0].attrib["data-color-index"] == "3"
    for row in rows:
        assert row.attrib["fill"] == palette[int(row.attrib["data-color-index"]) - 1]
    overlap = [
        row.attrib["fill"]
        for row in rows
        if row.attrib["cx"] == "6100" and row.attrib["cy"] == "-1400"
    ]
    assert overlap == ["#ffa500", "#00c000"]


def test_overlay_layers_source_trace_labels_and_extents():
    geometry = _geometry()
    leg = {"start": [-100, 200], "end": [300, -400], "source_indices": [2, 3], "group_id": 5}
    geometry["survey"] = [leg]
    geometry["splays"] = [leg]
    geometry["stations"] = [{"position": [300, -400], "label": "0123456789.-", "raw": 0}]
    geometry["xsections"] = [
        {
            "element_index": 2,
            "position": [-9000, 8000],
            "station_raw": 0,
            "direction": -1,
            "status": "projected",
            "connector": {"start": [-9000, 8000], "end": [300, -400]},
            "splays": [leg],
        },
        {
            "element_index": 3,
            "position": [500, 600],
            "station_raw": 7,
            "direction": 16384,
            "status": "unresolved",
            "connector": None,
            "splays": [],
        },
    ]
    svg, metadata = make_svg(_drawing(), geometry, "side", True, DrawingSettings())
    root = _xml(svg)
    for layer in ("survey", "splays"):
        row = _layer(root, layer).find("s:polyline", NS)
        assert row.attrib["points"] == "-100,200 300,-400"
        assert json.loads(row.attrib["data-source-indices"]) == [2, 3]
        assert row.attrib["data-group-id"] == "5"
    assert len(_layer(root, "xsections")) == 2
    assert len(_layer(root, "xsections")[0].findall("s:polyline", NS)) == 2
    label = _layer(root, "stations").find("s:g/s:g", NS)
    assert label.attrib["aria-label"] == "0123456789.-"
    assert label.find("s:path", NS).attrib["d"]
    x, y, width, height = metadata["viewport"]["viewbox_mm"]
    assert x < -9000 and y < -1000 and x + width > 300 and y + height > 8000
    assert metadata["axes"] == "x_right_y_down"


def test_warnings_are_visible_only_on_overlay_and_do_not_move_sketch():
    geometry = _geometry()
    geometry["notices"] = ["disconnected_components_local_origins", "unadjusted_closure"]
    overlay, metadata = make_svg(_drawing(), geometry, "plan", True, DrawingSettings())
    plain, _ = make_svg(_drawing(), geometry, "plan", False, DrawingSettings())
    root = _xml(overlay)
    warning = _layer(root, "stations").find("s:g[@id='overlay-notice']", NS)
    assert "disconnected" in warning.find("s:title", NS).text
    assert warning.find("s:g", NS).attrib["aria-label"] == "CHECK OVERLAY"
    assert metadata["overlay_notices"] == geometry["notices"]
    assert ET.tostring(_layer(root, "sketch")) == ET.tostring(_layer(_xml(plain), "sketch"))
    assert "CHECK OVERLAY" not in plain


@pytest.mark.parametrize(
    "points",
    [
        (Point(-2147483648, -2147483648), Point(2147483647, 2147483647)),
        (Point(0, 0), Point(2147483647, 0)),
        (Point(0, 0), Point(0, 2147483647)),
    ],
)
@pytest.mark.parametrize("budget", [1, 13, 1000, 16_000_000])
def test_raster_budget_extreme_aspect_ratios_preserves_complete_bounds(points, budget):
    settings = DrawingSettings(max_pixels=budget)
    _, metadata = make_svg(_drawing(points), _geometry(), "plan", False, settings)
    viewport = metadata["viewport"]
    assert 1 <= viewport["width_px"] <= 4096
    assert 1 <= viewport["height_px"] <= 4096
    assert viewport["width_px"] * viewport["height_px"] <= budget
    left, top, width, height = viewport["viewbox_mm"]
    assert all(left < point.x < left + width and top < point.y < top + height for point in points)


def test_transparency_settings_immutable_and_scaled_resolution():
    settings = DrawingSettings(background=None)
    with pytest.raises(FrozenInstanceError):
        settings.padding_mm = 1
    plain, metadata = make_svg(_drawing(), _geometry(), "plan", False, settings)
    assert _xml(plain).find("s:rect", NS) is None
    _, double = make_svg(
        _drawing(), _geometry(), "plan", False, replace(settings, pixels_per_metre=80)
    )
    assert double["viewport"]["viewbox_mm"] == metadata["viewport"]["viewbox_mm"]
    assert double["viewport"]["width_px"] >= metadata["viewport"]["width_px"] * 2


@pytest.mark.parametrize(
    "field,value",
    [
        ("pixels_per_metre", True),
        ("pixels_per_metre", "40"),
        ("pixels_per_metre", float("nan")),
        ("padding_mm", 0),
        ("padding_mm", -1),
        ("stroke_width_mm", float("inf")),
        ("label_height_mm", 1e100),
        ("max_dimension", 0),
        ("max_dimension", 16385),
        ("max_dimension", True),
        ("max_pixels", 1.5),
        ("max_pixels", 100_000_001),
        ("background", "red"),
        ("background", "#ffff"),
        ("background", 1),
    ],
)
def test_invalid_render_settings_fail_before_source_or_subprocess(field, value):
    with pytest.raises(ValueError, match=field):
        export_drawings(b"not top", settings=replace(DrawingSettings(), **{field: value}))


@pytest.mark.parametrize("background", [None, "#ffffff", "#01AaF9"])
def test_allowed_backgrounds(background):
    validate_settings(DrawingSettings(background=background))


@pytest.mark.parametrize("timeout", [False, "1", 0, -1, float("nan"), float("inf")])
def test_invalid_renderer_timeout(timeout):
    with pytest.raises(ValueError, match="renderer_timeout"):
        export_drawings(b"", renderer_timeout=timeout)


def test_invalid_source_and_parser_limits_are_not_bypassed():
    with pytest.raises(ParseError, match="truncated"):
        export_drawings(b"Top\x03")
    with pytest.raises(ParseError, match="resource_limit"):
        export_drawings(_native("api-drawings"), limits=ParseLimits(max_bytes=2))


@pytest.mark.parametrize("error", [OSError("unavailable"), subprocess.TimeoutExpired("resvg", 1)])
def test_renderer_execution_failure(monkeypatch, error):
    def fail(*args, **kwargs):
        raise error

    monkeypatch.setattr(subprocess, "run", fail)
    with pytest.raises(RenderingError, match="execution failed"):
        _run(["resvg"], 1)


def test_renderer_nonzero_and_wrong_version(monkeypatch):
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 1, b"", b"broken \xff"),
    )
    with pytest.raises(RenderingError, match="resvg exited 1"):
        _renderer_version("resvg", 1)
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 0, b"0.49.0\n", b""),
    )
    with pytest.raises(RenderingError, match="0.48.1 is required"):
        _renderer_version("resvg", 1)


@pytest.mark.parametrize(
    "output,match",
    [
        (None, "readable PNG"),
        (b"not PNG", "no PNG IHDR"),
        (
            b"\x89PNG\r\n\x1a\n\0\0\0\rIHDR" + struct.pack(">II", 1, 2) + bytes(9),
            "dimensions differ",
        ),
    ],
)
def test_renderer_missing_invalid_or_wrong_sized_output(monkeypatch, output, match):
    def fake(command, **kwargs):
        assert command[1:5] == ["--skip-system-fonts", "--dpi", "96", "--width"]
        assert Path(command[-2]).read_text(encoding="utf-8") == "source SVG"
        if output is not None:
            Path(command[-1]).write_bytes(output)
        return subprocess.CompletedProcess(command, 0, b"", b"")

    monkeypatch.setattr(subprocess, "run", fake)
    with pytest.raises(RenderingError, match=match):
        _png("source SVG", {"viewport": {"width_px": 10, "height_px": 20}}, "resvg", 1)


@pytest.fixture
def resvg():
    path = os.environ.get("RESVG")
    if not path:
        if os.environ.get("JKTZ_REQUIRE_RESVG") == "1":
            pytest.fail("RESVG must point to the pinned renderer in required renderer CI")
        pytest.skip("Set RESVG for the pinned real raster integration checks")
    assert _renderer_version(path, 10) == "0.48.1"
    return path


def test_pinned_renderer_matches_independent_p01_png_byte_for_byte(resvg):
    directory = EVIDENCE / "p01/renderer"
    svg = (directory / "renderer-probe.svg").read_text(encoding="utf-8")
    for width, height, name in (
        (480, 320, "renderer-probe-macos.png"),
        (960, 640, "renderer-probe-2x-macos.png"),
    ):
        png = _png(svg, {"viewport": {"width_px": width, "height_px": height}}, resvg, 10)
        assert png == (directory / name).read_bytes()


@pytest.mark.parametrize("name", ["api-drawings", "api-references", "gui-colors"])
def test_four_real_png_exports_exact_svg_resolution_and_repeatability(resvg, name):
    data = _native(name)
    result = export_drawings(data, resvg_path=resvg)
    assert set(result.pngs) == VARIANTS
    assert result.pngs == export_drawings(data, resvg_path=resvg).pngs
    assert result.report["drawings"]["renderer"]["status"] == "rendered"
    assert result.report["drawings"]["renderer"]["actual_version"] == "0.48.1"
    assert result.report["completeness"]["png_drawings_created"] == 4
    for key, png in result.pngs.items():
        root = _xml(result.svgs[key])
        assert struct.unpack(">II", png[16:24]) == (
            int(root.attrib["width"]),
            int(root.attrib["height"]),
        )
        assert png.endswith(b"\0\0\0\0IEND\xaeB`\x82")


def _rgba(png):
    """Independent standard-library PNG decoder for the pinned renderer's RGBA8."""
    width, height, depth, color, compression, filtering, interlace = struct.unpack(
        ">IIBBBBB", png[16:29]
    )
    assert (depth, color, compression, filtering, interlace) == (8, 6, 0, 0, 0)
    compressed = b""
    offset = 8
    while offset < len(png):
        size = struct.unpack(">I", png[offset : offset + 4])[0]
        kind = png[offset + 4 : offset + 8]
        data = png[offset + 8 : offset + 8 + size]
        crc = struct.unpack(">I", png[offset + 8 + size : offset + 12 + size])[0]
        assert zlib.crc32(kind + data) == crc
        if kind == b"IDAT":
            compressed += data
        offset += size + 12
    packed = zlib.decompress(compressed)
    rows = []
    previous = bytearray(width * 4)
    for y in range(height):
        start = y * (width * 4 + 1)
        kind = packed[start]
        row = bytearray(packed[start + 1 : start + 1 + width * 4])
        for i in range(len(row)):
            left, upper, diagonal = (
                (row[i - 4] if i >= 4 else 0),
                previous[i],
                (previous[i - 4] if i >= 4 else 0),
            )
            prediction = left + upper - diagonal
            paeth = min((left, upper, diagonal), key=lambda candidate: abs(prediction - candidate))
            predictor = (0, left, upper, (left + upper) // 2, paeth)[kind]
            row[i] = (row[i] + predictor) & 255
        rows.append([tuple(row[i : i + 4]) for i in range(0, len(row), 4)])
        previous = row
    return rows


@pytest.mark.parametrize("background", [None, "#ffffff"])
def test_actual_pixels_palette_axes_open_polylines_singletons_layer_order_and_padding(
    resvg, background
):
    elements = []
    expected = [
        (0, 0, 0, 255),
        (176, 176, 176, 255),
        (165, 42, 42, 255),
        (0, 0, 255, 255),
        (255, 0, 0, 255),
        (0, 192, 0, 255),
        (255, 165, 0, 255),
    ]
    for index in range(7):
        elements.extend(
            (
                Polygon((Point(0, index * 1000), Point(1000, index * 1000)), index + 1),
                Polygon((Point(2000, index * 1000),), index + 1),
            )
        )
    elements.extend(
        (
            Polygon((Point(3500, 0), Point(4000, 1000), Point(4500, 0)), 4),
            Polygon((Point(3000, 6000),), 5),
            Polygon((Point(3000, 6000),), 6),
        )
    )
    drawing = Drawing(Mapping(Point(1234, -5678), 123), tuple(elements))
    settings = DrawingSettings(
        pixels_per_metre=100, padding_mm=200, stroke_width_mm=80, background=background
    )
    svg, metadata = make_svg(drawing, _geometry(), "plan", False, settings)
    pixels = _rgba(_png(svg, metadata, resvg, 10))
    left, top, width, height = metadata["viewport"]["viewbox_mm"]
    assert len(pixels) == int(height / 10)
    assert len(pixels[0]) == int(width / 10)

    def at(x, y):
        return pixels[int((y - top) / 10)][int((x - left) / 10)]

    for index, color in enumerate(expected):
        assert at(500, index * 1000) == color
        assert at(2000, index * 1000) == color
    assert at(3000, 6000) == expected[5]
    blank = (0, 0, 0, 0) if background is None else (255, 255, 255, 255)
    assert at(4000, 0) == blank  # The implied closing side must remain absent.
    assert at(2000, 500) == blank
    assert all(pixel == blank for pixel in pixels[0] + pixels[-1])
    assert all(row[0] == blank and row[-1] == blank for row in pixels)


def _chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))


def _minimal_png():
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0))
        + _chunk(b"IDAT", zlib.compress(bytes(5)))
        + _chunk(b"IEND", b"")
    )


def test_complete_png_required_and_every_truncation_rejected():
    png = _minimal_png()
    _validate_png(png, 1, 1)
    for index in range(len(png)):
        with pytest.raises(RenderingError):
            _validate_png(png[:index], 1, 1)


@pytest.mark.parametrize(
    "suffix,match",
    [
        (_chunk(b"IEND", b""), "premature IEND"),
        (_chunk(b"IDAT", b"") + _chunk(b"IEND", b""), "premature IEND"),
        (_chunk(b"IDAT", b"pixels"), "missing IEND"),
        (_chunk(b"IDAT", b"pixels") + _chunk(b"IEND", b"x"), "invalid or premature IEND"),
        (_chunk(b"IDAT", b"pixels") + _chunk(b"IEND", b"") + b"x", "invalid or premature IEND"),
        (
            _chunk(b"IDAT", b"pixels") + _chunk(b"tEXt", b"label") + _chunk(b"IDAT", b"pixels"),
            "noncontiguous",
        ),
        (_chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)), "duplicate IHDR"),
    ],
)
def test_png_invalid_structure_rejected(suffix, match):
    with pytest.raises(RenderingError, match=match):
        _validate_png(_minimal_png()[:33] + suffix, 1, 1)


def test_png_crc_and_rgba_contract_and_ancillary_chunks():
    png = _minimal_png()
    damaged = bytearray(png)
    damaged[-1] ^= 1
    with pytest.raises(RenderingError, match="CRC mismatch"):
        _validate_png(bytes(damaged), 1, 1)
    damaged = bytearray(png)
    damaged[25] = 2
    with pytest.raises(RenderingError, match="RGBA8"):
        _validate_png(bytes(damaged), 1, 1)
    _validate_png(png[:33] + _chunk(b"tEXt", b"comment") + png[33:], 1, 1)


@pytest.mark.parametrize(
    "compressed,match",
    [
        (b"pixels", "not valid zlib"),
        (zlib.compress(b""), "scanline length"),
        (zlib.compress(bytes((255, 0, 0, 0, 0))), "invalid scanline filter"),
        (zlib.compress(bytes(6)), "scanline length"),
        (zlib.compress(bytes(5))[:-1], "truncated or has trailing"),
        (zlib.compress(bytes(5)) + b"trailing", "truncated or has trailing"),
        (zlib.compress(bytes(5)) + zlib.compress(bytes(5)), "truncated or has trailing"),
        (zlib.compress(bytes(1_000_000)), "scanline length"),
    ],
)
def test_png_image_data_must_decode_to_exact_filtered_scanlines(compressed, match):
    png = _minimal_png()[:33] + _chunk(b"IDAT", compressed) + _chunk(b"IEND", b"")
    with pytest.raises(RenderingError, match=match):
        _validate_png(png, 1, 1)


def test_png_decompression_size_is_bounded_before_allocating_malicious_image(monkeypatch):
    original = zlib.decompressobj
    maximums = []

    class Decoder:
        def __init__(self):
            self.decoder = original()

        def decompress(self, data, maximum):
            maximums.append(maximum)
            return self.decoder.decompress(data, maximum)

    monkeypatch.setattr(zlib, "decompressobj", Decoder)
    png = (
        _minimal_png()[:33]
        + _chunk(b"IDAT", zlib.compress(bytes(10_000_000)))
        + _chunk(b"IEND", b"")
    )
    with pytest.raises(RenderingError, match="scanline length"):
        _validate_png(png, 1, 1)
    assert maximums == [6]


def test_png_all_standard_scanline_filters_and_split_idat_are_accepted():
    header = b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 5, 8, 6, 0, 0, 0))
    compressed = zlib.compress(b"".join(bytes((i, 1, 2, 3, 4)) for i in range(5)))
    png = (
        header
        + _chunk(b"IDAT", compressed[:3])
        + _chunk(b"IDAT", compressed[3:])
        + _chunk(b"IEND", b"")
    )
    _validate_png(png, 1, 5)


def test_svg_bounds_include_full_xsection_paint_for_minimal_padding():
    geometry = _geometry()
    geometry["xsections"] = [
        {
            "element_index": 0,
            "position": [0, 0],
            "station_raw": 0,
            "direction": -1,
            "status": "projected",
            "connector": None,
            "splays": [],
        }
    ]
    settings = DrawingSettings(padding_mm=1, stroke_width_mm=30)
    _, metadata = make_svg(_drawing((Point(0, 0),)), geometry, "plan", True, settings)
    left, top, width, height = metadata["viewport"]["viewbox_mm"]
    assert left <= -76 and top <= -76 and left + width >= 76 and top + height >= 76


def test_minimal_padding_xsection_png_has_uncropped_white_perimeter(resvg):
    geometry = _geometry()
    geometry["xsections"] = [
        {
            "element_index": 0,
            "position": [0, 0],
            "station_raw": 0,
            "direction": -1,
            "status": "projected",
            "connector": None,
            "splays": [],
        }
    ]
    settings = DrawingSettings(padding_mm=1, stroke_width_mm=30, pixels_per_metre=1000)
    svg, metadata = make_svg(_drawing((Point(0, 0),)), geometry, "plan", True, settings)
    pixels = _rgba(_png(svg, metadata, resvg, 10))
    white = (255, 255, 255, 255)
    assert all(pixel == white for pixel in pixels[0] + pixels[-1])
    assert all(row[0] == white and row[-1] == white for row in pixels)
    assert any(pixel != white for row in pixels for pixel in row)


def test_missing_xsection_station_has_visible_notice_even_without_held_shots():
    mapping = struct.pack("<iii", 0, 0, 500)
    section = b"\3" + struct.pack("<iiii", 100, 200, -2147483647, -1)
    data = b"Top\x03" + bytes(12) + mapping + mapping + section + b"\0" + mapping + b"\0"
    result = export_drawings(data)
    assert result.report["completeness"]["held_shots"] == 0
    assert (
        "station_not_in_active_overlay"
        in result.report["drawings"]["artifacts"]["plan-measurements"]["overlay_notices"]
    )
    assert "CHECK OVERLAY" in result.svgs["plan-measurements"]


def test_confirmed_mixed_flip_series_has_visible_review_notice():
    mapping = struct.pack("<iii", 0, 0, 500)

    def shot(flip):
        return struct.pack("<iiihhBBh", -2147483647, -2147483646, 1000, 0, 0, flip, 0, 0)

    data = (
        b"Top\x03"
        + struct.pack("<i", 1)
        + struct.pack("<qBh", 632401344000000000, 0, 0)
        + struct.pack("<i", 2)
        + shot(0)
        + shot(1)
        + bytes(4)
        + mapping
        + mapping
        + b"\0"
        + mapping
        + b"\0"
    )
    plan = ProcessingPlan(
        hashlib.sha256(data).hexdigest(),
        (RepeatConfirmation((0, 1), "independently confirmed test repeat"),),
    )
    result = export_drawings(data, plan=plan)
    assert (
        "mixed_flip_preserved_for_drawing_review"
        in result.report["drawings"]["artifacts"]["side-measurements"]["overlay_notices"]
    )
    assert "CHECK OVERLAY" in result.svgs["side-measurements"]
