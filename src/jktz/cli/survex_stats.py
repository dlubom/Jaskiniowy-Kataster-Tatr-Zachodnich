from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

from jktz.exports import tools
from jktz.exports.tools import ExternalToolError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compile a Survex .svx/.wpj file and print cavern statistics."
    )
    parser.add_argument("source", type=Path, help="Path to a .svx or .wpj file")
    args = parser.parse_args(argv)

    source = args.source.resolve()
    if not source.is_file():
        print(f"ERROR: file not found: {args.source}", file=sys.stderr)
        return 1

    print(f"=== Compiling: {args.source} ===")
    print()
    try:
        with tempfile.TemporaryDirectory(prefix="jktz-survex-stats-") as tmp_dir:
            output = Path(tmp_dir) / "out"
            tools.cavern(
                ["--no-auxiliary-files", "-o", str(output), source.name],
                cwd=source.parent,
            )
    except ExternalToolError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print()
    print("=== Done ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
