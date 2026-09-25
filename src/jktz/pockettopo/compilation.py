"""Independent compiler checks for P06, without inferred fixes or source edits."""

from __future__ import annotations

import math
import os
import re
import subprocess
import tempfile
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path

from jktz.pockettopo.export import SurveyExport

# P04: .3d stores centimetres; subtracting an origin combines two rounded values.
COORDINATE_TOLERANCE_M = 0.010001
PROCESS_TIMEOUT_SECONDS = 30
_NEIGHBOR_OFFSETS = tuple(product((-1, 0, 1), repeat=3))


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


def _station_root(parents: dict[int, int], station: int) -> int:
    parents.setdefault(station, station)
    while parents[station] != station:
        parents[station] = parents[parents[station]]
        station = parents[station]
    return station


def _named_pair_ids(groups: list[dict]) -> dict[int, tuple[int, int]]:
    """Keep named pair identity after only explicit zero links are equated."""
    parents: dict[int, int] = {}
    for group in groups:
        if group["kind"] == "zero_link":
            start = _station_root(parents, group["from_raw"])
            end = _station_root(parents, group["to_raw"])
            parents[start] = end
    return {
        group["id"]: tuple(
            sorted(
                (
                    _station_root(parents, group["from_raw"]),
                    _station_root(parents, group["to_raw"]),
                )
            )
        )
        for group in groups
        if group["kind"] == "leg"
    }


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


def _assign_splay(
    index: int, candidates: list[tuple], capacities: Counter, assigned: dict, owners: dict
) -> bool:
    """Find an augmenting path without trusting endpoint order or using recursion."""
    pending = [index]
    predecessors = {}
    for current in pending:
        for position in candidates[current]:
            if position in predecessors:
                continue
            predecessors[position] = current
            if len(assigned[position]) == capacities[position]:
                pending.extend(assigned[position])
                continue
            # Reassign the whole path only after reaching an anchor with room.
            while True:
                previous = owners.get(current)
                assigned[position].append(current)
                owners[current] = position
                if previous is None:
                    return True
                assigned[previous].remove(current)
                position = previous
                current = predecessors[position]
    return False


def _splay_anchors(expected: dict, compiled: dict) -> bool:
    anchors = Counter(
        compiled["nodes"][name]
        for group in expected["groups"]
        if group["kind"] == "splay"
        for name in (expected["names"][group["from_raw"]],)
        if name in compiled["nodes"]
    )
    splays = [leg for leg in compiled["legs"] if leg["splay"]]
    if sum(anchors.values()) != len(splays):
        return False
    # A splay tip can coincide with another named station after cm rounding.
    # Match all splays to anchor capacities, allowing earlier choices to move.
    # Keep leg indices distinct even for identical geometry; each leg has at
    # most two candidates, without expanding anchors into capacity-many slots.
    candidates = [
        tuple(
            position for position in dict.fromkeys((leg["from"], leg["to"])) if position in anchors
        )
        for leg in splays
    ]
    assigned = {position: [] for position in anchors}
    owners = {}
    return all(
        _assign_splay(index, candidates, anchors, assigned, owners) for index in range(len(splays))
    )


def _underrepresented_named_edges(
    edges: list[dict], pair_ids: dict, named: list[dict]
) -> list[int]:
    pairs_by_edge = defaultdict(set)
    ids_by_edge = defaultdict(list)
    for edge in edges:
        key = _edge_key(edge)
        pairs_by_edge[key].add(pair_ids[edge["group_id"]])
        ids_by_edge[key].append(edge["group_id"])
    compiled_keys = Counter(_edge_key(leg) for leg in named)
    return sorted(
        group_id
        for key, pairs in pairs_by_edge.items()
        if compiled_keys[key] < len(pairs)
        for group_id in ids_by_edge[key]
    )


