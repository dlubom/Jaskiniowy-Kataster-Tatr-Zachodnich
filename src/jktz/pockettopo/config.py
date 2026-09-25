"""Strict, source-pinned JSON decisions for the PocketTopo CLI.

The loader validates the document shape, without inferring a survey date or
confirming repeated readings. Source identity and record-dependent decisions
are validated by the processing and correction APIs before export.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

from jktz.pockettopo.export_policy import CorrectionOverride, CorrectionPolicy
from jktz.pockettopo.grouping import Exclusion, RepeatConfirmation
from jktz.pockettopo.report import ProcessingPlan


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"Nonfinite JSON number is not allowed: {value}")


def _finite_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"Nonfinite JSON number is not allowed: {value}")
    return number


def _object(value: object, context: str, required: set[str], optional: set[str]) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{context} must be a JSON object")
    missing = required - value.keys()
    if missing:
        raise ValueError(f"{context} is missing required keys: {', '.join(sorted(missing))}")
    unknown = value.keys() - required - optional
    if unknown:
        raise ValueError(f"{context} has unknown keys: {', '.join(sorted(unknown))}")
    return value


def _rows(document: dict, name: str, keys: set[str]) -> list[dict]:
    rows = document.get(name, [])
    if not isinstance(rows, list):
        raise ValueError(f"{name} must be a JSON array")
    return [_object(row, f"{name}[{index}]", keys, set()) for index, row in enumerate(rows)]


def _index(value: object, context: str, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise ValueError(f"{context} must be an integer >= {minimum}")
    return value


def _reason(value: object, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{context}.reason must be nonblank text")
    return value


def _confirmations(document: dict) -> tuple[RepeatConfirmation, ...]:
    confirmations = []
    for position, row in enumerate(_rows(document, "confirmations", {"indices", "reason"})):
        context = f"confirmations[{position}]"
        indices = row["indices"]
        if not isinstance(indices, list) or len(indices) < 2:
            raise ValueError(f"{context}.indices must be an array of at least two record indices")
        checked = tuple(_index(index, f"{context}.indices") for index in indices)
        confirmations.append(RepeatConfirmation(checked, _reason(row["reason"], context)))
    return tuple(confirmations)


def _exclusions(document: dict) -> tuple[Exclusion, ...]:
    exclusions = []
    for position, row in enumerate(_rows(document, "exclusions", {"index", "reason"})):
        context = f"exclusions[{position}]"
        exclusions.append(
            Exclusion(_index(row["index"], f"{context}.index"), _reason(row["reason"], context))
        )
    return tuple(exclusions)


def _corrections(document: dict) -> tuple[CorrectionOverride, ...]:
    corrections = []
    for position, row in enumerate(
        _rows(document, "corrections", {"trip_index", "degrees", "reason"})
    ):
        context = f"corrections[{position}]"
        index = _index(row["trip_index"], f"{context}.trip_index", -1)
        degrees = row["degrees"]
        if type(degrees) not in (int, float) or not -180 <= degrees <= 180:
            raise ValueError(f"{context}.degrees must be a finite number from -180 to 180")
        corrections.append(
            CorrectionOverride(index, float(degrees), _reason(row["reason"], context))
        )
    return tuple(corrections)


def load_decisions(path: Path) -> tuple[ProcessingPlan, CorrectionPolicy]:
    """Load explicit decisions; reject unknown/duplicate keys and malformed values.

    Reasons are retained verbatim as evidence. Defaults preserve individual
    readings and stored explicit corrections. File access errors remain OSError;
    invalid UTF-8, JSON and decision documents raise ValueError.
    """
    try:
        document = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
            parse_float=_finite_float,
        )
    except (ValueError, RecursionError) as error:
        raise ValueError(f"Invalid decision JSON in {path}: {error}") from error
    document = _object(
        document, "decisions", {"source_sha256"}, {"confirmations", "exclusions", "corrections"}
    )
    digest = document["source_sha256"]
    if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
        raise ValueError("source_sha256 must contain exactly 64 lowercase hexadecimal characters")
    plan = ProcessingPlan(digest, _confirmations(document), _exclusions(document))
    return plan, CorrectionPolicy(digest, _corrections(document))
