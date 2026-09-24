"""Run lint, fresh branch coverage, and CRAP checks from the repository root."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from jktz.quality import SOURCE_DIRS, configuration, coverage_result, write_result


def main() -> int:
    root = Path.cwd()
    output = root / "logs/quality"
    report = output / "coverage.json"
    commands = [
        ["ruff", "format", "--check", *SOURCE_DIRS, "tests"],
        ["ruff", "check", *SOURCE_DIRS, "tests"],
        ["coverage", "erase"],
        ["coverage", "run", "-m", "pytest", "-q"],
        ["coverage", "json", "-o", str(report)],
        ["coverage", "html", "-d", str(output / "html")],
    ]
    try:
        output.mkdir(parents=True, exist_ok=True)
        report.unlink(missing_ok=True)
        (output / "quality.json").unlink(missing_ok=True)
        if (output / "html").exists():
            shutil.rmtree(output / "html")
        policy = configuration(root)["tool"]["jktz"]["quality"]
        for command in commands:
            subprocess.run([sys.executable, "-m", *command], check=True)
        result = coverage_result(root, json.loads(report.read_text()), policy)
        print(f"Lines: {result['line_percent']:.2f}%; branches: {result['branch_percent']:.2f}%")
        return write_result(output / "quality.json", result)
    except subprocess.CalledProcessError as exc:
        return exc.returncode
    except (OSError, ValueError, KeyError) as exc:
        print(f"Quality gate failed: {exc}", file=sys.stderr)
        return 1
