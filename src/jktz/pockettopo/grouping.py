"""Explicit, auditable repeat plans; station names alone never create groups."""

from __future__ import annotations

from dataclasses import dataclass

from .model import Shot, TopFile


@dataclass(frozen=True)
class RepeatConfirmation:
    """Zero-based consecutive indices with independently supplied evidence."""

    indices: tuple[int, ...]
    evidence: str


@dataclass(frozen=True)
class Exclusion:
    """Keep a source record in the audit trail, but not in active measurements."""

    index: int
    reason: str


@dataclass(frozen=True)
class RecordGroup:
    indices: tuple[int, ...]
    evidence: str | None = None


def shot_problem(shot: Shot) -> str | None:
    """Return the first geometric defect without changing the source record.

    A zero-length self-link cannot connect distinct stations and is invalid.
    Unknown session identity is retained on individual records, not a geometry
    defect; it is insufficient evidence for confirming repeat groups.
    """
    if shot.distance_mm < 0:
        return "negative_distance"
    if not -16384 <= shot.inclination_raw <= 16384:
        return "inclination_out_of_range"
    undefined = (shot.from_id.kind == "undefined", shot.to_id.kind == "undefined")
    if all(undefined):
        return "both_stations_undefined"
    if shot.from_id == shot.to_id:
        return "self_link" if shot.distance_mm == 0 else "self_shot"
    if shot.distance_mm == 0 and any(undefined):
        return "zero_unnamed_shot"
    return None


def shot_kind(shot: Shot) -> str:
    """Classify a record without treating Flip as a reversed measurement."""
    if shot_problem(shot) is not None:
        return "invalid"
    if shot.distance_mm == 0:
        return "zero_link"
    if shot.from_id.kind == "undefined" or shot.to_id.kind == "undefined":
        return "splay"
    return "leg"


def _check_index(index: int, count: int) -> None:
    if type(index) is not int or not 0 <= index < count:
        raise ValueError("record_index_must_be_an_in_range_integer")


def _check_text(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name}_must_be_nonblank_text")


def _exclusion_indices(exclusions: tuple[Exclusion, ...], count: int) -> set[int]:
    indices: set[int] = set()
    for exclusion in exclusions:
        _check_index(exclusion.index, count)
        _check_text(exclusion.reason, "exclusion_reason")
        if exclusion.index in indices:
            raise ValueError("duplicate_exclusion")
        indices.add(exclusion.index)
    return indices


def _validate_confirmation(source: TopFile, confirmation: RepeatConfirmation) -> None:
    indices = confirmation.indices
    if not isinstance(indices, tuple) or len(indices) < 2:
        raise ValueError("repeat_indices_must_be_a_tuple_with_at_least_two_records")
    _check_text(confirmation.evidence, "repeat_evidence")
    for index in indices:
        _check_index(index, len(source.shots))
    if indices != tuple(range(indices[0], indices[0] + len(indices))):
        raise ValueError("repeat_indices_must_be_sorted_and_consecutive")
    first = source.shots[indices[0]]
    if not 0 <= first.trip_index < len(source.trips):
        raise ValueError("repeat_requires_known_session")
    pair = {first.from_id.raw, first.to_id.raw}
    for index in indices:
        shot = source.shots[index]
        if shot_kind(shot) != "leg":
            raise ValueError("repeat_requires_valid_nonzero_named_legs")
        if shot.trip_index != first.trip_index:
            raise ValueError("repeat_session_changed")
        if {shot.from_id.raw, shot.to_id.raw} != pair:
            raise ValueError("repeat_station_pair_changed")


def make_groups(
    source: TopFile,
    confirmations: tuple[RepeatConfirmation, ...] = (),
    exclusions: tuple[Exclusion, ...] = (),
) -> tuple[RecordGroup, ...]:
    """Validate the whole plan, then cover every source shot exactly once.

    Plans may be supplied in any order. Each confirmed group is consecutive;
    output follows the source order. Exclusions remain singletons so downstream
    reports can record their reason without losing the original measurement.
    """
    excluded = _exclusion_indices(exclusions, len(source.shots))
    claimed: set[int] = set()
    starts: dict[int, RecordGroup] = {}
    for confirmation in confirmations:
        _validate_confirmation(source, confirmation)
        indices = confirmation.indices
        if claimed.intersection(indices):
            raise ValueError("overlapping_repeat_confirmations")
        if excluded.intersection(indices):
            raise ValueError("repeat_contains_excluded_record")
        claimed.update(indices)
        starts[indices[0]] = RecordGroup(indices, confirmation.evidence)
    groups = []
    index = 0
    while index < len(source.shots):
        group = starts.get(index, RecordGroup((index,)))
        groups.append(group)
        index += len(group.indices)
    return tuple(groups)
