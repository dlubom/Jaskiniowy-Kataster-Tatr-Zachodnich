"""One-off audit companion; run from the repository root, with cavern and dump3d."""

from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BASE = "446edc42a470e653253a29fdcf78bc89ba562d35"
TRANSCRIPTION = "c878b7bd1e428595854a8191a5c5b2339bb978b9"
CAVE = Path("Poligony/D_Koscieliska/Organy/Czarna")
OLD = ["CZ_Z_S.SRV", "CZ_B_DAV.SRV", "CZ_K_S.SRV", "CZ_W_S.SRV", "CZ_N_S.SRV"]
THIRD = "Czarna:Kujat:0"
ADOPTED_DATE = "1975-08-20"


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True, encoding="utf-8")


def measurements(text: str) -> list[list[str]]:
    rows = []
    in_metadata = False
    for line in text.splitlines():
        if line.startswith("#["):
            in_metadata = True
        if line.startswith("#]"):
            in_metadata = False
        line = line.split(";", 1)[0].strip()
        if not line or in_metadata or line.startswith("#"):
            continue
        fields = line.split()
        assert len(fields) == 5, fields
        rows.append(fields)
    return rows


def main() -> None:
    root = Path.cwd()
    project = (root / "KATASTER.wpj").read_text()
    join_block = (
        ".SURVEY\tHIPOTEZA Kujat 74 = Borowiec 70 - dojscie do III otworu\n"
        ".NAME\tCZ_GL_P\n.STATUS\t8\n"
    )
    assert project.count(join_block) == 1
    parallel_project = project.replace(join_block, "")
    join_rows = measurements((root / CAVE / "CZ_GL_P.SRV").read_text())
    assert join_rows == [["CiagSkany:74", "Borowiec:70", "0", "0", "0"]]
    baseline = run("git", "show", f"{BASE}:KATASTER.wpj")
    fixes = (root / "Poligony/OTWORY.SRV").read_text()
    transcription = (root / CAVE / "CZ_GL_R.SRV").read_text()
    old_transcription = run("git", "show", f"{TRANSCRIPTION}:{CAVE}/CZ_GL_R.SRV")
    rows = measurements(transcription)
    original_rows = measurements(old_transcription)
    expected_rows = [row.copy() for row in original_rows]
    corrected = [row for row in expected_rows if row[:2] == ["49", "50"]]
    assert corrected == [["49", "50", "14.20", "68", "61"]]
    corrected[0][3] = "88"  # User's source reading, accepted 2026-09-19.
    assert rows == expected_rows, "Unexpected transcription change"
    assert len(rows) == 78
    assert re.findall(r"^#date\s+(\S+)", transcription, re.M) == [ADOPTED_DATE]
    assert not re.search(r"^#units[^\n]*\bDECL=", transcription, re.M | re.I)
    # Every previously active SRV is byte-identical, including the GPS snapshot.
    old_paths = run("git", "ls-tree", "-r", "--name-only", BASE).splitlines()
    preserved = [p for p in old_paths if p.upper().endswith(".SRV") and "/_RAW/" not in p]
    for path in preserved:
        original = subprocess.check_output(["git", "show", f"{BASE}:{path}"])
        assert (root / path).read_bytes() == original, path
    ref = next(line for line in project.splitlines() if line.startswith(".REF"))

    def compile_case(
        directory: Path,
        text: str,
        one_fix: bool = False,
        cave_only: bool = False,
        without_date: bool = False,
        tail_route_only: bool = False,
    ):
        directory.mkdir()
        paths = [Path(p) for p in preserved] + [
            CAVE / n for n in ["CZ_GL_R.SRV", "CZ_GL_N.SRV", "CZ_GL_P.SRV"]
        ]
        for path in paths:
            target_path = directory / path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / path, target_path)
        if without_date:
            control = transcription.replace(f"#date {ADOPTED_DATE}", "#units DECL=0")
            assert measurements(control) == rows
            (directory / CAVE / "CZ_GL_R.SRV").write_text(control)
        if tail_route_only:
            # Keep the original AVD readings and date of III entrance -> B70.
            # Other branches are irrelevant to this independent, loop-free route.
            tail = (root / CAVE / "CZ_K_S.SRV").read_text()
            route = tail.split(";Korytarz Trzech Studni", 1)[0]
            tie = next(s for s in tail.splitlines() if s.split()[:2] == ["12", "Borowiec:70"])
            route += tie + "\n"
            assert measurements(route) == tail_route
            (directory / CAVE / "CZ_K_S.SRV").write_text(route)
        fix_text = fixes
        if cave_only:
            fix_text = (
                "#units meters order=ENU\n"
                + "\n".join(
                    line
                    for line in fixes.splitlines()
                    if line.lower().startswith("#fix") and "Czarna:" in line
                )
                + "\n"
            )
        if one_fix:
            lines = fix_text.splitlines(keepends=True)
            removed = [s for s in lines if s.lower().startswith("#fix") and THIRD in s]
            assert len(removed) == 1
            fix_text = "".join(s for s in lines if s not in removed)
        (directory / "Poligony/OTWORY.SRV").write_text(fix_text)
        (directory / "KATASTER.wpj").write_text(text)
        proc = subprocess.run(
            ["cavern", "-o", str(directory / "KATASTER.3d"), str(directory / "KATASTER.wpj")],
            capture_output=True,
            text=True,
            check=False,
        )
        log = proc.stdout + proc.stderr
        assert proc.returncode == 0, log
        assert not re.search(r"warning:|error:", log, re.I), log
        dump = run("dump3d", str(directory / "KATASTER.3d"))
        nodes = {}
        for line in dump.splitlines():
            match = re.match(r"NODE (\S+) (\S+) (\S+) \[([^]]+)\]", line)
            if match:
                nodes[match[4]] = tuple(float(v) for v in match.group(1, 2, 3))
        counts = re.search(r"contains (\d+) survey stations, joined by (\d+) legs", log)
        assert counts, log
        loops = re.search(r"There (?:are|is) (\d+) loops?\.", log)
        # cavern says "no loops" for a tree.
        loop_count = int(loops[1]) if loops else 0
        if not loops:
            assert "no loops" in log.lower(), log
        return nodes, {"stations": int(counts[1]), "legs": int(counts[2]), "loops": loop_count}

    def isolated(files: list[str]) -> str:
        body = (
            ";WALLS Project File\n.BOOK Audit\n.NAME\tKATASTER\n.STATUS\t2563\n"
            + ref
            + "\n.SURVEY Fixes\n.NAME\tOTWORY\n.PATH Poligony\n.STATUS\t8\n"
        )
        for name in files:
            body += f".SURVEY {name}\n.NAME {Path(name).stem}\n.PATH {CAVE}\n.STATUS 8\n"
        return body + ".ENDBOOK\n"

    tail_rows = measurements((root / CAVE / "CZ_K_S.SRV").read_text())
    tail_route = tail_rows[:12] + [r for r in tail_rows if r[:2] == ["12", "Borowiec:70"]]
    assert len(tail_route) == 13 and tail_route[0][:2] == ["0", "1"]
    tail_length = sum(float(r[4]) for r in tail_route)  # AVD, unlike the main DAV journal.

    with tempfile.TemporaryDirectory(prefix="czarna-dwa-ciagi-") as tmp:
        scratch = Path(tmp)
        old, old_counts = compile_case(scratch / "baseline", baseline)
        new, new_counts = compile_case(scratch / "new", project)
        parallel, parallel_counts = compile_case(scratch / "parallel-no-join", parallel_project)
        undated, _ = compile_case(
            scratch / "control-decl-zero", parallel_project, without_date=True
        )
        old_free, _ = compile_case(scratch / "baseline-one-fix", baseline, True)
        new_free, _ = compile_case(scratch / "new-one-fix", project, True)
        parallel_free, _ = compile_case(scratch / "parallel-one-fix", parallel_project, True)
        borowiec, _ = compile_case(
            scratch / "isolated-one-fix", isolated(["CZ_B_DAV.SRV", "CZ_K_S.SRV"]), True, True
        )
        kujat, kujat_counts = compile_case(
            scratch / "kujat-route-one-fix",
            isolated(["CZ_GL_R.SRV", "CZ_GL_N.SRV", "CZ_GL_P.SRV", "CZ_K_S.SRV"]),
            one_fix=True,
            cave_only=True,
            tail_route_only=True,
        )
        assert kujat_counts["loops"] == 0, "Kujat closure must be measured on an unadjusted route"
        assert all(pos == parallel[name] for name, pos in old.items())
        assert all(pos == parallel_free[name] for name, pos in old_free.items())
        max_shift = max(math.dist(pos, new[name]) for name, pos in old.items())
        max_free_shift = max(math.dist(pos, new_free[name]) for name, pos in old_free.items())
        assert parallel_counts["loops"] == old_counts["loops"]
        assert new_counts["loops"] == old_counts["loops"] + 1
        assert new_counts["stations"] - old_counts["stations"] == 79
        assert new_counts["legs"] - old_counts["legs"] == 80
        assert new["Czarna:CiagSkany:74"] == new["Czarna:Borowiec:70"]
        assert all(pos == undated[name] for name, pos in old.items())
        target = old[THIRD]
        assert new[THIRD] == target and new["Czarna:M:otwor1"] == old["Czarna:M:otwor1"]

        def difference(left, right):
            delta = [round(a - b, 2) for a, b in zip(left, right)]
            return {
                "delta_ENZ_m": delta,
                "horizontal_m": math.hypot(*delta[:2]),
                "spatial_m": math.hypot(*delta),
            }

        k0, k76, b73 = "Czarna:CiagSkany:0", "Czarna:CiagSkany:76", "Czarna:Borowiec:73"

        def bearing(nodes):
            east = nodes[k76][0] - nodes[k0][0]
            north = nodes[k76][1] - nodes[k0][1]
            return math.degrees(math.atan2(east, north))

        rotation = (bearing(parallel) - bearing(undated) + 180) % 360 - 180
        assert abs(rotation) > 0.01, "Adopted date did not change the traverse orientation"
        # Date correction rotates the traverse horizontally; it cannot change heights.
        assert all(
            pos[2] == undated[name][2]
            for name, pos in parallel.items()
            if name.startswith("Czarna:CiagSkany:")
        )

        def closure(nodes):
            delta = [round(a - b, 2) for a, b in zip(nodes[THIRD], target)]
            return {
                "delta_ENZ_m": delta,
                "horizontal_m": math.hypot(*delta[:2]),
                "spatial_m": math.hypot(*delta),
            }

        def endpoint(records):
            vector = [0.0, 0.0, 0.0]
            for _, _, d, a, v in records:
                distance, azimuth, inclination = (
                    float(d),
                    math.radians(float(a if a != "--" else 0)),
                    math.radians(float(v)),
                )
                h = distance * math.cos(inclination)
                for i, value in enumerate(
                    (h * math.sin(azimuth), h * math.cos(azimuth), distance * math.sin(inclination))
                ):
                    vector[i] += value
            return vector

        b_rows = measurements((root / CAVE / "CZ_B_DAV.SRV").read_text())[1:]
        assert b_rows[0][:2] == ["0W", "0"] and b_rows[-1][:2] == ["72", "73"]
        delta = [k - b for k, b in zip(endpoint(rows[:76]), endpoint(b_rows))]
        paths = [Path("KATASTER.wpj"), Path("Poligony/OTWORY.SRV")]
        paths += [CAVE / name for name in [*OLD, "CZ_GL_R.SRV", "CZ_GL_N.SRV", "CZ_GL_P.SRV"]]
        kujat_length = sum(float(r[2]) for r in rows[:74]) + tail_length
        assert rows[73][:2] == ["73", "74"]
        borowiec_length = sum(float(r[2]) for r in b_rows[:71]) + tail_length
        assert b_rows[70][:2] == ["69", "70"]
        shifts = sorted(
            ((math.dist(pos, new[name]), name) for name, pos in old.items()), reverse=True
        )
        report = {
            "base_commit": BASE,
            "transcription_commit": TRANSCRIPTION,
            "survex": run("cavern", "--version").strip(),
            "coordinate_resolution_m": 0.01,
            "input_sha256": {
                str(p): hashlib.sha256((root / p).read_bytes()).hexdigest() for p in paths
            },
            "previous_srv_files_byte_identical": len(preserved),
            "transcription_rows_unchanged": sum(a == b for a, b in zip(rows, original_rows)),
            "approved_transcription_changes": [
                {
                    "from": "49",
                    "to": "50",
                    "field": "A",
                    "old_deg": 68,
                    "new_deg": 88,
                    "basis": "User source reading, 2026-09-19",
                }
            ],
            "transcription_length_m": round(sum(float(row[2]) for row in rows), 2),
            "baseline": old_counts,
            "both_traverses": new_counts,
            "parallel_without_join": parallel_counts,
            "old_node_labels_checked": len(old),
            "max_existing_node_shift_m": max_shift,
            "max_existing_node_shift_one_fix_m": max_free_shift,
            "existing_labels_shifted": sum(d > 0 for d, _ in shifts),
            "largest_existing_node_shifts": [
                {"station": n, "distance_m": d} for d, n in shifts[:5]
            ],
            "gnss_III_UTM34N": target,
            "closure_mixed": closure(new_free),
            "closure_mixed_without_join": closure(parallel_free),
            "closure_borowiec_with_old_kujat_tail": closure(borowiec),
            "closure_new_kujat_conditional_on_K74_B70": closure(kujat),
            "independent_routes": {
                "kujat": {
                    "length_m": round(kujat_length, 2),
                    "measured_legs": 74 + 13,
                    "closure_percent": 100 * closure(kujat)["spatial_m"] / kujat_length,
                },
                "borowiec": {
                    "length_m": round(borowiec_length, 2),
                    "measured_legs": 71 + 13,
                    "closure_percent": 100 * closure(borowiec)["spatial_m"] / borowiec_length,
                },
                "shared_tail_length_m": round(tail_length, 2),
            },
            "hypothetical_join": {
                "identity": "CiagSkany:74 = Borowiec:70 = historical Kujat:13",
                "status": "Review hypothesis authorized by user; physical identity unconfirmed",
                "selection_basis": (
                    "Known B70 junction to III entrance; local proximity and terminal route "
                    "to Colorado, not closure optimization"
                ),
                "before_join_K74_minus_B70": difference(
                    parallel["Czarna:CiagSkany:74"], parallel["Czarna:Borowiec:70"]
                ),
                "before_join_K70_minus_B70": difference(
                    parallel["Czarna:CiagSkany:70"], parallel["Czarna:Borowiec:70"]
                ),
                "candidate_region_before_join": [
                    {
                        "kujat_station": i,
                        **difference(
                            parallel[f"Czarna:CiagSkany:{i}"], parallel["Czarna:Borowiec:70"]
                        ),
                    }
                    for i in range(70, 77)
                ],
                "junction_residual_between_independent_routes": difference(
                    kujat["Czarna:CiagSkany:74"], borowiec["Czarna:Borowiec:70"]
                ),
            },
            "new_kujat_limitation": (
                "Closure is conditional on assumed K74=B70 and K0 at main GNSS; "
                "both routes share the old Kujat tail. Joint-network closure is not "
                "either traverse's independent error."
            ),
            "adopted_survey_date": {
                "value": ADOPTED_DATE,
                "status": "User-adopted calculation date, not a confirmed journal date",
                "source": "Taternik 4/1977 p.184: opening expedition 20-21 August 1975",
                "historical_journal_date": None,
                "explicit_declination_override": False,
            },
            "date_effect_in_compiled_project_NOT_closure": {
                "context": "Parallel traverses with hypothetical internal join removed",
                "rotation_from_DECL0_deg": rotation,
                "K76_movement_from_DECL0": difference(parallel[k76], undated[k76]),
                "K76_minus_B73_before_date": difference(undated[k76], undated[b73]),
                "K76_minus_B73_with_date": difference(parallel[k76], parallel[b73]),
                "endpoint_identity_confirmed": False,
                "compiled_endpoints_UTM34N_m": {
                    "K0": parallel[k0],
                    "K76_DECL0": undated[k76],
                    "K76_dated": parallel[k76],
                    "B73": parallel[b73],
                },
            },
            "raw_endpoint_comparison_NOT_closure": {
                "delta_ENZ_m": delta,
                "horizontal_m": math.hypot(*delta[:2]),
                "spatial_m": math.hypot(*delta),
            },
        }
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if len(sys.argv) == 2:
        Path(sys.argv[1]).write_text(output, encoding="utf-8")
    else:
        print(output, end="")


if __name__ == "__main__":
    main()
