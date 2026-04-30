#!/usr/bin/env python3
"""Build a flat object-level location registry from TPN and PIG/Geoportal CSV exports."""

from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "_RAW"
DATA_DIR = ROOT / "dane"
DICT_DIR = ROOT / "slowniki"
REGISTRY_DIR = ROOT / "rejestr"
OBJECTS_DIR = REGISTRY_DIR / "obiekty"

DEFAULT_TPN = RAW_DIR / "tpn_otwory_jaskin_2026-04-29.csv"
DEFAULT_PIG = RAW_DIR / "pig_geoportal_otwory_jaskin_2026-04-29.csv"

IMPORT_DATE = "2026-04-29"
UNKNOWN = {"", "<Null>", "<pusta wartość>", "<blank>"}


@dataclass
class IdGenerator:
    prefix: str
    width: int
    used: set[str]

    def __post_init__(self) -> None:
        self.current = 0
        pattern = re.compile(rf"^{re.escape(self.prefix)}(\d+)$")
        for value in self.used:
            match = pattern.match(value or "")
            if match:
                self.current = max(self.current, int(match.group(1)))

    def next(self) -> str:
        while True:
            self.current += 1
            candidate = f"{self.prefix}{self.current:0{self.width}d}"
            if candidate not in self.used:
                self.used.add(candidate)
                return candidate


def clean(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    return "" if text in UNKNOWN else text


def decimal_text(value: object) -> str:
    text = clean(value).replace(" ", "").replace(",", ".")
    if not text:
        return ""
    try:
        number = Decimal(text)
    except InvalidOperation:
        return text
    normalized = format(number.normalize(), "f")
    return "0" if normalized == "-0" else normalized


def date_from_datetime(value: object) -> str:
    text = clean(value)
    if not text:
        return ""
    match = re.search(r"(\d{4})-(\d{2})-(\d{2})", text)
    return match.group(0) if match else text


def date_from_text(value: object) -> str:
    text = clean(value)
    match = re.search(r"\b(\d{2})-(\d{2})-(\d{4})\b", text)
    if not match:
        return ""
    day, month, year = match.groups()
    return f"{year}-{month}-{day}"


def is_cave_inventory(value: str) -> bool:
    return clean(value).startswith("T.")


def normalize_geneza(value: object) -> str:
    text = clean(value).lower()
    return "jaskinia" if text == "jasknia" else text


def object_type_from_geneza(value: object) -> str:
    geneza = normalize_geneza(value)
    if geneza == "jaskinia":
        return "otwor_jaskini"
    if geneza == "sztolnia":
        return "sztolnia"
    if geneza == "jaskinia/sztolnia":
        return "otwor_jaskini_lub_sztolnia"
    return "obiekt_terenowy"


def tpn_verification(value: object) -> str:
    text = clean(value)
    if text == "1":
        return "zweryfikowane"
    if text == "0":
        return "niezweryfikowane"
    return f"tpn_weryf_{text}" if text else ""


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def existing_map(path: Path, key_field: str, id_field: str) -> dict[str, str]:
    if not path.exists():
        return {}
    rows = read_csv(path)
    return {clean(row.get(key_field)): clean(row.get(id_field)) for row in rows if clean(row.get(key_field))}


def source_json(row: dict[str, str]) -> str:
    return json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def slug(value: str, fallback: str) -> str:
    text = clean(value) or fallback
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^A-Za-z0-9._-]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("._")
    return text or fallback


