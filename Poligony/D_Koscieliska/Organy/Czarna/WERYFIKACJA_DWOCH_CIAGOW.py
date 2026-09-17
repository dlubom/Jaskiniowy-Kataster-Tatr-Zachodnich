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
    baseline = run("git", "show", f"{BASE}:KATASTER.wpj")
    fixes = (root / "Poligony/OTWORY.SRV").read_text()
    transcription = (root / CAVE / "CZ_GL_R.SRV").read_text()
    old_transcription = run("git", "show", f"{TRANSCRIPTION}:{CAVE}/CZ_GL_R.SRV")
    rows = measurements(transcription)
    assert rows == measurements(old_transcription), "Transcription measurements changed"
    assert len(rows) == 78
    # Every previously active SRV is byte-identical, including the GPS snapshot.
    old_paths = run("git", "ls-tree", "-r", "--name-only", BASE).splitlines()
    preserved = [p for p in old_paths if p.upper().endswith(".SRV") and "/_RAW/" not in p]
    for path in preserved:
        original = subprocess.check_output(["git", "show", f"{BASE}:{path}"])
        assert (root / path).read_bytes() == original, path
    ref = next(line for line in project.splitlines() if line.startswith(".REF"))

    def compile_case(directory: Path, text: str, one_fix: bool = False, cave_only: bool = False):
        directory.mkdir()
        paths = [Path(p) for p in preserved] + [CAVE / n for n in ["CZ_GL_R.SRV", "CZ_GL_N.SRV"]]
        for path in paths:
            target_path = directory / path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / path, target_path)
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

    with tempfile.TemporaryDirectory(prefix="czarna-dwa-ciagi-") as tmp:
        scratch = Path(tmp)
        old, old_counts = compile_case(scratch / "baseline", baseline)
        new, new_counts = compile_case(scratch / "new", project)
        old_free, _ = compile_case(scratch / "baseline-one-fix", baseline, True)
        new_free, _ = compile_case(scratch / "new-one-fix", project, True)
        borowiec, _ = compile_case(
            scratch / "isolated-one-fix", isolated(["CZ_B_DAV.SRV", "CZ_K_S.SRV"]), True, True
        )
        max_shift = max(math.dist(pos, new[name]) for name, pos in old.items())
        max_free_shift = max(math.dist(pos, new_free[name]) for name, pos in old_free.items())
        assert max_shift == max_free_shift == 0, "Existing network shifted at dump3d resolution"
        assert new_counts["loops"] == old_counts["loops"]
        assert new_counts["stations"] - old_counts["stations"] == 79
        assert new_counts["legs"] - old_counts["legs"] == 79
        target = old[THIRD]

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
        paths += [CAVE / name for name in [*OLD, "CZ_GL_R.SRV", "CZ_GL_N.SRV"]]
        report = {
            "base_commit": BASE,
            "transcription_commit": TRANSCRIPTION,
            "survex": run("cavern", "--version").strip(),
            "coordinate_resolution_m": 0.01,
            "input_sha256": {
                str(p): hashlib.sha256((root / p).read_bytes()).hexdigest() for p in paths
            },
            "previous_srv_files_byte_identical": len(preserved),
            "transcription_rows_unchanged": len(rows),
            "transcription_length_m": round(sum(float(row[2]) for row in rows), 2),
            "baseline": old_counts,
            "both_traverses": new_counts,
            "old_node_labels_checked": len(old),
            "max_existing_node_shift_m": max_shift,
            "max_existing_node_shift_one_fix_m": max_free_shift,
            "gnss_III_UTM34N": target,
            "closure_mixed": closure(new_free),
            "closure_borowiec_with_old_kujat_tail": closure(borowiec),
            "closure_new_kujat": None,
            "new_kujat_limitation": "No second identified tie; no loop closure available.",
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
