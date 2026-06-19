from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path


def is_raw_path(path: Path) -> bool:
    """Return whether ``path`` belongs to an archival ``_RAW`` subtree."""
    return "_RAW" in path.parts


def non_raw_paths(root: Path, pattern: str = "*") -> Iterable[Path]:
    """Yield paths matching ``pattern`` outside archival ``_RAW`` subtrees."""
    for path in root.rglob(pattern):
        if not is_raw_path(path):
            yield path


def srv_files(root: Path) -> Iterable[Path]:
    """Yield every ``*.SRV`` file under ``root`` outside ``_RAW`` subtrees."""
    return non_raw_paths(root, "*.SRV")
