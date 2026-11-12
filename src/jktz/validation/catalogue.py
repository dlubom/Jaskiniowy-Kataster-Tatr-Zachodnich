"""Check survey references against the GPS catalogue and compiled stations."""

from __future__ import annotations

import csv
import re
import tempfile
from collections import defaultdict
from collections.abc import Mapping
from pathlib import Path

from jktz.entrances.render import GPS_FIX_RE, RenderError, _parse_gps_fix_args
from jktz.exports import tools
from jktz.gps_catalog import Catalogue, GpsSnapshot, effective_cave_id, read_catalogue
from jktz.metadata.identity import ObjectRef, SurveyIdentity
from jktz.reporting import CheckFailed
from jktz.validation._utils import active_lines

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
        if error := _reference_error(ObjectRef(station_id, object_id), None, catalogue):
            errors.append(f"OTWORY.SRV.j2: {error}")
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


def _fix_binding(station_id: str, object_id: str, *, suffix: str = "") -> ObjectRef:
    if not isinstance(station_id, str) or not isinstance(object_id, str):
        raise RenderError("gps_fix station_id and object_id must be strings")
    return ObjectRef(station_id.lstrip(":"), object_id)


def _entrance_bindings(template: Path) -> dict[str, str]:
    bindings: dict[str, str] = {}
    text = template.read_text(encoding="utf-8")
    lines = text.splitlines()
    for number, _ in active_lines(text):
        # Match on the original line: a quoted suffix can contain a semicolon.
        if not (match := GPS_FIX_RE.match(lines[number - 1].lstrip())):
            continue
        args, kwargs = _parse_gps_fix_args(match.group(1))
        try:
            ref = _fix_binding(*args, **kwargs)
        except TypeError as exc:
            raise RenderError(f"Invalid gps_fix arguments: {match.group(0)}") from exc
        previous = bindings.setdefault(ref.station_id, ref.object_id)
        if previous != ref.object_id:
            raise RenderError(
                f"{template}: {ref.station_id}: conflicting object_ids {previous}, {ref.object_id}"
            )
    return bindings


def check_catalogue(
    snapshot: GpsSnapshot, template: Path, identities: Mapping[Path, SurveyIdentity]
) -> None:
    """Check the catalogue and all claimed station/object pairs before compiling."""
    try:
        catalogue = read_catalogue(snapshot)
        bindings = _entrance_bindings(template)
    except (OSError, ValueError) as exc:
        raise CheckFailed(f"ERROR: GPS catalogue check failed: {exc}") from exc
    if errors := validate_identities(identities, catalogue, bindings):
        raise CheckFailed("ERROR: GPS catalogue references:\n" + "\n".join(errors))


def read_station_names(three_d: Path) -> set[str]:
    """Export all named stations using the pinned Survex CSV format."""
    with tempfile.TemporaryDirectory(prefix="jktz-stations-") as directory:
        output = Path(directory) / "stations.csv"
        tools.survexport(["--station-names", "--csv", str(three_d.resolve()), str(output)])
        with output.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            if not reader.fieldnames or "Station Name" not in reader.fieldnames:
                raise ValueError(f"{three_d}: survexport CSV lacks the Station Name column")
            return {row["Station Name"] for row in reader if row["Station Name"]}


def check_compiled_references(three_d: Path, identities: Mapping[Path, SurveyIdentity]) -> None:
    try:
        stations = read_station_names(three_d)
    except (OSError, ValueError) as exc:
        raise CheckFailed(f"ERROR: cannot read compiled stations: {exc}") from exc
    if errors := check_reference_stations(identities, stations):
        raise CheckFailed("ERROR: compiled station references:\n" + "\n".join(errors))
