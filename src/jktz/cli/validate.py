from __future__ import annotations

import sys
from collections.abc import Callable

from jktz.reporting import CheckFailed
from jktz.validation import (
    coordinates,
    decimal_format,
    directives,
    filenames,
    non_ascii,
    prefixes,
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


def main() -> int:
    _reconfigure_streams_utf8()
    print("=== Validation Started ===")
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
        print("      (deferred - run scripts/render_otwory_from_gps.py --check separately)")

        _run(
            7,
            "Checking entrance coordinates are inside Tatras extent",
            "Entrance coordinates in Tatras extent",
            coordinates.check,
        )

        print("[8/10] Compiling with cavern...")
        print("      (deferred to phase 4)")
        print("[9/10] Checking for unattached stations...")
        print("      (deferred to phase 4 - requires cavern log)")
        print("[10/10] Checking exports...")
        print("      (deferred to phases 3 + 4)")
    except CheckFailed as exc:
        print(str(exc))
        return 1

    print()
    print("=== Validation Passed ✔ ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
