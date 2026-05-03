from __future__ import annotations

import csv
from pathlib import Path

from jktz_locations.exporters import collect_current_locations, export_current_locations
from jktz_locations.schema import (
    IDENTIFIER_HEADERS,
    IMPORT_ISSUE_HEADERS,
    OBJECT_HEADERS,
    OBSERVATION_HEADERS,
    RELATED_RECORD_HEADERS,
)
from jktz_locations.validation import validate_locations


def test_minimal_registry_validates(tmp_path: Path) -> None:
    root = _minimal_registry(tmp_path)

    report = validate_locations(root)

    assert report.errors == []
    assert report.object_count == 1
    assert report.observation_count == 1


def test_current_observation_must_exist(tmp_path: Path) -> None:
    root = _minimal_registry(tmp_path, current_observation_id="JKTZ-OBS-999999")

    report = validate_locations(root)

    assert any(finding.code == "current_observation_missing" for finding in report.errors)


def test_collect_and_export_current_locations(tmp_path: Path) -> None:
    root = _minimal_registry(tmp_path)
    out_dir = tmp_path / "out"

    rows = collect_current_locations(root)
    written = export_current_locations(root, out_dir, ["csv", "gpx", "xlsx", "shp"])

    assert rows[0]["jktz_object_id"] == "JKTZ-OBJ-000001"
    assert rows[0]["lat_wgs84"]
    assert (out_dir / "aktualne_lokalizacje.csv") in written
    assert (out_dir / "aktualne_lokalizacje.gpx") in written
    assert (out_dir / "aktualne_lokalizacje.xlsx") in written
    assert (out_dir / "aktualne_lokalizacje_2180.shp") in written


def _minimal_registry(tmp_path: Path, current_observation_id: str = "JKTZ-OBS-000001") -> Path:
    root = tmp_path / "Lokalizacje"
    (root / "rejestr" / "obiekty").mkdir(parents=True)
    (root / "dane").mkdir()
    (root / "slowniki").mkdir()

    _write_rows(
        root / "slowniki" / "zrodla.csv",
        ["source", "source_name", "current_location_priority", "scope", "notes"],
        [
            {
                "source": "JKTZ_GNSS",
                "source_name": "GNSS",
                "current_location_priority": "100",
                "scope": "object",
                "notes": "",
            }
        ],
    )
    _write_rows(
        root / "slowniki" / "klasy_dokladnosci.csv",
        ["accuracy_class", "label", "min_m_exclusive", "max_m_inclusive", "notes"],
        [
            {
                "accuracy_class": "0_10_1_m",
                "label": "0.10-1 m",
                "min_m_exclusive": "0.10",
                "max_m_inclusive": "1",
                "notes": "",
            }
        ],
    )

    (root / "rejestr" / "obiekty" / "JKTZ-OBJ-000001.yaml").write_text(
        f"""
id: "JKTZ-OBJ-000001"
type: "otwor_jaskini"
name: "Testowy otwor"
label: "A"
cave:
  inventory_id: "T.X-00.01"
  name: "Jaskinia Testowa"
  assignment_status: "explicit"
systems: []
source_ids: {{}}
current_observation_id: "{current_observation_id}"
accuracy_class: "0_10_1_m"
verification_status: "robocze"
review_status: "ok"
notes: ""
observations:
  - id: "JKTZ-OBS-000001"
    source: "JKTZ_GNSS"
    observation_date: "2026-05-01"
    source_data_date: "2026-05-01"
    method: "GNSS RTK"
    device: "test"
    coords:
      epsg2180:
        northing: "152971.36"
        easting: "562235.67"
        z: "1297.37"
      wgs84:
        lat: ""
        lon: ""
    accuracy_class: "0_10_1_m"
    estimated_accuracy_m: "0.5"
    verification_status: "robocze"
    verification_notes: ""
    tags: "teren;rtk"
    match_status: "source_object"
related_source_records: []
""".lstrip(),
        encoding="utf-8",
    )

    _write_rows(
        root / "dane" / "obiekty.csv",
        OBJECT_HEADERS,
        [
            {
                "jktz_object_id": "JKTZ-OBJ-000001",
                "object_type": "otwor_jaskini",
                "object_subtype": "jaskinia",
                "name": "Testowy otwor",
                "source_name": "Testowy otwor",
                "object_label": "A",
                "cave_inventory_id": "T.X-00.01",
                "cave_name": "Jaskinia Testowa",
                "cave_assignment_status": "explicit",
                "current_observation_id": current_observation_id,
                "current_source": "JKTZ_GNSS",
                "current_x1992": "152971.36",
                "current_y1992": "562235.67",
                "current_z": "1297.37",
                "current_lat_wgs84": "",
                "current_lon_wgs84": "",
                "accuracy_class": "0_10_1_m",
                "verification_status": "robocze",
                "review_status": "ok",
                "notes": "",
                "source_tpn_globalid": "",
                "import_key": "test",
            }
        ],
    )
    _write_rows(
        root / "dane" / "pomiary_lokalizacji.csv",
        OBSERVATION_HEADERS,
        [
            {
                "jktz_observation_id": "JKTZ-OBS-000001",
                "jktz_object_id": "JKTZ-OBJ-000001",
                "source": "JKTZ_GNSS",
                "source_record_id": "",
                "source_external_id": "",
                "source_inventory_id": "T.X-00.01",
                "inferred_inventory_id": "",
                "source_name": "Testowy otwor",
                "source_object_label": "A",
                "observation_date": "2026-05-01",
                "source_data_date": "2026-05-01",
                "method": "GNSS RTK",
                "device": "test",
                "x1992": "152971.36",
                "y1992": "562235.67",
                "z": "1297.37",
                "lat_wgs84": "",
                "lon_wgs84": "",
                "accuracy_class": "0_10_1_m",
                "estimated_accuracy_m": "0.5",
                "verification_status": "robocze",
                "verification_notes": "",
                "tags": "teren;rtk",
                "match_status": "source_object",
                "raw_json": "{}",
                "import_key": "test:obs",
            }
        ],
    )
    _write_rows(root / "dane" / "powiazane_rekordy_zrodel.csv", RELATED_RECORD_HEADERS, [])
    _write_rows(root / "dane" / "identyfikatory_zrodel.csv", IDENTIFIER_HEADERS, [])
    _write_rows(root / "dane" / "problemy_importu.csv", IMPORT_ISSUE_HEADERS, [])
    return root


def _write_rows(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
