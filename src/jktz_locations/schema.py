"""Shared constants for the location registry schema."""

from __future__ import annotations

OBJECT_ID_PREFIX = "JKTZ-OBJ-"
OBSERVATION_ID_PREFIX = "JKTZ-OBS-"

ALLOWED_OBJECT_TYPES = {
    "obiekt_terenowy",
    "otwor_jaskini",
    "otwor_jaskini_lub_sztolnia",
    "ponor",
    "sztolnia",
    "wywierzysko",
}

ALLOWED_CAVE_ASSIGNMENT_STATUSES = {
    "explicit",
    "inferred_by_unique_name",
    "missing",
}

ALLOWED_REVIEW_STATUSES = {
    "ok",
    "needs_inventory_id",
    "needs_inventory_id_confirmation",
    "needs_review",
}

ALLOWED_VERIFICATION_STATUSES = {
    "",
    "niezweryfikowane",
    "odrzucone",
    "robocze",
    "zweryfikowane",
}

ALLOWED_RELATION_TYPES = {
    "cave_level_source_record",
    "system_level_source_record",
}

OBJECT_HEADERS = [
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
]

OBSERVATION_HEADERS = [
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
]

RELATED_RECORD_HEADERS = [
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
]

IDENTIFIER_HEADERS = [
    "jktz_object_id",
    "source",
    "identifier_type",
    "identifier_value",
    "scope",
    "match_status",
]

IMPORT_ISSUE_HEADERS = [
    "issue_type",
    "source",
    "source_record_id",
    "object_id",
    "inventory_id",
    "name",
    "detail",
]

CSV_HEADERS = {
    "obiekty.csv": OBJECT_HEADERS,
    "pomiary_lokalizacji.csv": OBSERVATION_HEADERS,
    "powiazane_rekordy_zrodel.csv": RELATED_RECORD_HEADERS,
    "identyfikatory_zrodel.csv": IDENTIFIER_HEADERS,
    "problemy_importu.csv": IMPORT_ISSUE_HEADERS,
}

CURRENT_EXPORT_HEADERS = [
    "jktz_object_id",
    "object_type",
    "name",
    "label",
    "cave_inventory_id",
    "cave_name",
    "current_observation_id",
    "source",
    "observation_date",
    "method",
    "x1992",
    "y1992",
    "z",
    "lat_wgs84",
    "lon_wgs84",
    "accuracy_class",
    "estimated_accuracy_m",
    "verification_status",
    "review_status",
    "notes",
]

# Broad Western Tatra project bounds. Values outside these ranges are warnings, not schema errors.
EPSG2180_NORTHING_RANGE = (120_000.0, 180_000.0)
EPSG2180_EASTING_RANGE = (530_000.0, 610_000.0)
WGS84_LAT_RANGE = (49.0, 49.4)
WGS84_LON_RANGE = (19.5, 20.2)
ELEVATION_RANGE = (700.0, 2_700.0)
