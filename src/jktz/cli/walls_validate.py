"""Run the native Walls driver against an isolated source snapshot."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from jktz.walls import validate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path("KATASTER.wpj"))
    parser.add_argument("--walls", type=Path, required=True)
    parser.add_argument("--driver", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="New evidence directory")
    parser.add_argument("--wine", help="Wine executable (POSIX only; use a dedicated WINEPREFIX)")
    parser.add_argument("--scratch-root", type=Path, help="Short local root, e.g. C:\\ or /tmp")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument(
        "--duplicates", action="store_true", help="Enable optional duplicate-vector audit"
    )
    args = parser.parse_args(argv)
    if not 1 <= args.timeout <= 1800:
        parser.error("--timeout must be 1..1800 seconds")
    if args.wine and not os.environ.get("WINEPREFIX"):
        parser.error("--wine requires an explicit dedicated WINEPREFIX")
    try:
        result = validate(
            args.project,
            args.walls,
            args.driver,
            args.output,
            wine=args.wine,
            timeout=args.timeout,
            duplicates=args.duplicates,
            scratch_root=args.scratch_root,
        )
    except (OSError, ValueError) as exc:
        print(f"FAIL: {exc}")
        return 1
    print(f"{result['status']}: {args.output / 'result.json'}")
    for reason in result["reason"]:
        print(reason)
    return 0 if result["status"] == "PASS" else 1
