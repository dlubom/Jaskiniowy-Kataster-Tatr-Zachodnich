from __future__ import annotations

import posixpath
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

SINGLE_FIELDS = (
    "CAVE_ID",
    "CAVE_NAME",
    "SURVEY_ID",
    "SURVEY_NAME",
    "UPDATE_DATE",
    "PROJECT_NAME",
    "COORDINATOR",
    "COORDINATOR_EMAIL",
    "LICENSE",
)
REPEATED_FIELDS = (
    "SOURCE_REF",
    "TEAM",
    "INSTRUMENT",
    "SURVEY_DATE",
    "SURVEY_GRADE",
    "PROCESSING",
)
STRUCTURAL_FIELDS = {"CAVE_ID", "CAVE_NAME", "SURVEY_ID", "SURVEY_NAME", "SOURCE_REF", "LICENSE"}
ALL_FIELDS = set(SINGLE_FIELDS) | set(REPEATED_FIELDS)

RAW_FIELDS = (
    "Status materiału",
    "Pochodzenie danych",
    "Autorzy pomiarów",
    "Daty pomiarów",
    "Data pozyskania",
    "Dodał do _RAW",
    "Licencja źródłowa",
    "Kompletność",
)
RAW_STATUSES = {"dostępny", "częściowy", "niedostępny"}

_FIELD_RE = re.compile(r'^([A-Z][A-Z0-9_]*)\s+"([^"]*)"$')
_METADATA_OPEN_RE = re.compile(r"#\[\r?\n")
_METADATA_CLOSE_RE = re.compile(r"(?m)^#\](?:\r?\n|$)")
_DATE_RE = re.compile(r"^\d{4}(-\d{2})?(-\d{2})?$")
_UPDATE_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_GRADE_RE = re.compile(
    r"^(nieznane|BCRA:([1-6X][A-D]?|nieznane)|[A-Z][A-Z0-9_-]*:[A-Za-z0-9._-]+)$"
)
_RAW_ITEM_RE = re.compile(r"^- \*\*([^*]+):\*\*\s*(.*)$")
_DATE_DIRECTIVE_RE = re.compile(r"^\s*#date\b", re.IGNORECASE)
_UNITS_DIRECTIVE_RE = re.compile(r"^\s*#units\b", re.IGNORECASE)
_DECL_DIRECTIVE_RE = re.compile(r"^\s*#units\b.*\bDECL\s*=", re.IGNORECASE)
_ORDER_RE = re.compile(r"\border\s*=\s*([A-Z]+)", re.IGNORECASE)
_RECT_RE = re.compile(r"\brect\b", re.IGNORECASE)


class MetadataError(ValueError):
    """Raised when SRV or RAW metadata violates the repository contract."""


@dataclass(frozen=True)
class SrvMetadata:
    single: dict[str, str]
    repeated: dict[str, list[str]]
    body: str


@dataclass(frozen=True)
class RawReadme:
    fields: dict[str, str]
    content_items: list[str]


def is_active_srv_path(path: Path) -> bool:
    parts = path.parts
    if path.suffix != ".SRV" or "_RAW" in parts:
        return False
    if parts[:1] == ("Poligony",):
        poligony_path = path.as_posix()
    elif "Poligony" in parts:
        poligony_index = parts.index("Poligony")
        poligony_path = "/".join(parts[poligony_index:])
    else:
        return False
    return poligony_path != "Poligony/OTWORY.SRV"


def _validate_date(name: str, value: str) -> None:
    if value == "nieznane":
        return
    if "/" in value:
        left, sep, right = value.partition("/")
        if not sep or not _is_valid_contract_date(left) or not _is_valid_contract_date(right):
            raise MetadataError(f"{name} has invalid date range {value!r}")
        return
    if not _is_valid_contract_date(value):
        raise MetadataError(f"{name} has invalid date {value!r}")


def _is_valid_contract_date(value: str) -> bool:
    if not _DATE_RE.fullmatch(value):
        return False
    if value.count("-") == 2:
        try:
            date.fromisoformat(value)
        except ValueError:
            return False
    return True


def _validate_field(name: str, value: str) -> None:
    if name in STRUCTURAL_FIELDS and value == "nieznane":
        raise MetadataError(f"{name} cannot be nieznane")
    if name == "UPDATE_DATE" and value != "nieznane":
        if not _UPDATE_DATE_RE.fullmatch(value) or not _is_valid_contract_date(value):
            raise MetadataError(f"UPDATE_DATE has invalid date {value!r}")
    if name == "SURVEY_DATE":
        _validate_date(name, value)
    if name == "SURVEY_GRADE" and not _GRADE_RE.fullmatch(value):
        raise MetadataError(f"SURVEY_GRADE has invalid value {value!r}")


