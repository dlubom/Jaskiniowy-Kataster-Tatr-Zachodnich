from __future__ import annotations

from pathlib import Path

import pyogrio
from pyogrio.errors import DataLayerError, DataSourceError

from jktz.reporting import CheckFailed


def read_local_info(path: Path) -> dict:
    """Read a local SHP and its sidecars, preserving literal filename characters."""
    for extension in (".shx", ".dbf", ".prj"):
        sidecar = path.with_suffix(extension)
        if not sidecar.is_file():
            raise CheckFailed(f"ERROR: Missing shapefile component: {sidecar}")
    # An explicit GDAL path bypasses pyogrio's archive syntax for '!'.
    # Offset zero with no length exposes the whole file.
    try:
        return pyogrio.read_info(f"/vsisubfile/0,{path.absolute().as_posix()}")
    except (DataLayerError, DataSourceError) as exc:
        raise CheckFailed(f"ERROR: Cannot read shapefile {path}: {exc}") from exc
