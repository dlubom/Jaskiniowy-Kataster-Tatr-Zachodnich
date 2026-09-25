"""P06 compiler failures, completeness and independent native fixture checks."""

from __future__ import annotations

import json
import os
import shutil
import struct
import subprocess
from pathlib import Path

import pytest

from jktz.pockettopo import SurveyExport, compilation, export_surveys

CASES = Path(__file__).resolve().parents[1] / "doc/pockettopo/evidence/p01/cases"


def _export(*, kind="nonempty", repeated=False):
    groups = [
        {"id": 0, "kind": "leg", "from_raw": 10, "to_raw": 20, "export": {"status": "exported"}},
        {"id": 1, "kind": "splay", "from_raw": 20, "to_raw": -1, "export": {"status": "exported"}},
        {
            "id": 2,
            "kind": "zero_link",
            "from_raw": 20,
            "to_raw": 30,
            "export": {"status": "exported"},
        },
        {"id": 3, "kind": "leg", "from_raw": 30, "to_raw": 40, "export": {"status": "held"}},
    ]
    if kind == "empty":
        groups = []
    elif kind == "constraints_only":
        groups = [groups[2]]
    if repeated:
        groups.append({**groups[0], "id": 4})
    report = {
        "groups": groups,
        "station_map": [
            {"raw": raw, "walls_name": walls, "survex_name": survex}
            for raw, walls, survex in [
                (10, "a", "alpha"),
                (20, "b", "beta"),
                (30, "c", "gamma"),
                (40, "d", "delta"),
            ]
        ],
        "exports": {"geometry_status": kind},
    }
    return SurveyExport({}, report, "; Test source\n", "; Test source\n")


def _dump(kind, *, offset=0, mode="ok"):
    names = ["a", "b", "c"] if kind == "SRV" else ["alpha", "beta", "gamma"]
    positions = [
        (offset, offset, offset),
        (offset, 10 + offset, offset),
        (offset, 10 + offset, offset),
    ]
    if mode == "different" and kind == "svx":
        positions[1] = (offset, 11 + offset, offset)
    if mode == "bad_constraint":
        positions[2] = (offset, 11 + offset, offset)
    nodes = [
        f"NODE {' '.join(map(str, position))} [{name}]" for name, position in zip(names, positions)
    ]
    legs = [
        f"LEG {offset} {offset} {offset} {offset} {offset + 10} {offset} [] STYLE=NORMAL",
        f"LEG {offset} {offset + 10} {offset} {offset + 1} {offset + 10} {offset} [] SPLAY",
    ]
    if mode == "missing_station":
        nodes.pop()
    elif mode == "unexpected_station":
        nodes.append("NODE 0 0 0 [unexpected]")
    elif mode == "missing_leg":
        legs.pop(0)
    elif mode == "missing_splay":
        legs.pop()
    elif mode == "extra_leg":
        legs.append(legs[0])
    elif mode == "bad_edge":
        legs[0] = "LEG 0 0 0 0 11 0 [] STYLE=NORMAL"
    elif mode == "bad_splay_anchor":
        legs[1] = "LEG 9 9 9 8 8 8 [] STYLE=NORMAL SPLAY"
    elif mode == "different_splay" and kind == "svx":
        legs[1] = (
            f"LEG {offset} {offset + 10} {offset} {offset + 2} {offset + 10} {offset} [] SPLAY"
        )
    elif mode == "constraints_only":
        nodes.pop(0)
        legs = []
    elif mode == "empty":
        nodes, legs = [], []
    elif mode == "reverse_edges":
        legs = ["LEG 0 10 0 0 0 0 [] NORMAL", "LEG 1 10 0 0 10 0 [] SPLAY"]
    elif mode == "anonymous":
        nodes.append("NODE 1 10 0 [] ANON WALL")
    return "TITLE test\n" + "\n".join(legs + nodes) + "\nSTOP\n"


def _mock_tools(monkeypatch, *, mode="ok", offset=0, dump_override=None):
    calls = []

    def run(command, **kwargs):
        calls.append((command, kwargs))
        assert kwargs["env"]["LC_ALL"] == kwargs["env"]["LANG"] == "C"
        assert kwargs["timeout"] == 30
        if "--version" in command:
            return subprocess.CompletedProcess(
                command, 1 if mode == "version_failure" else 0, "Survex test\n", ""
            )
        if "-o" in command:
            if mode == "timeout":
                raise subprocess.TimeoutExpired(
                    command, 30, output=b"partial\xff", stderr=b"detail"
                )
            if mode == "empty_timeout":
                raise subprocess.TimeoutExpired(command, 30)
            if mode == "missing_tool":
                raise FileNotFoundError("missing cavern")
            if mode == "os_error":
                raise PermissionError("permission denied")
            code = {"failure": 2, "signal": -11}.get(mode, 0)
            if not code and mode != "no_output":
                Path(command[2]).write_bytes(b"fake .3d")
            warning = "Warning: disconnected\n" if mode == "warning" else ""
            return subprocess.CompletedProcess(command, code, "compiler progress\n", warning)
        code = 1 if mode == "dump_failure" else 0
        suffix = Path(kwargs["cwd"]).name
        contents = (
            dump_override
            if dump_override is not None
            else _dump(suffix, offset=offset if suffix == "svx" else 0, mode=mode)
        )
        warning = "warning: dump issue\n" if mode == "dump_warning" else ""
        return subprocess.CompletedProcess(command, code, contents, warning)

    monkeypatch.setattr(compilation.subprocess, "run", run)
    return calls


