from __future__ import annotations

import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from jktz.exports import pipeline
from jktz.exports import tools as exports_tools
from jktz.exports.tools import ExternalToolError
from jktz.reporting import CheckFailed
from jktz.validation import (
    coordinates,
    decimal_format,
    directives,
    empty_shapefiles,
    filenames,
    non_ascii,
    prefixes,
    shapefiles_count,
    shapefiles_extent,
    unattached,
)


def _reconfigure_streams_utf8() -> None:
    # On Windows ✔ (U+2714) breaks under cp1252 when stdout is redirected.
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


def _run(step: int, header: str, footer: str, fn: Callable[[], None]) -> None:
    print(f"[{step}/10] {header}...")
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
        _run(2, "Checking for invalid directives", "Invalid directives", directives.check)
        _run(
            3,
            "Checking decimal format in numeric fields",
            "Decimal format",
            decimal_format.check,
        )
        _run(
            4,
            "Checking for non-ASCII bytes in SRV files",
            "Non-ASCII bytes",
            non_ascii.check,
        )
        _run(5, "Checking #prefix values", "#prefix values", prefixes.check)

        print("[6/10] Checking rendered entrance snapshot...")
        _run_render_check()
        print("      OK")

        _run(
            7,
            "Checking entrance coordinates are inside Tatras extent",
            "Entrance coordinates in Tatras extent",
            coordinates.check,
        )

        print("[8/10] Compiling with cavern...")
        exports_tools.cavern(["KATASTER.wpj"], log_to=cavern_log)

        _run(
            9,
            "Checking for unattached stations",
            "Unattached stations",
            lambda: unattached.check(log_path=cavern_log),
        )

        print("[10/10] Checking exports...")
        try:
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
