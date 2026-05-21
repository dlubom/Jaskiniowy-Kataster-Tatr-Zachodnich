from __future__ import annotations

import os
from pathlib import Path

from jktz.reporting import CheckFailed


def _is_allowed(b: int) -> bool:
    # TAB (9), CR (13), and printable ASCII (32-126).
    return b == 9 or b == 13 or (32 <= b <= 126)


def check(root: Path = Path("Poligony")) -> None:
    """Reject non-ASCII bytes in SRV filenames, directory names, and SRV content.

    Walls' file paths and survey text require ASCII (CLAUDE.md:128). Bytes
    outside ``[TAB, CR, printable ASCII]`` are flagged. Excludes ``_RAW/``.
    """
    path_errors: list[str] = []
    content_errors: list[str] = []

    for path in root.rglob("*"):
        parts = path.parts
        if "_RAW" in parts:
            continue
        # Scan the basename byte-by-byte. fsencode round-trips the platform
        # filesystem name back to its on-disk byte sequence.
        base_bytes = os.fsencode(path.name)
        for col, byte in enumerate(base_bytes, start=1):
            if _is_allowed(byte):
                continue
            path_errors.append(f"  {path.as_posix()}  byte 0x{byte:02x} at col {col} (path)")
            break

    for path in root.rglob("*.SRV"):
        if "_RAW" in path.parts:
            continue
        with path.open("rb") as f:
            for line_num, line in enumerate(f, start=1):
                # awk reads up to LF and leaves the line WITHOUT it; CR may
                # still be present and is allowed by the check.
                line = line.rstrip(b"\n")
                for col, byte in enumerate(line, start=1):
                    if _is_allowed(byte):
                        continue
                    content_errors.append(
                        f"  {path.as_posix()}:{line_num}  byte 0x{byte:02x} at col {col}"
                    )
                    break

    if path_errors or content_errors:
        lines = [
            "ERROR: non-ASCII byte(s) found in SRV files or paths "
            "(use ASCII equivalents per CLAUDE.md):"
        ]
        lines.extend(path_errors)
        lines.extend(content_errors)
        raise CheckFailed("\n".join(lines))
