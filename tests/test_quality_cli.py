from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from jktz.cli import mutation, quality


@pytest.fixture
def workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text(
        """\
[tool.jktz.quality]
line_min = 90
branch_min = 85
crap_max = 30
mutation_min = 80
[tool.mutmut]
only_mutate = ["src/example.py"]
also_copy = [".agents/skills/helper.py"]
""",
        encoding="utf-8",
    )
    (tmp_path / "src").mkdir()
    (tmp_path / "src/example.py").write_text("value = 1\n", encoding="utf-8")
    return tmp_path


def coverage_report() -> dict:
    return {
        "meta": {"branch_coverage": True},
        "files": {"src/example.py": {"functions": {}}},
        "totals": {
            "num_statements": 1,
            "covered_lines": 1,
            "num_branches": 0,
            "covered_branches": 0,
        },
    }


def fake_mutmut(root: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    binary = root / "bin" / "mutmut"
    binary.parent.mkdir()
    binary.touch()
    monkeypatch.setattr(mutation.sys, "executable", str(binary.with_name("python")))
    return binary


def test_quality_runs_fresh_coverage_after_lint_and_writes_results(
    workspace: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    commands = []

    def run(command: list[str], *, check: bool) -> None:
        assert check
        commands.append(command[2:])
        if command[2:4] == ["coverage", "json"]:
            Path(command[-1]).write_text(json.dumps(coverage_report()), encoding="utf-8")

    monkeypatch.setattr(quality.subprocess, "run", run)

    assert quality.main() == 0

    assert [command[:2] for command in commands] == [
        ["ruff", "format"],
        ["ruff", "check"],
        ["coverage", "erase"],
        ["coverage", "run"],
        ["coverage", "json"],
        ["coverage", "html"],
    ]
    assert commands[0][2] == "--check"
    assert {"src", "scripts", ".agents/skills", "web", "tests"} <= set(commands[0])
    assert commands[3] == ["coverage", "run", "-m", "pytest", "-q"]
    result = json.loads((workspace / "logs/quality/quality.json").read_text())
    assert result["failures"] == []
    assert "Lines: 100.00%; branches: 100.00%" in capsys.readouterr().out


@pytest.mark.parametrize("failure_index", range(6))
def test_quality_stops_and_propagates_each_external_failure(
    workspace: Path, monkeypatch: pytest.MonkeyPatch, failure_index: int
) -> None:
    commands = []

    def run(command: list[str], *, check: bool) -> None:
        assert check
        commands.append(command)
        if len(commands) - 1 == failure_index:
            raise subprocess.CalledProcessError(7, command)

    monkeypatch.setattr(quality.subprocess, "run", run)

    assert quality.main() == 7
    assert len(commands) == failure_index + 1
    assert not (workspace / "logs/quality/quality.json").exists()


def test_quality_removes_stale_reports_even_when_lint_fails(
    workspace: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = workspace / "logs/quality"
    (output / "html").mkdir(parents=True)
    for name in ("quality.json", "coverage.json", "html/index.html"):
        (output / name).write_text("old passing report", encoding="utf-8")
    (output / "mutation.json").write_text("separate mutation evidence", encoding="utf-8")

    def run(command: list[str], *, check: bool) -> None:
        assert check
        assert not (output / "quality.json").exists()
        assert not (output / "coverage.json").exists()
        assert not (output / "html").exists()
        raise subprocess.CalledProcessError(1, command)

    monkeypatch.setattr(quality.subprocess, "run", run)

    assert quality.main() == 1
    assert (output / "mutation.json").read_text() == "separate mutation evidence"


@pytest.mark.parametrize("report", [None, "not JSON", "{}"])
def test_quality_rejects_missing_or_malformed_coverage_report(
    workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    report: str,
) -> None:
    def run(command: list[str], *, check: bool) -> None:
        assert check
        if report is not None and command[2:4] == ["coverage", "json"]:
            Path(command[-1]).write_text(report, encoding="utf-8")

    monkeypatch.setattr(quality.subprocess, "run", run)

    assert quality.main() == 1
    assert "Quality gate failed:" in capsys.readouterr().err


def test_quality_returns_failure_for_measured_threshold_breach(
    workspace: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    report = coverage_report()
    report["totals"]["covered_lines"] = 0

    def run(command: list[str], *, check: bool) -> None:
        assert check
        if command[2:4] == ["coverage", "json"]:
            Path(command[-1]).write_text(json.dumps(report), encoding="utf-8")

    monkeypatch.setattr(quality.subprocess, "run", run)

    assert quality.main() == 1
    result = json.loads((workspace / "logs/quality/quality.json").read_text())
    assert result["failures"] == ["Line coverage 0.00% < 90%"]


def test_mutation_deletes_cached_campaign_and_prepares_nested_copy_paths(
    workspace: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    executable = fake_mutmut(workspace, monkeypatch)
    (workspace / "mutants").mkdir()
    (workspace / "mutants" / "old-cache").write_text("old result", encoding="utf-8")
    output = workspace / "logs/quality"
    output.mkdir(parents=True)
    (output / "mutation.json").write_text("stale passing report", encoding="utf-8")
    (output / "quality.json").write_text("separate quality evidence", encoding="utf-8")

    def run(command: list[str], *, check: bool) -> None:
        assert check
        assert command == [str(executable), "run", "--max-children", "4"]
        assert not (workspace / "mutants" / "old-cache").exists()
        assert (workspace / "mutants/.agents/skills").is_dir()
        assert not (output / "mutation.json").exists()
        metadata = workspace / "mutants/src/example.py.meta"
        metadata.parent.mkdir(parents=True)
        metadata.write_text(json.dumps({"exit_code_by_key": {"mutant": 1}}), encoding="utf-8")

    monkeypatch.setattr(mutation.subprocess, "run", run)

    assert mutation.main() == 0
    result = json.loads((output / "mutation.json").read_text())
    assert result["score"] == 100
    assert result["failures"] == []
    assert "Mutation score: 1/1 = 100.00%" in capsys.readouterr().out
    assert (output / "quality.json").read_text() == "separate quality evidence"


def test_mutation_missing_runner_fails_without_reusing_report(
    workspace: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(mutation.sys, "executable", str(workspace / "bin/python"))
    output = workspace / "logs/quality"
    output.mkdir(parents=True)
    (output / "mutation.json").write_text("stale passing report", encoding="utf-8")

    assert mutation.main() == 1
    assert "requires Python >=3.10 and POSIX" in capsys.readouterr().err
    assert not (output / "mutation.json").exists()


def test_mutation_propagates_runner_failure_without_reading_cached_results(
    workspace: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_mutmut(workspace, monkeypatch)

    def run(command: list[str], *, check: bool) -> None:
        assert check
        raise subprocess.CalledProcessError(5, command)

    monkeypatch.setattr(mutation.subprocess, "run", run)

    assert mutation.main() == 5
    assert not (workspace / "logs/quality/mutation.json").exists()


@pytest.mark.parametrize("metadata", [None, "not JSON", "{}"])
def test_mutation_rejects_missing_or_malformed_results(
    workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    metadata: str,
) -> None:
    fake_mutmut(workspace, monkeypatch)

    def run(command: list[str], *, check: bool) -> None:
        assert check
        if metadata is not None:
            output = workspace / "mutants/src/example.py.meta"
            output.parent.mkdir(parents=True)
            output.write_text(metadata, encoding="utf-8")

    monkeypatch.setattr(mutation.subprocess, "run", run)

    assert mutation.main() == 1
    assert "Mutation gate failed:" in capsys.readouterr().err


def test_mutation_returns_failure_for_surviving_mutants(
    workspace: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_mutmut(workspace, monkeypatch)

    def run(command: list[str], *, check: bool) -> None:
        assert check
        output = workspace / "mutants/src/example.py.meta"
        output.parent.mkdir(parents=True)
        output.write_text(json.dumps({"exit_code_by_key": {"survivor": 0}}), encoding="utf-8")

    monkeypatch.setattr(mutation.subprocess, "run", run)

    assert mutation.main() == 1
    result = json.loads((workspace / "logs/quality/mutation.json").read_text())
    assert result["survivors"] == ["survivor"]
    assert result["failures"] == ["Mutation score 0.00% < 80%: src/example.py"]


@pytest.mark.parametrize("gate", [quality, mutation])
def test_gates_report_missing_configuration(
    workspace: Path, capsys: pytest.CaptureFixture[str], gate: object
) -> None:
    (workspace / "pyproject.toml").unlink()
    assert gate.main() == 1
    assert "gate failed:" in capsys.readouterr().err
