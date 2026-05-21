from __future__ import annotations

import re
from pathlib import Path

from jktz.reporting import CheckFailed

_NOT_ATTACHED_TRIGGER_RE = re.compile(r"not attached to a (fixed|control) point")
_NOT_ATTACHED_SEPARATOR_RE = re.compile(r"not attached to a .* point")


def check(log_path: Path = Path("cavern_output.txt")) -> None:
    """Reject cavern logs that mention 'not attached to a fixed/control point'."""
    text = log_path.read_text(encoding="latin-1")
    if not _NOT_ATTACHED_TRIGGER_RE.search(text):
        return

    # Reproduce sed -n '/not attached to a .* point/,/^$/p' — print blocks
    # starting at the trigger line through the next blank line.
    block: list[str] = []
    in_block = False
    for line in text.splitlines():
        if _NOT_ATTACHED_SEPARATOR_RE.search(line):
            in_block = True
            block.append(line)
            continue
        if in_block:
            block.append(line)
            if line.strip() == "":
                in_block = False

    raise CheckFailed(
        "ERROR: Cavern detected survey stations not attached to a fixed point:\n" + "\n".join(block)
    )
