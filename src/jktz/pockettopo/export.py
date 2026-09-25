"""Auditable, in-memory P04 Walls and Survex export; no files or inferred fixes."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass

from jktz.pockettopo.export_policy import (
    CorrectionPolicy,
    map_station_names,
    resolve_corrections,
)
from jktz.pockettopo.parser import DEFAULT_LIMITS, ParseLimits
from jktz.pockettopo.report import ProcessingPlan, prepare_conversion


@dataclass(frozen=True)
class SurveyExport:
    source_document: dict
    report: dict
    srv: str
    svx: str


def _comment(label: str, value: object) -> list[str]:
    # Fixed ASCII comment lines also contain untrusted newlines/directives safely.
    encoded = json.dumps(value, ensure_ascii=True, allow_nan=False, separators=(",", ":"))
    chunks = [encoded[index : index + 160] for index in range(0, len(encoded), 160)]
    return [f"; {label} {index + 1}/{len(chunks)} {chunk}" for index, chunk in enumerate(chunks)]


def _number(value: float) -> str:
    # Fixed decimals avoid exponent syntax and preserve source angular resolution.
    result = f"{value:.12f}".rstrip("0").rstrip(".")
    return "0" if result == "-0" else result


def _headers(source: dict, report: dict) -> tuple[list[str], list[str]]:
    comments = [
        "; PocketTopo P04 survey export. See source document and conversion report.",
        "; Device dates are unverified. No dates, CRS or reference fixes are inferred.",
    ]
    comments += _comment("provenance", report["provenance"])
    for station in report["station_map"]:
        comments += _comment("station", station)
    for trip in report["trips"]:
        comments += _comment("trip", trip)
    for index, reference in enumerate(source["records"]["references"]):
        comments += _comment("reference_not_fixed", {"index": index, **reference})
    srv = comments + ["#units reset meters order=DAV A=D V=D case=mixed", ""]
    svx = comments + [
        "*begin",
        "*case preserve",
        "*truncate off",
        "*set separator :",
        "*set names ._-",
        "*units tape metres",
        "*units compass clino degrees",
        "*calibrate tape 0",
        "*calibrate compass clino 0",
        "*data normal from to tape compass clino",
        "",
    ]
    return srv, svx


def _decision(group: dict, corrections: dict[int, dict]) -> dict:
    result = {
        "status": "held",
        "reason": group["reason"],
        "declination_degrees": None,
        "correction_provenance": None,
        "correction_evidence": None,
        "srv_line": None,
        "svx_line": None,
    }
    if group["status"] != "ready":
        return result
    if group["kind"] == "zero_link":
        result.update(status="exported", reason="zero_link_no_angular_correction")
        return result
    correction = corrections[group["trip_index"]]
    if correction["degrees"] is None:
        result["reason"] = correction["reason"]
        return result
    result.update(
        status="exported",
        reason="explicit_correction",
        declination_degrees=correction["degrees"],
        correction_provenance=correction["provenance"],
        correction_evidence=correction["evidence"],
    )
    return result


def _emit_group(group: dict, stations: dict[int, dict], srv: list[str], svx: list[str]) -> None:
    decision = group["export"]
    if decision["status"] != "exported":
        return
    start = stations[group["from_raw"]]
    if group["kind"] == "zero_link":
        end = stations[group["to_raw"]]
        srv.append(f"{start['walls_name']}\t{end['walls_name']}\t0\t0\t0")
        svx.append(f"*equate {start['survex_name']} {end['survex_name']}")
    else:
        degrees = _number(decision["declination_degrees"])
        srv.append(f"#units DECL={degrees}")
        svx.append(f"*declination {degrees} degrees")
        mean = group["average"]
        values = "\t".join(
            _number(mean[key]) for key in ("distance_m", "azimuth_deg", "inclination_deg")
        )
        if group["kind"] == "splay":
            walls_end, survex_end = "-", "::"
        else:
            end = stations[group["to_raw"]]
            walls_end, survex_end = end["walls_name"], end["survex_name"]
        srv.append(f"{start['walls_name']}\t{walls_end}\t{values}")
        svx.append(f"{start['survex_name']}\t{survex_end}\t{values}")
    decision.update(srv_line=len(srv), svx_line=len(svx))


def _update_trips(report: dict, corrections: dict[int, dict]) -> None:
    applied_trips = {
        group["trip_index"]
        for group in report["groups"]
        if group["export"]["declination_degrees"] is not None
    }
    for trip in report["trips"]:
        correction = corrections[trip["index"]]
        applied = trip["index"] in applied_trips
        trip["declination"].update(
            selected_degrees=correction["degrees"],
            applied_degrees=correction["degrees"] if applied else None,
            status="applied" if applied else "not_applied",
            provenance=correction["provenance"],
            evidence=correction["evidence"],
            unresolved_reason=correction["reason"],
        )


def _finish_report(report: dict) -> None:
    by_id = {group["id"]: group["export"] for group in report["groups"]}
    for row in report["record_trace"]:
        row["export"] = dict(by_id[row["group_id"]])
    active = [group for group in report["groups"] if group["export"]["status"] == "exported"]
    exported = sum(len(group["source_indices"]) for group in active)
    held = report["completeness"]["source_shots"] - exported
    report["completeness"].update(
        exported_measurements=len(active),
        exported_source_shots=exported,
        held_shots=held,
        measurement_export_complete=held == 0,
        exports_created=True,
        survey_texts_created=True,
        conversion_complete=False,
    )
    geometry_status = "empty"
    if active:
        geometry_status = (
            "nonempty"
            if any(group["kind"] != "zero_link" for group in active)
            else "constraints_only"
        )
    report["exports"] = {
        "srv": {"status": "created"},
        "svx": {"status": "created", "minimum_version": "1.4.12"},
        "active_measurements": len(active),
        "geometry_status": geometry_status,
        "validation": "not_run_by_library",
    }
    report["settings"]["declination_applied"] = any(
        group["export"]["declination_degrees"] is not None for group in active
    )


def export_surveys(
    data: bytes,
    *,
    plan: ProcessingPlan | None = None,
    correction_policy: CorrectionPolicy | None = None,
    min_resultant: float = 1e-12,
    limits: ParseLimits = DEFAULT_LIMITS,
) -> SurveyExport:
    """Return source, augmented report, SRV and SVX texts without writing files.

    Only explicitly confirmed repeats are averaged by P03. Nonzero groups need
    a stored explicit declination or a source-pinned override with evidence.
    Auto and missing-trip groups remain visible but inactive until resolved.
    Zero links need no angular correction. Dates and unknown-CRS references
    remain comments/source evidence. Compiler loop adjustment is external to
    this arithmetic; no assertion of historical correctness is implied.
    """
    source, report = prepare_conversion(data, plan=plan, min_resultant=min_resultant, limits=limits)
    corrections = resolve_corrections(report, correction_policy)
    stations = map_station_names(report["station_map"])
    report["stage"] = "P04"
    for document in (source, report):
        document["provenance"]["algorithm_version"] = "p04-1"
    report["settings"].update(
        correction_policy="stored_explicit_or_source_pinned_override",
        correction_overrides=asdict(correction_policy) if correction_policy is not None else None,
        angular_correction="compiler_declination_directive",
        decimal_places=12,
        walls_name_limit=8,
        survex_separator=":",
        source_comments="ascii_json_chunks_160_characters",
    )
    report["limitations"] = [
        "Device dates remain unverified; no date or IGRF directive was emitted.",
        "Stored explicit corrections are reproduced, not historically verified.",
        "Auto and missing-trip corrections require independently evidenced overrides.",
        "Reference CRS is unknown; source coordinates produce no active fixes.",
        "Unconfirmed readings remain separate, including duplicate named vectors.",
        "Compiler loop adjustment is not an oracle for the source readings.",
        "Sketches, CLI and atomic package output remain P05/P06; conversion is incomplete.",
    ]
    for group in report["groups"]:
        group["export"] = _decision(group, corrections)
    _update_trips(report, corrections)
    srv, svx = _headers(source, report)
    for group in report["groups"]:
        comments = _comment(
            "group",
            {"id": group["id"], "source_indices": group["source_indices"], **group["export"]},
        )
        for index in group["source_indices"]:
            comments += _comment(
                "source_shot", {"index": index, **source["records"]["shots"][index]}
            )
        srv.extend(comments)
        svx.extend(comments)
        _emit_group(group, stations, srv, svx)
    svx.append("*end")
    _finish_report(report)
    return SurveyExport(source, report, "\n".join(srv) + "\n", "\n".join(svx) + "\n")
