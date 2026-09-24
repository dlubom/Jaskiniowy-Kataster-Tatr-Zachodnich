from __future__ import annotations

import io
import sys
from pathlib import Path, PureWindowsPath
from unittest.mock import Mock

import pytest

from jktz.entrances.render import RenderError, RenderResult
from jktz.reporting import CheckFailed
from jktz.validation import suite
from jktz.validation.suite import (
    ValidationContext,
    ValidationStep,
    run_steps,
    run_validation,
    validation_steps,
)


def test_validation_contract_has_twelve_named_steps(tmp_path: Path) -> None:
    context = ValidationContext(
        cavern_log=tmp_path / "cavern.log",
        exports_dir=tmp_path / "exports",
    )

    steps = validation_steps(context)

    assert len(steps) == 12
    assert steps[0].heading == "Checking SRV filenames format"
    assert steps[-1].heading == "Checking exports"


def test_run_steps_derives_progress_total_from_collection(capsys) -> None:
    calls: list[str] = []
    steps = (
        ValidationStep("First", "First", lambda: calls.append("first")),
        ValidationStep("Second", None, lambda: calls.append("second")),
    )

    run_steps(steps)

    assert calls == ["first", "second"]
    assert capsys.readouterr().out == ("[1/2] First...\n      First: Passed ✔\n[2/2] Second...\n")


def test_run_validation_removes_exports_after_failure(tmp_path: Path, monkeypatch) -> None:
    exports_dir = tmp_path / "exports"
    context = ValidationContext(
        cavern_log=tmp_path / "cavern.log",
        exports_dir=exports_dir,
    )

    def failing_steps(_context: ValidationContext) -> tuple[ValidationStep, ...]:
        def fail() -> None:
            exports_dir.mkdir()
            (exports_dir / "partial.shp").write_bytes(b"partial")
            raise RuntimeError("boom")

        return (ValidationStep("Fail", None, fail),)

    monkeypatch.setattr("jktz.validation.suite.validation_steps", failing_steps)

    try:
        run_validation(context)
    except RuntimeError as exc:
        assert str(exc) == "boom"
    else:
        raise AssertionError("run_validation should propagate validation failures")

    assert not exports_dir.exists()


def test_rendered_entrances_check_uses_package_api(monkeypatch, capsys) -> None:
    def fake_render(*, check: bool) -> RenderResult:
        assert check is True
        return RenderResult(
            output=PureWindowsPath("Poligony/OTWORY.SRV"),
            source="gps-kataster@v1",
            gps_fixes=87,
        )

    monkeypatch.setattr(suite, "render_entrances", fake_render)

    suite._check_rendered_entrances()

    assert capsys.readouterr().out == (
        "Checked Poligony/OTWORY.SRV from gps-kataster@v1\nGPS fixes: 87\n"
    )


def test_rendered_entrances_check_wraps_renderer_errors(monkeypatch) -> None:
    def fail(*, check: bool) -> RenderResult:
        raise RenderError("snapshot is stale")

    monkeypatch.setattr(suite, "render_entrances", fail)

    with pytest.raises(CheckFailed, match="entrance snapshot check failed: snapshot is stale"):
        suite._check_rendered_entrances()


def test_indentation_handles_partial_writes_and_preserves_stream_interface():
    target = io.StringIO()
    stream = suite._IndentingStream(target, "> ")

    assert stream.write("") == 0
    stream.write("first")
    stream.write(" line\nsecond\n")
    stream.write("third\r")
    stream.write("fourth")
    stream.flush()

    assert target.getvalue() == "> first line\n> second\n> third\r> fourth"
    assert stream.getvalue() == target.getvalue()


def test_indentation_restores_stdout_when_export_fails():
    original = sys.stdout

    with pytest.raises(RuntimeError, match="export failed"), suite._indent_stdout():
        raise RuntimeError("export failed")

    assert sys.stdout is original


def test_exports_run_before_artifact_checks_with_shared_destination(tmp_path, monkeypatch, capsys):
    context = ValidationContext(exports_dir=tmp_path / "artifacts", exports_version="custom")
    calls = []

    def export(**kwargs):
        calls.append(("export", kwargs))
        print("compiler output")

    monkeypatch.setattr(suite.pipeline, "run_exports", export)
    for name in ("empty_shapefiles", "shapefiles_count", "shapefiles_extent"):
        monkeypatch.setattr(
            getattr(suite, name),
            "check",
            lambda _name=name, **kwargs: calls.append((_name, kwargs)),
        )

    suite._check_exports(context)

    assert calls == [
        ("export", {"version": "custom", "outdir": context.exports_dir}),
        ("empty_shapefiles", {"outdir": context.exports_dir}),
        ("shapefiles_count", {"outdir": context.exports_dir, "version": "custom"}),
        ("shapefiles_extent", {"outdir": context.exports_dir, "version": "custom"}),
    ]
    assert capsys.readouterr().out == "                   compiler output\n"


def test_validation_contract_compiles_then_checks_the_same_log(tmp_path, monkeypatch):
    context = ValidationContext(cavern_log=tmp_path / "compile.txt")
    compile_project = Mock()
    unattached = Mock()
    warnings = Mock()
    exports = Mock()
    monkeypatch.setattr(suite.exports_tools, "cavern", compile_project)
    monkeypatch.setattr(suite.unattached, "check", unattached)
    monkeypatch.setattr(suite.cavern_warnings, "check", warnings)
    monkeypatch.setattr(suite, "_check_exports", exports)

    for step in validation_steps(context)[8:]:
        step.check()

    compile_project.assert_called_once_with(["KATASTER.wpj"], log_to=context.cavern_log)
    unattached.assert_called_once_with(log_path=context.cavern_log)
    warnings.assert_called_once_with(log_path=context.cavern_log)
    exports.assert_called_once_with(context)


@pytest.mark.parametrize("create_exports", [False, True])
def test_successful_default_validation_cleans_only_its_temporary_exports(
    tmp_path, monkeypatch, create_exports
):
    monkeypatch.chdir(tmp_path)
    retained = tmp_path / "retained.txt"
    retained.write_text("keep")
    contexts = []

    def steps(context):
        contexts.append(context)

        def generate():
            if create_exports:
                context.exports_dir.mkdir()
                (context.exports_dir / "generated.txt").write_text("remove")

        return (ValidationStep("Generate", None, generate),)

    monkeypatch.setattr(suite, "validation_steps", steps)

    run_validation()

    assert contexts == [ValidationContext()]
    assert not (tmp_path / "validate-exports").exists()
    assert retained.read_text() == "keep"


def test_validation_stops_at_first_failure_without_success_message(capsys):
    later = Mock()
    steps = [
        ValidationStep("Invalid", "Invalid", Mock(side_effect=CheckFailed("bad data"))),
        ValidationStep("Later", "Later", later),
    ]

    with pytest.raises(CheckFailed, match="bad data"):
        run_steps(steps)

    later.assert_not_called()
    assert capsys.readouterr().out == "[1/2] Invalid...\n"