def yaml_scalar(value: Any) -> str:
    if value is None or value == "":
        return '""'
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def to_yaml(value: Any, indent: int = 0) -> list[str]:
    prefix = " " * indent
    if isinstance(value, dict):
        lines: list[str] = []
        for key, item in value.items():
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}{key}:")
                lines.extend(to_yaml(item, indent + 2))
            else:
                lines.append(f"{prefix}{key}: {yaml_scalar(item)}")
        return lines
    if isinstance(value, list):
        lines = []
        for item in value:
            if isinstance(item, dict):
                if not item:
                    lines.append(f"{prefix}- {{}}")
                    continue
                first_key = next(iter(item))
                first_value = item[first_key]
                rest = {key: val for key, val in item.items() if key != first_key}
                if isinstance(first_value, (dict, list)):
                    lines.append(f"{prefix}- {first_key}:")
                    lines.extend(to_yaml(first_value, indent + 4))
                else:
                    lines.append(f"{prefix}- {first_key}: {yaml_scalar(first_value)}")
                lines.extend(to_yaml(rest, indent + 2))
            elif isinstance(item, list):
                lines.append(f"{prefix}-")
                lines.extend(to_yaml(item, indent + 2))
            else:
                lines.append(f"{prefix}- {yaml_scalar(item)}")
        return lines
    return [f"{prefix}{yaml_scalar(value)}"]


def write_yaml(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# Generated by Lokalizacje/tools/import_locations.py\n" + "\n".join(to_yaml(value)) + "\n",
        encoding="utf-8",
    )


def extract_inventory_ids(text: str) -> list[str]:
    return sorted(set(re.findall(r"T\.[A-Z]-\d{2}\.\d{2,3}", text or "")))


def build_cave_contexts(tpn_rows: list[dict[str, str]], pig_rows: list[dict[str, str]]) -> dict[str, dict[str, object]]:
    contexts: dict[str, dict[str, object]] = {}

    def ensure(inventory_id: str) -> dict[str, object]:
        if inventory_id not in contexts:
            contexts[inventory_id] = {
                "inventory_id": inventory_id,
                "name": "",
                "tpn_name": "",
                "pig_name": "",
                "pig_id": "",
                "pig_link": "",
                "object_count": 0,
                "systems": [],
            }
        return contexts[inventory_id]

    for row in tpn_rows:
        inventory_id = clean(row.get("NR_INWENT"))
        if not is_cave_inventory(inventory_id):
            continue
        context = ensure(inventory_id)
        context["tpn_name"] = context["tpn_name"] or clean(row.get("NAZWA"))
        context["object_count"] = int(context["object_count"]) + 1

    system_records: dict[str, dict[str, str]] = {}
    for row in pig_rows:
        inventory_id = clean(row.get("Nr inw."))
        if is_cave_inventory(inventory_id):
            context = ensure(inventory_id)
            context["pig_name"] = clean(row.get("Nazwa"))
            context["pig_id"] = clean(row.get("ID"))
            context["pig_link"] = clean(row.get("Link"))
        elif inventory_id:
            system_records[inventory_id] = row

    system_names = {clean(row.get("Nazwa")).lower(): inventory_id for inventory_id, row in system_records.items()}
    members_by_system: defaultdict[str, set[str]] = defaultdict(set)

    for inventory_id, row in system_records.items():
        for member_inventory_id in extract_inventory_ids(clean(row.get("Inne nazwy"))):
            members_by_system[inventory_id].add(member_inventory_id)

    for row in pig_rows:
        inventory_id = clean(row.get("Nr inw."))
        if not is_cave_inventory(inventory_id):
            continue
        aliases = clean(row.get("Inne nazwy")).lower()
        for system_name, system_inventory_id in system_names.items():
            if system_name and system_name in aliases:
                members_by_system[system_inventory_id].add(inventory_id)

    for system_inventory_id, member_ids in members_by_system.items():
        system_row = system_records.get(system_inventory_id, {})
        system_context = {
            "inventory_id": system_inventory_id,
            "name": clean(system_row.get("Nazwa")),
            "pig_id": clean(system_row.get("ID")),
            "pig_link": clean(system_row.get("Link")),
            "relation": "part_of_system",
            "source": "Geoportal_PIG",
        }
        for member_inventory_id in member_ids:
            if member_inventory_id in contexts:
                contexts[member_inventory_id]["systems"].append(system_context)

    for context in contexts.values():
        context["name"] = context["tpn_name"] or context["pig_name"]
        context["systems"] = sorted(context["systems"], key=lambda item: item["inventory_id"])

    return contexts