def test_validates_both_formats_offsets_names_counts_and_retains_diagnostics(monkeypatch):
    calls = _mock_tools(monkeypatch, offset=100)
    export = _export()
    before = json.dumps(export.report)
    result = compilation.validate_surveys(export, cavern="custom-cavern", dump3d="custom-dump3d")
    assert result["complete"]
    assert result["comparison"]["max_station_delta_m"] == 0
    assert result["comparison"]["origin_raw"] == 10
    assert result["geometry_status"] == "nonempty"
    assert result["tools"]["cavern"]["stdout"] == "Survex test\n"
    for kind in ("srv", "svx"):
        row = result["formats"][kind]
        assert row["complete"]
        assert row["compile"]["returncode"] == 0
        assert "compiler progress" in row["compile"]["stdout"]
        assert row["checks"]["legs"]["compiled_named_legs"] == 1
        assert row["checks"]["legs"]["compiled_splays"] == 1
        assert len(row["checks"]["compiled_named_stations"]) == 3
    assert len(calls) == 6
    assert calls[0][0][0] == "custom-cavern"
    assert calls[1][0][0] == "custom-dump3d"
    assert all(not Path(kwargs["cwd"]).exists() for _, kwargs in calls)
    assert "<scratch>" in str(result)
    assert json.dumps(export.report) == before
    json.dumps(result, allow_nan=False)


