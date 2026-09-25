"""Inspect PocketTopo sources or publish audited SRV/SVX and SVG/PNG packages."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from jktz.pockettopo.config import load_decisions
from jktz.pockettopo.drawings import DrawingSettings, RenderingError
from jktz.pockettopo.export import export_surveys
from jktz.pockettopo.package import convert_package


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("inspect", "convert"):
        sub = commands.add_parser(command)
        sub.add_argument("source", type=Path, help="PocketTopo v3 source; never modified")
        sub.add_argument("--decisions", type=Path, help="Source SHA-256 pinned JSON decisions")
        sub.add_argument("--min-resultant", type=float, default=1e-12)
        if command == "convert":
            sub.add_argument(
                "--output",
                type=Path,
                required=True,
                help="New directory in an existing parent; existing paths are refused",
            )
            sub.add_argument(
                "--resvg",
                default=os.environ.get("RESVG", "resvg"),
                help="Path to resvg 0.48.1 (default: RESVG or PATH)",
            )
            sub.add_argument("--cavern", default="cavern")
            sub.add_argument("--dump3d", default="dump3d")
            sub.add_argument("--pixels-per-metre", type=float, default=40.0)
            sub.add_argument("--background", default="#ffffff", help="#RRGGBB or transparent")
    return parser


def _execute(args: argparse.Namespace) -> int:
    plan, corrections = load_decisions(args.decisions) if args.decisions else (None, None)
    options = {"plan": plan, "correction_policy": corrections, "min_resultant": args.min_resultant}
    if args.command == "inspect":
        result = export_surveys(args.source.read_bytes(), **options)
        result.report["limitations"] = [
            item for item in result.report["limitations"] if not item.startswith("Sketches, CLI")
        ] + ["Inspection only: drawings, compilation and package publication have not run."]
        print(json.dumps({"source": result.source_document, "report": result.report}, indent=2))
        return 0
    settings = DrawingSettings(
        pixels_per_metre=args.pixels_per_metre,
        background=None if args.background == "transparent" else args.background,
    )
    report = convert_package(
        args.source,
        args.output,
        **options,
        settings=settings,
        resvg_path=args.resvg,
        cavern=args.cavern,
        dump3d=args.dump3d,
    )
    complete = report["completeness"]["conversion_complete"]
    print(
        json.dumps(
            {
                "output": str(args.output.resolve()),
                "completeness": report["completeness"],
                "report": str(args.output.resolve() / "conversion-report.json"),
            },
            indent=2,
        )
    )
    if not complete:
        print(
            "INCOMPLETE: package saved; review held records, compilation and drawing notices "
            "in conversion-report.json",
            file=sys.stderr,
        )
    return 0 if complete else 2


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        return _execute(args)
    except (OSError, ValueError, RenderingError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