def build_name_index(contexts: dict[str, dict[str, object]]) -> dict[str, set[str]]:
    names: defaultdict[str, set[str]] = defaultdict(set)
    for inventory_id, context in contexts.items():
        for key in ("tpn_name", "pig_name", "name"):
            name = clean(context.get(key))
            if name:
                names[name.lower()].add(inventory_id)
    return names


def tpn_observation(row: dict[str, str], observation_id: str, object_id: str, inferred_inventory_id: str) -> dict[str, object]:
    return {
        "jktz_observation_id": observation_id,
        "jktz_object_id": object_id,
        "source": "TPN",
        "source_record_id": clean(row.get("GLOBALID")),
        "source_external_id": clean(row.get("GLOBALID")),
        "source_inventory_id": clean(row.get("NR_INWENT")),
        "inferred_inventory_id": inferred_inventory_id,
        "source_name": clean(row.get("NAZWA")),
        "source_object_label": clean(row.get("OTWÓR")),
        "observation_date": date_from_text(row.get("WER_LOK")),
        "source_data_date": date_from_datetime(row.get("LAST_EDI_1")) or date_from_datetime(row.get("CREATED_DA")),
        "method": clean(row.get("WER_LOK")),
        "device": "",
        "x1992": decimal_text(row.get("X1992")),
        "y1992": decimal_text(row.get("Y1992")),
        "z": decimal_text(row.get("Z")),
        "lat_wgs84": "",
        "lon_wgs84": "",
        "accuracy_class": "nieokreslona",
        "estimated_accuracy_m": "",
        "verification_status": tpn_verification(row.get("WERYF")),
        "verification_notes": clean(row.get("UWAGI")),
        "tags": f"import:{IMPORT_DATE};zrodlo:tpn",
        "match_status": "source_object" if clean(row.get("NR_INWENT")) else ("inferred_cave_by_unique_name" if inferred_inventory_id else "source_object_without_cave"),
        "raw_json": source_json(row),
        "import_key": f"tpn:{clean(row.get('GLOBALID'))}:location",
    }


def pig_observation(row: dict[str, str], observation_id: str, object_id: str, match_status: str) -> dict[str, object]:
    return {
        "jktz_observation_id": observation_id,
        "jktz_object_id": object_id,
        "source": "Geoportal_PIG",
        "source_record_id": clean(row.get("ID")),
        "source_external_id": clean(row.get("Link")),
        "source_inventory_id": clean(row.get("Nr inw.")),
        "inferred_inventory_id": "",
        "source_name": clean(row.get("Nazwa")),
        "source_object_label": "",
        "observation_date": "",
        "source_data_date": clean(row.get("Stan na rok")),
        "method": "",
        "device": "",
        "x1992": decimal_text(row.get("X 1992")),
        "y1992": decimal_text(row.get("Y 1992")),
        "z": decimal_text(row.get("H (wg PIG)")),
        "lat_wgs84": decimal_text(row.get("B")),
        "lon_wgs84": decimal_text(row.get("L")),
        "accuracy_class": "nieokreslona",
        "estimated_accuracy_m": "",
        "verification_status": "",
        "verification_notes": "",
        "tags": f"import:{IMPORT_DATE};zrodlo:pig_geoportal",
        "match_status": match_status,
        "raw_json": source_json(row),
        "import_key": f"pig:{clean(row.get('ID'))}:location",
    }


def related_source_record(
    row: dict[str, str],
    relation_type: str,
    object_ids: list[str],
    note: str,
) -> dict[str, object]:
    return {
        "source": "Geoportal_PIG",
        "source_record_id": clean(row.get("ID")),
        "source_external_id": clean(row.get("Link")),
        "source_inventory_id": clean(row.get("Nr inw.")),
        "source_name": clean(row.get("Nazwa")),
        "relation_type": relation_type,
        "candidate_object_ids": ";".join(object_ids),
        "note": note,
        "x1992": decimal_text(row.get("X 1992")),
        "y1992": decimal_text(row.get("Y 1992")),
        "z": decimal_text(row.get("H (wg PIG)")),
        "lat_wgs84": decimal_text(row.get("B")),
        "lon_wgs84": decimal_text(row.get("L")),
        "raw_json": source_json(row),
    }


