from __future__ import annotations

from pathlib import Path

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
