from __future__ import annotations

import posixpath
import re
from dataclasses import dataclass
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
_DATE_RE = re.compile(r"^\d{4}(-\d{2})?(-\d{2})?$")
_UPDATE_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_GRADE_RE = re.compile(
    r"^(nieznane|BCRA:([1-6X][A-D]?|nieznane)|[A-Z][A-Z0-9_-]*:[A-Za-z0-9._-]+)$"
)
_RAW_ITEM_RE = re.compile(r"^- \*\*([^*]+):\*\*\s*(.*)$")
_SHOT_RE = re.compile(r"^\s*\S+\s+\S+\s+(-?\d+(?:\.\d+)?)\s+\S+\s+\S+")
_DATE_DIRECTIVE_RE = re.compile(r"^\s*#date\b", re.IGNORECASE)
_DECL_DIRECTIVE_RE = re.compile(r"^\s*#units\b.*\bDECL\s*=", re.IGNORECASE)


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
        if not sep or not _DATE_RE.fullmatch(left) or not _DATE_RE.fullmatch(right):
            raise MetadataError(f"{name} has invalid date range {value!r}")
        return
    if not _DATE_RE.fullmatch(value):
        raise MetadataError(f"{name} has invalid date {value!r}")


def _validate_field(name: str, value: str) -> None:
    if name in STRUCTURAL_FIELDS and value == "nieznane":
        raise MetadataError(f"{name} cannot be nieznane")
    if name == "UPDATE_DATE" and value != "nieznane" and not _UPDATE_DATE_RE.fullmatch(value):
        raise MetadataError(f"UPDATE_DATE has invalid date {value!r}")
    if name == "SURVEY_DATE":
        _validate_date(name, value)
    if name == "SURVEY_GRADE" and not _GRADE_RE.fullmatch(value):
        raise MetadataError(f"SURVEY_GRADE has invalid value {value!r}")


def parse_srv_metadata(path: Path, text: str) -> SrvMetadata:
    if not text.startswith("#[\n"):
        raise MetadataError(f"{path.as_posix()} must start with #[")
    end = text.find("#]\n")
    if end == -1:
        raise MetadataError(f"{path.as_posix()} metadata block is not closed with #]")

    block = text[3:end]
    body = text[end + 3 :]
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
    content_items: list[str] = []
    for line in text.splitlines():
        if line == "## Zawartość":
            in_contents = True
            continue
        if in_contents:
            if line.startswith("- "):
                content_items.append(line[2:])
            continue
        match = _RAW_ITEM_RE.fullmatch(line)
        if match:
            fields[match.group(1)] = match.group(2).strip()

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
    for raw_line in text.splitlines():
        line = raw_line.split(";", 1)[0].strip()
        if not line:
            continue
        if _DATE_DIRECTIVE_RE.match(line) or _DECL_DIRECTIVE_RE.match(line):
            has_orientation_state = True
            continue
        if line.startswith("#"):
            continue
        match = _SHOT_RE.match(line)
        if not match:
            continue
        distance = float(match.group(1))
        if distance == 0:
            continue
        if not has_orientation_state:
            return False
    return True
