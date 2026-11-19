"""Interpret survey identity fields independently of the SRV header parser."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from jktz.gps_catalog import CAVE_ID, OBJECT_ID
from jktz.metadata.errors import MetadataError

_CAVE_NAME = re.compile(r"[ -~]+")


@dataclass(frozen=True)
class ObjectRef:
    station_id: str
    object_id: str


@dataclass(frozen=True)
class SurveyIdentity:
    kind: Literal["underground", "surface"]
    cave_id: str | None
    object_refs: tuple[ObjectRef, ...]


def parse_identity(single: dict[str, str], repeated: dict[str, list[str]]) -> SurveyIdentity:
    """Check the identity fields and preserve the order of explicit references."""
    for field in ("SURVEY_KIND", "CAVE_ID", "CAVE_NAME"):
        if field in repeated:
            raise MetadataError(f"{field} is a single field")
    if "OBJECT_REF" in single:
        raise MetadataError("OBJECT_REF is a repeatable field")

    kind = single.get("SURVEY_KIND")
    if kind not in ("underground", "surface"):
        raise MetadataError(f"SURVEY_KIND must be underground or surface, got {kind!r}")

    if kind == "underground":
        cave_id = single.get("CAVE_ID", "")
        if CAVE_ID.fullmatch(cave_id) is None:
            raise MetadataError(f"CAVE_ID must be one GPS cave ID, got {cave_id!r}")
        name = single.get("CAVE_NAME", "")
        if not name.strip() or _CAVE_NAME.fullmatch(name) is None:
            raise MetadataError(f"CAVE_NAME must be a nonempty ASCII description, got {name!r}")
        return SurveyIdentity(kind, cave_id, _parse_refs(repeated.get("OBJECT_REF", [])))

    for field in ("CAVE_ID", "CAVE_NAME"):
        if field in single:
            raise MetadataError(f"{field} is forbidden for surface surveys, got {single[field]!r}")
    refs = _parse_refs(repeated.get("OBJECT_REF", []))
    if not refs:
        raise MetadataError("OBJECT_REF is required for surface surveys")
    return SurveyIdentity(kind, None, refs)


def _parse_refs(values: list[str]) -> tuple[ObjectRef, ...]:
    refs = []
    by_station: dict[str, str] = {}
    for value in values:
        if value.count("=") != 1:
            raise MetadataError(f"OBJECT_REF must be station=object_id, got {value!r}")
        station_id, object_id = value.split("=")
        _check_station_id(station_id)
        if OBJECT_ID.fullmatch(object_id) is None:
            raise MetadataError(f"OBJECT_REF {station_id!r} has invalid object_id {object_id!r}")

        # Walls omits leading empty prefix levels when displaying a station name.
        station_label = station_id.lstrip(":")
        if previous := by_station.get(station_label):
            if previous == object_id:
                raise MetadataError(f"OBJECT_REF duplicate for {station_label}={object_id}")
            raise MetadataError(f"OBJECT_REF {station_label} names both {previous} and {object_id}")
        by_station[station_label] = object_id
        refs.append(ObjectRef(station_id, object_id))
    return tuple(refs)


def _check_station_id(station_id: str) -> None:
    prefix, _, name = station_id.rpartition(":")
    if (
        not 1 <= len(name) <= 8
        or name in {"-", "--"}
        or len(prefix) > 127
        or station_id.count(":") > 3
        or not station_id.isascii()
        or not station_id.isprintable()
        or any(character in station_id for character in ' ,;#"')
    ):
        raise MetadataError(f"OBJECT_REF has invalid Walls station name {station_id!r}")
