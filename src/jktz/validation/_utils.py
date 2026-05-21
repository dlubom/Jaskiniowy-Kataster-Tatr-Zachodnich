from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path


def srv_files(root: Path) -> Iterable[Path]:
    """Yield every ``*.SRV`` file under ``root``, excluding ``_RAW/`` subtrees."""
    for path in root.rglob("*.SRV"):
        if "_RAW" in path.parts:
            continue
        yield path
