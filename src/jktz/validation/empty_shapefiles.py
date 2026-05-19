from __future__ import annotations

from pathlib import Path

from jktz.reporting import CheckFailed

# An empty ESRI Shapefile is exactly 100 bytes — just the header, no features.
_EMPTY_SHAPEFILE_SIZE = 100


def check(outdir: Path) -> None:
    """Reject any zero-feature shapefile produced by the export pipeline."""
    empty: list[str] = []
    for path in outdir.rglob("*.shp"):
        if path.is_file() and path.stat().st_size == _EMPTY_SHAPEFILE_SIZE:
            empty.append(f"  {path.as_posix()}")
    if empty:
        raise CheckFailed("ERROR: Detected empty Shapefiles:\n" + "\n".join(empty))
