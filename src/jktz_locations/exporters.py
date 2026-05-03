"""Export current object locations to common field formats."""

from __future__ import annotations

import csv
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Optional, Union

import gpxpy.gpx
import openpyxl
import shapefile
from openpyxl.worksheet.table import Table, TableStyleInfo

from jktz_locations.coordinates import (
    Epsg2180Point,
    Wgs84Point,
    ensure_both,
    epsg2180_prj,
    format_float,
    read_epsg2180,
    read_wgs84,
)
from jktz_locations.registry import as_dict, current_observation, load_objects
from jktz_locations.schema import CURRENT_EXPORT_HEADERS


def collect_current_locations(root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for obj in load_objects(root):
        data = obj.data
        observation = current_observation(obj)
        if observation is None:
            continue
        coords = as_dict(observation.get("coords"))
        epsg2180, wgs84 = ensure_both(read_epsg2180(coords), read_wgs84(coords))
        cave = as_dict(data.get("cave"))
        row = {
            "jktz_object_id": str(data.get("id", "")),
            "object_type": str(data.get("type", "")),
            "name": str(data.get("name", "")),
            "label": str(data.get("label", "")),
            "cave_inventory_id": str(cave.get("inventory_id", "")),
            "cave_name": str(cave.get("name", "")),
            "current_observation_id": str(data.get("current_observation_id", "")),
            "source": str(observation.get("source", "")),
            "observation_date": str(observation.get("observation_date", "")),
            "method": str(observation.get("method", "")),
            "x1992": format_float(epsg2180.northing, 3) if epsg2180 else "",
            "y1992": format_float(epsg2180.easting, 3) if epsg2180 else "",
            "z": _z_text(epsg2180, observation),
            "lat_wgs84": format_float(wgs84.lat, 8) if wgs84 else "",
            "lon_wgs84": format_float(wgs84.lon, 8) if wgs84 else "",
            "accuracy_class": str(observation.get("accuracy_class", data.get("accuracy_class", ""))),
            "estimated_accuracy_m": str(observation.get("estimated_accuracy_m", "")),
            "verification_status": str(observation.get("verification_status", data.get("verification_status", ""))),
            "review_status": str(data.get("review_status", "")),
            "notes": str(data.get("notes", "")),
        }
        rows.append(row)
    return sorted(rows, key=lambda item: item["jktz_object_id"])


def export_current_locations(root: Path, out_dir: Path, formats: Iterable[str]) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = collect_current_locations(root)
    written: list[Path] = []
    requested = {item.lower() for item in formats}
    if "csv" in requested:
        written.append(write_csv(out_dir / "aktualne_lokalizacje.csv", rows))
    if "xlsx" in requested:
        written.append(write_xlsx(out_dir / "aktualne_lokalizacje.xlsx", rows))
    if "gpx" in requested:
        written.append(write_gpx(out_dir / "aktualne_lokalizacje.gpx", rows))
    if "shp" in requested or "shapefile" in requested:
        written.extend(write_shapefile(out_dir / "aktualne_lokalizacje_2180", rows))
    return written


def write_csv(path: Path, rows: list[dict[str, str]]) -> Path:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CURRENT_EXPORT_HEADERS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return path


def write_xlsx(path: Path, rows: list[dict[str, str]]) -> Path:
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "aktualne_lokalizacje"
    worksheet.append(CURRENT_EXPORT_HEADERS)
    for row in rows:
        worksheet.append([row.get(field, "") for field in CURRENT_EXPORT_HEADERS])
    worksheet.freeze_panes = "A2"
    worksheet.auto_filter.ref = worksheet.dimensions
    if rows:
        table = Table(displayName="AktualneLokalizacje", ref=worksheet.dimensions)
        table.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
        worksheet.add_table(table)
    for column_cells in worksheet.columns:
        max_length = max(len(str(cell.value or "")) for cell in column_cells)
        worksheet.column_dimensions[column_cells[0].column_letter].width = min(max(max_length + 2, 10), 48)
    workbook.save(path)
    return path


def write_gpx(path: Path, rows: list[dict[str, str]]) -> Path:
    gpx = gpxpy.gpx.GPX()
    for row in rows:
        lat = _to_float(row.get("lat_wgs84"))
        lon = _to_float(row.get("lon_wgs84"))
        if lat is None or lon is None:
            continue
        waypoint = gpxpy.gpx.GPXWaypoint(
            latitude=lat,
            longitude=lon,
            elevation=_to_float(row.get("z")),
            name=f"{row['jktz_object_id']} {row['name']}".strip(),
            description=_description(row),
        )
        gpx.waypoints.append(waypoint)
    path.write_text(gpx.to_xml(), encoding="utf-8")
    return path


def write_shapefile(base_path: Path, rows: list[dict[str, str]]) -> list[Path]:
    writer = shapefile.Writer(str(base_path), shapeType=shapefile.POINT)
    writer.autoBalance = True
    writer.field("OBJ_ID", "C", size=18)
    writer.field("TYPE", "C", size=32)
    writer.field("NAME", "C", size=180)
    writer.field("LABEL", "C", size=80)
    writer.field("INV_ID", "C", size=32)
    writer.field("CAVE_NAME", "C", size=180)
    writer.field("OBS_ID", "C", size=18)
    writer.field("SRC", "C", size=32)
    writer.field("OBS_DATE", "C", size=16)
    writer.field("METHOD", "C", size=120)
    writer.field("Z_M", "N", size=12, decimal=3)
    writer.field("LAT", "N", size=12, decimal=8)
    writer.field("LON", "N", size=12, decimal=8)
    writer.field("ACC_CLASS", "C", size=32)
    writer.field("VERIF", "C", size=32)
    writer.field("REVIEW", "C", size=48)

    for row in rows:
        northing = _to_float(row.get("x1992"))
        easting = _to_float(row.get("y1992"))
        if northing is None or easting is None:
            continue
        writer.point(easting, northing)
        writer.record(
            row["jktz_object_id"],
            _truncate(row["object_type"], 32),
            _truncate(row["name"], 180),
            _truncate(row["label"], 80),
            _truncate(row["cave_inventory_id"], 32),
            _truncate(row["cave_name"], 180),
            row["current_observation_id"],
            _truncate(row["source"], 32),
            row["observation_date"],
            _truncate(row["method"], 120),
            _dbf_number(row.get("z")),
            _dbf_number(row.get("lat_wgs84")),
            _dbf_number(row.get("lon_wgs84")),
            _truncate(row["accuracy_class"], 32),
            _truncate(row["verification_status"], 32),
            _truncate(row["review_status"], 48),
        )
    writer.close()
    prj_path = base_path.with_suffix(".prj")
    cpg_path = base_path.with_suffix(".cpg")
    prj_path.write_text(epsg2180_prj(), encoding="utf-8")
    cpg_path.write_text("UTF-8\n", encoding="ascii")
    return [
        base_path.with_suffix(".shp"),
        base_path.with_suffix(".shx"),
        base_path.with_suffix(".dbf"),
        prj_path,
        cpg_path,
    ]


def _z_text(epsg2180: Optional[Epsg2180Point], observation: dict[str, Any]) -> str:
    if epsg2180 and epsg2180.z is not None:
        return format_float(epsg2180.z, 3)
    coords = as_dict(observation.get("coords"))
    wgs84 = read_wgs84(coords)
    if isinstance(wgs84, Wgs84Point) and wgs84.z is not None:
        return format_float(wgs84.z, 3)
    return ""


def _to_float(value: object) -> Optional[float]:
    try:
        if value is None or str(value).strip() == "":
            return None
        return float(str(value).replace(",", "."))
    except ValueError:
        return None


def _dbf_number(value: object) -> Union[float, str]:
    parsed = _to_float(value)
    return "" if parsed is None else parsed


def _truncate(value: str, max_length: int) -> str:
    return value if len(value) <= max_length else value[: max_length - 1] + "."


def _description(row: dict[str, str]) -> str:
    parts = [
        f"typ: {row['object_type']}",
        f"obserwacja: {row['current_observation_id']} ({row['source']})",
    ]
    if row["cave_inventory_id"]:
        parts.append(f"inwentarz: {row['cave_inventory_id']}")
    if row["accuracy_class"]:
        parts.append(f"dokladnosc: {row['accuracy_class']}")
    return "; ".join(parts)
