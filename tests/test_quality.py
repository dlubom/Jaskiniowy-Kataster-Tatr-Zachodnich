from __future__ import annotations

import json
from pathlib import Path

import pytest

from jktz.quality import configuration, coverage_result, crap, mutation_result, write_result

POLICY = {"line_min": 90, "branch_min": 85, "crap_max": 30}


def summary(lines: int = 10, covered: int = 10, branches: int = 2, hit: int = 2) -> dict:
    return {
        "num_statements": lines,
        "covered_lines": covered,
        "num_branches": branches,
        "covered_branches": hit,
    }


def make_report(root: Path, source: str, functions: dict) -> dict:
    path = root / "src" / "example.py"
    path.parent.mkdir(parents=True)
    path.write_text(source, encoding="utf-8")
    return {
        "meta": {"branch_coverage": True},
        "files": {"src/example.py": {"functions": functions}},
        "totals": summary(),
    }


def mutation_metadata(root: Path, source: str, outcomes: dict) -> None:
    path = root / "mutants" / (source + ".meta")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"exit_code_by_key": outcomes}), encoding="utf-8")


def test_configuration_loads_repository_policy(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[tool.jktz.quality]\nline_min = 90\n", encoding="utf-8"
    )
    assert configuration(tmp_path)["tool"]["jktz"]["quality"]["line_min"] == 90


@pytest.mark.parametrize("complexity, coverage, expected", [(30, 1, 30), (5, 0, 30), (4, 0.5, 6)])
def test_crap_formula_uses_cubic_uncovered_fraction(
    complexity: int, coverage: float, expected: float
) -> None:
    assert crap(complexity, coverage) == pytest.approx(expected)


def test_coverage_gate_accepts_thresholds_and_handles_functions_without_branches(
    tmp_path: Path,
) -> None:
    report = make_report(
        tmp_path,
        "def identity(value):\n    return value\n",
        {"identity": {"summary": summary(branches=0, hit=0)}},
    )
    report["totals"] = summary(lines=100, covered=90, branches=100, hit=85)

    result = coverage_result(tmp_path, report, POLICY)

    assert result["failures"] == []
    assert result["line_percent"] == 90
    assert result["branch_percent"] == 85
    assert result["functions"] == [
        {
            "file": "src/example.py",
            "function": "identity",
            "complexity": 1,
            "coverage": 1,
            "crap": 1,
        }
    ]


def test_missing_branch_coverage_cannot_pass(tmp_path: Path) -> None:
    report = make_report(tmp_path, "", {})
    report["meta"]["branch_coverage"] = False
    with pytest.raises(ValueError, match="Branch coverage is required"):
        coverage_result(tmp_path, report, POLICY)


def test_windows_coverage_paths_match_portable_source_inventory(tmp_path: Path) -> None:
    report = make_report(
        tmp_path,
        "def identity(value):\n    return value\n",
        {"identity": {"summary": summary(branches=0, hit=0)}},
    )
    report["files"][r"src\example.py"] = report["files"].pop("src/example.py")

    result = coverage_result(tmp_path, report, POLICY)

    assert result["failures"] == []
    assert result["functions"][0]["file"] == "src/example.py"


def test_duplicate_normalized_coverage_paths_are_rejected(tmp_path: Path) -> None:
    report = make_report(tmp_path, "", {})
    report["files"][r"src\example.py"] = {"functions": {}}
    with pytest.raises(ValueError, match="Ambiguous duplicate coverage paths"):
        coverage_result(tmp_path, report, POLICY)


@pytest.mark.parametrize("directory", ["src", "scripts", ".agents/skills", "web"])
def test_missing_source_file_cannot_be_hidden_from_coverage(tmp_path: Path, directory: str) -> None:
    report = make_report(tmp_path, "", {})
    omitted = tmp_path / directory / "untested.py"
    omitted.parent.mkdir(parents=True, exist_ok=True)
    omitted.write_text("value = 1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Missing coverage files"):
        coverage_result(tmp_path, report, POLICY)


def test_missing_function_coverage_cannot_pass(tmp_path: Path) -> None:
    report = make_report(tmp_path, "def omitted():\n    return 1\n", {})
    with pytest.raises(ValueError, match="Missing function coverage: src/example.py:omitted"):
        coverage_result(tmp_path, report, POLICY)


def test_wholly_untested_function_cannot_hide_behind_high_global_coverage(tmp_path: Path) -> None:
    report = make_report(
        tmp_path,
        "def omitted(value):\n    return value\n",
        {"omitted": {"summary": summary(lines=1, covered=0, branches=0, hit=0)}},
    )

    result = coverage_result(tmp_path, report, POLICY)

    assert result["line_percent"] == 100
    assert result["functions"][0]["crap"] == 2
    assert result["failures"] == ["Untested function: src/example.py:omitted"]
    assert result["files"] == ["src/example.py"]


def test_placeholder_function_with_zero_statements_cannot_pass(tmp_path: Path) -> None:
    # Coverage.py reports 0/0 statements for an uncalled ellipsis-only function.
    report = make_report(
        tmp_path,
        "def placeholder():\n    ...\n",
        {"placeholder": {"summary": summary(lines=0, covered=0, branches=0, hit=0)}},
    )

    result = coverage_result(tmp_path, report, POLICY)

    assert result["line_percent"] == 100
    assert result["failures"] == ["Untested function: src/example.py:placeholder"]


