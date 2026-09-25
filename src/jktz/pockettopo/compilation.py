"""Independent compiler checks for P06, without inferred fixes or source edits."""

from __future__ import annotations

import math
import os
import re
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

from jktz.pockettopo.export import SurveyExport

# P04: .3d stores centimetres; subtracting an origin combines two rounded values.
COORDINATE_TOLERANCE_M = 0.010001
PROCESS_TIMEOUT_SECONDS = 30


def _text(value: str | bytes | None) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value or ""


def _run(command: list[str], directory: Path) -> dict:
    result = {
        "command": [part.replace(str(directory), "<scratch>") for part in command],
        "status": "failed",
        "returncode": None,
        "signal": None,
        "stdout": "",
        "stderr": "",
        "warnings": [],
    }
    try:
        process = subprocess.run(
            command,
            cwd=directory,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env={**os.environ, "LC_ALL": "C", "LANG": "C"},
            timeout=PROCESS_TIMEOUT_SECONDS,
            check=False,
        )
        result.update(returncode=process.returncode, stdout=process.stdout, stderr=process.stderr)
        if process.returncode == 0:
            result["status"] = "ok"
        elif process.returncode < 0:
            result.update(status="signal", signal=-process.returncode)
    except subprocess.TimeoutExpired as error:
        result.update(status="timeout", stdout=_text(error.stdout), stderr=_text(error.stderr))
    except FileNotFoundError as error:
        result.update(status="unavailable", stderr=str(error))
    except OSError as error:
        result.update(status="os_error", stderr=str(error))
    for key in ("stdout", "stderr"):
        result[key] = result[key].replace(str(directory), "<scratch>")
    output = result["stdout"] + "\n" + result["stderr"]
    result["warnings"] = [
        line for line in output.splitlines() if re.search(r"\bwarning:", line, re.I)
    ]
    return result


def _coordinates(text: str, count: int) -> tuple[float, ...]:
    values = tuple(map(float, text.split()))
    if len(values) != count or not all(math.isfinite(value) for value in values):
        raise ValueError(f"Invalid dump3d coordinates: {text!r}")
    return values


def _parse_dump(text: str) -> dict:
    nodes, legs = {}, []
    for line in text.splitlines():
        if not line.startswith(("NODE ", "LEG ")):
            continue
        coordinates, remainder = line[5 if line.startswith("NODE ") else 4 :].split(" [", 1)
        name, flags = remainder.split("]", 1)
        if line.startswith("NODE "):
            position = _coordinates(coordinates, 3)
            if name:
                if name in nodes:
                    raise ValueError(f"Duplicate named dump3d station: {name!r}")
                nodes[name] = position
        else:
            values = _coordinates(coordinates, 6)
            legs.append({"from": values[:3], "to": values[3:], "splay": "SPLAY" in flags.split()})
    if "STOP" not in text.splitlines():
        raise ValueError("Incomplete dump3d output: missing STOP")
    return {"nodes": nodes, "legs": legs}


def _expected(export: SurveyExport, target: str) -> dict:
    groups = [group for group in export.report["groups"] if group["export"]["status"] == "exported"]
    active_ids = {group[key] for group in groups for key in ("from_raw", "to_raw")}
    names = {
        row["raw"]: row[target + "_name"]
        for row in export.report["station_map"]
        if row["raw"] in active_ids
    }
    return {"names": names, "groups": groups}


def _close(first: tuple, second: tuple) -> bool:
    return all(abs(a - b) <= COORDINATE_TOLERANCE_M for a, b in zip(first, second))


def _same_edge(first: dict, second: dict) -> bool:
    return (_close(first["from"], second["from"]) and _close(first["to"], second["to"])) or (
        _close(first["from"], second["to"]) and _close(first["to"], second["from"])
    )


def _edge_key(edge: dict) -> tuple:
    # Inside one .3d file NODE/LEG coordinates share the same rounding exactly.
    return tuple(sorted((edge["from"], edge["to"])))


def _named_edges(expected: dict, nodes: dict) -> list[dict]:
    return [
        {
            "group_id": group["id"],
            "from": nodes[names[group["from_raw"]]],
            "to": nodes[names[group["to_raw"]]],
        }
        for group in expected["groups"]
        if group["kind"] == "leg"
        for names in (expected["names"],)
        if names[group["from_raw"]] in nodes and names[group["to_raw"]] in nodes
    ]