def observation_for_yaml(row: dict[str, object]) -> dict[str, Any]:
    return {
        "id": row["jktz_observation_id"],
        "source": row["source"],
        "source_record_id": row["source_record_id"],
        "source_inventory_id": row["source_inventory_id"],
        "inferred_inventory_id": row["inferred_inventory_id"],
        "source_name": row["source_name"],
        "source_object_label": row["source_object_label"],
        "observation_date": row["observation_date"],
        "source_data_date": row["source_data_date"],
        "method": row["method"],
        "device": row["device"],
        "coords": {
            "epsg2180": {"northing": row["x1992"], "easting": row["y1992"], "z": row["z"]},
            "wgs84": {"lat": row["lat_wgs84"], "lon": row["lon_wgs84"]},
        },
        "accuracy_class": row["accuracy_class"],
        "estimated_accuracy_m": row["estimated_accuracy_m"],
        "verification_status": row["verification_status"],
        "verification_notes": row["verification_notes"],
        "tags": row["tags"],
        "match_status": row["match_status"],
    }


def related_for_yaml(row: dict[str, object]) -> dict[str, Any]:
    return {
        "source": row["source"],
        "source_record_id": row["source_record_id"],
        "source_inventory_id": row["source_inventory_id"],
        "source_name": row["source_name"],
        "relation_type": row["relation_type"],
        "candidate_object_ids": list(filter(None, str(row["candidate_object_ids"]).split(";"))),
        "note": row["note"],
        "coords": {
            "epsg2180": {"northing": row["x1992"], "easting": row["y1992"], "z": row["z"]},
            "wgs84": {"lat": row["lat_wgs84"], "lon": row["lon_wgs84"]},
        },
    }


