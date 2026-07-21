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
