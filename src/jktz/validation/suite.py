from __future__ import annotations

import contextlib
import shutil
import subprocess
import sys
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

from jktz.exports import pipeline
from jktz.exports import tools as exports_tools
from jktz.reporting import CheckFailed
from jktz.validation import (
    cavern_warnings,
    coordinates,
    decimal_format,
    directives,
    empty_shapefiles,
    filenames,
    metadata,
    non_ascii,
    prefixes,
    shapefiles_count,
    shapefiles_extent,
    unattached,
)

_EXPORTS_INDENT = " " * 19


@dataclass(frozen=True)
class ValidationContext:
    """Paths and labels shared by checks that exchange generated artefacts."""

    cavern_log: Path = Path("cavern_output.txt")
    exports_dir: Path = Path("validate-exports")
    exports_version: str = "validate"


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


def _check_rendered_entrances() -> None:
    script = Path("scripts") / "render_otwory_from_gps.py"
    proc = subprocess.run([sys.executable, str(script), "--check"], check=False)
    if proc.returncode != 0:
        raise CheckFailed(
            f"ERROR: render_otwory_from_gps.py --check failed (exit {proc.returncode})"
        )


def _check_exports(context: ValidationContext) -> None:
    with _indent_stdout():
        pipeline.run_exports(
            version=context.exports_version,
            outdir=context.exports_dir,
        )
    empty_shapefiles.check(outdir=context.exports_dir)
    shapefiles_count.check(
        outdir=context.exports_dir,
        version=context.exports_version,
    )
    shapefiles_extent.check(
        outdir=context.exports_dir,
        version=context.exports_version,
    )


def validation_steps(context: ValidationContext) -> tuple[ValidationStep, ...]:
    """Build the ordered validation contract from small, independently testable steps."""
    return (
        ValidationStep(
            "Checking SRV filenames format",
            "SRV filenames format",
            filenames.check,
        ),
        ValidationStep(
            "Checking SRV metadata contract",
            "SRV metadata contract",
            metadata.check,
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
            "Checking rendered entrances snapshot",
            "Rendered entrances snapshot",
            _check_rendered_entrances,
        ),
        ValidationStep(
            "Checking entrance coordinates are inside Tatras extent",
            "Entrance coordinates in Tatras extent",
            coordinates.check,
        ),
        ValidationStep(
            "Compiling with cavern",
            None,
            lambda: exports_tools.cavern(["KATASTER.wpj"], log_to=context.cavern_log),
        ),
        ValidationStep(
            "Checking for unattached stations",
            "Unattached stations",
            lambda: unattached.check(log_path=context.cavern_log),
        ),
        ValidationStep(
            "Checking cavern compile warnings",
            "Cavern compile warnings",
            lambda: cavern_warnings.check(log_path=context.cavern_log),
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
    try:
        run_steps(validation_steps(context))
    finally:
        if context.exports_dir.exists():
            shutil.rmtree(context.exports_dir, ignore_errors=True)
