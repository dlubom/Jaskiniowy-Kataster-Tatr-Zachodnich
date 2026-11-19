"""Reject geometric duplicate candidates, excluding SPLAY and DUPLICATE legs."""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
from pathlib import Path


def report_count(path: Path) -> int:
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.reader(stream, strict=True)
        header = next(reader, [])
        if header[:2] != ["leg_a", "leg_b"]:
            raise ValueError("Invalid survex-duplicates CSV header")
        count = 0
        for row in reader:
            if len(row) != len(header):
                raise ValueError("Malformed survex-duplicates CSV row")
            count += 1
    return count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", type=Path, default=Path("KATASTER.3d"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--detector", default=os.environ.get("SURVEX_DUPLICATES", "survex-duplicates")
    )
    args = parser.parse_args(argv)
    command = [
        args.detector,
        str(args.input),
        "--exclude-splays",
        "--relative-percent",
        "5",
        "--out",
        str(args.output),
    ]
    try:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        completed = subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8", timeout=180, check=False
        )
        args.output.with_suffix(".log").write_text(
            completed.stdout + completed.stderr, encoding="utf-8"
        )
        completed.check_returncode()
        summary = json.loads(completed.stderr)
        count = report_count(args.output)
        if type(summary["K"]) is not int or summary["K"] != count:
            raise ValueError("Detector summary and CSV pair count disagree")
    except (OSError, ValueError, TypeError, KeyError, csv.Error, subprocess.SubprocessError) as exc:
        print(f"FAIL: survex-duplicates: {exc}")
        return 1
    print(f"{'FAIL' if count else 'PASS'}: {count} geometric duplicate pairs; {args.output}")
    return 1 if count else 0
