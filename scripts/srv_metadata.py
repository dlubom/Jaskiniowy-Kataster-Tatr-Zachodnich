from __future__ import annotations

import argparse
import hashlib
from dataclasses import dataclass
from pathlib import Path

from jktz.metadata_contract import SrvMetadata, format_srv_metadata, parse_srv_metadata


@dataclass(frozen=True)
class MaterialHash:
    path: Path
    sha256: str


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
        },
        repeated={
            "SOURCE_REF": source_refs,
            "TEAM": team or ["nieznane"],
            "INSTRUMENT": instruments or ["nieznane"],
            "SURVEY_DATE": survey_dates or ["nieznane"],
            "SURVEY_GRADE": [survey_grade],
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


def canonical_raw_readme(
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage JKTZ SRV metadata helpers.")
    subparsers = parser.add_subparsers(dest="cmd", required=True)
    hash_cmd = subparsers.add_parser("hash-raw")
    hash_cmd.add_argument("root", type=Path, nargs="?", default=Path("Poligony"))
    args = parser.parse_args()

    if args.cmd == "hash-raw":
        for item in material_hashes(args.root):
            print(f"{item.sha256}  {item.path.as_posix()}")
        return 0
    raise AssertionError(args.cmd)


if __name__ == "__main__":
    raise SystemExit(main())
