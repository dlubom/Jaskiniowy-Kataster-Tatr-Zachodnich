from pathlib import Path

ROOT = Path(__file__).parents[1]
SURVEX_VERSION = "1.4.22"


def test_validate_job_runs_windows_pytest_after_sync_before_external_tools() -> None:
    workflow_path = ROOT / ".github" / "workflows" / "validate.yml"
    workflow = workflow_path.read_text(encoding="utf-8")

    assert (
        """\
      - name: Sync Python tooling
        run: uv sync --locked

      - name: Run Pytest (Windows)
        if: runner.os == 'Windows'
        run: uv run pytest

      - name: Install Survex
"""
        in workflow
    )


def test_workflows_pin_current_survex_release() -> None:
    workflow_dir = ROOT / ".github" / "workflows"
    workflows = sorted(
        path for path in workflow_dir.glob("*.yml") if "SURVEX_VERSION" in path.read_text()
    )

    assert workflows
    for workflow_path in workflows:
        workflow = workflow_path.read_text(encoding="utf-8")
        assert f'SURVEX_VERSION: "{SURVEX_VERSION}"' in workflow, workflow_path.name
        assert 'SURVEX_VERSION: "1.4.21"' not in workflow, workflow_path.name


def test_install_survex_action_uses_current_release_example() -> None:
    action_path = ROOT / ".github" / "actions" / "install-survex" / "action.yml"
    action = action_path.read_text(encoding="utf-8")

    assert f"description: Survex version (e.g. {SURVEX_VERSION})" in action


def test_validate_job_uses_shared_survex_action_instead_of_windows_installer() -> None:
    workflow_path = ROOT / ".github" / "workflows" / "validate.yml"
    workflow = workflow_path.read_text(encoding="utf-8")

    assert "survex-microsoft-windows" not in workflow
    assert "mamba-org/setup-micromamba" not in workflow
    assert workflow.count("uses: ./.github/actions/install-survex") == 2


def test_install_survex_action_builds_from_source_on_windows() -> None:
    action_path = ROOT / ".github" / "actions" / "install-survex" / "action.yml"
    action = action_path.read_text(encoding="utf-8")

    assert "msys2/setup-msys2@v2" in action
    assert "survex-${{ inputs.version }}.tar.gz" in action
    assert "mingw-w64-ucrt-x86_64-wxwidgets3.2-msw" in action
    assert "SURVEXLIB=" in action
