from __future__ import annotations

import re
from pathlib import Path

from jktz.reporting import CheckFailed

_WARNING_LINE_RE = re.compile(r"\bwarning\s*:", re.IGNORECASE)
_WARNING_COUNT_RE = re.compile(
    r"\b[1-9][0-9]*\s+warning(?:\(s\)|s)?(?=\W|$)",
    re.IGNORECASE,
)


def _warning_lines(text: str) -> list[str]:
    return [
        line
        for line in text.splitlines()
        if _WARNING_LINE_RE.search(line) or _WARNING_COUNT_RE.search(line)
    ]


def check(log_path: Path = Path("cavern_output.txt")) -> None:
    """Reject cavern logs with any compile warnings."""
    text = log_path.read_bytes().decode("utf-8", errors="replace")
    warnings = _warning_lines(text)
    if not warnings:
        return

    raise CheckFailed(
        "ERROR: Cavern emitted warnings during survey compilation:\n"
        + "\n".join(f"  {line}" for line in warnings)
    )
