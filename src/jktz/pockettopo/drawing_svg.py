"""Deterministic SVG drawing in source millimetres, with a tiny path-only font."""

from __future__ import annotations

import json
import math
import re
from dataclasses import asdict, dataclass
from xml.etree.ElementTree import Element, SubElement, tostring

from jktz.pockettopo.model import Drawing, Polygon, XSection

# PocketTopo 1.372 MainForm pens, independently recorded by the P05 native probe.
PALETTE = ("#000000", "#b0b0b0", "#a52a2a", "#0000ff", "#ff0000", "#00c000", "#ffa500")
SVG_NS = "http://www.w3.org/2000/svg"
INKSCAPE_NS = "http://www.inkscape.org/namespaces/inkscape"
FONT = {
    "0": "111/101/101/101/111",
    "1": "010/110/010/010/111",
    "2": "111/001/111/100/111",
    "3": "111/001/111/001/111",
    "4": "101/101/111/001/001",
    "5": "111/100/111/001/111",
    "6": "111/100/111/101/111",
    "7": "111/001/010/010/010",
    "8": "111/101/111/101/111",
    "9": "111/101/111/001/111",
    ".": "000/000/000/000/010",
    "-": "000/000/111/000/000",
    "E": "111/100/110/100/111",
    "M": "101/111/111/101/101",
    "P": "111/101/111/100/100",
    "T": "111/010/010/010/010",
    "Y": "101/101/010/010/010",
    "S": "111/100/111/001/111",
    "K": "101/101/110/101/101",
    "C": "111/100/100/100/111",
    "H": "101/101/111/101/101",
    "O": "111/101/101/101/111",
    "V": "101/101/101/101/010",
    "R": "111/101/110/101/101",
    "L": "100/100/100/100/111",
    "A": "010/101/111/101/101",
    " ": "000/000/000/000/000",
}


@dataclass(frozen=True)
class DrawingSettings:
    pixels_per_metre: float = 40.0
    padding_mm: float = 250.0
    stroke_width_mm: float = 30.0
    label_height_mm: float = 200.0
    background: str | None = "#ffffff"
    max_dimension: int = 4096
    max_pixels: int = 16_000_000


