from __future__ import annotations

from pathlib import Path

import pyogrio

from jktz.reporting import CheckFailed


def check(outdir: Path, version: str) -> None:
    """The whole-project shapefile's feature count must equal the sum across caves.

    Reads ``<outdir>/JKTZ-<version>-all.shp`` and ``<outdir>/caves/*.shp`` using
    ``pyogrio.read_info`` and compares the totals. A mismatch means the
    per-cave split lost or duplicated features in the export pipeline.
    """
    all_shp = outdir / f"JKTZ-{version}-all.shp"
    all_count = int(pyogrio.read_info(all_shp)["features"])

    caves_dir = outdir / "caves"
    sum_count = 0
    breakdown: list[str] = []
    for shp in sorted(caves_dir.glob("*.shp")):
        cave = shp.stem
        count = int(pyogrio.read_info(shp)["features"])
        sum_count += count
        breakdown.append(f"    {cave}: {count}")

    if all_count != sum_count:
        lines = [
            "ERROR: Feature count mismatch between whole-project and per-cave shapefiles:",
            f"  Whole-project (JKTZ-{version}-all.shp): {all_count}",
            f"  Sum of per-cave shapefiles:                      {sum_count}",
            f"  Difference (all - sum):                          {all_count - sum_count}",
            "",
            "  Per-cave breakdown:",
        ]
        lines.extend(breakdown)
        raise CheckFailed("\n".join(lines))
