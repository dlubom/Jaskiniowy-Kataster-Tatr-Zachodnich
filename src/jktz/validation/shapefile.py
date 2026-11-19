from __future__ import annotations

import struct
from pathlib import Path

import pyogrio
import pyogrio.raw
from pyogrio.errors import DataLayerError, DataSourceError

from jktz.reporting import CheckFailed

_EXPORT_FIELDS = ("Layer", "PaperSpace", "SubClasses", "Linetype", "EntHandle", "Text")
# Older GDAL drivers store the DXF PaperSpace flag as a DBF integer.
_EXPORT_DTYPES = {
    ("object", flag, "object", "object", "object", "object") for flag in ("bool", "int32", "int64")
}


def _check_export_dbf(dbf: Path, info: dict) -> None:
    # A DBF stores the row count, header size and fixed row size at offsets 4-11.
    # GDAL may silently read only as many rows as there are SHP geometries.
    with dbf.open("rb") as stream:
        header = stream.read(12)
    if len(header) < 12:
        raise CheckFailed(f"ERROR: Incomplete DBF header in {dbf}")
    rows, header_size, row_size = struct.unpack("<4xIHH", header)
    required = header_size + rows * row_size
    size = dbf.stat().st_size
    if rows != info["features"] or size < required:
        raise CheckFailed(
            f"ERROR: {dbf} declares {rows} records for {info['features']} shapes "
            f"and requires {required} bytes (found {size})."
        )

    fields, dtypes = tuple(info["fields"]), tuple(info["dtypes"])
    if fields != _EXPORT_FIELDS or dtypes not in _EXPORT_DTYPES:
        raise CheckFailed(f"ERROR: Unexpected DXF fields in {dbf}: {list(zip(fields, dtypes))}")


def read_local_info(path: Path, *, verify_export: bool = False) -> dict:
    """Read a local SHP and its sidecars, preserving literal filename characters."""
    for extension in (".shx", ".dbf", ".prj"):
        sidecar = path.with_suffix(extension)
        if not sidecar.is_file():
            raise CheckFailed(f"ERROR: Missing shapefile component: {sidecar}")
    # An explicit GDAL path bypasses pyogrio's archive syntax for '!'.
    # Offset zero with no length exposes the whole file.
    source = f"/vsisubfile/0,{path.absolute().as_posix()}"
    try:
        info = pyogrio.read_info(source)
        if verify_export:
            dbf = path.with_suffix(".dbf")
            _check_export_dbf(dbf, info)
            _, _, geometries, _ = pyogrio.raw.read(source)
            if len(geometries) != info["features"]:
                raise CheckFailed(f"ERROR: Expected {info['features']} readable records in {dbf}")
            if None in geometries:
                raise CheckFailed(f"ERROR: Null or unreadable geometry in {path}")
        return info
    except (DataLayerError, DataSourceError) as exc:
        raise CheckFailed(f"ERROR: Cannot read shapefile {path}: {exc}") from exc
