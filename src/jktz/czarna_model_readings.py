"""Read the archived Czarna model transcripts without correcting their claims.

The three supplied transcripts all order columns as FROM, TO, A, V, D, Lh,
dh. Repeated photographs remain separate rows, linked by ``duplicate_of_line``;
callers must choose a photograph policy before scoring or summing measurements.
Alternatives contain only explicit alternative readings, never numbers mined
from explanatory prose. Aggregate and marginal annotations remain unparsed:
their scope and meaning require inspection of the original photograph.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

FIELDS = ("D", "A", "V", "Lh", "dh")
_COLUMN_FIELDS = ("A", "V", "D", "Lh", "dh")
_NUMBER = r"[+-]?\s*\d+(?:[.,]\d+)?"
_LEADING_NUMBER = re.compile(rf"^({_NUMBER})(?![\d.,])")
_NUMERIC_LIST = re.compile(rf"{_NUMBER}(?:\s*(?:/|;|\blub\b|\balbo\b)\s*{_NUMBER})*")
_STATION = re.compile(r"(?:\d+|[ab])")
_PHOTO = re.compile(r"^(?:Zdjęcie\s+\d+\b|#+\s+(?:Plik:\s*\d+\.jpg|\d{8}_.*\.jpg))")
_AGGREGATE_NUMBER = re.compile(r"\d+[.,]\d+|Σ|\\(?:sum|Sigma)")
_ALT_LABEL = re.compile(r"^(?:skorygowane\s+na|możliwe\s*:|alternatywnie\s*:?)\s*", re.I)


def _plain(raw: str) -> str:
    """Remove presentational escaping, but retain signs and uncertainty marks."""
    return (
        re.sub(r"\\([+\-\[\]])", r"\1", raw)
        .translate(str.maketrans({"−": "-", "–": "-", "—": "-", "*": "", "`": "", "$": ""}))
        .strip()
    )


def _number(raw: str) -> float:
    return float(re.sub(r"\s+", "", raw).replace(",", "."))


def _alternative_list(raw: str) -> list[float]:
    """Accept a whole numeric list, optionally introduced by a known label."""
    text = _ALT_LABEL.sub("", raw.strip()).strip()
    if not _NUMERIC_LIST.fullmatch(text):
        return []
    return [_number(match.group()) for match in re.finditer(_NUMBER, text)]


def _read_field(raw: str) -> tuple[float | None, list[float], bool]:
    text = _plain(raw)
    if text.lower() in {"", "-", "--", "brak", "brak wpisu"}:
        return None, [], False

    # A sign ambiguity is a reading pair, not a measurement uncertainty bound.
    sign_ambiguity = re.match(r"^(±|\+\s*/\s*-|-\s*/\s*\+)\s*(\d+(?:[.,]\d+)?)", text)
    alternatives: list[float] = []
    if sign_ambiguity:
        magnitude = _number(sign_ambiguity.group(2))
        value = -magnitude if sign_ambiguity.group(1).startswith("-") else magnitude
        alternatives.append(-value)
        remainder = text[sign_ambiguity.end() :]
    else:
        match = _LEADING_NUMBER.match(text)
        value = _number(match.group(1)) if match else None
        remainder = text[match.end() :] if match else text

    for bracket in re.finditer(r"\[\?\s*([^\]]*)\]", remainder):
        alternatives.extend(_alternative_list(bracket.group(1)))

    # A bare slash/lub/albo also explicitly separates readings, if the entire
    # suffix is numeric. A note such as '(wiersz 25)' is not an alternative.
    suffix = re.sub(r"\[.*?\]", "", remainder).strip().lstrip("°").strip()
    separator = re.match(r"^(?:/|lub\b|albo\b)\s*", suffix)
    if separator:
        alternatives.extend(_alternative_list(suffix[separator.end() :]))

    alternatives = list(dict.fromkeys(alt for alt in alternatives if alt != value))
    uncertain = value is None or "?" in text or bool(sign_ambiguity) or bool(alternatives)
    return value, alternatives, uncertain


def read_model(path: str | Path) -> dict[str, Any]:
    """Return lossless source references and conservative numeric readings.

    ``line`` and ``duplicate_of_line`` use one-based source line numbers. The
    latter points to the first occurrence of a pair even when photographs
    disagree. It does not assert equal values or independent measurements.
    ``raw_fields`` preserves each trimmed Markdown cell verbatim. Missing or
    unrecognized numeric fields have value ``None``; unrecognized text is
    flagged as uncertain. Known empty-field markers are not uncertain.
    """
    path = Path(path)
    source = path.read_bytes()
    rows: list[dict[str, Any]] = []
    aggregates: list[dict[str, Any]] = []
    first_line: dict[tuple[str, str], int] = {}
    photo: str | None = None

    for line_number, raw_line in enumerate(source.decode("utf-8").splitlines(), 1):
        stripped = raw_line.strip()
        if _PHOTO.match(stripped):
            photo = stripped.lstrip("# ")
            continue

        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        is_table = stripped.startswith("|")
        is_shot = (
            is_table and len(cells) >= 2 and all(_STATION.fullmatch(cell) for cell in cells[:2])
        )
        if is_shot:
            pair = (cells[0], cells[1])
            numeric_cells = (cells[2:7] + [""] * 5)[:5]
            by_column = dict(zip(_COLUMN_FIELDS, numeric_cells))
            raw_fields = {field: by_column[field] for field in FIELDS}
            parsed = {field: _read_field(raw_fields[field]) for field in FIELDS}
            rows.append(
                {
                    "from": pair[0],
                    "to": pair[1],
                    "line": line_number,
                    "photo": photo,
                    "raw": raw_line,
                    "raw_fields": raw_fields,
                    "values": {field: parsed[field][0] for field in FIELDS},
                    "alternatives": {field: parsed[field][1] for field in FIELDS},
                    "uncertain_fields": [field for field in FIELDS if parsed[field][2]],
                    "raw_extra_fields": cells[7:],
                    "duplicate_of_line": first_line.get(pair),
                }
            )
            first_line.setdefault(pair, line_number)
            annotation = " | ".join(cells[7:])
            if _AGGREGATE_NUMBER.search(annotation):
                aggregates.append(
                    {
                        "line": line_number,
                        "photo": photo,
                        "kind": "row_annotation",
                        "from": pair[0],
                        "to": pair[1],
                        "raw": raw_line,
                        "raw_annotation": annotation,
                    }
                )
        elif _AGGREGATE_NUMBER.search(stripped):
            aggregates.append(
                {
                    "line": line_number,
                    "photo": photo,
                    "kind": "table_annotation" if is_table else "margin_annotation",
                    "raw": raw_line,
                }
            )

    return {
        "model": path.stem,
        "sha256": hashlib.sha256(source).hexdigest(),
        "rows": rows,
        "aggregates": aggregates,
    }
