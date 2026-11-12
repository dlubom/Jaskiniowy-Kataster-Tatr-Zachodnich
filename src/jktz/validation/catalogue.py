"""Check survey references against the GPS catalogue and compiled stations."""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Mapping
from pathlib import Path

from jktz.gps_catalog import Catalogue, effective_cave_id
from jktz.metadata.identity import ObjectRef, SurveyIdentity

_SURVEX_EMPTY_PREFIX = re.compile(r"(?<=:) (?=:)")


def validate_identities(
    identities: Mapping[Path, SurveyIdentity],
    catalogue: Catalogue,
    entrance_bindings: Mapping[str, str],
) -> list[str]:
    """Validate catalogue links and compare station bindings across all sources."""
    errors: list[str] = []
    bindings: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for station_id, object_id in entrance_bindings.items():
        bindings[station_id.lstrip(":")].add((object_id, "OTWORY.SRV.j2"))

    for path, identity in identities.items():
        source = path.as_posix()
        cave_id = _terminal_survey_cave(identity.cave_id, source, catalogue, errors)
        for ref in identity.object_refs:
            bindings[ref.station_id.lstrip(":")].add((ref.object_id, source))
            if error := _reference_error(ref, cave_id, catalogue):
                errors.append(f"{source}: {error}")

    for station_id, claims in bindings.items():
        if len({object_id for object_id, _ in claims}) > 1:
            sources = ", ".join(f"{object_id} ({source})" for object_id, source in sorted(claims))
            errors.append(f"OBJECT_REF {station_id}: conflicting object_ids {sources}")
    return sorted(errors)


def _terminal_survey_cave(
    cave_id: str | None, source: str, catalogue: Catalogue, errors: list[str]
) -> str | None:
    if cave_id is None:
        return None
    try:
        terminal_id = effective_cave_id(cave_id, catalogue)
    except ValueError as exc:
        errors.append(f"{source}: CAVE_ID {cave_id}: {exc}")
        return None
    if terminal_id != cave_id:
        errors.append(f"{source}: CAVE_ID {cave_id} must be terminal cave_id {terminal_id}")
    return terminal_id


def _reference_error(ref: ObjectRef, cave_id: str | None, catalogue: Catalogue) -> str | None:
    label = f"OBJECT_REF {ref.station_id}={ref.object_id}"
    obj = catalogue.objects.get(ref.object_id)
    if obj is None:
        return f"{label}: unknown object_id"
    if obj.cave_id is None:
        return f"{label}: object has no cave_id"
    try:
        terminal_id = effective_cave_id(obj.cave_id, catalogue)
    except ValueError as exc:
        return f"{label}: {exc}"
    if cave_id is not None and terminal_id != cave_id:
        return (
            f"{label}: object cave_id {obj.cave_id} resolves to {terminal_id}, "
            f"but survey CAVE_ID resolves to {cave_id}"
        )
    return None


def check_reference_stations(
    identities: Mapping[Path, SurveyIdentity], station_names: set[str]
) -> list[str]:
    """Compare full Walls labels to compiler output, preserving case."""
    # Survex's walls.rst documents the space placeholder for empty prefix levels.
    names = {_SURVEX_EMPTY_PREFIX.sub("", name) for name in station_names}
    return sorted(
        f"{path.as_posix()}: OBJECT_REF {ref.station_id}={ref.object_id}: "
        "station is missing from compiler output"
        for path, identity in identities.items()
        for ref in identity.object_refs
        if ref.station_id.lstrip(":") not in names
    )
