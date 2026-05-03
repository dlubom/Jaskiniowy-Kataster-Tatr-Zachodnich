"""Validation for the Lokalizacje registry."""

from __future__ import annotations

import csv
import json
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Optional

import yaml

from jktz_locations.coordinates import (
    distance_m,
    epsg2180_to_wgs84,
    parse_float,
    read_epsg2180,
    read_wgs84,
)
from jktz_locations.registry import (
    RegistryObject,
    as_dict,
    as_list,
    current_observation,
    object_files,
    observations,
    related_source_records,
)
from jktz_locations.schema import (
    ALLOWED_CAVE_ASSIGNMENT_STATUSES,
    ALLOWED_OBJECT_TYPES,
    ALLOWED_RELATION_TYPES,
    ALLOWED_REVIEW_STATUSES,
    ALLOWED_VERIFICATION_STATUSES,
    CSV_HEADERS,
    ELEVATION_RANGE,
    EPSG2180_EASTING_RANGE,
    EPSG2180_NORTHING_RANGE,
    WGS84_LAT_RANGE,
    WGS84_LON_RANGE,
)

OBJECT_ID_RE = re.compile(r"^JKTZ-OBJ-\d{6}$")
OBSERVATION_ID_RE = re.compile(r"^JKTZ-OBS-\d{6}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
YEAR_OR_DATE_RE = re.compile(r"^(\d{4}|\d{4}-\d{2}-\d{2})$")


@dataclass(frozen=True)
class Finding:
    severity: Literal["error", "warning"]
    code: str
    path: str
    message: str


@dataclass
class ValidationReport:
    findings: list[Finding]
    object_count: int
    observation_count: int

    @property
    def errors(self) -> list[Finding]:
        return [finding for finding in self.findings if finding.severity == "error"]

    @property
    def warnings(self) -> list[Finding]:
        return [finding for finding in self.findings if finding.severity == "warning"]

    @property
    def ok(self) -> bool:
        return not self.errors


def validate_locations(root: Path) -> ValidationReport:
    findings: list[Finding] = []
    source_values = _dictionary_values(root / "slowniki" / "zrodla.csv", "source", findings)
    accuracy_values = _dictionary_values(root / "slowniki" / "klasy_dokladnosci.csv", "accuracy_class", findings)
    object_type_values = _optional_dictionary_values(
        root / "slowniki" / "typy_obiektow.csv",
        "object_type",
        ALLOWED_OBJECT_TYPES,
        findings,
    )
    yaml_files = object_files(root)
    if not yaml_files:
        findings.append(Finding("error", "registry_missing", str(root), "Brak plikow YAML w rejestr/obiekty."))
        return ValidationReport(findings=findings, object_count=0, observation_count=0)

    objects: list[RegistryObject] = []
    for path in yaml_files:
        try:
            objects.append(RegistryObject(path=path, data=_load_yaml_for_validation(path)))
        except (OSError, ValueError, yaml.YAMLError) as exc:
            findings.append(Finding("error", "yaml_parse_error", str(path), str(exc)))

    object_ids = _validate_objects(objects, source_values, accuracy_values, object_type_values, findings)
    observation_ids = _validate_observations(objects, source_values, accuracy_values, findings)
    _validate_related_records(objects, object_ids, source_values, findings)
    _validate_csv_tables(root, object_ids, observation_ids, source_values, accuracy_values, findings)

    return ValidationReport(findings=findings, object_count=len(objects), observation_count=len(observation_ids))


def format_report(report: ValidationReport) -> str:
    lines = [
        f"Obiekty: {report.object_count}",
        f"Obserwacje: {report.observation_count}",
        f"Bledy: {len(report.errors)}",
        f"Ostrzezenia: {len(report.warnings)}",
    ]
    for finding in report.findings:
        marker = "ERROR" if finding.severity == "error" else "WARN"
        lines.append(f"{marker} {finding.code} {finding.path}: {finding.message}")
    if report.ok and not report.warnings:
        lines.append("OK: rejestr lokalizacji przechodzi walidacje.")
    elif report.ok:
        lines.append("OK: brak bledow krytycznych, sa ostrzezenia do przejrzenia.")
    return "\n".join(lines)


def _load_yaml_for_validation(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if loaded is None:
        return {}
    if not isinstance(loaded, dict):
        raise ValueError("YAML root must be a mapping")
    for key in ("systems", "observations", "related_source_records"):
        if loaded.get(key) is None:
            loaded[key] = []
    if loaded.get("cave") is None:
        loaded["cave"] = {}
    if loaded.get("source_ids") is None:
        loaded["source_ids"] = {}
    return loaded


def _validate_objects(
    objects: Iterable[RegistryObject],
    source_values: set[str],
    accuracy_values: set[str],
    object_type_values: set[str],
    findings: list[Finding],
) -> set[str]:
    ids: set[str] = set()
    for obj in objects:
        path = str(obj.path)
        data = obj.data
        object_id = str(data.get("id", ""))
        if not OBJECT_ID_RE.match(object_id):
            findings.append(Finding("error", "object_id_invalid", path, f"Niepoprawne ID obiektu: {object_id!r}."))
        if object_id in ids:
            findings.append(Finding("error", "object_id_duplicate", path, f"Powtorzone ID obiektu: {object_id}."))
        if object_id and obj.path.stem != object_id:
            findings.append(
                Finding("error", "object_id_filename_mismatch", path, "ID obiektu nie zgadza sie z nazwa pliku.")
            )
        ids.add(object_id)

        object_type = str(data.get("type", ""))
        if object_type not in object_type_values:
            findings.append(Finding("error", "object_type_invalid", path, f"Nieznany typ obiektu: {object_type!r}."))

        if not str(data.get("name", "")).strip():
            findings.append(Finding("error", "object_name_missing", path, "Brak nazwy obiektu."))

        cave = as_dict(data.get("cave"))
        assignment_status = str(cave.get("assignment_status", ""))
        if assignment_status and assignment_status not in ALLOWED_CAVE_ASSIGNMENT_STATUSES:
            findings.append(
                Finding(
                    "error", "cave_assignment_invalid", path, f"Nieznany status przypisania: {assignment_status!r}."
                )
            )

        review_status = str(data.get("review_status", ""))
        if review_status and review_status not in ALLOWED_REVIEW_STATUSES:
            findings.append(
                Finding("warning", "review_status_unknown", path, f"Nieznany review_status: {review_status!r}.")
            )

        verification_status = str(data.get("verification_status", ""))
        if verification_status and verification_status not in ALLOWED_VERIFICATION_STATUSES:
            findings.append(
                Finding(
                    "warning",
                    "verification_status_unknown",
                    path,
                    f"Nieznany verification_status: {verification_status!r}.",
                )
            )

        accuracy_class = str(data.get("accuracy_class", ""))
        if accuracy_class and accuracy_class not in accuracy_values:
            findings.append(
                Finding("error", "accuracy_class_unknown", path, f"Nieznana klasa dokladnosci: {accuracy_class!r}.")
            )

        _validate_current_observation_pointer(obj, source_values, findings)
    return ids


def _validate_observations(
    objects: Iterable[RegistryObject],
    source_values: set[str],
    accuracy_values: set[str],
    findings: list[Finding],
) -> set[str]:
    ids: set[str] = set()
    for obj in objects:
        for index, observation in enumerate(observations(obj), start=1):
            path = f"{obj.path}#observations[{index}]"
            observation_id = str(observation.get("id", ""))
            if not OBSERVATION_ID_RE.match(observation_id):
                findings.append(
                    Finding("error", "observation_id_invalid", path, f"Niepoprawne ID: {observation_id!r}.")
                )
            if observation_id in ids:
                findings.append(
                    Finding("error", "observation_id_duplicate", path, f"Powtorzone ID obserwacji: {observation_id}.")
                )
            ids.add(observation_id)

            source = str(observation.get("source", ""))
            if source not in source_values:
                findings.append(Finding("error", "source_unknown", path, f"Nieznane zrodlo: {source!r}."))

            accuracy_class = str(observation.get("accuracy_class", ""))
            if accuracy_class and accuracy_class not in accuracy_values:
                findings.append(
                    Finding("error", "accuracy_class_unknown", path, f"Nieznana klasa dokladnosci: {accuracy_class!r}.")
                )

            verification_status = str(observation.get("verification_status", ""))
            if verification_status and verification_status not in ALLOWED_VERIFICATION_STATUSES:
                findings.append(
                    Finding(
                        "warning",
                        "verification_status_unknown",
                        path,
                        f"Nieznany verification_status: {verification_status!r}.",
                    )
                )

            _validate_date(observation.get("observation_date"), DATE_RE, "observation_date", path, findings)
            _validate_date(observation.get("source_data_date"), YEAR_OR_DATE_RE, "source_data_date", path, findings)
            _validate_coordinates(as_dict(observation.get("coords")), path, findings)
    return ids


def _validate_current_observation_pointer(
    obj: RegistryObject,
    source_values: set[str],
    findings: list[Finding],
) -> None:
    del source_values
    current_id = str(obj.data.get("current_observation_id", ""))
    if not current_id:
        findings.append(Finding("error", "current_observation_missing", str(obj.path), "Brak current_observation_id."))
        return
    if current_observation(obj) is None:
        findings.append(
            Finding("error", "current_observation_missing", str(obj.path), f"Nie znaleziono obserwacji {current_id}.")
        )


def _validate_related_records(
    objects: Iterable[RegistryObject],
    object_ids: set[str],
    source_values: set[str],
    findings: list[Finding],
) -> None:
    for obj in objects:
        for index, related in enumerate(related_source_records(obj), start=1):
            path = f"{obj.path}#related_source_records[{index}]"
            source = str(related.get("source", ""))
            if source not in source_values:
                findings.append(Finding("error", "source_unknown", path, f"Nieznane zrodlo: {source!r}."))
            relation_type = str(related.get("relation_type", ""))
            if relation_type not in ALLOWED_RELATION_TYPES:
                findings.append(
                    Finding("warning", "relation_type_unknown", path, f"Nieznany relation_type: {relation_type!r}.")
                )
            for candidate_id in as_list(related.get("candidate_object_ids")):
                candidate_text = str(candidate_id)
                if candidate_text and candidate_text not in object_ids:
                    findings.append(
                        Finding(
                            "error",
                            "candidate_object_missing",
                            path,
                            f"Nieznany candidate_object_id: {candidate_text}.",
                        )
                    )
            _validate_coordinates(as_dict(related.get("coords")), path, findings, require_complete=False)


def _validate_csv_tables(
    root: Path,
    object_ids: set[str],
    observation_ids: set[str],
    source_values: set[str],
    accuracy_values: set[str],
    findings: list[Finding],
) -> None:
    data_dir = root / "dane"
    for filename, headers in CSV_HEADERS.items():
        path = data_dir / filename
        if not path.exists():
            findings.append(Finding("error", "csv_missing", str(path), "Brak wymaganej tabeli CSV."))
            continue
        rows, actual_headers = _read_csv(path, findings)
        if actual_headers != headers:
            missing = [header for header in headers if header not in actual_headers]
            extra = [header for header in actual_headers if header not in headers]
            if missing:
                findings.append(
                    Finding("error", "csv_header_missing", str(path), f"Brak kolumn: {', '.join(missing)}.")
                )
            if extra:
                findings.append(
                    Finding("warning", "csv_header_extra", str(path), f"Dodatkowe kolumny: {', '.join(extra)}.")
                )
        _validate_csv_rows(path, filename, rows, object_ids, observation_ids, source_values, accuracy_values, findings)


def _validate_csv_rows(
    path: Path,
    filename: str,
    rows: list[dict[str, str]],
    object_ids: set[str],
    observation_ids: set[str],
    source_values: set[str],
    accuracy_values: set[str],
    findings: list[Finding],
) -> None:
    if filename == "obiekty.csv":
        csv_object_ids = {row.get("jktz_object_id", "") for row in rows}
        _compare_id_sets(path, "object", object_ids, csv_object_ids, findings)
        _check_duplicate_values(path, rows, "jktz_object_id", findings)
        for line, row in enumerate(rows, start=2):
            object_id = row.get("jktz_object_id", "")
            if row.get("current_observation_id", "") not in observation_ids:
                findings.append(Finding("error", "csv_current_observation_missing", f"{path}:{line}", object_id))
            if row.get("object_type", "") not in ALLOWED_OBJECT_TYPES:
                findings.append(
                    Finding("error", "csv_object_type_invalid", f"{path}:{line}", row.get("object_type", ""))
                )
            if row.get("accuracy_class", "") and row.get("accuracy_class", "") not in accuracy_values:
                findings.append(
                    Finding("error", "csv_accuracy_class_unknown", f"{path}:{line}", row.get("accuracy_class", ""))
                )
    elif filename == "pomiary_lokalizacji.csv":
        csv_observation_ids = {row.get("jktz_observation_id", "") for row in rows}
        _compare_id_sets(path, "observation", observation_ids, csv_observation_ids, findings)
        _check_duplicate_values(path, rows, "jktz_observation_id", findings)
        for line, row in enumerate(rows, start=2):
            if row.get("jktz_object_id", "") not in object_ids:
                findings.append(
                    Finding("error", "csv_observation_object_missing", f"{path}:{line}", row.get("jktz_object_id", ""))
                )
            if row.get("source", "") not in source_values:
                findings.append(Finding("error", "csv_source_unknown", f"{path}:{line}", row.get("source", "")))
            if row.get("accuracy_class", "") and row.get("accuracy_class", "") not in accuracy_values:
                findings.append(
                    Finding("error", "csv_accuracy_class_unknown", f"{path}:{line}", row.get("accuracy_class", ""))
                )
            _validate_raw_json(row.get("raw_json", ""), f"{path}:{line}", findings)
    elif filename == "identyfikatory_zrodel.csv":
        for line, row in enumerate(rows, start=2):
            if row.get("jktz_object_id", "") not in object_ids:
                findings.append(
                    Finding("error", "csv_identifier_object_missing", f"{path}:{line}", row.get("jktz_object_id", ""))
                )
            if row.get("source", "") not in source_values:
                findings.append(Finding("error", "csv_source_unknown", f"{path}:{line}", row.get("source", "")))
    elif filename == "powiazane_rekordy_zrodel.csv":
        for line, row in enumerate(rows, start=2):
            if row.get("source", "") not in source_values:
                findings.append(Finding("error", "csv_source_unknown", f"{path}:{line}", row.get("source", "")))
            for candidate_id in filter(None, row.get("candidate_object_ids", "").split(";")):
                if candidate_id not in object_ids:
                    findings.append(Finding("error", "csv_candidate_object_missing", f"{path}:{line}", candidate_id))
            _validate_raw_json(row.get("raw_json", ""), f"{path}:{line}", findings)


def _validate_coordinates(
    coords: dict[str, object],
    path: str,
    findings: list[Finding],
    require_complete: bool = True,
) -> None:
    epsg_raw = as_dict(coords.get("epsg2180"))
    wgs_raw = as_dict(coords.get("wgs84"))
    epsg2180 = read_epsg2180(coords)
    wgs84 = read_wgs84(coords)

    if require_complete and epsg2180 is None and wgs84 is None:
        findings.append(
            Finding("error", "coords_missing", path, "Brak kompletnych wspolrzednych EPSG:2180 albo WGS84.")
        )
    if bool(epsg_raw.get("northing")) != bool(epsg_raw.get("easting")):
        findings.append(Finding("error", "epsg2180_incomplete", path, "EPSG:2180 wymaga northing i easting."))
    if bool(wgs_raw.get("lat")) != bool(wgs_raw.get("lon")):
        findings.append(Finding("error", "wgs84_incomplete", path, "WGS84 wymaga lat i lon."))

    if epsg2180 is not None:
        _warn_if_outside(epsg2180.northing, EPSG2180_NORTHING_RANGE, "epsg2180_northing_out_of_range", path, findings)
        _warn_if_outside(epsg2180.easting, EPSG2180_EASTING_RANGE, "epsg2180_easting_out_of_range", path, findings)
        if epsg2180.z is not None:
            _warn_if_outside(epsg2180.z, ELEVATION_RANGE, "elevation_out_of_range", path, findings)
    if wgs84 is not None:
        _warn_if_outside(wgs84.lat, WGS84_LAT_RANGE, "wgs84_lat_out_of_range", path, findings)
        _warn_if_outside(wgs84.lon, WGS84_LON_RANGE, "wgs84_lon_out_of_range", path, findings)
    if epsg2180 is not None and wgs84 is not None:
        calculated = epsg2180_to_wgs84(epsg2180)
        delta = distance_m(wgs84, calculated)
        if delta > 25:
            findings.append(
                Finding(
                    "warning",
                    "coordinate_system_mismatch",
                    path,
                    f"EPSG:2180 i WGS84 roznia sie o ok. {delta:.1f} m; sprawdz kolejnosc x1992/y1992.",
                )
            )


def _validate_date(
    value: object,
    pattern: re.Pattern[str],
    field_name: str,
    path: str,
    findings: list[Finding],
) -> None:
    text = str(value or "").strip()
    if text and not pattern.match(text):
        findings.append(
            Finding("warning", "date_format_invalid", path, f"{field_name} ma nieoczekiwany format: {text!r}.")
        )


def _dictionary_values(path: Path, field: str, findings: list[Finding]) -> set[str]:
    if not path.exists():
        findings.append(Finding("error", "dictionary_missing", str(path), "Brak slownika."))
        return set()
    rows, headers = _read_csv(path, findings)
    if field not in headers:
        findings.append(Finding("error", "dictionary_field_missing", str(path), f"Brak kolumny {field}."))
        return set()
    return {row[field] for row in rows if row.get(field)}


def _optional_dictionary_values(
    path: Path,
    field: str,
    fallback: set[str],
    findings: list[Finding],
) -> set[str]:
    if not path.exists():
        findings.append(Finding("warning", "dictionary_missing", str(path), "Brak opcjonalnego slownika."))
        return set(fallback)
    values = _dictionary_values(path, field, findings)
    return values or set(fallback)


def _read_csv(path: Path, findings: list[Finding]) -> tuple[list[dict[str, str]], list[str]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            return list(reader), list(reader.fieldnames or [])
    except csv.Error as exc:
        findings.append(Finding("error", "csv_parse_error", str(path), str(exc)))
        return [], []


def _compare_id_sets(
    path: Path,
    label: str,
    expected: set[str],
    actual: set[str],
    findings: list[Finding],
) -> None:
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing:
        findings.append(Finding("error", f"csv_{label}_ids_missing", str(path), f"Brak ID: {', '.join(missing[:20])}."))
    if extra:
        findings.append(
            Finding("error", f"csv_{label}_ids_extra", str(path), f"Nadmiarowe ID: {', '.join(extra[:20])}.")
        )


def _check_duplicate_values(
    path: Path,
    rows: list[dict[str, str]],
    field_name: str,
    findings: list[Finding],
) -> None:
    seen: set[str] = set()
    for line, row in enumerate(rows, start=2):
        value = row.get(field_name, "")
        if not value:
            continue
        if value in seen:
            findings.append(
                Finding("error", "csv_duplicate_id", f"{path}:{line}", f"Powtorzona wartosc {field_name}: {value}.")
            )
        seen.add(value)


def _validate_raw_json(raw_json: str, path: str, findings: list[Finding]) -> None:
    if not raw_json:
        return
    try:
        json.loads(raw_json)
    except json.JSONDecodeError as exc:
        findings.append(Finding("error", "raw_json_invalid", path, str(exc)))


def _warn_if_outside(
    value: Optional[float],
    allowed_range: tuple[float, float],
    code: str,
    path: str,
    findings: list[Finding],
) -> None:
    if value is None:
        return
    low, high = allowed_range
    if value < low or value > high:
        findings.append(Finding("warning", code, path, f"Wartosc {value} poza zakresem roboczym {low}-{high}."))


def numeric_or_none(value: object) -> Optional[float]:
    try:
        return parse_float(value)
    except ValueError:
        return None
