"""Quality policy and report checks shared by the local and CI gates."""

from __future__ import annotations

import json
from pathlib import Path

from radon.complexity import cc_visit

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

SOURCE_DIRS = ("src", "scripts", ".agents/skills", "web")


def configuration(root: Path) -> dict:
    with (root / "pyproject.toml").open("rb") as stream:
        return tomllib.load(stream)


def fraction(summary: dict, covered: str, total: str) -> float:
    return summary[covered] / summary[total] if summary[total] else 1.0


def crap(complexity: int, coverage: float) -> float:
    return complexity**2 * (1 - coverage) ** 3 + complexity


def _functions(blocks, prefix: str = ""):
    for block in blocks:
        # Radon lists class methods twice: inside Class.methods and flattened
        # into the top-level result. Coverage uses only their qualified names.
        if not prefix and getattr(block, "is_method", False):
            continue
        name = prefix + block.name
        if hasattr(block, "methods"):
            yield from _functions(block.methods, name + ".")
            yield from _functions(block.inner_classes, name + ".")
        else:
            yield name, block.complexity
            yield from _functions(block.closures, name + ".")


def coverage_result(root: Path, report: dict, policy: dict) -> dict:
    """Reject missing files/functions and calculate per-function branch-aware CRAP."""
    if not report["meta"]["branch_coverage"]:
        raise ValueError("Branch coverage is required")
    files = {name.replace("\\", "/"): measured for name, measured in report["files"].items()}
    if len(files) != len(report["files"]):
        raise ValueError("Ambiguous duplicate coverage paths")
    expected = {
        path.relative_to(root).as_posix()
        for directory in SOURCE_DIRS
        for path in (root / directory).rglob("*.py")
    }
    missing = expected - files.keys()
    if missing:
        raise ValueError(f"Missing coverage files: {sorted(missing)}")
    totals = report["totals"]
    if not totals["num_statements"]:
        raise ValueError("Empty coverage report")
    line_pct = 100 * fraction(totals, "covered_lines", "num_statements")
    branch_pct = 100 * fraction(totals, "covered_branches", "num_branches")
    failures = []
    if line_pct < policy["line_min"]:
        failures.append(f"Line coverage {line_pct:.2f}% < {policy['line_min']}%")
    if branch_pct < policy["branch_min"]:
        failures.append(f"Branch coverage {branch_pct:.2f}% < {policy['branch_min']}%")
    functions = []
    for filename in sorted(expected):
        measured = files[filename]["functions"]
        for name, complexity in _functions(cc_visit((root / filename).read_text(encoding="utf-8"))):
            if name not in measured:
                raise ValueError(f"Missing function coverage: {filename}:{name}")
            summary = measured[name]["summary"]
            if summary["num_statements"] and not summary["covered_lines"]:
                failures.append(f"Untested function: {filename}:{name}")
            coverage = min(
                fraction(summary, "covered_lines", "num_statements"),
                fraction(summary, "covered_branches", "num_branches"),
            )
            score = crap(complexity, coverage)
            functions.append(
                {
                    "file": filename,
                    "function": name,
                    "complexity": complexity,
                    "coverage": coverage,
                    "crap": score,
                }
            )
            if score > policy["crap_max"]:
                failures.append(f"CRAP {score:.2f} > {policy['crap_max']}: {filename}:{name}")
    return {
        "files": sorted(expected),
        "line_percent": line_pct,
        "branch_percent": branch_pct,
        "functions": sorted(functions, key=lambda row: row["crap"], reverse=True),
        "failures": failures,
    }


def mutation_result(root: Path, paths: list[str], minimum: float) -> dict:
    """Only pytest assertion failures count as kills; incomplete/error runs fail closed.

    The JSON metadata adapter is tied to the pinned mutmut version. Exit code 3
    is a pytest internal error, even though mutmut itself counts it as a kill.
    """
    failures = []
    modules = []
    survivors = []
    total = killed = 0
    if not paths:
        raise ValueError("Empty mutation scope")
    for source in paths:
        metadata = json.loads((root / "mutants" / (source + ".meta")).read_text())
        outcomes = metadata["exit_code_by_key"]
        if not outcomes:
            raise ValueError(f"No mutants generated: {source}")
        count = sum(code == 1 for code in outcomes.values())
        score = 100 * count / len(outcomes)
        modules.append({"file": source, "killed": count, "total": len(outcomes), "score": score})
        if score < minimum:
            failures.append(f"Mutation score {score:.2f}% < {minimum}%: {source}")
        for mutant, code in outcomes.items():
            if code == 0:
                survivors.append(mutant)
            elif code != 1:
                failures.append(f"Incomplete or invalid mutation result ({code}): {mutant}")
        total += len(outcomes)
        killed += count
    return {
        "killed": killed,
        "total": total,
        "score": 100 * killed / total,
        "modules": modules,
        "survivors": survivors,
        "failures": failures,
    }


def write_result(path: Path, result: dict) -> int:
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for failure in result["failures"]:
        print(failure)
    print(f"Report: {path}")
    return int(bool(result["failures"]))
