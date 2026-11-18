from __future__ import annotations

from pathlib import Path

import pyogrio


def read_local_info(path: Path) -> dict:
    """Read a local SHP and its sidecars, preserving literal filename characters."""
    # An explicit GDAL path bypasses pyogrio's archive syntax for '!'.
    # Offset zero with no length exposes the whole file.
    return pyogrio.read_info(f"/vsisubfile/0,{path.absolute().as_posix()}")
