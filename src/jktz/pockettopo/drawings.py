"""P05 in-memory SVG/PNG exports; package collision/atomicity belongs to P06."""

from __future__ import annotations

import math
import struct
import subprocess
import tempfile
import zlib
from dataclasses import dataclass
from pathlib import Path

from jktz.pockettopo.drawing_svg import DrawingSettings, make_svg, validate_settings
from jktz.pockettopo.export import export_surveys
from jktz.pockettopo.export_policy import CorrectionPolicy
from jktz.pockettopo.parser import DEFAULT_LIMITS, ParseLimits, parse_bytes
from jktz.pockettopo.projection import project_geometry
from jktz.pockettopo.report import ProcessingPlan

RESVG_VERSION = "0.48.1"
DEFAULT_DRAWING_SETTINGS = DrawingSettings()


@dataclass(frozen=True)
class DrawingExport:
    source_document: dict
    report: dict
    svgs: dict[str, str]
    pngs: dict[str, bytes]


class RenderingError(RuntimeError):
    """An unavailable, mismatched or failed pinned renderer produced no result."""


def _run(command: list[str], timeout: float) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run(command, capture_output=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise RenderingError(f"resvg execution failed: {error}") from error
    if result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace")[:1000]
        raise RenderingError(f"resvg exited {result.returncode}: {detail}")
    return result


def _renderer_version(path: str, timeout: float) -> str:
    result = _run([path, "--version"], timeout)
    version = result.stdout.decode("utf-8", errors="replace").strip()
    if version != RESVG_VERSION:
        raise RenderingError(f"resvg {RESVG_VERSION} is required; received {version!r}")
    return version


def _validate_png_pixels(compressed: bytes, width: int, height: int) -> None:
    expected = height * (1 + 4 * width)
    decoder = zlib.decompressobj()
    try:
        # One excess byte detects oversized output without expanding an arbitrary bomb.
        pixels = decoder.decompress(compressed, expected + 1)
    except zlib.error as error:
        raise RenderingError("resvg PNG image data is not valid zlib") from error
    if len(pixels) != expected:
        raise RenderingError("resvg PNG scanline length differs from its dimensions")
    if not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
        raise RenderingError("resvg PNG image stream is truncated or has trailing data")
    if any(pixels[offset] > 4 for offset in range(0, expected, 1 + 4 * width)):
        raise RenderingError("resvg PNG contains an invalid scanline filter")


def _validate_png(data: bytes, width: int, height: int) -> None:
    """Require a whole CRC-checked PNG, including nonempty image data and IEND."""
    if len(data) < 33 or data[:16] != b"\x89PNG\r\n\x1a\n\0\0\0\rIHDR":
        raise RenderingError("resvg output has no PNG IHDR")
    if struct.unpack(">II", data[16:24]) != (width, height):
        raise RenderingError("resvg PNG dimensions differ from the declared viewport")
    if data[24:29] != bytes((8, 6, 0, 0, 0)):
        raise RenderingError("resvg PNG must use non-interlaced RGBA8")
    offset, seen_data, data_ended = 8, False, False
    image_chunks = []
    while offset < len(data):
        if len(data) - offset < 12:
            raise RenderingError("resvg PNG has a truncated chunk header")
        size = struct.unpack(">I", data[offset : offset + 4])[0]
        end = offset + size + 12
        if end > len(data):
            raise RenderingError("resvg PNG has a truncated chunk")
        kind = data[offset + 4 : offset + 8]
        payload = data[offset + 8 : end - 4]
        crc = struct.unpack(">I", data[end - 4 : end])[0]
        if zlib.crc32(kind + payload) != crc:
            raise RenderingError("resvg PNG chunk CRC mismatch")
        if kind == b"IDAT":
            if data_ended:
                raise RenderingError("resvg PNG has noncontiguous image data")
            seen_data = seen_data or bool(payload)
            image_chunks.append(payload)
        elif kind == b"IEND":
            if payload or not seen_data or end != len(data):
                raise RenderingError("resvg PNG has invalid or premature IEND")
            _validate_png_pixels(b"".join(image_chunks), width, height)
            return
        elif kind == b"IHDR" and offset != 8:
            raise RenderingError("resvg PNG has a duplicate IHDR")
        else:
            data_ended = seen_data
        offset = end
    raise RenderingError("resvg PNG is incomplete: missing IEND")


def _png(svg: str, metadata: dict, path: str, timeout: float) -> bytes:
    viewport = metadata["viewport"]
    width, height = viewport["width_px"], viewport["height_px"]
    with tempfile.TemporaryDirectory(prefix="jktz-pockettopo-png-") as directory:
        source = Path(directory) / "drawing.svg"
        target = Path(directory) / "drawing.png"
        source.write_text(svg, encoding="utf-8")
        _run(
            [
                path,
                "--skip-system-fonts",
                "--dpi",
                "96",
                "--width",
                str(width),
                "--height",
                str(height),
                str(source),
                str(target),
            ],
            timeout,
        )
        try:
            result = target.read_bytes()
        except OSError as error:
            raise RenderingError(f"resvg did not produce a readable PNG: {error}") from error
    _validate_png(result, width, height)
    return result


def _notices(geometry: dict, report: dict) -> None:
    notices = [item["code"] for item in geometry["diagnostics"]]
    if report["completeness"]["held_shots"]:
        notices.append("held_source_shots_not_projected")
    if any(
        "mixed_flip_preserved_for_drawing_review" in group["warnings"] for group in report["groups"]
    ):
        notices.append("mixed_flip_preserved_for_drawing_review")
    for view_geometry in geometry["views"].values():
        missing = [
            row["status"] for row in view_geometry["xsections"] if row["status"] != "projected"
        ]
        view_geometry["notices"] = list(dict.fromkeys(notices + missing))


def export_drawings(
    data: bytes,
    *,
    plan: ProcessingPlan | None = None,
    correction_policy: CorrectionPolicy | None = None,
    settings: DrawingSettings = DEFAULT_DRAWING_SETTINGS,
    resvg_path: str | Path | None = None,
    renderer_timeout: float = 60.0,
    min_resultant: float = 1e-12,
    limits: ParseLimits = DEFAULT_LIMITS,
) -> DrawingExport:
    """Return four lossless sketches and explicitly selected measurement overlays.

    The sketch never moves to match survey geometry. Mapping origins/scales remain
    metadata. PNG is optional only to permit SVG inspection without a renderer;
    callers requesting PNG must supply resvg 0.48.1. Every raster uses its exact
    corresponding SVG, explicit dimensions, 96 dpi and no system fonts.
    """
    validate_settings(settings)
    if isinstance(renderer_timeout, bool) or not isinstance(renderer_timeout, (int, float)):
        raise ValueError("renderer_timeout must be a finite positive number")
    if not math.isfinite(renderer_timeout) or renderer_timeout <= 0:
        raise ValueError("renderer_timeout must be a finite positive number")
    surveys = export_surveys(
        data,
        plan=plan,
        correction_policy=correction_policy,
        min_resultant=min_resultant,
        limits=limits,
    )
    model = parse_bytes(data, limits=limits)
    geometry = project_geometry(model, surveys.report)
    _notices(geometry, surveys.report)
    svgs, pngs, drawings = {}, {}, {}
    version = None if resvg_path is None else _renderer_version(str(resvg_path), renderer_timeout)
    for view, drawing in (("plan", model.outline), ("side", model.sideview)):
        for measurements in (False, True):
            name = f"{view}-{'measurements' if measurements else 'sketch'}"
            svg, metadata = make_svg(drawing, geometry["views"][view], view, measurements, settings)
            svgs[name] = svg
            drawings[name] = metadata
            if resvg_path is not None:
                pngs[name] = _png(svg, metadata, str(resvg_path), renderer_timeout)
    report = surveys.report
    report["stage"] = "P05"
    for document in (surveys.source_document, report):
        document["provenance"]["algorithm_version"] = "p05-1"
    report["drawings"] = {
        "artifacts": drawings,
        "geometry": geometry,
        "renderer": {
            "name": "resvg",
            "required_version": RESVG_VERSION,
            "actual_version": version,
            "dpi": 96,
            "system_fonts": False,
            "status": "rendered" if pngs else "not_requested",
        },
    }
    report["completeness"].update(
        svg_drawings_created=len(svgs),
        png_drawings_created=len(pngs),
        conversion_complete=False,
        atomic_package_created=False,
    )
    report["limitations"] = [
        row for row in report["limitations"] if not row.startswith("Sketches, CLI")
    ]
    report["limitations"].extend(
        [
            "Survey overlays follow the declared projection policy; source sketches do not move.",
            "CLI, atomic package output and skill remain P06; conversion is incomplete.",
        ]
    )
    return DrawingExport(surveys.source_document, report, svgs, pngs)