def build_registry(tpn_path: Path, pig_path: Path) -> dict[str, int]:
    tpn_rows = read_csv(tpn_path)
    pig_rows = read_csv(pig_path)

    existing_objects = existing_map(DATA_DIR / "obiekty.csv", "import_key", "jktz_object_id")
    existing_observations = existing_map(DATA_DIR / "pomiary_lokalizacji.csv", "import_key", "jktz_observation_id")
    object_gen = IdGenerator("JKTZ-OBJ-", 6, set(existing_objects.values()))
    observation_gen = IdGenerator("JKTZ-OBS-", 6, set(existing_observations.values()))

    cave_contexts = build_cave_contexts(tpn_rows, pig_rows)
    name_index = build_name_index(cave_contexts)

    objects: list[dict[str, object]] = []
    observations: list[dict[str, object]] = []
    related_records: list[dict[str, object]] = []
    identifiers: list[dict[str, object]] = []
    issues: list[dict[str, object]] = []
    observations_by_object: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    related_by_object: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    object_ids_by_inventory: defaultdict[str, list[str]] = defaultdict(list)
    object_by_id: dict[str, dict[str, object]] = {}

    for row_number, row in enumerate(tpn_rows, start=2):
        global_id = clean(row.get("GLOBALID"))
        source_inventory_id = clean(row.get("NR_INWENT"))
        canonical_inventory_id = source_inventory_id
        inferred_inventory_id = ""

        if not canonical_inventory_id:
            candidates = name_index.get(clean(row.get("NAZWA")).lower(), set())
            if len(candidates) == 1:
                canonical_inventory_id = next(iter(candidates))
                inferred_inventory_id = canonical_inventory_id

        import_key = f"tpn:{global_id}"
        object_id = existing_objects.get(import_key) or object_gen.next()
        observation_key = f"{import_key}:location"
        observation_id = existing_observations.get(observation_key) or observation_gen.next()
        label = clean(row.get("OTWÓR"))
        source_name = clean(row.get("NAZWA"))
        object_type = object_type_from_geneza(row.get("GENEZA"))
        display_name = f"{source_name}, {label}" if label else source_name
        cave_context = cave_contexts.get(canonical_inventory_id, {})

        if source_inventory_id:
            assignment_status = "explicit"
            review_status = "ok"
            notes = ""
        elif inferred_inventory_id:
            assignment_status = "inferred_by_unique_name"
            review_status = "needs_inventory_id_confirmation"
            notes = f"Brak NR_INWENT w TPN; kandydat po nazwie: {inferred_inventory_id}."
            issues.append(
                {
                    "issue_type": "tpn_missing_inventory_id_inferred",
                    "source": "TPN",
                    "source_record_id": global_id,
                    "object_id": object_id,
                    "inventory_id": inferred_inventory_id,
                    "name": source_name,
                    "detail": f"TPN row {row_number} nie ma NR_INWENT; kandydat po nazwie: {inferred_inventory_id}.",
                }
            )
        else:
            assignment_status = "missing"
            review_status = "needs_inventory_id"
            notes = "Brak NR_INWENT w zrodle TPN."
            issues.append(
                {
                    "issue_type": "tpn_missing_inventory_id",
                    "source": "TPN",
                    "source_record_id": global_id,
                    "object_id": object_id,
                    "inventory_id": "",
                    "name": source_name,
                    "detail": f"TPN row {row_number} nie ma NR_INWENT.",
                }
            )

        obs = tpn_observation(row, observation_id, object_id, inferred_inventory_id)
        observations.append(obs)
        observations_by_object[object_id].append(obs)

        obj = {
            "jktz_object_id": object_id,
            "object_type": object_type,
            "object_subtype": normalize_geneza(row.get("GENEZA")),
            "name": display_name,
            "source_name": source_name,
            "object_label": label,
            "cave_inventory_id": canonical_inventory_id,
            "cave_name": clean(cave_context.get("name")),
            "cave_assignment_status": assignment_status,
            "systems": cave_context.get("systems", []),
            "current_observation_id": observation_id,
            "current_source": "TPN",
            "current_x1992": obs["x1992"],
            "current_y1992": obs["y1992"],
            "current_z": obs["z"],
            "current_lat_wgs84": "",
            "current_lon_wgs84": "",
            "accuracy_class": obs["accuracy_class"],
            "verification_status": obs["verification_status"],
            "review_status": review_status,
            "notes": notes,
            "source_tpn_globalid": global_id,
            "import_key": import_key,
        }
        objects.append(obj)
        object_by_id[object_id] = obj
        if canonical_inventory_id:
            object_ids_by_inventory[canonical_inventory_id].append(object_id)

        identifiers.append(
            {
                "jktz_object_id": object_id,
                "source": "TPN",
                "identifier_type": "GLOBALID",
                "identifier_value": global_id,
                "scope": "object",
                "match_status": "source_object",
            }
        )
        if source_inventory_id:
            identifiers.append(
                {
                    "jktz_object_id": object_id,
                    "source": "TPN",
                    "identifier_type": "NR_INWENT",
                    "identifier_value": source_inventory_id,
                    "scope": "cave_context",
                    "match_status": "matched_inventory",
                }
            )

    for row in pig_rows:
        pig_id = clean(row.get("ID"))
        inventory_id = clean(row.get("Nr inw."))
        object_ids = object_ids_by_inventory.get(inventory_id, [])

        if is_cave_inventory(inventory_id) and len(object_ids) == 1:
            object_id = object_ids[0]
            observation_key = f"pig:{pig_id}:location"
            observation_id = existing_observations.get(observation_key) or observation_gen.next()
            obs = pig_observation(row, observation_id, object_id, "cave_single_object_assumed")
            observations.append(obs)
            observations_by_object[object_id].append(obs)
        elif is_cave_inventory(inventory_id) and object_ids:
            related = related_source_record(
                row,
                "cave_level_source_record",
                object_ids,
                "Rekord PIG/Geoportal dotyczy jaskini, nie konkretnego obiektu terenowego.",
            )
            related_records.append(related)
            for object_id in object_ids:
                related_by_object[object_id].append(related)
        elif is_cave_inventory(inventory_id):
            issues.append(
                {
                    "issue_type": "pig_cave_without_object",
                    "source": "Geoportal_PIG",
                    "source_record_id": pig_id,
                    "object_id": "",
                    "inventory_id": inventory_id,
                    "name": clean(row.get("Nazwa")),
                    "detail": "Rekord PIG/Geoportal nie ma odpowiadajacego obiektu TPN.",
                }
            )
        else:
            member_inventory_ids = extract_inventory_ids(clean(row.get("Inne nazwy")))
            candidate_object_ids = [
                object_id
                for member_inventory_id in member_inventory_ids
                for object_id in object_ids_by_inventory.get(member_inventory_id, [])
            ]
            if not candidate_object_ids:
                issues.append(
                    {
                        "issue_type": "pig_system_without_candidate_objects",
                        "source": "Geoportal_PIG",
                        "source_record_id": pig_id,
                        "object_id": "",
                        "inventory_id": inventory_id,
                        "name": clean(row.get("Nazwa")),
                        "detail": "Rekord PIG/Geoportal dotyczy systemu, ale importer nie znalazl obiektow kandydackich.",
                    }
                )
            related = related_source_record(
                row,
                "system_level_source_record",
                candidate_object_ids,
                "Rekord PIG/Geoportal dotyczy systemu/agregatu, nie konkretnego obiektu terenowego.",
            )
            related_records.append(related)
            for object_id in candidate_object_ids:
                related_by_object[object_id].append(related)

        if object_ids:
            for object_id in object_ids:
                identifiers.append(
                    {
                        "jktz_object_id": object_id,
                        "source": "Geoportal_PIG",
                        "identifier_type": "PIG_ID",
                        "identifier_value": pig_id,
                        "scope": "cave_context",
                        "match_status": "cave_single_object_assumed" if len(object_ids) == 1 else "cave_level_source_record",
                    }
                )

    write_outputs(
        objects,
        observations,
        related_records,
        identifiers,
        issues,
        observations_by_object,
        related_by_object,
        tpn_rows,
        pig_rows,
        cave_contexts,
    )
    return {
        "tpn_rows": len(tpn_rows),
        "pig_rows": len(pig_rows),
        "objects": len(objects),
        "object_observations": len(observations),
        "related_source_records": len(related_records),
        "issues": len(issues),
    }


