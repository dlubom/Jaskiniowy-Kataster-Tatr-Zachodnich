"""Command line interface for location registry tools."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Optional

from jktz_locations.exporters import export_current_locations
from jktz_locations.paths import default_export_dir, locations_root
from jktz_locations.validation import format_report, validate_locations


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="jktz-locations")
    parser.add_argument("--root", type=Path, default=None, help="Sciezka do Lokalizacje albo katalogu repo.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Waliduj rejestr YAML, CSV i slowniki.")
    validate_parser.add_argument("--strict", action="store_true", help="Zwracaj blad takze przy ostrzezeniach.")

    export_parser = subparsers.add_parser("export", help="Eksportuj aktualne lokalizacje.")
    export_parser.add_argument("--out", type=Path, default=None, help="Katalog wyjsciowy.")
    export_parser.add_argument(
        "--formats",
        default="csv,xlsx,gpx,shp",
        help="Lista formatow po przecinku: csv,xlsx,gpx,shp.",
    )
    export_parser.add_argument("--skip-validate", action="store_true", help="Pomin walidacje przed eksportem.")

    args = parser.parse_args(argv)
    root = locations_root(args.root)

    if args.command == "validate":
        report = validate_locations(root)
        print(format_report(report))
        if report.errors or (args.strict and report.warnings):
            return 1
        return 0

    if args.command == "export":
        if not args.skip_validate:
            report = validate_locations(root)
            if report.errors:
                print(format_report(report), file=sys.stderr)
                return 1
        out_dir = args.out or default_export_dir(root)
        formats = [item.strip() for item in args.formats.split(",") if item.strip()]
        written = export_current_locations(root, out_dir, formats)
        for path in written:
            print(path)
        return 0

    parser.error(f"Nieznana komenda: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
