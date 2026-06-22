from __future__ import annotations

from pathlib import Path

from jktz.reporting import CheckFailed
from jktz.validation._utils import srv_files


def check(root: Path = Path("Poligony")) -> None:
    """No ``#<`` directive should appear in non-archival ``*.SRV`` files."""
    matches: list[str] = []
    for path in srv_files(root):
        # latin-1 maps every byte 1:1 to a codepoint; "#<" is pure ASCII so a
        # substring match is byte-equivalent regardless of file encoding.
        text = path.read_text(encoding="latin-1")
        for line in text.splitlines():
            if "#<" in line:
                matches.append(f"{path.as_posix()}:{line}")
    if matches:
        raise CheckFailed("ERROR: Invalid #< directive found\n" + "\n".join(matches))