def test_relative_tool_paths_resolve_from_caller_directory(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    calls = _mock_tools(monkeypatch)
    result = compilation.validate_surveys(_export(), cavern="./bin/cavern", dump3d="bin/dump3d")
    assert result["complete"]
    expected = {str(tmp_path / "bin" / tool) for tool in ("cavern", "dump3d")}
    assert {command[0] for command, _ in calls} == expected


def test_real_relative_tool_paths_compile_from_install_directory(monkeypatch):
    executables = {tool: shutil.which(tool) for tool in ("cavern", "dump3d")}
    if not all(executables.values()):
        if os.environ.get("JKTZ_REQUIRE_CAVERN") == "1":
            pytest.fail("P06 validation requires cavern and dump3d")
        pytest.skip("P06 validation requires cavern and dump3d")
    executables = {tool: os.path.abspath(executable) for tool, executable in executables.items()}
    directory = Path(executables["cavern"]).parent
    # Exercise relative paths without relocating the installed tools or their siblings.
    relative = {
        tool: "./" + os.path.relpath(executable, directory)
        for tool, executable in executables.items()
    }
    data = next((CASES / "api-cardinal").glob("*.top")).read_bytes()
    monkeypatch.chdir(directory)
    result = compilation.validate_surveys(export_surveys(data), **relative)
    assert result["complete"], json.dumps(result, indent=2)
    assert all(row["compile"]["status"] == "ok" for row in result["formats"].values())
    assert result["tools"]["cavern"]["command"][0] == executables["cavern"]
    assert result["tools"]["dump3d"]["command"][0] == executables["dump3d"]


@pytest.mark.parametrize(
    "mode,status",
    [
        ("failure", "failed"),
        ("signal", "signal"),
        ("timeout", "timeout"),
        ("empty_timeout", "timeout"),
        ("missing_tool", "unavailable"),
        ("os_error", "os_error"),
    ],
)
def test_compiler_process_failures_are_incomplete_reports(monkeypatch, mode, status):
    calls = _mock_tools(monkeypatch, mode=mode)
    result = compilation.validate_surveys(_export())
    assert not result["complete"]
    for row in result["formats"].values():
        assert row["compile"]["status"] == status
        assert row["dump"] is None
    assert len(calls) == 4  # Both compilation attempts and both version queries.
    if mode == "signal":
        assert result["formats"]["srv"]["compile"]["signal"] == 11
    elif mode == "timeout":
        assert result["formats"]["srv"]["compile"]["stdout"] == "partial\ufffd"


@pytest.mark.parametrize(
    "mode", ["warning", "dump_warning", "no_output", "dump_failure", "version_failure"]
)
def test_zero_exit_or_versions_do_not_hide_incomplete_validation(monkeypatch, mode):
    _mock_tools(monkeypatch, mode=mode)
    result = compilation.validate_surveys(_export())
    assert not result["complete"]
    if mode == "warning":
        assert result["formats"]["srv"]["compile"]["warnings"] == ["Warning: disconnected"]
        assert result["comparison"]["complete"]
    elif mode == "no_output":
        assert result["formats"]["srv"]["failure"] == "compiler_produced_no_3d_file"


@pytest.mark.parametrize(
    "mode",
    [
        "missing_station",
        "unexpected_station",
        "missing_leg",
        "missing_splay",
        "extra_leg",
        "bad_edge",
        "bad_splay_anchor",
        "bad_constraint",
    ],
)
def test_missing_stations_edges_splays_and_unexpected_output_fail(monkeypatch, mode):
    _mock_tools(monkeypatch, mode=mode)
    result = compilation.validate_surveys(_export())
    assert not result["complete"]
    assert all(not row["checks"]["complete"] for row in result["formats"].values())
    if mode == "missing_station":
        assert result["comparison"]["status"] == "missing_stations"
    elif mode == "missing_leg":
        assert result["formats"]["srv"]["checks"]["legs"]["missing_named_edge_group_ids"] == [0]


@pytest.mark.parametrize("mode", ["different", "different_splay"])
def test_geometry_comparison_checks_station_positions_and_splay_endpoints(monkeypatch, mode):
    _mock_tools(monkeypatch, mode=mode)
    result = compilation.validate_surveys(_export())
    assert not result["complete"]
    assert result["comparison"]["status"] == "different"
    if mode == "different":
        assert result["comparison"]["mismatched_station_raw"] == [20]


@pytest.mark.parametrize("mode", ["ok", "reverse_edges", "anonymous"])
def test_duplicate_named_edge_aggregation_and_undirected_geometry_are_valid(monkeypatch, mode):
    _mock_tools(monkeypatch, mode=mode)
    result = compilation.validate_surveys(_export(repeated=True))
    assert result["complete"]
    for row in result["formats"].values():
        assert row["checks"]["legs"]["compiler_combined_named_edges"]


@pytest.mark.parametrize("kind,complete", [("empty", False), ("constraints_only", True)])
def test_empty_and_constraints_only_have_explicit_classification(monkeypatch, kind, complete):
    _mock_tools(monkeypatch, mode=kind)
    result = compilation.validate_surveys(_export(kind=kind))
    assert result["complete"] is complete
    assert result["geometry_status"] == kind
    if kind == "empty":
        assert result["comparison"]["status"] == "empty"


@pytest.mark.parametrize(
    "dump",
    [
        "NODE invalid\nSTOP\n",
        "NODE 0 0 [a]\nSTOP\n",
        "NODE nan 0 0 [a]\nSTOP\n",
        "NODE 0 0 0 [a]\nNODE 0 0 0 [a]\nSTOP\n",
        "LEG 0 0 0 1 0 []\nSTOP\n",
        "NODE 0 0 0 [a]\n",
    ],
)
def test_malformed_dump_is_retained_and_rejected(monkeypatch, dump):
    _mock_tools(monkeypatch, dump_override=dump)
    result = compilation.validate_surveys(_export())
    assert not result["complete"]
    for row in result["formats"].values():
        assert row["failure"]
        assert row["dump"]["stdout"] == dump


def test_text_timeout_output_and_unmatched_extra_geometry():
    assert compilation._text("text") == "text"
    assert not compilation._match_legs([], [{"from": (0, 0, 0), "to": (1, 1, 1), "splay": True}])


@pytest.mark.parametrize("disconnect", [False, True])
def test_native_fixture_real_compiler_checks_disconnected_geometry(disconnect):
    if not shutil.which("cavern") or not shutil.which("dump3d"):
        if os.environ.get("JKTZ_REQUIRE_CAVERN") == "1":
            pytest.fail("P06 validation requires cavern and dump3d")
        pytest.skip("P06 validation requires cavern and dump3d")
    data = next((CASES / "api-cardinal").glob("*.top")).read_bytes()
    if disconnect:
        before = struct.pack("<iii", -2147483647, -2147483646, 10000)
        after = struct.pack("<iii", -2147483547, -2147483546, 10000)
        assert data.count(before) == 1
        data = data.replace(before, after, 1)
    result = compilation.validate_surveys(export_surveys(data))
    assert result["complete"] is not disconnect
    for row in result["formats"].values():
        assert row["compile"]["returncode"] == 0
        if disconnect:
            assert row["compile"]["warnings"]
            assert row["checks"]["missing_named_stations"]
        else:
            assert row["checks"]["legs"]["compiler_combined_named_edges"]
