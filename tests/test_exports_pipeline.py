from __future__ import annotations

from pathlib import Path

import pytest

from jktz.exports import pipeline


@pytest.fixture
def call_log(monkeypatch, tmp_path: Path) -> list[tuple[str, list[str]]]:
    """Capture every cavern/survexport/ogr2ogr invocation as (tool, args)."""
    calls: list[tuple[str, list[str]]] = []

    def fake_cavern(args, cwd=None, log_to=None):
        calls.append(("cavern", list(args)))
        if log_to is not None:
            log_to.write_text("fake cavern log\n")
        # Simulate cavern's KATASTER.3d / KATASTER.err side effects.
        root = Path(cwd) if cwd else Path.cwd()
        (root / "KATASTER.3d").write_bytes(b"fake-3d")
        (root / "KATASTER.err").write_bytes(b"fake-err")

    def fake_survexport(args, cwd=None):
        calls.append(("survexport", list(args)))
        # If this is the --entrances --csv call, write a tiny CSV so the
        # pipeline can parse cave names from it.
        if "--entrances" in args and "--csv" in args:
            csv_path = Path(args[-1])
            csv_path.write_text("Name,X,Y,Station,Z\nA,1,2,CaveA:0,3\nB,4,5,CaveB:0,6\n")
        # For each per-cave --dxf call, create an empty output file so ogr2ogr
        # has something to read on the next step.
        if "--dxf" in args:
            out = Path(args[-1])
            out.write_bytes(b"fake-dxf")

    def fake_ogr2ogr(args, cwd=None):
        calls.append(("ogr2ogr", list(args)))

    monkeypatch.setattr(pipeline.tools, "cavern", fake_cavern)
    monkeypatch.setattr(pipeline.tools, "survexport", fake_survexport)
    monkeypatch.setattr(pipeline.tools, "ogr2ogr", fake_ogr2ogr)
    monkeypatch.chdir(tmp_path)
    return calls


def test_pipeline_invokes_all_4_steps_in_order(call_log, tmp_path: Path) -> None:
    pipeline.run_exports(version="v1", outdir=Path("exports"))

    tools_in_order = [t for t, _ in call_log]
    # First call must be cavern, then a single survexport DXF, then ogr2ogr,
    # then survexport --entrances, then per-cave survexport+ogr2ogr pairs.
    assert tools_in_order[0] == "cavern"
    assert tools_in_order[1] == "survexport"
    assert tools_in_order[2] == "ogr2ogr"
    assert tools_in_order[3] == "survexport"  # --entrances
    # 2 caves in fake CSV -> 2 (survexport, ogr2ogr) pairs after that.
    assert tools_in_order[4:] == ["survexport", "ogr2ogr", "survexport", "ogr2ogr"]


def test_pipeline_passes_correct_cavern_args(call_log, tmp_path: Path) -> None:
    pipeline.run_exports(version="v1", outdir=Path("exports"))
    cavern_args = next(args for tool, args in call_log if tool == "cavern")
    assert cavern_args == ["KATASTER.wpj"]


def test_pipeline_passes_correct_survexport_full_dxf_args(call_log, tmp_path: Path) -> None:
    pipeline.run_exports(version="v1", outdir=Path("exports"))
    # First survexport call is the full DXF.
    survexport_calls = [args for tool, args in call_log if tool == "survexport"]
    full_dxf = survexport_calls[0]
    assert "--legs" in full_dxf
    assert "--full-coordinates" in full_dxf
    assert "--dxf" in full_dxf
    assert full_dxf[-1].endswith("JKTZ-v1.dxf")


def test_pipeline_passes_correct_ogr2ogr_sql_clause(call_log, tmp_path: Path) -> None:
    pipeline.run_exports(version="v1", outdir=Path("exports"))
    ogr2ogr_args = next(args for tool, args in call_log if tool == "ogr2ogr")
    # SQL clause is in -sql + next arg
    sql_idx = ogr2ogr_args.index("-sql")
    assert "EntityHandle AS EntHandle" in ogr2ogr_args[sql_idx + 1]
    assert "FROM entities" in ogr2ogr_args[sql_idx + 1]
    # And the CRS is EPSG:32634
    crs_idx = ogr2ogr_args.index("-a_srs")
    assert ogr2ogr_args[crs_idx + 1] == "EPSG:32634"


def test_pipeline_creates_per_cave_outputs(call_log, tmp_path: Path) -> None:
    pipeline.run_exports(version="v1", outdir=Path("exports"))
    # Per-cave ogr2ogr calls (after the first one) target caves/<name>.shp
    ogr2ogr_calls = [args for tool, args in call_log if tool == "ogr2ogr"]
    per_cave = ogr2ogr_calls[1:]
    assert len(per_cave) == 2  # CaveA + CaveB from fake CSV
    targets = {args[-2] for args in per_cave}  # arg before the DXF input
    assert any("caves/CaveA.shp" in t.replace("\\", "/") for t in targets)
    assert any("caves/CaveB.shp" in t.replace("\\", "/") for t in targets)


def test_pipeline_creates_outdir_and_caves_subdir(call_log, tmp_path: Path) -> None:
    outdir = Path("custom-exports")
    pipeline.run_exports(version="v1", outdir=outdir)
    assert outdir.is_dir()
    assert (outdir / "caves").is_dir()
