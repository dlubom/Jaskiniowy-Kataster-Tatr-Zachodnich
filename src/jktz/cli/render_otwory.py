from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from dataclasses import replace
from pathlib import Path

from jktz.entrances.render import (
    DEFAULT_GITHUB_REPO,
    DEFAULT_OUTPUT,
    DEFAULT_TEMPLATE,
    RenderResult,
    render_entrances,
)
from jktz.exports.tools import ExternalToolError, cavern
from jktz.gps_catalog import download_snapshot, load_snapshot, read_catalogue
from jktz.metadata.identity import SurveyIdentity
from jktz.metadata.io import atomic_write
from jktz.reporting import CheckFailed
from jktz.validation import catalogue, coordinates, metadata, unattached
from jktz.walls import source_files


def _render_checked_project(
    template: Path, output: Path, csv_path: Path, identities: dict[Path, SurveyIdentity]
) -> RenderResult:
    """Compile with the candidate snapshot in isolation before replacing OTWORY."""
    root = Path.cwd()
    with tempfile.TemporaryDirectory(prefix="jktz-render-") as directory:
        scratch = Path(directory)
        for source in source_files(root):
            destination = scratch / source.relative_to(root)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
        candidate = scratch / DEFAULT_OUTPUT
        candidate.parent.mkdir(parents=True, exist_ok=True)
        result = render_entrances(template_path=template, output_path=candidate, csv_path=csv_path)
        coordinates.check(candidate)
        log = scratch / "cavern.log"
        cavern(["--warnings-are-errors", "KATASTER.wpj"], cwd=scratch, log_to=log)
        unattached.check(log_path=log)
        catalogue.check_compiled_references(scratch / "KATASTER.3d", identities)
        atomic_write(output, candidate.read_bytes())
    return replace(result, output=output)


def snapshot_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Download both assets from one GPS release.")
    parser.add_argument("directory", type=Path)
    args = parser.parse_args(argv)
    try:
        snapshot = download_snapshot(DEFAULT_GITHUB_REPO, args.directory)
        read_catalogue(snapshot)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"Downloaded {snapshot.repo}@{snapshot.tag} (release {snapshot.release_id})")
    return 0


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
    inputs = parser.add_mutually_exclusive_group()
    inputs.add_argument(
        "--gps-snapshot", type=Path, metavar="DIR", help="Use a complete local GPS snapshot."
    )
    inputs.add_argument(
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

    in_place = args.output.resolve() == DEFAULT_OUTPUT.resolve() and not args.check
    if in_place and args.csv is not None:
        parser.error("--csv only previews to a separate output; use a complete GPS snapshot")

    try:
        with tempfile.TemporaryDirectory(prefix="jktz-render-gps-") as directory:
            result = _render(args, in_place, Path(directory) / "gps")
    except (OSError, ValueError, CheckFailed, ExternalToolError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    action = "Checked" if args.check else "Rendered"
    print(f"{action} {result.output.as_posix()} from {result.source}")
    print(f"GPS fixes: {result.gps_fixes}")
    return 0


def _render(args: argparse.Namespace, in_place: bool, destination: Path) -> RenderResult:
    if args.gps_snapshot is None and not in_place:
        return render_entrances(
            template_path=args.template,
            output_path=args.output,
            csv_path=args.csv,
            github_repo=args.github_repo,
            check=args.check,
        )

    snapshot = (
        load_snapshot(args.gps_snapshot)
        if args.gps_snapshot is not None
        else download_snapshot(args.github_repo, destination)
    )
    identities = metadata.check() if in_place else {}
    catalogue.check_catalogue(snapshot, args.template, identities)
    if in_place:
        result = _render_checked_project(args.template, args.output, snapshot.csv_path, identities)
    else:
        result = render_entrances(
            template_path=args.template,
            output_path=args.output,
            csv_path=snapshot.csv_path,
            check=args.check,
        )
    return replace(result, source=f"{snapshot.repo}@{snapshot.tag}")


if __name__ == "__main__":
    raise SystemExit(main())
