from __future__ import annotations

import argparse
import sys
from pathlib import Path

from jktz.entrances.render import (
    DEFAULT_GITHUB_REPO,
    DEFAULT_OUTPUT,
    DEFAULT_TEMPLATE,
    RenderError,
    render_entrances,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render Poligony/OTWORY.SRV from gps-kataster latest best measurements."
    )
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify that the output file matches the rendered template without writing it.",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        help="Use an already downloaded best-measurements.csv instead of GitHub latest.",
    )
    parser.add_argument(
        "--github-repo",
        default=DEFAULT_GITHUB_REPO,
        help="GitHub repository to read latest release from, as owner/repo.",
    )
    args = parser.parse_args(argv)

    try:
        result = render_entrances(
            template_path=args.template,
            output_path=args.output,
            csv_path=args.csv,
            github_repo=args.github_repo,
            check=args.check,
        )
    except (OSError, RenderError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    action = "Checked" if args.check else "Rendered"
    print(f"{action} {result.output} from {result.source}")
    print(f"GPS fixes: {result.gps_fixes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
