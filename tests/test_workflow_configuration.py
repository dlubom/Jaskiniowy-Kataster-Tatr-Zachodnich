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