def _splay_anchors(expected: dict, compiled: dict) -> bool:
    anchors = Counter(
        compiled["nodes"][name]
        for group in expected["groups"]
        if group["kind"] == "splay"
        for name in (expected["names"][group["from_raw"]],)
        if name in compiled["nodes"]
    )
    remaining = [leg for leg in compiled["legs"] if leg["splay"]]
    for position, count in anchors.items():
        matches = [leg for leg in remaining if position in (leg["from"], leg["to"])]
        if len(matches) < count:
            return False
        for leg in matches[:count]:
            remaining.remove(leg)
    return not remaining


def _leg_checks(expected: dict, compiled: dict) -> dict:
    groups = expected["groups"]
    named = [leg for leg in compiled["legs"] if not leg["splay"]]
    splays = [leg for leg in compiled["legs"] if leg["splay"]]
    edges = _named_edges(expected, compiled["nodes"])
    compiled_keys = {_edge_key(leg) for leg in named}
    expected_keys = {_edge_key(edge) for edge in edges}
    missing = [edge["group_id"] for edge in edges if _edge_key(edge) not in compiled_keys]
    unexpected = [index for index, leg in enumerate(named) if _edge_key(leg) not in expected_keys]
    named_count = sum(group["kind"] == "leg" for group in groups)
    splay_count = sum(group["kind"] == "splay" for group in groups)
    counts_valid = len(named) <= named_count and len(splays) == splay_count
    anchors_valid = _splay_anchors(expected, compiled)
    return {
        "source_named_leg_groups": named_count,
        "source_splay_groups": splay_count,
        "compiled_named_legs": len(named),
        "compiled_splays": len(splays),
        "missing_named_edge_group_ids": missing,
        "unexpected_named_leg_indices": unexpected,
        "compiler_combined_named_edges": (
            len(named) < named_count and len(edges) == named_count and not missing
        ),
        "splay_anchors_complete": anchors_valid,
        "complete": counts_valid and anchors_valid and not missing and not unexpected,
    }


def _inspect_geometry(expected: dict, compiled: dict) -> dict:
    expected_names = set(expected["names"].values())
    actual_names = set(compiled["nodes"])
    legs = _leg_checks(expected, compiled)
    broken_constraints = [
        group["id"]
        for group in expected["groups"]
        if group["kind"] == "zero_link"
        for first, second in (
            (expected["names"][group["from_raw"]], expected["names"][group["to_raw"]]),
        )
        if first in actual_names and second in actual_names
        if compiled["nodes"][first] != compiled["nodes"][second]
    ]
    return {
        "expected_named_stations": sorted(expected_names),
        "compiled_named_stations": sorted(actual_names),
        "missing_named_stations": sorted(expected_names - actual_names),
        "unexpected_named_stations": sorted(actual_names - expected_names),
        "broken_zero_link_group_ids": broken_constraints,
        "legs": legs,
        "complete": expected_names == actual_names and legs["complete"] and not broken_constraints,
    }


def _compile(
    text: str, suffix: str, expected: dict, tools: dict, root: Path
) -> tuple[dict, dict | None]:
    directory = root / suffix
    directory.mkdir()
    source = directory / ("survey." + suffix)
    output = directory / "survey.3d"
    source.write_text(text, encoding="ascii", newline="\n")
    process = _run([tools["cavern"], "-o", str(output), str(source)], directory)
    result = {"compile": process, "dump": None, "checks": None, "complete": False}
    if process["status"] != "ok":
        return result, None
    if not output.is_file():
        result["failure"] = "compiler_produced_no_3d_file"
        return result, None
    dumped = _run([tools["dump3d"], "--legs", str(output)], directory)
    result["dump"] = dumped
    if dumped["status"] != "ok":
        return result, None
    try:
        compiled = _parse_dump(dumped["stdout"])
    except ValueError as error:
        result["failure"] = str(error)
        return result, None
    checks = _inspect_geometry(expected, compiled)
    result.update(
        checks=checks,
        complete=checks["complete"] and not process["warnings"] and not dumped["warnings"],
    )
    return result, compiled


