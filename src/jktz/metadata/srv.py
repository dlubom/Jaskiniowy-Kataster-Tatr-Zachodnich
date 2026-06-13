from __future__ import annotations

import posixpath
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from jktz.metadata.errors import MetadataError

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
    "SURVEY_GRADE",
)
REPEATED_FIELDS = (
    "SOURCE_REF",
    "TEAM",
    "INSTRUMENT",
    "SURVEY_DATE",
    "PROCESSING",
)
STRUCTURAL_FIELDS = {"CAVE_ID", "CAVE_NAME", "SURVEY_ID", "SURVEY_NAME", "SOURCE_REF", "LICENSE"}
ALL_FIELDS = set(SINGLE_FIELDS) | set(REPEATED_FIELDS)

_FIELD_RE = re.compile(r'^([A-Z][A-Z0-9_]*)\s+"([^"]*)"$')
_METADATA_OPEN_RE = re.compile(r"#\[\r?\n")
_METADATA_CLOSE_RE = re.compile(r"(?m)^#\](?:\r?\n|$)")
_DATE_RE = re.compile(r"^\d{4}(-\d{2})?(-\d{2})?$")
_UPDATE_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_GRADE_RE = re.compile(
    r"^(nieznane|BCRA:([1-6X][A-D]?|nieznane)|(?!BCRA:)[A-Z][A-Z0-9_-]*:[A-Za-z0-9._-]+)$"
)


@dataclass(frozen=True)
class SrvMetadata:
    single: dict[str, str]
    repeated: dict[str, list[str]]
    body: str


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
        if name == "SURVEY_GRADE":
            continue
        if name == "LICENSE":
            for value in metadata.repeated["SOURCE_REF"]:
                lines.append(_format_field("SOURCE_REF", value))
        lines.append(_format_field(name, metadata.single[name]))
    lines.append("")
    for name in ("TEAM", "INSTRUMENT", "SURVEY_DATE"):
        for value in metadata.repeated[name]:
            lines.append(_format_field(name, value))
    lines.append(_format_field("SURVEY_GRADE", metadata.single["SURVEY_GRADE"]))
    for value in metadata.repeated["PROCESSING"]:
        lines.append(_format_field("PROCESSING", value))
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


def default_metadata(
    *,
    cave_id: str,
    cave_name: str,
    survey_id: str,
    survey_name: str,
    source_refs: list[str],
    update_date: str,
    project_name: str = "Kataster jaskin tatrzanskich",
    coordinator: str = "nieznane",
    coordinator_email: str = "nieznane",
    license_value: str = "http://creativecommons.org/licenses/by-sa/4.0/",
    team: list[str] | None = None,
    instruments: list[str] | None = None,
    survey_dates: list[str] | None = None,
    survey_grade: str = "nieznane",
    processing: list[str] | None = None,
) -> SrvMetadata:
    return SrvMetadata(
        single={
            "CAVE_ID": cave_id,
            "CAVE_NAME": cave_name,
            "SURVEY_ID": survey_id,
            "SURVEY_NAME": survey_name,
            "UPDATE_DATE": update_date,
            "PROJECT_NAME": project_name,
            "COORDINATOR": coordinator,
            "COORDINATOR_EMAIL": coordinator_email,
            "LICENSE": license_value,
            "SURVEY_GRADE": survey_grade,
        },
        repeated={
            "SOURCE_REF": source_refs,
            "TEAM": team or ["nieznane"],
            "INSTRUMENT": instruments or ["nieznane"],
            "SURVEY_DATE": survey_dates or ["nieznane"],
            "PROCESSING": processing or ["nieznane"],
        },
        body="",
    )


def replace_or_insert_metadata(text: str, metadata: SrvMetadata) -> str:
    try:
        existing = parse_srv_metadata(Path("Poligony/MEMORY.SRV"), text)
        body = existing.body
    except ValueError:
        body = text.lstrip("\r\n")
    return format_srv_metadata(metadata) + body


def append_processing(metadata: SrvMetadata, note: str) -> SrvMetadata:
    values = [value for value in metadata.repeated["PROCESSING"] if value != "nieznane"]
    if note not in values:
        values.append(note)
    repeated = dict(metadata.repeated)
    repeated["PROCESSING"] = values or ["nieznane"]
    return SrvMetadata(single=dict(metadata.single), repeated=repeated, body=metadata.body)
