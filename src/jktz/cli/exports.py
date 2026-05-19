from __future__ import annotations

import argparse
import sys
from pathlib import Path

from jktz.exports import pipeline
from jktz.exports.tools import ExternalToolError


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build JKTZ release artefacts (.3d, .dxf, .shp) from KATASTER.wpj. "
            "Requires Survex (cavern, survexport) and GDAL (ogr2ogr) on PATH."
        ),
    )
    parser.add_argument(
        "version",
        nargs="?",
        default="local",
        help="Version label embedded in output filenames (default: 'local')",
    )
    parser.add_argument(
        "outdir",
        nargs="?",
        default="exports",
        help="Output directory (default: 'exports')",
    )
    args = parser.parse_args()

    try:
        pipeline.run_exports(version=args.version, outdir=Path(args.outdir))
    except ExternalToolError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
