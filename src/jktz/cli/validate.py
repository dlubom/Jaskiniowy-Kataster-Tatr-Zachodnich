from __future__ import annotations

import argparse
import sys
from pathlib import Path

from jktz.exports.tools import ExternalToolError
from jktz.reporting import CheckFailed
from jktz.validation.suite import ValidationContext, run_validation


def _reconfigure_streams_utf8() -> None:
    """Keep progress output readable and timely on redirected Windows streams."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace", line_buffering=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate surveys and exports against GPS.")
    inputs = parser.add_mutually_exclusive_group()
    inputs.add_argument(
        "--gps-snapshot", type=Path, metavar="DIR", help="Use a local GPS snapshot."
    )
    inputs.add_argument("--csv", type=Path, help=argparse.SUPPRESS)
    parser.add_argument(
        "--export-version", help="Keep validated exports in exports/ for packaging."
    )
    args = parser.parse_args(argv)
    if args.csv is not None:
        parser.error(
            "--csv is for jktz-render-otwory only; validation needs a complete GPS snapshot"
        )

    context = ValidationContext(gps_snapshot=args.gps_snapshot)
    if args.export_version is not None:
        context = ValidationContext(
            gps_snapshot=args.gps_snapshot,
            exports_dir=Path("exports"),
            exports_version=args.export_version,
            keep_exports=True,
        )
    _reconfigure_streams_utf8()
    print("=== Validation Started ===")

    try:
        run_validation(context)
    except CheckFailed as exc:
        print(str(exc))
        return 1
    except (ExternalToolError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print()
    print("=== Validation Passed ✔ ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