def parse_srv_metadata(path: Path, text: str) -> SrvMetadata:
    opening = _METADATA_OPEN_RE.match(text)
    if opening is None:
        raise MetadataError(f"{path.as_posix()} must start with #[")
    closing = _METADATA_CLOSE_RE.search(text, opening.end())
    if closing is None:
        raise MetadataError(f"{path.as_posix()} metadata block is not closed with #]")

    block = text[opening.end() : closing.start()]
    body = text[closing.end() :]
    single: dict[str, str] = {}
    repeated: dict[str, list[str]] = {name: [] for name in REPEATED_FIELDS}

    for line_num, line in enumerate(block.splitlines(), start=2):
        if not line.strip():
            continue
        match = _FIELD_RE.fullmatch(line)
        if not match:
            raise MetadataError(f"{path.as_posix()}:{line_num}: invalid metadata line {line!r}")
        name, value = match.groups()
        if name not in ALL_FIELDS:
            raise MetadataError(f"{path.as_posix()}:{line_num}: unknown field {name}")
        _validate_field(name, value)
        if name in SINGLE_FIELDS:
            if name in single:
                raise MetadataError(f"{path.as_posix()}:{line_num}: duplicate single field {name}")
            single[name] = value
        else:
            repeated[name].append(value)

    missing = [name for name in SINGLE_FIELDS if name not in single]
    missing.extend(name for name in REPEATED_FIELDS if not repeated[name])
    if missing:
        raise MetadataError(f"{path.as_posix()} missing metadata field(s): {', '.join(missing)}")

    return SrvMetadata(single=single, repeated=repeated, body=body.lstrip("\r\n"))


def format_srv_metadata(metadata: SrvMetadata) -> str:
    lines = ["#["]
    for name in SINGLE_FIELDS:
        if name == "LICENSE":
            for value in metadata.repeated["SOURCE_REF"]:
                lines.append(_format_field("SOURCE_REF", value))
        lines.append(_format_field(name, metadata.single[name]))
    lines.append("")
    for name in ("TEAM", "INSTRUMENT", "SURVEY_DATE", "SURVEY_GRADE", "PROCESSING"):
        for value in metadata.repeated[name]:
            lines.append(_format_field(name, value))
    lines.append("#]")
    lines.append("")
    return "\n".join(lines) + "\n"


def _format_field(name: str, value: str) -> str:
    padding = " " * max(1, 16 - len(name))
    return f'{name}{padding}"{value}"'


def resolve_source_ref(srv_path: Path, value: str, poligony_root: Path) -> Path:
    normalized = posixpath.normpath(value)
    parts = normalized.split("/")
    if len(parts) < 2 or parts[-2] != "_RAW" or not re.fullmatch(r"\d{2}", parts[-1]):
        raise MetadataError(f"SOURCE_REF {value!r} must end with _RAW/NN")
    if normalized.startswith("/"):
        raise MetadataError(f"SOURCE_REF {value!r} must be relative")

    resolved = (srv_path.parent / Path(normalized)).resolve()
    root = poligony_root.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise MetadataError(f"SOURCE_REF {value!r} resolves outside Poligony") from exc
    return resolved


def parse_raw_readme(path: Path, text: str) -> RawReadme:
    fields: dict[str, str] = {}
    in_contents = False
    after_contents = False
    seen_contents_heading = False
    content_items: list[str] = []
    for line in text.splitlines():
        if line == "## Zawartość":
            if seen_contents_heading:
                in_contents = False
                after_contents = True
                continue
            seen_contents_heading = True
            in_contents = True
            after_contents = False
            continue
        if in_contents:
            if line.startswith("## "):
                in_contents = False
                after_contents = True
                continue
            if line.startswith("- "):
                content_items.append(line[2:])
            continue
        if after_contents:
            continue
        match = _RAW_ITEM_RE.fullmatch(line)
        if match:
            name = match.group(1)
            if name in fields:
                raise MetadataError(f"{path.as_posix()} duplicate RAW field {name}")
            fields[name] = match.group(2).strip()

    missing = [name for name in RAW_FIELDS if name not in fields]
    if missing:
        raise MetadataError(f"{path.as_posix()} missing RAW field(s): {', '.join(missing)}")
    if fields["Status materiału"] not in RAW_STATUSES:
        raise MetadataError(
            f"{path.as_posix()} invalid Status materiału {fields['Status materiału']!r}"
        )
    if not content_items:
        raise MetadataError(f"{path.as_posix()} missing ## Zawartość items")
    if fields["Status materiału"] != "niedostępny" and content_items == [
        "Brak materiałów źródłowych."
    ]:
        raise MetadataError(
            f"{path.as_posix()} available package cannot have empty source inventory"
        )
    return RawReadme(fields=fields, content_items=content_items)


def has_dated_or_declared_active_shots(text: str) -> bool:
    has_orientation_state = False
    distance_token_index = 2
    is_rectangular = False
    for raw_line in text.splitlines():
        line = raw_line.split(";", 1)[0].strip()
        if not line:
            continue
        if _DATE_DIRECTIVE_RE.match(line):
            has_orientation_state = True
            continue
        if _UNITS_DIRECTIVE_RE.match(line):
            if _DECL_DIRECTIVE_RE.match(line):
                has_orientation_state = True
            is_rectangular = bool(_RECT_RE.search(line))
            distance_token_index = _distance_token_index(line)
            continue
        if line.startswith("#"):
            continue
        if is_rectangular:
            continue
        tokens = line.split()
        if len(tokens) <= distance_token_index:
            continue
        distance = _as_float(tokens[distance_token_index])
        if distance is None:
            continue
        if distance == 0:
            continue
        if not has_orientation_state:
            return False
    return True


def _distance_token_index(units_line: str) -> int:
    match = _ORDER_RE.search(units_line)
    if match is None:
        return 2
    order = match.group(1).upper()
    if "D" not in order:
        return 2
    return 2 + order.index("D")


def _as_float(value: str) -> float | None:
    try:
        return float(value)
    except ValueError:
        return None
