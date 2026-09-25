"""Prepare lossless source data and an auditable P03 measurement report in memory.

No file writes, name conversion, date inference, declination application or
exports happen here. A plan is pinned to the exact input bytes, not a filename.
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from importlib.metadata import version

from jktz.pockettopo.averaging import (
    average_readings,
    normalize_reading,
    validate_min_resultant,
)
from jktz.pockettopo.grouping import (
    Exclusion,
    RecordGroup,
    RepeatConfirmation,
    make_groups,
    shot_kind,
    shot_problem,
)
from jktz.pockettopo.model import Drawing, Shot, TopFile, Trip, XSection
from jktz.pockettopo.parser import DEFAULT_LIMITS, ParseLimits, parse_bytes


@dataclass(frozen=True)
class ProcessingPlan:
    source_sha256: str
    confirmations: tuple[RepeatConfirmation, ...] = ()
    exclusions: tuple[Exclusion, ...] = ()


def _source_document(source: TopFile, provenance: dict) -> dict:
    records = asdict(source)
    # Element.kind is a ClassVar, deliberately absent from dataclasses.asdict.
    for name in ("outline", "sideview"):
        for record, element in zip(records[name]["elements"], getattr(source, name).elements):
            record["kind"] = element.kind
    return {"schema_version": 1, "provenance": dict(provenance), "records": records}


def _station_map(source: TopFile) -> list[dict]:
    ids = [station for shot in source.shots for station in (shot.from_id, shot.to_id)]
    ids.extend(reference.station for reference in source.references)
    for drawing in (source.outline, source.sideview):
        ids.extend(item.station for item in drawing.elements if isinstance(item, XSection))
    return [
        {
            "raw": station.raw,
            "kind": station.kind,
            "source_text": station.text,
            "walls_name": None,
            "survex_name": None,
            "status": "target_mapping_deferred_p04",
        }
        for station in dict.fromkeys(ids)
        if station.text is not None
    ]


def _trip_report(index: int, trip: Trip) -> dict:
    explicit = trip.declination_mode == "explicit"
    return {
        "index": index,
        "source_ticks": trip.ticks,
        "comment": trip.comment,
        "date_reliability": "unverified_device_clock",
        "established_date": None,
        "date_evidence": None,
        "used_date": None,
        "declination": {
            "source_raw": trip.declination_raw,
            "mode": trip.declination_mode,
            "stored_degrees": trip.declination_raw * 360 / 65536 if explicit else None,
            "applied_degrees": None,
            "status": "not_applied_p03" if explicit else "unresolved_auto",
        },
    }


def _drawing_report(drawing: Drawing) -> dict:
    return {
        "elements": len(drawing.elements),
        "status": "retained_not_exported" if drawing.elements else "empty",
        "mapping_applied": False,
    }


def _group_warnings(shots: tuple[Shot, ...], kind: str) -> list[str]:
    warnings = []
    if any(shot.trip_index == -1 for shot in shots):
        warnings.append("missing_trip")
    if any(abs(shot.inclination_raw) == 16384 for shot in shots):
        warnings.append("vertical_azimuth_not_geometrically_determined")
    if len({shot.flipped for shot in shots}) > 1:
        warnings.append("mixed_flip_preserved_for_drawing_review")
    if kind == "zero_link":
        warnings.append("zero_link_angles_have_no_geometric_effect")
    return warnings


def _measurement_group(
    source: TopFile,
    group: RecordGroup,
    group_index: int,
    excluded: dict[int, str],
    min_resultant: float,
) -> dict:
    shots = tuple(source.shots[index] for index in group.indices)
    first = shots[0]
    kind = shot_kind(first)
    problem = shot_problem(first)
    exclusion = excluded.get(group.indices[0])
    result = {
        "id": group_index,
        "source_indices": group.indices,
        "confirmation_evidence": group.evidence,
        "kind": kind,
        "trip_index": first.trip_index,
        "from_raw": first.from_id.raw,
        "to_raw": first.to_id.raw,
        "status": "ready",
        "reason": None,
        "normalized_readings": [],
        "average": None,
        "warnings": _group_warnings(shots, kind),
    }
    if exclusion is not None:
        result.update(status="excluded", reason=exclusion)
        return result
    if problem is not None:
        result.update(status="invalid", reason=problem)
        return result
    # A splay stored with undefined FROM is oriented from its known station.
    reverse_splay = first.from_id.text is None
    readings = tuple(
        normalize_reading(shot, reverse=reverse_splay or shot.from_id != first.from_id)
        for shot in shots
    )
    if reverse_splay:
        result.update(from_raw=first.to_id.raw, to_raw=first.from_id.raw)
    result["normalized_readings"] = [
        {"source_index": index, **asdict(reading)}
        for index, reading in zip(group.indices, readings)
    ]
    mean = average_readings(readings, min_resultant=min_resultant)
    result["average"] = asdict(mean)
    if mean.azimuth_deg is None:
        result.update(status="unresolved", reason="undefined_circular_mean")
    return result


def _record_trace(source: TopFile, groups: list[dict]) -> list[dict]:
    trace = []
    for group in groups:
        for index in group["source_indices"]:
            shot = source.shots[index]
            disposition = group["status"]
            reason = group["reason"]
            if disposition == "ready":
                if len(group["source_indices"]) > 1:
                    disposition, reason = "averaged_member", "explicit_repeat_confirmation"
                else:
                    disposition, reason = "retained_single", "not_averaged"
            trace.append(
                {
                    "source_index": index,
                    "group_id": group["id"],
                    "disposition": disposition,
                    "reason": reason,
                    "comment": shot.comment,
                    "flags": shot.flags,
                    "flipped": shot.flipped,
                    "roll_raw": shot.roll_raw,
                }
            )
    return trace


def prepare_conversion(
    data: bytes,
    *,
    plan: ProcessingPlan | None = None,
    min_resultant: float = 1e-12,
    limits: ParseLimits = DEFAULT_LIMITS,
) -> tuple[dict, dict]:
    """Return (source document, report) or raise without producing partial output.

    Indices are zero-based source shot indices. Explicit confirmations are the
    caller's documented evidence, not something inferred from station names.
    All unconfirmed readings stay separate. ``ready`` describes D/A/V arithmetic
    only; even such groups still need the P04 export/correction/name policies.
    """
    validate_min_resultant(min_resultant)
    sha256 = hashlib.sha256(data).hexdigest()
    if plan is None:
        plan = ProcessingPlan(sha256)
    if plan.source_sha256 != sha256:
        raise ValueError("Processing plan source_sha256 does not match input bytes")
    source = parse_bytes(data, limits=limits)
    grouped = make_groups(source, plan.confirmations, plan.exclusions)
    excluded = {item.index: item.reason for item in plan.exclusions}
    groups = [
        _measurement_group(source, group, index, excluded, min_resultant)
        for index, group in enumerate(grouped)
    ]
    provenance = {
        "sha256": sha256,
        "bytes": len(data),
        "input_format": "PocketTopo v3",
        "tool": "jktz-release-tools",
        "tool_version": version("jktz-release-tools"),
        "algorithm_version": "p03-1",
    }
    trace = _record_trace(source, groups)
    report = {
        "schema_version": 1,
        "stage": "P03",
        "provenance": dict(provenance),
        "settings": {
            "index_base": 0,
            "repeat_policy": "explicit_source_pinned_confirmation_only",
            "min_resultant": min_resultant,
            "ambiguity_rule": "resultant_length <= min_resultant",
            "distance_mean": "arithmetic",
            "azimuth_mean": "circular_fsum",
            "inclination_mean": "signed_arithmetic_after_direction_normalization",
            "outlier_removal": False,
            "declination_applied": False,
            "date_inference": False,
            "crs_assumed": None,
        },
        "plan": asdict(plan),
        "groups": groups,
        "record_trace": trace,
        "station_map": _station_map(source),
        "trips": [_trip_report(index, trip) for index, trip in enumerate(source.trips)],
        "references": {
            "count": len(source.references),
            "crs": None,
            "status": "retained_only_crs_unknown",
            "active_fixes": 0,
        },
        "drawings": {
            "outline": _drawing_report(source.outline),
            "sideview": _drawing_report(source.sideview),
        },
        "completeness": {
            "source_decode": "complete",
            "source_shots": len(source.shots),
            "traced_shots": len(trace),
            "ready_measurements": sum(group["status"] == "ready" for group in groups),
            "held_shots": sum(
                row["disposition"] in {"excluded", "invalid", "unresolved"} for row in trace
            ),
            "exports_created": False,
            "conversion_complete": False,
        },
        "limitations": [
            "Device dates are unverified; no date-derived correction was applied.",
            "Stored explicit declinations are retained, not validated or applied in P03.",
            "Auto declination and reference CRS need independent evidence.",
            "Target station names, survey and drawing exports remain P04-P06.",
        ],
    }
    return _source_document(source, provenance), report
