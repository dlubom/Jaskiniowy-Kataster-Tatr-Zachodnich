"""Run a fresh, bounded mutmut campaign and enforce its complete results."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from jktz.quality import configuration, mutation_result, write_result


def main() -> int:
    root = Path.cwd()
    output = root / "logs/quality"
    try:
        output.mkdir(parents=True, exist_ok=True)
        (output / "mutation.json").unlink(missing_ok=True)
        config = configuration(root)
        executable = Path(sys.executable).with_name("mutmut")
        if not executable.is_file():
            print(
                "Mutation gate requires Python >=3.10 and POSIX (Linux/macOS/WSL).", file=sys.stderr
            )
            return 1
        # Never certify cached results after changes to tests, configuration, or code.
        mutants = root / "mutants"
        if mutants.exists():
            shutil.rmtree(mutants)
        for source in config["tool"]["mutmut"].get("also_copy", []):
            (mutants / source).parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([str(executable), "run", "--max-children", "4"], check=True)
        result = mutation_result(
            root,
            config["tool"]["mutmut"]["only_mutate"],
            config["tool"]["jktz"]["quality"]["mutation_min"],
        )
        print(f"Mutation score: {result['killed']}/{result['total']} = {result['score']:.2f}%")
        return write_result(output / "mutation.json", result)
    except subprocess.CalledProcessError as exc:
        return exc.returncode
    except (OSError, ValueError, KeyError) as exc:
        print(f"Mutation gate failed: {exc}", file=sys.stderr)
        return 1
