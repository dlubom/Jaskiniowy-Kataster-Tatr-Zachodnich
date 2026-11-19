from __future__ import annotations

import contextlib
import sys
import tempfile
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from typing import TextIO

from jktz.entrances.render import (
    DEFAULT_GITHUB_REPO,
    DEFAULT_TEMPLATE,
    RenderError,
    render_entrances,
)
from jktz.exports import pipeline
from jktz.gps_catalog import GpsSnapshot, download_snapshot, load_snapshot
from jktz.metadata.identity import SurveyIdentity
from jktz.reporting import CheckFailed
from jktz.validation import (
    catalogue,
    cavern_warnings,
    coordinates,
    decimal_format,
    directives,
    filenames,
    metadata,
    non_ascii,
    prefixes,
    unattached,
)

_EXPORTS_INDENT = " " * 19


@dataclass(frozen=True)
class ValidationContext:
    """Paths and labels shared by checks that exchange generated artefacts."""

    cavern_log: Path = Path("cavern_output.txt")
    exports_dir: Path = Path("validate-exports")
    exports_version: str = "validate"
    gps_snapshot: Path | None = None
    keep_exports: bool = False


@dataclass(frozen=True)
class ValidationStep:
    """One user-visible validation step."""

    heading: str
    success: str | None
    check: Callable[[], None]


class _IndentingStream:
    """Prefix each output line while preserving the wrapped stream interface."""

    def __init__(self, target: TextIO, prefix: str) -> None:
        self._target = target
        self._prefix = prefix
        self._at_line_start = True

    def write(self, value: str) -> int:
        if not value:
            return 0

        parts: list[str] = []
        for line in value.splitlines(keepends=True):
            if self._at_line_start:
                parts.append(self._prefix)
            parts.append(line)
            self._at_line_start = line.endswith(("\n", "\r"))
        return self._target.write("".join(parts))

    def flush(self) -> None:
        self._target.flush()

    def __getattr__(self, name: str):  # type: ignore[override]
        return getattr(self._target, name)


@contextlib.contextmanager
def _indent_stdout(prefix: str = _EXPORTS_INDENT) -> Iterator[None]:
    original = sys.stdout
    sys.stdout = _IndentingStream(original, prefix)  # type: ignore[assignment]
    try:
        yield
    finally:
        sys.stdout = original


def _check_rendered_entrances(snapshot: GpsSnapshot) -> None:
    try:
        result = render_entrances(check=True, csv_path=snapshot.csv_path)
    except (OSError, RenderError) as exc:
        raise CheckFailed(f"ERROR: entrance snapshot check failed: {exc}") from exc

    print(f"Checked {result.output.as_posix()} from {result.source}")
    print(f"Rendered gps_fix calls: {result.gps_fixes}")


def _check_exports(context: ValidationContext) -> None:
    with _indent_stdout():
        pipeline.export_formats(
            version=context.exports_version,
            outdir=context.exports_dir,
        )


def validation_steps(
    context: ValidationContext, snapshot: GpsSnapshot
) -> tuple[ValidationStep, ...]:
    """Build the checks around one release and one set of survey identities."""
    identities: dict[Path, SurveyIdentity] = {}
    compiled = context.exports_dir / f"JKTZ-{context.exports_version}.3d"
    compile_log = context.exports_dir / f"JKTZ-{context.exports_version}-cavern-log.txt"

    def check_metadata() -> None:
        identities.update(metadata.check())

    def check_catalogue() -> None:
        catalogue.check_catalogue(snapshot, DEFAULT_TEMPLATE, identities)

    return (
        ValidationStep(
            "Checking SRV filenames format",
            "SRV filenames format",
            filenames.check,
        ),
        ValidationStep(
            "Checking SRV metadata contract",
            "SRV metadata contract",
            check_metadata,
        ),
        ValidationStep(
            "Checking for invalid directives",
            "Invalid directives",
            directives.check,
        ),
        ValidationStep(
            "Checking decimal format in numeric fields",
            "Decimal format",
            decimal_format.check,
        ),
        ValidationStep(
            "Checking for non-ASCII bytes in SRV files",
            "Non-ASCII bytes",
            non_ascii.check,
        ),
        ValidationStep(
            "Checking #prefix values",
            "#prefix values",
            prefixes.check,
        ),
        ValidationStep(
            "Checking GPS catalogue references",
            "GPS catalogue references",
            check_catalogue,
        ),
        ValidationStep(
            "Checking rendered entrances snapshot",
            "Rendered entrances snapshot",
            lambda: _check_rendered_entrances(snapshot),
        ),
        ValidationStep(
            "Checking entrance coordinates are inside Tatras extent",
            "Entrance coordinates in Tatras extent",
            coordinates.check,
        ),
        ValidationStep(
            "Compiling with cavern",
            None,
            lambda: pipeline.compile_model(
                context.exports_version, context.exports_dir, log_to=context.cavern_log
            ),
        ),
        ValidationStep(
            "Checking for unattached stations",
            "Unattached stations",
            lambda: unattached.check(log_path=compile_log),
        ),
        ValidationStep(
            "Checking cavern compile warnings",
            "Cavern compile warnings",
            lambda: cavern_warnings.check(log_path=compile_log),
        ),
        ValidationStep(
            "Checking compiled station references",
            "Compiled station references",
            lambda: catalogue.check_compiled_references(compiled, identities),
        ),
        ValidationStep(
            "Checking exports",
            "Exports",
            lambda: _check_exports(context),
        ),
    )


def run_steps(steps: Sequence[ValidationStep]) -> None:
    """Run steps with numbering derived from the actual validation contract."""
    total = len(steps)
    for number, step in enumerate(steps, start=1):
        print(f"[{number}/{total}] {step.heading}...")
        step.check()
        if step.success is not None:
            print(f"      {step.success}: Passed ✔")


def run_validation(context: ValidationContext | None = None) -> None:
    """Run the complete repository validation suite and remove temporary exports."""
    context = context or ValidationContext()
    if context.exports_dir.exists():
        raise CheckFailed(
            f"ERROR: validation output already exists: {context.exports_dir}; "
            "choose an unused directory or move the existing files first"
        )
    # Only publish after all checks. A discarded run only cleans its own directory.
    parent = context.exports_dir.parent if context.keep_exports else None
    with tempfile.TemporaryDirectory(prefix=".jktz-validation-", dir=parent) as directory:
        snapshot = _prepare_snapshot(context.gps_snapshot, Path(directory) / "gps")
        staging = Path(directory) / "checked"
        run_steps(validation_steps(replace(context, exports_dir=staging), snapshot))
        if context.keep_exports:
            staging.rename(context.exports_dir)


def _prepare_snapshot(source: Path | None, destination: Path) -> GpsSnapshot:
    try:
        snapshot = (
            load_snapshot(source)
            if source is not None
            else download_snapshot(DEFAULT_GITHUB_REPO, destination)
        )
    except (OSError, ValueError) as exc:
        raise CheckFailed(f"ERROR: GPS snapshot: {exc}") from exc
    print(f"GPS snapshot: {snapshot.repo}@{snapshot.tag} (release ID: {snapshot.release_id})")
    print(f"  Best CSV SHA-256: {snapshot.csv_sha256}")
    print(f"  Catalogue SHA-256: {snapshot.gpkg_sha256}")
    return snapshot
