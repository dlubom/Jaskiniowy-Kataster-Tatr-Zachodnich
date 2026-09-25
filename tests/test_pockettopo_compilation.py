"""Independent P04 geometry checks through the installed Survex compiler.

The source files were written by PocketTopo before the exporter existed. Long
station names and a reverse splay are narrow byte mutations of those fixtures.
Tests use analytical coordinates, not the exporter's computed report, as oracle.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import shutil
import struct
import subprocess
from pathlib import Path

import pytest

from jktz.pockettopo import (
    CorrectionOverride,
    CorrectionPolicy,
    ProcessingPlan,
    RepeatConfirmation,
    export_surveys,
)

EVIDENCE = Path(__file__).resolve().parents[1] / "doc/pockettopo/evidence"
# .3d stores centimetres, and subtracting the chosen origin can combine two
# independently rounded coordinates. Export text has much higher precision.
COORDINATE_TOLERANCE_M = 0.010001
CONFIRMATION = "P01 native helper explicitly defines synthetic repeat A1/A2/A3"


def native_source(name: str) -> tuple[bytes, dict]:
    case = EVIDENCE / "p01/cases" / name
    return next(case.glob("*.top")).read_bytes(), json.loads(
        (case / "expected.json").read_text(encoding="utf-8")
    )


def confirmed_plan(data: bytes) -> ProcessingPlan:
    return ProcessingPlan(
        hashlib.sha256(data).hexdigest(),
        confirmations=(RepeatConfirmation((4, 5, 6), CONFIRMATION),),
    )


def explicit_test_policy(data: bytes) -> CorrectionPolicy:
    """Document test choices; neither degree value is inferred from source dates."""
    return CorrectionPolicy(
        hashlib.sha256(data).hexdigest(),
        overrides=(
            CorrectionOverride(2, 8.0, "Synthetic P04 test explicitly chooses +8 degrees"),
            CorrectionOverride(-1, -12.0, "Synthetic P04 test explicitly chooses -12 degrees"),
        ),
    )


def reverse_splay_source() -> bytes:
    data, _ = native_source("api-cardinal")
    before = struct.pack("<iii", -2147483640, -2147483648, 1234)
    after = struct.pack("<iii", -2147483648, -2147483640, 1234)
    assert data.count(before) == 1
    return data.replace(before, after, 1)


def long_id_source() -> bytes:
    data, oracle = native_source("api-trips-ids")
    # Boundary IDs render as 32767.65535 and 2147483646, exceeding Walls' eight
    # characters. Plain 0 and major.minor 0.0 stay in the same connected source.
    replacements = {851967: 2147483647, 851968: -1}
    for shot in oracle["source"]["shots"]:
        from_raw, to_raw = shot["from_id"]["raw"], shot["to_id"]["raw"]
        before = struct.pack("<iii", from_raw, to_raw, shot["distance_mm"])
        after = struct.pack(
            "<iii",
            replacements.get(from_raw, from_raw),
            replacements.get(to_raw, to_raw),
            shot["distance_mm"],
        )
        assert data.count(before) == 1
        data = data.replace(before, after, 1)
    return data


def compiler_tools() -> tuple[str, str]:
    cavern, dump3d = shutil.which("cavern"), shutil.which("dump3d")
    if cavern and dump3d:
        return cavern, dump3d
    message = "P04 compilation checks require both cavern and dump3d on PATH"
    if os.environ.get("JKTZ_REQUIRE_CAVERN") == "1":
        pytest.fail(message)
    pytest.skip(message)


def compile_export(
    text: str, suffix: str, directory: Path, *, require_warning_free: bool = True
) -> dict:
    cavern, dump3d = compiler_tools()
    directory.mkdir(parents=True, exist_ok=True)
    source_path = directory / f"survey.{suffix}"
    output_path = directory / "survey.3d"
    source_path.write_text(text, encoding="ascii", newline="\n")
    environment = {**os.environ, "LC_ALL": "C", "LANG": "C"}
    compiled = subprocess.run(
        [cavern, "-o", str(output_path), str(source_path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=environment,
        timeout=30,
        check=False,
    )
    output = compiled.stdout + compiled.stderr
    assert compiled.returncode == 0, output
    if require_warning_free:
        assert not re.search(r"\bwarning:", output, flags=re.IGNORECASE), output
    dumped = subprocess.run(
        [dump3d, "--legs", str(output_path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=environment,
        timeout=30,
        check=True,
    ).stdout
    nodes = {}
    legs = []
    for line in dumped.splitlines():
        if line.startswith("NODE "):
            position, remainder = line[5:].split(" [", 1)
            name, flags = remainder.split("]", 1)
            nodes[name] = {"position": tuple(map(float, position.split())), "flags": flags.strip()}
        elif line.startswith("LEG "):
            coordinates, remainder = line[4:].split(" [", 1)
            survey, flags = remainder.split("]", 1)
            values = tuple(map(float, coordinates.split()))
            legs.append({"from": values[:3], "to": values[3:], "flags": flags.strip()})
    return {"compiler_output": output, "dump3d": dumped, "nodes": nodes, "legs": legs}


def mapped_nodes(export, compiled: dict, target: str) -> dict:
    result = {}
    for row in export.report["station_map"]:
        name = row[target + "_name"]
        if name in compiled["nodes"]:
            result[row["source_text"]] = compiled["nodes"][name]["position"]
    return result


def subtract(left, right) -> tuple[float, float, float]:
    return tuple(a - b for a, b in zip(left, right))


def add(left, right) -> tuple[float, float, float]:
    return tuple(a + b for a, b in zip(left, right))


def vector(distance: float, azimuth: float, inclination: float) -> tuple[float, float, float]:
    a, v = math.radians(azimuth), math.radians(inclination)
    return (
        distance * math.sin(a) * math.cos(v),
        distance * math.cos(a) * math.cos(v),
        distance * math.sin(v),
    )


def cardinal_expected() -> dict:
    expected = {
        "0": (0, 0, 0),
        "1": (0, 10, 0),
        "2": (2, 10, 0),
        "3": (2, 7, 0),
        "4": (-2, 7, 0),
    }
    # Three explicit repeated records normalize to A=0; V=1820 raw units.
    expected["5"] = add(expected["4"], vector(5, 0, 1820 * 360 / 65536))
    expected["6"] = add(expected["5"], (0, 0, 1))
    expected["7"] = expected["5"]
    expected["8"] = expected["7"]
    return expected


def trips_expected(*, long_names: bool) -> dict:
    first = vector(1, 910 * 360 / 65536, 0)
    second = add(first, vector(2, 90 - 637 * 360 / 65536, 1820 * 360 / 65536))
    last = add(second, vector(4, 270 - 12, 0))
    return {
        "0": (0, 0, 0),
        "0.0": first,
        "32767.65535" if long_names else "12.65535": second,
        "2147483646" if long_names else "13.0": last,
    }


def assert_geometry(actual: dict, expected: dict) -> None:
    assert actual.keys() == expected.keys()
    origin = actual["0"]
    for name, position in expected.items():
        assert subtract(actual[name], origin) == pytest.approx(
            position, rel=0, abs=COORDINATE_TOLERANCE_M
        ), name


def assert_splay(compiled: dict, direction: tuple) -> None:
    splays = [leg for leg in compiled["legs"] if "SPLAY" in leg["flags"]]
    assert len(splays) == 1
    actual = subtract(splays[0]["to"], splays[0]["from"])
    assert actual == pytest.approx(direction, rel=0, abs=COORDINATE_TOLERANCE_M)


@pytest.mark.parametrize("reverse_splay", [False, True], ids=["forward", "reversed"])
def test_confirmed_native_repeats_zero_link_and_splay_have_analytical_geometry(
    tmp_path: Path, reverse_splay: bool
) -> None:
    data = reverse_splay_source() if reverse_splay else native_source("api-cardinal")[0]
    export = export_surveys(data, plan=confirmed_plan(data))
    expected = cardinal_expected()
    inclination = -3641 * 360 / 65536
    splay = vector(
        1.234, 225 if reverse_splay else 45, -inclination if reverse_splay else inclination
    )
    geometries = []
    for suffix, target in (("SRV", "walls"), ("svx", "survex")):
        compiled = compile_export(getattr(export, suffix.lower()), suffix, tmp_path / suffix)
        assert len(compiled["legs"]) == 8  # Zero link compiles as a station equivalence.
        actual = mapped_nodes(export, compiled, target)
        assert_geometry(actual, expected)
        assert actual["7"] == actual["8"]
        assert_splay(compiled, splay)
        geometries.append(actual)
    assert geometries[0] == geometries[1]


@pytest.mark.parametrize("long_names", [False, True], ids=["native_ids", "long_ids"])
def test_trip_corrections_and_distinct_zero_identifiers_compile_without_collisions(
    tmp_path: Path, long_names: bool
) -> None:
    data = long_id_source() if long_names else native_source("api-trips-ids")[0]
    export = export_surveys(data, correction_policy=explicit_test_policy(data))
    geometries = []
    for suffix, target in (("SRV", "walls"), ("svx", "survex")):
        compiled = compile_export(getattr(export, suffix.lower()), suffix, tmp_path / suffix)
        assert len(compiled["legs"]) == 4
        actual = mapped_nodes(export, compiled, target)
        assert_geometry(actual, trips_expected(long_names=long_names))
        assert actual["0"] != actual["0.0"]
        assert_splay(compiled, vector(3, 180 + 8, -1820 * 360 / 65536))
        geometries.append(actual)
    assert geometries[0] == geometries[1]


def test_unconfirmed_native_repeated_records_remain_distinct_export_rows(tmp_path: Path) -> None:
    data, _ = native_source("api-cardinal")
    export = export_surveys(data)
    assert [group["source_indices"] for group in export.report["groups"]] == [
        (index,) for index in range(11)
    ]
    geometries = []
    for suffix, target in (("SRV", "walls"), ("svx", "survex")):
        compiled = compile_export(getattr(export, suffix.lower()), suffix, tmp_path / suffix)
        # The compiler may combine repeated edges during network adjustment.
        # The source exporter must still emit each unconfirmed group separately.
        line_key = suffix.lower() + "_line"
        exported_lines = [group["export"][line_key] for group in export.report["groups"]]
        assert len(set(exported_lines)) == 11
        assert all(line is not None for line in exported_lines)
        actual = mapped_nodes(export, compiled, target)
        assert len(actual) == 9
        geometries.append(actual)
    assert geometries[0] == geometries[1]


def test_disconnected_source_keeps_records_and_exposes_compiler_warning(tmp_path: Path) -> None:
    data, _ = native_source("api-cardinal")
    before = struct.pack("<iii", -2147483647, -2147483646, 10000)
    after = struct.pack("<iii", -2147483547, -2147483546, 10000)
    assert data.count(before) == 1
    data = data.replace(before, after, 1)
    export = export_surveys(data, plan=confirmed_plan(data))
    assert export.report["completeness"]["exported_source_shots"] == 11
    assert export.report["exports"]["validation"] == "not_run_by_library"
    for suffix in ("SRV", "svx"):
        compiled = compile_export(
            getattr(export, suffix.lower()), suffix, tmp_path / suffix, require_warning_free=False
        )
        assert "warning: Survey not all connected to fixed stations" in compiled["compiler_output"]
        # A zero exit code is not sufficient validation. Survex 1.4.22 can omit
        # disconnected components from .3d; preserve every input record anyway.
        lines = [group["export"][suffix.lower() + "_line"] for group in export.report["groups"]]
        assert len(set(lines)) == 9
        assert all(line is not None for line in lines)