def write_outputs(
    objects: list[dict[str, object]],
    observations: list[dict[str, object]],
    related_records: list[dict[str, object]],
    identifiers: list[dict[str, object]],
    issues: list[dict[str, object]],
    observations_by_object: defaultdict[str, list[dict[str, object]]],
    related_by_object: defaultdict[str, list[dict[str, object]]],
    tpn_rows: list[dict[str, str]],
    pig_rows: list[dict[str, str]],
    cave_contexts: dict[str, dict[str, object]],
) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DICT_DIR.mkdir(parents=True, exist_ok=True)
    OBJECTS_DIR.mkdir(parents=True, exist_ok=True)

    write_csv(
        DATA_DIR / "obiekty.csv",
        [
            "jktz_object_id",
            "object_type",
            "object_subtype",
            "name",
            "source_name",
            "object_label",
            "cave_inventory_id",
            "cave_name",
            "cave_assignment_status",
            "current_observation_id",
            "current_source",
            "current_x1992",
            "current_y1992",
            "current_z",
            "current_lat_wgs84",
            "current_lon_wgs84",
            "accuracy_class",
            "verification_status",
            "review_status",
            "notes",
            "source_tpn_globalid",
            "import_key",
        ],
        sorted(objects, key=lambda item: item["jktz_object_id"]),
    )
    write_csv(
        DATA_DIR / "pomiary_lokalizacji.csv",
        [
            "jktz_observation_id",
            "jktz_object_id",
            "source",
            "source_record_id",
            "source_external_id",
            "source_inventory_id",
            "inferred_inventory_id",
            "source_name",
            "source_object_label",
            "observation_date",
            "source_data_date",
            "method",
            "device",
            "x1992",
            "y1992",
            "z",
            "lat_wgs84",
            "lon_wgs84",
            "accuracy_class",
            "estimated_accuracy_m",
            "verification_status",
            "verification_notes",
            "tags",
            "match_status",
            "raw_json",
            "import_key",
        ],
        sorted(observations, key=lambda item: item["jktz_observation_id"]),
    )
    write_csv(
        DATA_DIR / "powiazane_rekordy_zrodel.csv",
        [
            "source",
            "source_record_id",
            "source_external_id",
            "source_inventory_id",
            "source_name",
            "relation_type",
            "candidate_object_ids",
            "note",
            "x1992",
            "y1992",
            "z",
            "lat_wgs84",
            "lon_wgs84",
            "raw_json",
        ],
        related_records,
    )
    write_csv(
        DATA_DIR / "identyfikatory_zrodel.csv",
        ["jktz_object_id", "source", "identifier_type", "identifier_value", "scope", "match_status"],
        sorted(
            {tuple(sorted(row.items())): row for row in identifiers}.values(),
            key=lambda item: (item["jktz_object_id"], item["source"], item["identifier_type"], item["identifier_value"]),
        ),
    )
    write_csv(
        DATA_DIR / "problemy_importu.csv",
        ["issue_type", "source", "source_record_id", "object_id", "inventory_id", "name", "detail"],
        issues,
    )
    write_csv(
        DICT_DIR / "klasy_dokladnosci.csv",
        ["accuracy_class", "label", "min_m_exclusive", "max_m_inclusive", "notes"],
        [
            {"accuracy_class": "do_0_10_m", "label": "do 0,10 m", "min_m_exclusive": 0, "max_m_inclusive": "0.10", "notes": ""},
            {"accuracy_class": "0_10_1_m", "label": "0,10-1 m", "min_m_exclusive": "0.10", "max_m_inclusive": 1, "notes": ""},
            {"accuracy_class": "1_5_m", "label": "1-5 m", "min_m_exclusive": 1, "max_m_inclusive": 5, "notes": ""},
            {"accuracy_class": "5_10_m", "label": "5-10 m", "min_m_exclusive": 5, "max_m_inclusive": 10, "notes": ""},
            {"accuracy_class": "10_30_m", "label": "10-30 m", "min_m_exclusive": 10, "max_m_inclusive": 30, "notes": ""},
            {"accuracy_class": "30_100_m", "label": "30-100 m", "min_m_exclusive": 30, "max_m_inclusive": 100, "notes": ""},
            {"accuracy_class": "ponad_100_m", "label": "powyzej 100 m", "min_m_exclusive": 100, "max_m_inclusive": "", "notes": ""},
            {"accuracy_class": "nieokreslona", "label": "nieokreslona", "min_m_exclusive": "", "max_m_inclusive": "", "notes": "Tymczasowe dla importow bez jawnej dokladnosci."},
        ],
    )
    write_csv(
        DICT_DIR / "zrodla.csv",
        ["source", "source_name", "current_location_priority", "scope", "notes"],
        [
            {"source": "JKTZ_GNSS", "source_name": "Wlasny pomiar GNSS JKTZ", "current_location_priority": 100, "scope": "object", "notes": "Docelowo najwyzszy priorytet po weryfikacji."},
            {"source": "TPN", "source_name": "Tatrzanski Park Narodowy - obiekty/otwory jaskin", "current_location_priority": 80, "scope": "object", "notes": "Na starcie uznane za lepsze od PIG/Geoportalu."},
            {"source": "Geoportal_PIG", "source_name": "PIG/Geoportal - dane jaskin", "current_location_priority": 50, "scope": "cave_or_system_context", "notes": "Do obserwacji obiektu trafia tylko przy jednoobiektowej jaskini; inaczej jako rekord powiazany."},
        ],
    )

    for obj in sorted(objects, key=lambda item: item["jktz_object_id"]):
        object_id = str(obj["jktz_object_id"])
        data = {
            "id": object_id,
            "type": obj["object_type"],
            "subtype": obj["object_subtype"],
            "name": obj["name"],
            "source_name": obj["source_name"],
            "label": obj["object_label"],
            "cave": {
                "inventory_id": obj["cave_inventory_id"],
                "name": obj["cave_name"],
                "assignment_status": obj["cave_assignment_status"],
            },
            "systems": obj["systems"],
            "source_ids": {"tpn_globalid": obj["source_tpn_globalid"]},
            "current_observation_id": obj["current_observation_id"],
            "accuracy_class": obj["accuracy_class"],
            "verification_status": obj["verification_status"],
            "review_status": obj["review_status"],
            "notes": obj["notes"],
            "observations": [observation_for_yaml(obs) for obs in observations_by_object.get(object_id, [])],
            "related_source_records": [related_for_yaml(row) for row in related_by_object.get(object_id, [])],
        }
        write_yaml(OBJECTS_DIR / f"{object_id}.yaml", data)

    write_report(tpn_rows, pig_rows, objects, observations, related_records, issues, cave_contexts)


