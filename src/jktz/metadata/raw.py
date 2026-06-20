from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

from jktz.metadata.errors import MetadataError

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

_RAW_ITEM_RE = re.compile(r"^- \*\*([^*]+):\*\*\s*(.*)$")


@dataclass(frozen=True)
class RawMetadata:
    fields: dict[str, str]
    content_items: list[str]


@dataclass(frozen=True)
class MaterialHash:
    path: Path
    sha256: str


def parse_raw_metadata(path: Path, text: str) -> RawMetadata:
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
                raise MetadataError(f"{path.as_posix()} duplicate RAW field {name!r}")
            fields[name] = match.group(2).strip()

    missing = [name for name in RAW_FIELDS if name not in fields]
    if missing:
        quoted_missing = ", ".join(repr(name) for name in missing)
        raise MetadataError(f"{path.as_posix()} missing RAW field(s): {quoted_missing}")
    if fields["Status materiału"] not in RAW_STATUSES:
        raise MetadataError(
            f"{path.as_posix()} invalid value for RAW field 'Status materiału': "
            f"{fields['Status materiału']!r}"
        )
    if not content_items:
        raise MetadataError(
            f"{path.as_posix()} section '## Zawartość' must contain at least one item"
        )
    if fields["Status materiału"] != "niedostępny" and content_items == [
        "Brak materiałów źródłowych."
    ]:
        raise MetadataError(
            f"{path.as_posix()} available package cannot have empty source inventory"
        )
    return RawMetadata(fields=fields, content_items=content_items)


def format_raw_metadata(
    *,
    title: str,
    status: str,
    origin: str,
    authors: str,
    dates: str,
    acquired: str,
    added_by: str,
    license_value: str,
    completeness: str,
    contents: list[str],
) -> str:
    lines = [
        f"# {title}",
        "",
        f"- **Status materiału:** {status}",
        f"- **Pochodzenie danych:** {origin}",
        f"- **Autorzy pomiarów:** {authors}",
        f"- **Daty pomiarów:** {dates}",
        f"- **Data pozyskania:** {acquired}",
        f"- **Dodał do _RAW:** {added_by}",
        f"- **Licencja źródłowa:** {license_value}",
        f"- **Kompletność:** {completeness}",
        "",
        "## Zawartość",
        "",
    ]
    lines.extend(f"- {item}" for item in contents)
    return "\n".join(lines) + "\n"


def material_hashes(root: Path) -> list[MaterialHash]:
    hashes: list[MaterialHash] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name == "README.md":
            continue
        if "_RAW" not in path.parts:
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        hashes.append(MaterialHash(path=path, sha256=digest))
    return hashes
