from __future__ import annotations

import argparse
import sys
from pathlib import Path

from jktz.packaging import build_release_zip


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build the user-facing JKTZ ZIP package from the current workspace, "
            "applying the project's exclude patterns."
        ),
    )
    parser.add_argument("version", help="Version label (used in default ZIP filename)")
    parser.add_argument(
        "zip_path",
        nargs="?",
        default=None,
        help="Output ZIP path (default: JKTZ-<VERSION>.zip in the cwd)",
    )
    args = parser.parse_args()

    build_release_zip(
        version=args.version,
        zip_path=Path(args.zip_path) if args.zip_path else None,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