def write_report(
    tpn_rows: list[dict[str, str]],
    pig_rows: list[dict[str, str]],
    objects: list[dict[str, object]],
    observations: list[dict[str, object]],
    related_records: list[dict[str, object]],
    issues: list[dict[str, object]],
    cave_contexts: dict[str, dict[str, object]],
) -> None:
    object_types = Counter(str(row["object_type"]) for row in objects)
    current_sources = Counter(str(row["current_source"]) for row in objects)
    observation_sources = Counter(str(row["source"]) for row in observations)
    issue_counts = Counter(str(row["issue_type"]) for row in issues)
    object_counts_by_inventory = Counter(str(row["cave_inventory_id"]) for row in objects if row["cave_inventory_id"])
    multi_object_caves = sorted(
        [
            (inventory_id, cave_contexts.get(inventory_id, {}).get("name", ""), count)
            for inventory_id, count in object_counts_by_inventory.items()
            if count > 1
        ],
        key=lambda item: item[0],
    )

    lines = [
        "# Raport importu lokalizacji",
        "",
        f"Data importu: {IMPORT_DATE}",
        "",
        "## Licznosci",
        "",
        f"- Rekordy TPN: {len(tpn_rows)}",
        f"- Rekordy PIG/Geoportal: {len(pig_rows)}",
        f"- Obiekty terenowe JKTZ: {len(objects)}",
        f"- Obserwacje przypisane do obiektow: {len(observations)}",
        f"- Rekordy zrodlowe powiazane kontekstowo: {len(related_records)}",
        "",
        "## Typy obiektow",
        "",
    ]
    for object_type, count in sorted(object_types.items()):
        lines.append(f"- {object_type}: {count}")

    lines.extend(["", "## Aktualne lokalizacje", ""])
    for source, count in sorted(current_sources.items()):
        lines.append(f"- {source}: {count}")

    lines.extend(["", "## Zrodla obserwacji przypisanych do obiektow", ""])
    for source, count in sorted(observation_sources.items()):
        lines.append(f"- {source}: {count}")

    lines.extend(["", "## Jaskinie z wieloma obiektami TPN", ""])
    if multi_object_caves:
        for inventory_id, name, count in multi_object_caves:
            lines.append(f"- {inventory_id} {name}: {count} obiekty")
    else:
        lines.append("- brak")

    lines.extend(["", "## Niejednoznacznosci i braki", ""])
    if issue_counts:
        for issue_type, count in sorted(issue_counts.items()):
            lines.append(f"- {issue_type}: {count}")
    else:
        lines.append("- brak")

    lines.extend(
        [
            "",
            "PIG/Geoportal trafia do obserwacji obiektu tylko wtedy, gdy numer inwentarzowy ma jeden obiekt TPN. Przy jaskiniach wielootworowych i systemach zostaje w `powiazane_rekordy_zrodel.csv` oraz `related_source_records` w YAML.",
            "",
        ]
    )
    (ROOT / "raport_importu.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tpn", type=Path, default=DEFAULT_TPN)
    parser.add_argument("--pig", type=Path, default=DEFAULT_PIG)
    args = parser.parse_args()

    summary = build_registry(args.tpn, args.pig)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
