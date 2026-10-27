import shlex
from pathlib import Path


def test_validate_job_runs_windows_pytest_after_sync_before_external_tools() -> None:
    workflow_path = Path(__file__).parents[1] / ".github" / "workflows" / "validate.yml"
    workflow = workflow_path.read_text(encoding="utf-8")

    assert (
        """\
      - name: Sync Python tooling
        run: uv sync --locked

      - name: Run Pytest (Windows)
        if: runner.os == 'Windows'
        run: uv run pytest

      - name: Install Survex (Linux)
"""
        in workflow
    )


def test_workflows_use_installed_entrance_renderer() -> None:
    workflows = Path(__file__).parents[1] / ".github" / "workflows"
    contents = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (workflows / "validate.yml", workflows / "release.yml")
    )

    assert "uv run jktz-render-otwory" in contents
    assert "scripts/render_otwory_from_gps.py" not in contents


def test_native_walls_is_a_package_gate_with_persistent_failure_evidence() -> None:
    import yaml

    root = Path(__file__).parents[1]
    workflow = yaml.safe_load((root / ".github/workflows/validate.yml").read_text())
    job = workflow["jobs"]["walls-windows"]
    assert job["runs-on"] == "windows-latest"
    assert not job.get("continue-on-error")
    assert "walls-windows" in workflow["jobs"]["pr-release-package"]["needs"]
    steps = job["steps"]
    assert any("tests/test_walls_native.py" in s.get("run", "") for s in steps)
    compile_step = next(s for s in steps if "jktz-walls-validate" in s.get("run", ""))
    assert "--duplicates" in shlex.split(compile_step["run"])
    assert not compile_step.get("continue-on-error")
    upload = next(s for s in steps if s.get("uses", "").startswith("actions/upload-artifact"))
    assert upload["if"] == "always()"
    assert upload["with"]["if-no-files-found"] == "error"


def test_survex_duplicates_blocks_validation_and_preserves_failed_report() -> None:
    import yaml

    root = Path(__file__).parents[1]
    workflow = yaml.safe_load((root / ".github/workflows/validate.yml").read_text())
    job = workflow["jobs"]["validate"]
    assert set(job["strategy"]["matrix"]["os"]) == {"ubuntu-latest", "windows-latest"}
    assert not job.get("continue-on-error")
    steps = job["steps"]
    install = next(
        s for s in steps if s.get("uses") == "./.github/actions/install-survex-duplicates"
    )
    gate = next(s for s in steps if "jktz-survex-duplicates" in s.get("run", ""))
    full = next(s for s in steps if s.get("run") == "uv run jktz-validate")
    assert steps.index(install) < steps.index(gate)
    assert steps.index(full) < steps.index(gate)
    assert not gate.get("continue-on-error")
    smoke = next(s for s in steps if "tests/test_survex_duplicates.py" in s.get("run", ""))
    assert smoke["env"]["JKTZ_REQUIRE_SURVEX_DUPLICATES"] == "1"
    assert steps.index(install) < steps.index(smoke) < steps.index(gate)
    upload = next(s for s in steps if s.get("name") == "Upload Survex duplicate report")
    assert upload["if"] == "always()"
    assert upload["with"]["path"] == "logs/survex-duplicates/"
    assert "matrix.os" in upload["with"]["name"]
    assert upload["with"]["if-no-files-found"] == "error"