def _relative(position: tuple, origin: tuple) -> tuple:
    return tuple(value - offset for value, offset in zip(position, origin))


def _relative_legs(compiled: dict, origin: tuple) -> list[dict]:
    return [
        {
            "from": _relative(leg["from"], origin),
            "to": _relative(leg["to"], origin),
            "splay": leg["splay"],
        }
        for leg in compiled["legs"]
    ]


def _match_legs(first: list[dict], second: list[dict]) -> bool:
    remaining = list(second)
    for leg in first:
        match = next(
            (
                index
                for index, other in enumerate(remaining)
                if leg["splay"] == other["splay"] and _same_edge(leg, other)
            ),
            None,
        )
        if match is None:
            return False
        remaining.pop(match)
    return not remaining


def _compare(expected: dict, compiled: dict) -> dict:
    result = {"complete": False, "status": "unavailable", "tolerance_m": COORDINATE_TOLERANCE_M}
    if any(value is None for value in compiled.values()):
        return result
    mapped = {
        kind: {
            raw: compiled[kind]["nodes"][name]
            for raw, name in row["names"].items()
            if name in compiled[kind]["nodes"]
        }
        for kind, row in expected.items()
    }
    ids = set(expected["srv"]["names"])
    if not ids:
        result["status"] = "empty"
        return result
    if any(set(nodes) != ids for nodes in mapped.values()):
        result["status"] = "missing_stations"
        return result
    origin_id = min(ids)
    origins = {kind: nodes[origin_id] for kind, nodes in mapped.items()}
    differences = {
        raw: max(
            abs(a - b)
            for a, b in zip(
                _relative(mapped["srv"][raw], origins["srv"]),
                _relative(mapped["svx"][raw], origins["svx"]),
            )
        )
        for raw in ids
    }
    mismatches = sorted(raw for raw, delta in differences.items() if delta > COORDINATE_TOLERANCE_M)
    leg_match = _match_legs(
        _relative_legs(compiled["srv"], origins["srv"]),
        _relative_legs(compiled["svx"], origins["svx"]),
    )
    complete = not mismatches and leg_match
    result.update(
        complete=complete,
        status="equivalent" if complete else "different",
        origin_raw=origin_id,
        max_station_delta_m=max(differences.values()),
        mismatched_station_raw=mismatches,
        leg_geometry_matches=leg_match,
    )
    return result


def validate_surveys(
    export: SurveyExport, *, cavern: str = "cavern", dump3d: str = "dump3d"
) -> dict:
    """Compile both exports and validate the active geometry in temporary files.

    ``complete`` validates only exported measurements. Held source records and
    sketch placement require their own completeness checks. Compiler adjustment
    can combine repeated named edges; every expected edge must remain represented.
    Empty exports are reported as empty, never as successfully validated geometry.
    """
    # Explicit paths are relative to the caller, not each compiler's scratch cwd.
    # Bare command names retain normal PATH lookup.
    tools = {
        name: os.path.abspath(executable) if os.path.dirname(executable) else executable
        for name, executable in (("cavern", cavern), ("dump3d", dump3d))
    }
    expected = {"srv": _expected(export, "walls"), "svx": _expected(export, "survex")}
    formats, compiled = {}, {}
    with tempfile.TemporaryDirectory(prefix="jktz-pockettopo-compile-") as temporary:
        root = Path(temporary)
        versions = {
            name: _run([executable, "--version"], root) for name, executable in tools.items()
        }
        for kind, suffix in (("srv", "SRV"), ("svx", "svx")):
            formats[kind], compiled[kind] = _compile(
                getattr(export, kind), suffix, expected[kind], tools, root
            )
    comparison = _compare(expected, compiled)
    return {
        "complete": all(row["complete"] for row in formats.values())
        and comparison["complete"]
        and all(row["status"] == "ok" for row in versions.values()),
        "geometry_status": export.report["exports"]["geometry_status"],
        "tools": versions,
        "formats": formats,
        "comparison": comparison,
        "scope": (
            "Exported active geometry only; dates, CRS and historical corrections "
            "remain unverified."
        ),
    }