def _leg_checks(expected: dict, compiled: dict) -> dict:
    groups = expected["groups"]
    named = [leg for leg in compiled["legs"] if not leg["splay"]]
    splays = [leg for leg in compiled["legs"] if leg["splay"]]
    edges = _named_edges(expected, compiled["nodes"])
    pair_ids = _named_pair_ids(groups)
    underrepresented = _underrepresented_named_edges(edges, pair_ids, named)
    compiled_keys = {_edge_key(leg) for leg in named}
    expected_keys = {_edge_key(edge) for edge in edges}
    missing = [edge["group_id"] for edge in edges if _edge_key(edge) not in compiled_keys]
    unexpected = [index for index, leg in enumerate(named) if _edge_key(leg) not in expected_keys]
    named_count = sum(group["kind"] == "leg" for group in groups)
    minimum_named = len(set(pair_ids.values()))
    splay_count = sum(group["kind"] == "splay" for group in groups)
    counts_valid = minimum_named <= len(named) <= named_count and len(splays) == splay_count
    anchors_valid = _splay_anchors(expected, compiled)
    return {
        "source_named_leg_groups": named_count,
        "minimum_distinct_named_legs": minimum_named,
        "source_splay_groups": splay_count,
        "compiled_named_legs": len(named),
        "compiled_splays": len(splays),
        "missing_named_edge_group_ids": missing,
        "underrepresented_named_edge_group_ids": underrepresented,
        "unexpected_named_leg_indices": unexpected,
        "compiler_combined_named_edges": (
            counts_valid
            and len(named) < named_count
            and len(edges) == named_count
            and not missing
            and not underrepresented
        ),
        "splay_anchors_complete": anchors_valid,
        "complete": counts_valid
        and anchors_valid
        and not missing
        and not unexpected
        and not underrepresented,
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


def _coordinate_cell(position: tuple) -> tuple[int, int, int]:
    width = 2 * COORDINATE_TOLERANCE_M
    return tuple(math.floor(value / width) for value in position)


def _leg_candidate_index(legs: list[dict]) -> dict:
    cells = defaultdict(list)
    for index, leg in enumerate(legs):
        for cell in {_coordinate_cell(leg["from"]), _coordinate_cell(leg["to"])}:
            cells[(leg["splay"], *cell)].append(index)
    return cells


def _nearby_leg_candidates(leg: dict, other: list[dict], cells: dict) -> list[int]:
    def nearby(position: tuple) -> set[int]:
        x, y, z = _coordinate_cell(position)
        return {
            index
            for dx, dy, dz in _NEIGHBOR_OFFSETS
            for index in cells.get((leg["splay"], x + dx, y + dy, z + dz), ())
        }

    # Both endpoints must be near an endpoint of the same compiled line.
    positions = nearby(leg["from"]) & nearby(leg["to"])
    return [index for index in sorted(positions) if _same_edge(leg, other[index])]


def _match_legs(first: list[dict], second: list[dict]) -> bool:
    """Find a one-to-one match within tolerance, regardless of dump order."""
    if len(first) != len(second):
        return False
    if Counter((leg["splay"], _edge_key(leg)) for leg in first) == Counter(
        (leg["splay"], _edge_key(leg)) for leg in second
    ):
        return True
    cells = _leg_candidate_index(second)
    candidates: dict[int, list[int]] = {}
    owners: dict[int, int] = {}
    assigned: dict[int, int] = {}
    for index in range(len(first)):
        pending = [index]
        seen = {index}
        predecessors: dict[int, int] = {}
        for current in pending:
            if current not in candidates:
                candidates[current] = _nearby_leg_candidates(first[current], second, cells)
            for position in candidates[current]:
                if position in predecessors:
                    continue
                predecessors[position] = current
                previous = owners.get(position)
                if previous is None:
                    while True:
                        previous_position = assigned.get(current)
                        owners[position] = current
                        assigned[current] = position
                        if previous_position is None:
                            break
                        position = previous_position
                        current = predecessors[position]
                    break
                if previous not in seen:
                    seen.add(previous)
                    pending.append(previous)
            else:
                continue
            break
        else:
            return False
    return True


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
