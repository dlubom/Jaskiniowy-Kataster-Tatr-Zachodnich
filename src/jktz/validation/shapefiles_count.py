from __future__ import annotations

from pathlib import Path

from jktz.reporting import CheckFailed
from jktz.validation.shapefile import read_local_info


def check(outdir: Path, version: str) -> None:
    """The whole-project shapefile's feature count must equal the sum across caves.

    Reads ``<outdir>/JKTZ-<version>-all.shp`` and ``<outdir>/caves/*.shp`` using
    ``pyogrio.read_info`` and compares the totals. A mismatch means the
    per-cave split lost or duplicated features in the export pipeline.
    """
    all_shp = outdir / f"JKTZ-{version}-all.shp"
    all_count = int(read_local_info(all_shp)["features"])

    caves_dir = outdir / "caves"
    sum_count = 0
    breakdown: list[str] = []
    for shp in sorted(caves_dir.glob("*.shp")):
        cave = shp.stem
        count = int(read_local_info(shp)["features"])
        sum_count += count
        breakdown.append(f"    {cave}: {count}")

    difference = all_count - sum_count
    if difference == 0:
        return

    if difference > 0:
        hint = (
            "  Check the top-level cave or system prefix (before the first ':') "
            "of each missing survey. It needs a compiled ENTRANCE under that prefix.\n"
            "  For example, WielkaSniezna:Ciag:0 selects caves/WielkaSniezna.shp "
            "for all sections of the system.\n"
            "  Review #prefix/#prefix2 in survey SRVs and #flag ... /ENTRANCE in "
            "Poligony/OTWORY.SRV.j2."
        )
    else:
        hint = "  Check for overlapping --survey filters or repeated geometry in caves/*.shp."

    lines = [
        "ERROR: Feature count mismatch between whole-project and per-cave shapefiles:",
        f"  Whole-project (JKTZ-{version}-all.shp): {all_count}",
        f"  Sum of per-cave shapefiles:                      {sum_count}",
        f"  Difference (all - sum):                          {difference}",
        hint,
        "",
        "  Per-cave breakdown:",
        *breakdown,
    ]
    raise CheckFailed("\n".join(lines))
