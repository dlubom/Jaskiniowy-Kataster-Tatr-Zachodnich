"""Independent native DXF audit, including every vertex of the Shadow source."""

from __future__ import annotations

import os
import shutil
from decimal import Decimal
from pathlib import Path
from xml.etree import ElementTree

import pytest

from jktz.pockettopo import Polygon, read_top
from jktz.pockettopo.drawings import export_drawings

EVIDENCE = Path(__file__).parent / "fixtures/pockettopo"
ACI = {1: 0, 2: 9, 3: 32, 4: 5, 5: 1, 6: 3, 7: 30}
SOURCES = (
    sorted((EVIDENCE / "p01/cases").glob("*/*.top"))
    + sorted((EVIDENCE / "repeat-candidates").glob("*/*.top"))
    + [EVIDENCE / "shadow/shadow.top"]
    + sorted((EVIDENCE / "p05/native").glob("*/*.top"))
)


def native_path(source: Path, view: str) -> Path:
    suffix = "P" if view == "outline" else "S"
    names = [
        "native-plan.dxf" if view == "outline" else "native-side.dxf",
        f"native{suffix}.dxf",
        f"shadow-native{suffix}.dxf",
    ]
    return next(source.parent / name for name in names if (source.parent / name).exists())


def dxf_entities(path: Path) -> list[tuple[str, dict[int, str]]]:
    lines = path.read_text(encoding="ascii").splitlines()
    assert len(lines) % 2 == 0
    pairs = [(int(lines[i]), lines[i + 1].strip()) for i in range(0, len(lines), 2)]
    assert pairs[-1] == (0, "EOF"), "Native exporter can fail without raising"
    start = pairs.index((2, "ENTITIES")) + 1
    result = []
    current = None
    for code, value in pairs[start:]:
        if code == 0:
            if current is not None:
                result.append(current)
            if value == "ENDSEC":
                break
            current = (value, {})
        else:
            assert current is not None
            assert code not in current[1], "Unexpected repeated group in audited DXF subset"
            current[1][code] = value
    return result


def native_sketch(path: Path) -> list[tuple[int, list[tuple[Decimal, Decimal]]]]:
    polygons = []
    current = None
    for kind, groups in dxf_entities(path):
        if kind == "SEQEND":
            current = None
            continue
        if groups.get(8) != "Sketch":
            continue
        if kind == "POLYLINE":
            assert current is None
            assert int(groups.get(70, "0")) & 1 == 0, "Sketch must remain open"
            current = (int(groups[62]), [])
            polygons.append(current)
        elif kind == "VERTEX":
            assert current is not None
            current[1].append((Decimal(groups[10]), Decimal(groups[20])))
        elif kind == "POINT":
            assert current is None
            polygons.append((int(groups[62]), [(Decimal(groups[10]), Decimal(groups[20]))]))
        elif kind == "LINE":
            # Native XSection connectors share Sketch; they are not source strokes.
            assert groups[6] == "DASH" and groups[62] == "255"
        else:
            raise AssertionError(f"Unexpected native sketch entity: {kind}")
    assert current is None
    return polygons


@pytest.mark.parametrize("source", SOURCES, ids=lambda p: p.parent.name)
@pytest.mark.parametrize("view", ["outline", "sideview"])
def test_every_native_sketch_vertex_color_order_and_open_path(source: Path, view: str) -> None:
    before = source.read_bytes()
    drawing = getattr(read_top(source), view)
    expected = [
        (
            ACI[element.color],
            [(Decimal(p.x) / 500, -Decimal(p.y) / 500) for p in element.points],
        )
        for element in drawing.elements
        if isinstance(element, Polygon)
    ]
    assert native_sketch(native_path(source, view)) == expected
    assert source.read_bytes() == before


def svg_sketch(svg: str) -> list[tuple[int, list[tuple[Decimal, Decimal]]]]:
    root = ElementTree.fromstring(svg)
    namespace = {"svg": "http://www.w3.org/2000/svg"}
    layer = root.find("svg:g[@id='sketch']", namespace)
    assert layer is not None and "transform" not in layer.attrib
    result = []
    indices = []
    for element in layer:
        if "data-element-index" not in element.attrib:
            continue
        indices.append(int(element.attrib["data-element-index"]))
        assert "transform" not in element.attrib
        color = int(element.attrib["data-color-index"])
        if element.tag.endswith("}circle"):
            points = [(Decimal(element.attrib["cx"]), Decimal(element.attrib["cy"]))]
        else:
            assert element.tag.endswith("}polyline")
            points = [
                tuple(map(Decimal, point.split(","))) for point in element.attrib["points"].split()
            ]
        result.append((ACI[color], [(x / 500, -y / 500) for x, y in points]))
    assert indices == sorted(indices)
    return result


@pytest.mark.parametrize("source", SOURCES, ids=lambda p: p.parent.name)
def test_all_four_svg_sketches_match_every_native_dxf_coordinate(source: Path) -> None:
    result = export_drawings(source.read_bytes())
    for view, native_view in (("plan", "outline"), ("side", "sideview")):
        expected = native_sketch(native_path(source, native_view))
        for variant in ("sketch", "measurements"):
            assert svg_sketch(result.svgs[f"{view}-{variant}"]) == expected


@pytest.mark.parametrize("source", SOURCES, ids=lambda p: p.parent.name)
def test_all_saved_png_examples_match_the_pinned_renderer_on_this_platform(source: Path) -> None:
    renderer = os.environ.get("RESVG") or shutil.which("resvg")
    if not renderer:
        if os.environ.get("JKTZ_REQUIRE_RESVG") == "1":
            pytest.fail("resvg is required for cross-platform image comparison")
        pytest.skip("resvg is not installed; required Linux CI executes this comparison")
    result = export_drawings(source.read_bytes(), resvg_path=renderer)
    name = source.parent.name
    if source.parent.parent == EVIDENCE / "p05/native":
        name = "native-" + name
    directory = EVIDENCE / "p05/examples" / name
    for artifact, png in result.pngs.items():
        assert png == (directory / f"{artifact}.png").read_bytes(), artifact