def test_empty_coverage_report_cannot_pass(tmp_path: Path) -> None:
    report = make_report(tmp_path, "", {})
    report["totals"] = summary(lines=0, covered=0, branches=0, hit=0)
    with pytest.raises(ValueError, match="Empty coverage report"):
        coverage_result(tmp_path, report, POLICY)


def test_line_and_branch_thresholds_are_independent(tmp_path: Path) -> None:
    report = make_report(tmp_path, "", {})
    report["totals"] = summary(lines=100, covered=89, branches=100, hit=84)
    result = coverage_result(tmp_path, report, POLICY)
    assert result["failures"] == ["Line coverage 89.00% < 90%", "Branch coverage 84.00% < 85%"]


def test_function_crap_uses_weaker_branch_coverage_and_accepts_exact_boundary(
    tmp_path: Path,
) -> None:
    report = make_report(
        tmp_path,
        "def choose(value):\n    return 1 if value else 2\n",
        {"choose": {"summary": summary(hit=1)}},
    )
    policy = {**POLICY, "crap_max": 2.5}

    result = coverage_result(tmp_path, report, policy)

    assert result["failures"] == []
    assert result["functions"][0]["coverage"] == 0.5
    assert result["functions"][0]["crap"] == 2.5
    report["files"]["src/example.py"]["functions"]["choose"]["summary"]["covered_branches"] = 0
    result = coverage_result(tmp_path, report, policy)
    assert result["failures"] == ["CRAP 6.00 > 2.5: src/example.py:choose"]


def test_methods_nested_classes_and_closures_have_unique_qualified_names(tmp_path: Path) -> None:
    source = """\
class Parser:
    class Nested:
        def parse(self, value):
            return value
    def parse(self, value):
        def clean(text):
            return text if text else "empty"
        return clean(value)

def outer(value):
    def inner(item):
        return item if item else 0
    return inner(value)
"""
    names = ["Parser.Nested.parse", "Parser.parse", "Parser.parse.clean", "outer", "outer.inner"]
    report = make_report(tmp_path, source, {name: {"summary": summary()} for name in names})

    result = coverage_result(tmp_path, report, POLICY)

    assert result["failures"] == []
    assert {item["function"] for item in result["functions"]} == set(names)
    assert len(result["functions"]) == len(names)
    assert [item["crap"] for item in result["functions"]] == [2, 2, 1, 1, 1]


def test_mutation_threshold_is_enforced_for_each_module(tmp_path: Path) -> None:
    first, second = "src/first.py", "src/second.py"
    mutation_metadata(tmp_path, first, {f"first_{index}": 1 for index in range(9)})
    mutation_metadata(tmp_path, second, {"survivor": 0})

    result = mutation_result(tmp_path, [first, second], 80)

    assert result["killed"] == 9
    assert result["total"] == 10
    assert result["score"] == 90
    assert result["modules"] == [
        {"file": first, "killed": 9, "total": 9, "score": 100},
        {"file": second, "killed": 0, "total": 1, "score": 0},
    ]
    assert result["survivors"] == ["survivor"]
    assert result["failures"] == ["Mutation score 0.00% < 80%: src/second.py"]


def test_mutation_score_accepts_exact_threshold(tmp_path: Path) -> None:
    mutation_metadata(tmp_path, "src/first.py", {"a": 1, "b": 1, "c": 1, "d": 1, "e": 0})
    result = mutation_result(tmp_path, ["src/first.py"], 80)
    assert result["score"] == 80
    assert result["failures"] == []


@pytest.mark.parametrize("exit_code", [None, 2, 3, 4, 5, -11, -9, 24, 33, 255])
def test_incomplete_crashed_or_invalid_mutants_are_never_kills(
    tmp_path: Path, exit_code: int
) -> None:
    mutation_metadata(tmp_path, "src/first.py", {"killed": 1, "invalid": exit_code})
    result = mutation_result(tmp_path, ["src/first.py"], 0)
    assert result["killed"] == 1
    assert result["total"] == 2
    assert result["score"] == 50
    assert result["failures"] == [f"Incomplete or invalid mutation result ({exit_code}): invalid"]


def test_missing_mutation_metadata_cannot_pass(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        mutation_result(tmp_path, ["src/first.py"], 80)


def test_empty_mutation_scope_cannot_pass(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Empty mutation scope"):
        mutation_result(tmp_path, [], 80)


def test_no_generated_mutants_cannot_pass(tmp_path: Path) -> None:
    mutation_metadata(tmp_path, "src/first.py", {})
    with pytest.raises(ValueError, match="No mutants generated: src/first.py"):
        mutation_result(tmp_path, ["src/first.py"], 80)


@pytest.mark.parametrize("failures, status", [([], 0), (["Gate failed"], 1)])
def test_result_writer_preserves_evidence_and_failure_exit_status(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], failures: list[str], status: int
) -> None:
    report = tmp_path / "quality.json"
    result = {"failures": failures, "score": 42}
    assert write_result(report, result) == status
    assert json.loads(report.read_text(encoding="utf-8")) == result
    assert report.read_bytes().endswith(b"\n")
    output = capsys.readouterr().out
    assert str(report) in output
    if failures:
        assert failures[0] in output
