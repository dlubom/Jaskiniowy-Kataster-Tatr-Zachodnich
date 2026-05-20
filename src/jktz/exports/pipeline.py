from __future__ import annotations

import csv
import shutil
import tempfile
import time
from pathlib import Path

from jktz.exports import tools


def _wait_for_readable(path: Path, timeout: float = 30.0, interval: float = 0.1) -> None:
    """Poll until ``path`` exists with stable size and is openable for read.

    On Windows, subprocess.run can return before the OS / antivirus has made a
    newly-written file accessible to other processes, so a subsequent ogr2ogr
    call may see ``Unable to open datasource``. We wait for two consecutive
    stable-size readings + a successful open before declaring the file ready.
    On Linux/Docker the first iteration succeeds, so this is essentially a no-op.
    """
    deadline = time.monotonic() + timeout
    last_size = -1
    stable = 0
    while time.monotonic() < deadline:
        try:
            size = path.stat().st_size
            if size > 0 and size == last_size:
                stable += 1
                if stable >= 2:
                    try:
                        with path.open("rb") as f:
                            f.read(1)
                        return
                    except OSError:
                        pass
            else:
                stable = 0
            last_size = size
        except FileNotFoundError:
            pass
        time.sleep(interval)
    raise TimeoutError(f"file not settled within {timeout}s: {path}")


# Field rename to fit Shapefile/DBF 10-char field-name limit; matches the
# exports.sh -sql clause verbatim.
_SHP_SQL = (
    "SELECT Layer, PaperSpace, SubClasses, Linetype, EntityHandle AS EntHandle, Text FROM entities"
)


def _cave_names_from_entrances_csv(csv_path: Path) -> list[str]:
    """Return sorted unique cave prefixes from survexport's --entrances CSV.

    Column 4 is the entrance station name like ``Marmurowa:0`` or
    ``WielkaSniezna:Ciag:0``. The cave name is the part before the first ``:``.

    Survex 1.4.20 had a bug where this CSV column used ``.`` as the separator
    on Windows; the per-cave loop relies on ``:`` so Survex >= 1.4.21 is
    required for local runs. CI/Docker pins SURVEX_COMMIT to a fixed version
    via the workflow, so this only affects developer machines.
    """
    caves: set[str] = set()
    with csv_path.open(encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header row
        for row in reader:
            if len(row) < 4:
                continue
            name = row[3].split(":", 1)[0]
            if name:
                caves.add(name)
    return sorted(caves)


def run_exports(
    version: str = "local",
    outdir: Path = Path("exports"),
    cwd: Path | None = None,
) -> None:
    """Compile KATASTER.wpj and write .3d, .dxf, .shp release artefacts.

    Mirrors exports.sh step-for-step:
      1. cavern KATASTER.wpj                  → .3d, .err, cavern-log.txt
      2. survexport --legs --dxf              → JKTZ-<version>.dxf
      3. ogr2ogr DXF → ESRI Shapefile         → JKTZ-<version>-all.shp
      4. survexport --entrances → cave list
         per cave: survexport --survey filter + ogr2ogr → caves/<cave>.shp
    """
    # Resolve to absolute paths so every arg passed to subprocess is absolute -
    # the Survex Windows launcher resolves some paths against argv[0]/cwd
    # inconsistently, and absolute paths sidestep the whole class of issues.
    outdir = Path(outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "caves").mkdir(exist_ok=True)

    print(f"=== JKTZ exports - version: {version} ===")
    print(f"    output: {outdir.as_posix()}/")
    print()

    print("[1/4] cavern - compiling survey network")
    cavern_log = outdir / f"JKTZ-{version}-cavern-log.txt"
    tools.cavern(["KATASTER.wpj"], cwd=cwd, log_to=cavern_log)
    project_root = cwd if cwd else Path.cwd()
    shutil.copy(project_root / "KATASTER.3d", outdir / f"JKTZ-{version}.3d")
    shutil.copy(project_root / "KATASTER.err", outdir / f"JKTZ-{version}.err")
    compiled_3d = outdir / f"JKTZ-{version}.3d"

    print("[2/4] survexport - full DXF")
    full_dxf = outdir / f"JKTZ-{version}.dxf"
    tools.survexport(
        ["--legs", "--full-coordinates", "--dxf", str(compiled_3d), str(full_dxf)],
        cwd=cwd,
    )
    _wait_for_readable(full_dxf)

    print("[3/4] ogr2ogr - shapefile (all caves)")
    all_shp = outdir / f"JKTZ-{version}-all.shp"
    tools.ogr2ogr(
        [
            "-f",
            "ESRI Shapefile",
            "-dim",
            "XYZ",
            "-a_srs",
            "EPSG:32634",
            "-sql",
            _SHP_SQL,
            str(all_shp),
            str(full_dxf),
        ],
        cwd=cwd,
    )

    print("[4/4] survexport - per-cave DXF + shapefiles")
    with tempfile.TemporaryDirectory(prefix="jktz-exports-", dir=outdir) as tmp_str:
        tmp = Path(tmp_str)
        entrances_csv = tmp / "entrances.csv"
        tools.survexport(
            ["--entrances", "--csv", str(compiled_3d), str(entrances_csv)],
            cwd=cwd,
        )
        _wait_for_readable(entrances_csv)
        for cave in _cave_names_from_entrances_csv(entrances_csv):
            print(f"      -> {cave}")
            cave_dxf = tmp / f"{cave}.dxf"
            tools.survexport(
                [
                    "--legs",
                    "--full-coordinates",
                    f"--survey={cave}",
                    "--dxf",
                    str(compiled_3d),
                    str(cave_dxf),
                ],
                cwd=cwd,
            )
            _wait_for_readable(cave_dxf)
            tools.ogr2ogr(
                [
                    "-f",
                    "ESRI Shapefile",
                    "-dim",
                    "XYZ",
                    "-a_srs",
                    "EPSG:32634",
                    "-sql",
                    _SHP_SQL,
                    str(outdir / "caves" / f"{cave}.shp"),
                    str(cave_dxf),
                ],
                cwd=cwd,
            )
    print()
    print("=== Done ===")
    print(f"    {outdir.as_posix()}/")