def validate_settings(settings: DrawingSettings) -> None:
    for key in ("pixels_per_metre", "padding_mm", "stroke_width_mm", "label_height_mm"):
        value = getattr(settings, key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{key} must be a finite positive number")
        if not math.isfinite(value) or not 0 < value <= 1_000_000_000:
            raise ValueError(f"{key} must be positive and at most 1000000000")
    for key, maximum in (("max_dimension", 16384), ("max_pixels", 100_000_000)):
        value = getattr(settings, key)
        if type(value) is not int or not 1 <= value <= maximum:
            raise ValueError(f"{key} must be a positive integer at most {maximum}")
    if settings.background is not None and (
        not isinstance(settings.background, str)
        or not re.fullmatch(r"#[0-9a-fA-F]{6}", settings.background)
    ):
        raise ValueError("background must be #RRGGBB or None")


def _number(value: float) -> str:
    result = f"{value:.9f}".rstrip("0").rstrip(".")
    return "0" if result in ("", "-0") else result


def _point(point) -> str:
    return ",".join(_number(value) for value in point)


def _glyphs(parent: Element, label: str, position, height: float, color: str) -> None:
    """Labels are geometry: no installed fonts, font discovery or external resources."""
    unit = height / 5
    group = SubElement(parent, "g", {"aria-label": label, "data-font": "jktz-grid-3x5-v1"})
    SubElement(group, "title").text = label
    commands = []
    for offset, character in enumerate(label):
        for row, pattern in enumerate(FONT[character].split("/")):
            for column, filled in enumerate(pattern):
                if filled == "1":
                    x = position[0] + (offset * 4 + column) * unit
                    y = position[1] + row * unit
                    commands.append(
                        f"M{_point((x, y))}h{_number(unit)}v{_number(unit)}h-{_number(unit)}z"
                    )
    SubElement(group, "path", {"d": " ".join(commands), "fill": color, "stroke": "none"})


def _line(parent: Element, row: dict, **extra: str) -> None:
    attributes = {"points": _point(row["start"]) + " " + _point(row["end"]), **extra}
    if "source_indices" in row:
        attributes["data-source-indices"] = json.dumps(row["source_indices"], separators=(",", ":"))
        attributes["data-group-id"] = str(row["group_id"])
    SubElement(parent, "polyline", attributes)


def _source_sketch(parent: Element, drawing: Drawing, width: float) -> int:
    count = 0
    for index, element in enumerate(drawing.elements):
        if not isinstance(element, Polygon):
            continue
        attributes = {"data-element-index": str(index), "data-color-index": str(element.color)}
        color = PALETTE[element.color - 1]
        if len(element.points) == 1:
            point = element.points[0]
            SubElement(
                parent,
                "circle",
                {
                    **attributes,
                    "cx": str(point.x),
                    "cy": str(point.y),
                    "r": _number(width / 2),
                    "fill": color,
                    "stroke": "none",
                },
            )
        else:
            SubElement(
                parent,
                "polyline",
                {
                    **attributes,
                    "points": " ".join(f"{point.x},{point.y}" for point in element.points),
                    "stroke": color,
                },
            )
        count += len(element.points)
    return count


def _xsections(parent: Element, rows: list[dict], width: float) -> None:
    for row in rows:
        group = SubElement(
            parent,
            "g",
            {
                "data-element-index": str(row["element_index"]),
                "data-station-raw": str(row["station_raw"]),
                "data-direction": str(row["direction"]),
                "data-status": row["status"],
            },
        )
        x, y = row["position"]
        SubElement(group, "circle", {"cx": _number(x), "cy": _number(y), "r": _number(width * 2)})
        if row["connector"] is not None:
            _line(
                group,
                row["connector"],
                **{"stroke-dasharray": f"{_number(width * 3)} {_number(width * 2)}"},
            )
        for splay in row["splays"]:
            _line(group, splay)


def _overlay_points(geometry: dict, settings: DrawingSettings) -> list[tuple[float, float]]:
    points = []
    for layer in ("survey", "splays"):
        for row in geometry[layer]:
            points.extend((row["start"], row["end"]))
    for station in geometry["stations"]:
        x, y = station["position"]
        points.extend(
            (
                (x, y),
                (
                    x
                    + settings.stroke_width_mm * 3
                    + len(station["label"]) * settings.label_height_mm * 4 / 5,
                    y + settings.label_height_mm,
                ),
            )
        )
    for row in geometry["xsections"]:
        points.append(row["position"])
        if row["connector"] is not None:
            points.extend((row["connector"]["start"], row["connector"]["end"]))
        for splay in row["splays"]:
            points.extend((splay["start"], splay["end"]))
    return points


def _viewport(points, settings: DrawingSettings) -> dict:
    # XSection circles have radius 2 * stroke and a centred outline of stroke/2.
    margin = settings.padding_mm + settings.stroke_width_mm * 2.5
    left = min(point[0] for point in points) - margin
    top = min(point[1] for point in points) - margin
    width = max(point[0] for point in points) + margin - left
    height = max(point[1] for point in points) + margin - top
    scale = min(
        settings.pixels_per_metre / 1000,
        settings.max_dimension / width,
        settings.max_dimension / height,
        math.sqrt(settings.max_pixels / (width * height)),
    )
    # Floor maintains both caps; one-pixel minimum still preserves the whole viewBox.
    pixel_width = max(1, math.floor(width * scale))
    pixel_height = max(1, math.floor(height * scale))
    if pixel_width * pixel_height > settings.max_pixels:
        if pixel_width >= pixel_height:
            pixel_width = max(1, settings.max_pixels // pixel_height)
        else:
            pixel_height = max(1, settings.max_pixels // pixel_width)
    return {
        "viewbox_mm": [left, top, width, height],
        "width_px": pixel_width,
        "height_px": pixel_height,
        "effective_pixels_per_metre": min(pixel_width / width, pixel_height / height) * 1000,
        "requested_pixels_per_metre": settings.pixels_per_metre,
    }


def make_svg(
    drawing: Drawing, geometry: dict, view: str, measurements: bool, settings: DrawingSettings
) -> tuple[str, dict]:
    """Keep source coordinates unchanged; viewBox is only a viewport."""
    points = [
        (point.x, point.y)
        for element in drawing.elements
        if isinstance(element, Polygon)
        for point in element.points
    ]
    empty = not points
    if measurements:
        points.extend(_overlay_points(geometry, settings))
    if empty:
        points.extend(((0, 0), (settings.label_height_mm * 9.6, settings.label_height_mm)))
    notices = geometry.get("notices", []) if measurements else []
    notice_position = None
    if notices:
        notice_position = (
            min(point[0] for point in points),
            min(point[1] for point in points) - 2 * settings.label_height_mm,
        )
        points.extend(
            (
                notice_position,
                (notice_position[0] + settings.label_height_mm * 10.4, notice_position[1]),
            )
        )
    viewport = _viewport(points, settings)
    metadata = {
        "view": view,
        "variant": "measurements" if measurements else "sketch",
        "sketch_status": "empty" if empty else "nonempty",
        "mapping": asdict(drawing.mapping),
        "mapping_applied_to_geometry": False,
        "source_units": "mm",
        "axes": "x_right_y_down",
        "viewport": viewport,
        "settings": asdict(settings),
        "font": "jktz-grid-3x5-v1-paths-no-system-fonts",
        "palette_srgb": list(PALETTE),
        "overlay_notices": notices,
        "xsections": [
            {"element_index": index, **asdict(element)}
            for index, element in enumerate(drawing.elements)
            if isinstance(element, XSection)
        ],
    }
    root = Element(
        "svg",
        {
            "xmlns": SVG_NS,
            "xmlns:inkscape": INKSCAPE_NS,
            "version": "1.1",
            "width": str(viewport["width_px"]),
            "height": str(viewport["height_px"]),
            "viewBox": " ".join(_number(value) for value in viewport["viewbox_mm"]),
            "data-sketch-status": metadata["sketch_status"],
        },
    )
    SubElement(
        root, "title"
    ).text = f"PocketTopo {view}: {metadata['variant']}; sketch {metadata['sketch_status']}"
    metadata["sketch_vertices"] = sum(
        len(element.points) for element in drawing.elements if isinstance(element, Polygon)
    )
    SubElement(root, "metadata").text = json.dumps(
        metadata, sort_keys=True, ensure_ascii=True, allow_nan=False
    )
    if settings.background is not None:
        x, y, width, height = viewport["viewbox_mm"]
        SubElement(
            root,
            "rect",
            {
                "id": "background",
                "x": _number(x),
                "y": _number(y),
                "width": _number(width),
                "height": _number(height),
                "fill": settings.background,
            },
        )
    layers = {}
    for layer in ("survey", "splays", "xsections", "sketch", "stations"):
        layers[layer] = SubElement(
            root,
            "g",
            {
                "id": layer,
                "inkscape:groupmode": "layer",
                "inkscape:label": layer,
                "fill": "none",
                "stroke-width": _number(settings.stroke_width_mm),
                "stroke-linecap": "round",
                "stroke-linejoin": "round",
                "stroke": "#666666",
            },
        )
    metadata["sketch_vertices"] = _source_sketch(
        layers["sketch"], drawing, settings.stroke_width_mm
    )
    if empty:
        _glyphs(layers["sketch"], "EMPTY SKETCH", (0, 0), settings.label_height_mm, "#666666")
    if measurements:
        if notice_position is not None:
            notice = SubElement(layers["stations"], "g", {"id": "overlay-notice"})
            SubElement(notice, "title").text = "; ".join(notices)
            _glyphs(notice, "CHECK OVERLAY", notice_position, settings.label_height_mm, "#cc0000")
        for row in geometry["survey"]:
            _line(layers["survey"], row, stroke="#b000b0")
        for row in geometry["splays"]:
            _line(layers["splays"], row, stroke="#008080")
        _xsections(layers["xsections"], geometry["xsections"], settings.stroke_width_mm)
        for station in geometry["stations"]:
            x, y = station["position"]
            group = SubElement(layers["stations"], "g", {"data-station-raw": str(station["raw"])})
            SubElement(
                group,
                "circle",
                {
                    "cx": _number(x),
                    "cy": _number(y),
                    "r": _number(settings.stroke_width_mm * 2),
                    "fill": "#b000b0",
                    "stroke": "none",
                },
            )
            _glyphs(
                group,
                station["label"],
                (x + settings.stroke_width_mm * 3, y),
                settings.label_height_mm,
                "#b000b0",
            )
    return tostring(root, encoding="unicode", short_empty_elements=True) + "\n", metadata
