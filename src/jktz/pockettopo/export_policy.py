"""Source-pinned declination decisions and collision-free target station names."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CorrectionOverride:
    """Use independently justified degrees for one trip (-1 means missing trip)."""

    trip_index: int
    degrees: float
    evidence: str


@dataclass(frozen=True)
class CorrectionPolicy:
    """Overrides are bound to exact input bytes; stored explicit values are default."""

    source_sha256: str
    overrides: tuple[CorrectionOverride, ...] = ()


def resolve_corrections(report: dict, policy: CorrectionPolicy | None) -> dict[int, dict]:
    """Validate the complete override policy before selecting per-trip corrections."""
    overrides = {}
    if policy is not None:
        if policy.source_sha256 != report["provenance"]["sha256"]:
            raise ValueError("Correction policy source_sha256 does not match input bytes")
        for override in policy.overrides:
            index = override.trip_index
            if type(index) is not int or not -1 <= index < len(report["trips"]):
                raise ValueError("correction_trip_index_must_be_in_range_integer")
            if index in overrides:
                raise ValueError("duplicate_correction_override")
            if type(override.degrees) not in (int, float) or not -180 <= override.degrees <= 180:
                raise ValueError("correction_degrees_must_be_finite_in_minus180_to_180")
            if not isinstance(override.evidence, str) or not override.evidence.strip():
                raise ValueError("correction_evidence_must_be_nonblank_text")
            overrides[index] = override
    corrections = {
        trip["index"]: {
            "degrees": trip["declination"]["stored_degrees"],
            "provenance": "stored_explicit" if trip["declination"]["mode"] == "explicit" else None,
            "evidence": None,
            "reason": None if trip["declination"]["mode"] == "explicit" else "unresolved_auto",
        }
        for trip in report["trips"]
    }
    corrections[-1] = {
        "degrees": None,
        "provenance": None,
        "evidence": None,
        "reason": "missing_trip_correction",
    }
    for index, override in overrides.items():
        corrections[index] = {
            "degrees": override.degrees,
            "provenance": "source_pinned_override",
            "evidence": override.evidence,
            "reason": None,
        }
    return corrections


def _base36(value: int) -> str:
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    result = ""
    while value:
        value, digit = divmod(value, 36)
        result = digits[digit] + result
    return result or "0"


def map_station_names(stations: list[dict]) -> dict[int, dict]:
    """Preserve numeric/dotted names; encode >8-char Walls names without truncation.

    PocketTopo names never start with p, so p + unsigned-raw base36 is disjoint
    from every literal source name. The full int32 domain fits in eight chars.
    Survex preserves dots by using ':' as its survey separator.
    """
    for station in stations:
        source_name = station["source_text"]
        station.update(
            walls_name=(
                source_name if len(source_name) <= 8 else "p" + _base36(station["raw"] & 0xFFFFFFFF)
            ),
            survex_name=source_name,
            status="mapped",
            walls_mapping="literal" if len(source_name) <= 8 else "unsigned_raw_base36",
            survex_mapping="literal",
        )
    return {station["raw"]: station for station in stations}
