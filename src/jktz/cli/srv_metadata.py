from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from jktz.metadata.errors import MetadataError
from jktz.metadata.io import atomic_write, encode_srv, read_srv
from jktz.metadata.raw import (
    format_raw_metadata,
    material_hashes,
    parse_raw_metadata,
)
from jktz.metadata.srv import (
    SrvMetadata,
    append_processing,
    default_metadata,
    format_srv_metadata,
    parse_srv_metadata,
    replace_or_insert_metadata,
    resolve_source_ref,
)


def _add_dry_run(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the generated document without modifying the target file.",
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage JKTZ SRV and RAW metadata.")
    subparsers = parser.add_subparsers(dest="cmd", required=True)

    srv_set = subparsers.add_parser("srv-set", help="Create or replace SRV metadata.")
    srv_set.add_argument("path", type=Path)
    srv_set.add_argument("--cave-id", required=True)
    srv_set.add_argument("--cave-name", required=True)
    srv_set.add_argument("--survey-id", required=True)
    srv_set.add_argument("--survey-name", required=True)
    srv_set.add_argument("--source-ref", action="append", required=True)
    srv_set.add_argument("--update-date", required=True)
    srv_set.add_argument("--project-name", default="Kataster jaskin tatrzanskich")
    srv_set.add_argument("--coordinator", default="nieznane")
    srv_set.add_argument("--coordinator-email", default="nieznane")
    srv_set.add_argument(
        "--license-value",
        default="http://creativecommons.org/licenses/by-sa/4.0/",
    )
    srv_set.add_argument("--team", action="append")
    srv_set.add_argument("--instrument", action="append")
    srv_set.add_argument("--survey-date", action="append")
    srv_set.add_argument("--survey-grade", default="nieznane")
    srv_set.add_argument("--processing", action="append")
    _add_dry_run(srv_set)

    srv_update = subparsers.add_parser("srv-update", help="Update existing SRV metadata.")
    srv_update.add_argument("path", type=Path)
    srv_update.add_argument("--update-date")
    srv_update.add_argument("--add-processing", action="append")
    _add_dry_run(srv_update)

    raw_set = subparsers.add_parser("raw-set", help="Create or replace RAW README metadata.")
    raw_set.add_argument("path", type=Path)
    raw_set.add_argument("--title", required=True)
    raw_set.add_argument("--status", required=True)
    raw_set.add_argument("--origin", required=True)
    raw_set.add_argument("--authors", required=True)
    raw_set.add_argument("--dates", required=True)
    raw_set.add_argument("--acquired", required=True)
    raw_set.add_argument("--added-by", required=True)
    raw_set.add_argument("--license-value", required=True)
    raw_set.add_argument("--completeness", required=True)
    raw_set.add_argument("--content", action="append", required=True)
    _add_dry_run(raw_set)

    hash_raw = subparsers.add_parser("hash-raw", help="Hash RAW material files.")
    hash_raw.add_argument("root", type=Path, nargs="?", default=Path("Poligony"))
    return parser


def _write_or_print(path: Path, data: bytes, *, dry_run: bool) -> None:
    if dry_run:
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()
        return
    atomic_write(path, data)


def _encode_metadata_block(metadata: SrvMetadata) -> None:
    try:
        format_srv_metadata(metadata).encode("ascii")
    except UnicodeEncodeError as exc:
        raise MetadataError("SRV metadata must contain ASCII only") from exc


def _poligony_root_for(path: Path) -> Path:
    return next((parent for parent in path.parents if parent.name == "Poligony"), path.parent)


def _run_srv_set(args: argparse.Namespace) -> None:
    metadata = default_metadata(
        cave_id=args.cave_id,
        cave_name=args.cave_name,
        survey_id=args.survey_id,
        survey_name=args.survey_name,
        source_refs=args.source_ref,
        update_date=args.update_date,
        project_name=args.project_name,
        coordinator=args.coordinator,
        coordinator_email=args.coordinator_email,
        license_value=args.license_value,
        team=args.team,
        instruments=args.instrument,
        survey_dates=args.survey_date,
        survey_grade=args.survey_grade,
        processing=args.processing,
    )
    poligony_root = _poligony_root_for(args.path)
    for source_ref in metadata.repeated["SOURCE_REF"]:
        resolve_source_ref(args.path, source_ref, poligony_root)
    _encode_metadata_block(metadata)
    current = read_srv(args.path) if args.path.exists() else ""
    updated = replace_or_insert_metadata(current, metadata)
    parse_srv_metadata(args.path, updated)
    _write_or_print(args.path, encode_srv(updated), dry_run=args.dry_run)


def _run_srv_update(args: argparse.Namespace) -> None:
    if not args.path.is_file():
        raise MetadataError(f"{args.path.as_posix()} does not exist")
    if args.update_date is None and not args.add_processing:
        raise MetadataError("srv-update requires --update-date or --add-processing")

    current = read_srv(args.path)
    metadata = parse_srv_metadata(args.path, current)
    single = dict(metadata.single)
    if args.update_date is not None:
        single["UPDATE_DATE"] = args.update_date
    updated = SrvMetadata(
        single=single,
        repeated={name: list(values) for name, values in metadata.repeated.items()},
        body=metadata.body,
    )
    for note in args.add_processing or []:
        updated = append_processing(updated, note)

    _encode_metadata_block(updated)
    rendered = format_srv_metadata(updated) + updated.body
    parse_srv_metadata(args.path, rendered)
    _write_or_print(args.path, encode_srv(rendered), dry_run=args.dry_run)


def _run_raw_set(args: argparse.Namespace) -> None:
    rendered = format_raw_metadata(
        title=args.title,
        status=args.status,
        origin=args.origin,
        authors=args.authors,
        dates=args.dates,
        acquired=args.acquired,
        added_by=args.added_by,
        license_value=args.license_value,
        completeness=args.completeness,
        contents=args.content,
    )
    parse_raw_metadata(args.path, rendered)
    _write_or_print(args.path, rendered.encode("utf-8"), dry_run=args.dry_run)


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.cmd == "srv-set":
            _run_srv_set(args)
        elif args.cmd == "srv-update":
            _run_srv_update(args)
        elif args.cmd == "raw-set":
            _run_raw_set(args)
        elif args.cmd == "hash-raw":
            for item in material_hashes(args.root):
                print(f"{item.sha256}  {item.path.as_posix()}")
        else:
            raise AssertionError(args.cmd)
    except (MetadataError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
