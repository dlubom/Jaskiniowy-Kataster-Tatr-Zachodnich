from __future__ import annotations

import contextlib
import shutil
import subprocess
import sys
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import TextIO

from jktz.exports import pipeline
from jktz.exports import tools as exports_tools
from jktz.exports.tools import ExternalToolError
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

_EXPORTS_INDENT = " " * 19  # matches the original bash `sed 's/^/<19 spaces>/'`
_TOTAL_STEPS = 12


class _IndentingStream:
    """Wrap a stream and prefix every line with ``prefix`` on write.

    Mirrors the bash idiom ``... | sed 's/^/<spaces>/'`` we used to apply to
    exports.sh output, so step 10's exports pipeline (which is loud) stands
    out from the rest of the validation log. Forwards every other attribute
    to the wrapped stream so existing callers (flush, encoding, fileno, …)
    keep working.
    """

    def __init__(self, target: TextIO, prefix: str) -> None:
        self._target = target
        self._prefix = prefix
        self._at_line_start = True

    def write(self, text: str) -> int:
        if not text:
            return 0
        out_parts: list[str] = []
        for line in text.splitlines(keepends=True):
            if self._at_line_start:
                out_parts.append(self._prefix)
            out_parts.append(line)
            self._at_line_start = line.endswith(("\n", "\r"))
        return self._target.write("".join(out_parts))

    def flush(self) -> None:
        self._target.flush()

    def __getattr__(self, name: str):  # type: ignore[override]
        return getattr(self._target, name)


@contextlib.contextmanager
def _indent_stdout(prefix: str = _EXPORTS_INDENT) -> Iterator[None]:
    """Indent every line printed during the ``with`` block by ``prefix``."""
    original = sys.stdout
    sys.stdout = _IndentingStream(original, prefix)  # type: ignore[assignment]
    try:
        yield
    finally:
        sys.stdout = original


def _reconfigure_streams_utf8() -> None:
    # On Windows ✔ (U+2714) breaks under cp1252 when stdout is redirected.
    # line_buffering=True flushes on every newline even when stdout isn't a
    # TTY. Without this, Windows block-buffers stdout in CI and the [N/10]
    # progress lines only appear at the end of the job (Linux line-buffers by
    # default, hence the historical asymmetry).
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace", line_buffering=True)


def _run(step: int, header: str, footer: str, fn: Callable[[], None]) -> None:
    print(f"[{step}/{_TOTAL_STEPS}] {header}...")
    fn()
    print(f"      {footer}: Passed ✔")


def _run_render_check() -> None:
    """Step 6: subprocess to scripts/render_otwory_from_gps.py --check."""
    script = Path("scripts") / "render_otwory_from_gps.py"
    proc = subprocess.run([sys.executable, str(script), "--check"], check=False)
    if proc.returncode != 0:
        raise CheckFailed(
            f"ERROR: render_otwory_from_gps.py --check failed (exit {proc.returncode})"
        )


def main() -> int:
    _reconfigure_streams_utf8()
    print("=== Validation Started ===")
    cavern_log = Path("cavern_output.txt")
    exports_dir = Path("validate-exports")
    exports_version = "validate"

    try:
        _run(1, "Checking SRV filenames format", "SRV filenames format", filenames.check)
        _run(2, "Checking SRV metadata contract", "SRV metadata contract", metadata.check)
        _run(3, "Checking for invalid directives", "Invalid directives", directives.check)
        _run(
            4,
            "Checking decimal format in numeric fields",
            "Decimal format",
            decimal_format.check,
        )
        _run(
            5,
            "Checking for non-ASCII bytes in SRV files",
            "Non-ASCII bytes",
            non_ascii.check,
        )
        _run(6, "Checking #prefix values", "#prefix values", prefixes.check)

        print(f"[7/{_TOTAL_STEPS}] Checking rendered entrances snapshot...")
        _run_render_check()
        print("      Rendered entrances snapshot: Passed ✔")

        _run(
            8,
            "Checking entrance coordinates are inside Tatras extent",
            "Entrance coordinates in Tatras extent",
            coordinates.check,
        )

        print(f"[9/{_TOTAL_STEPS}] Compiling with cavern...")
        exports_tools.cavern(["KATASTER.wpj"], log_to=cavern_log)

        _run(
            10,
            "Checking for unattached stations",
            "Unattached stations",
            lambda: unattached.check(log_path=cavern_log),
        )

        _run(
            11,
            "Checking cavern compile warnings",
            "Cavern compile warnings",
            lambda: cavern_warnings.check(log_path=cavern_log),
        )

        print(f"[12/{_TOTAL_STEPS}] Checking exports...")
        try:
            with _indent_stdout():
                pipeline.run_exports(version=exports_version, outdir=exports_dir)
            empty_shapefiles.check(outdir=exports_dir)
            shapefiles_count.check(outdir=exports_dir, version=exports_version)
            shapefiles_extent.check(outdir=exports_dir, version=exports_version)
            print("      Exports: Passed ✔")
        finally:
            if exports_dir.exists():
                shutil.rmtree(exports_dir, ignore_errors=True)

    except CheckFailed as exc:
        print(str(exc))
        return 1
    except ExternalToolError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print()
    print("=== Validation Passed ✔ ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
