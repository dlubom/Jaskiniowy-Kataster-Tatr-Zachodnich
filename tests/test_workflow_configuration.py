import shlex
import shutil
import subprocess
from pathlib import Path

import pytest


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
    full = next(s for s in steps if s.get("run", "").startswith("uv run jktz-validate "))
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


@pytest.mark.parametrize("missing_source", [False, True])
def test_pages_compile_rejects_missing_survey(tmp_path, missing_source):
    import yaml

    cavern = shutil.which("cavern")
    if cavern is None:
        pytest.skip("Survex is not installed")
    root = Path(__file__).parents[1]
    workflow = yaml.safe_load((root / ".github/workflows/deploy-pages.yml").read_text())
    compile_step = next(
        step
        for step in workflow["jobs"]["deploy"]["steps"]
        if step.get("name") == "Compile with cavern"
    )
    command = shlex.split(compile_step["run"])
    assert command[0] == "cavern"
    project = ".BOOK Fixture\n.NAME KATASTER\n.STATUS 3\n.SURVEY Data\n.NAME DATA\n.STATUS 8\n"
    if missing_source:
        project += ".SURVEY Missing\n.NAME ABSENT\n.STATUS 8\n"
    (tmp_path / "KATASTER.wpj").write_text(project + ".ENDBOOK\n")
    (tmp_path / "DATA.SRV").write_text("#units meters order=DAV\na b 1 0 0\n")

    result = subprocess.run(
        [cavern, *command[1:]], cwd=tmp_path, capture_output=True, text=True, timeout=15
    )

    assert (result.returncode == 0) is not missing_source, result.stdout + result.stderr
    assert (tmp_path / "KATASTER.3d").exists() is not missing_source


@pytest.mark.parametrize("inherited_hook_index", [False, True])
def test_pages_version_identifies_untagged_commit(tmp_path, monkeypatch, inherited_hook_index):
    if inherited_hook_index:
        monkeypatch.setenv("GIT_INDEX_FILE", str(tmp_path / "parent-hook" / "index"))
    import os

    import yaml

    git_env = {
        key: value for key, value in os.environ.items() if not key.upper().startswith("GIT_")
    }

    bash = shutil.which("bash")
    git = shutil.which("git")
    if bash is None or git is None:
        pytest.skip("Pages version command requires bash and git")
    root = Path(__file__).parents[1]
    workflow = yaml.safe_load((root / ".github/workflows/deploy-pages.yml").read_text())
    step = next(
        step
        for step in workflow["jobs"]["deploy"]["steps"]
        if step.get("name") == "Prepare public directory"
    )
    assignment = next(line.strip() for line in step["run"].splitlines() if "VERSION=" in line)
    for arguments in (
        ["init", "-q"],
        ["config", "user.name", "Fixture"],
        ["config", "user.email", "fixture@example.invalid"],
        ["commit", "-q", "--allow-empty", "-m", "Tagged fixture"],
        ["tag", "v1"],
    ):
        subprocess.run(
            [git, *arguments], cwd=tmp_path, env=git_env, check=True, capture_output=True
        )

    def version():
        return subprocess.run(
            [bash, "-c", assignment + "\nprintf '%s\\n' \"$VERSION\""],
            cwd=tmp_path,
            env=git_env,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    assert version() == "v1"
    subprocess.run(
        [git, "commit", "-q", "--allow-empty", "-m", "Newer fixture"],
        cwd=tmp_path,
        env=git_env,
        check=True,
        capture_output=True,
    )
    short_sha = subprocess.check_output(
        [git, "rev-parse", "--short", "HEAD"], cwd=tmp_path, env=git_env, text=True
    ).strip()
    assert version() == f"master@{short_sha}"


def test_j05_workflows_share_one_snapshot_and_gate_package_exports():
    import yaml

    workflows = Path(__file__).parents[1] / ".github/workflows"
    validation = yaml.safe_load((workflows / "validate.yml").read_text())["jobs"]
    release = yaml.safe_load((workflows / "release.yml").read_text())["jobs"]

    for jobs, consumers in (
        (validation, ["python-tools", "validate", "walls-windows", "pr-release-package"]),
        (release, ["release"]),
    ):
        assert [
            job
            for job, body in jobs.items()
            for step in body["steps"]
            if "jktz-gps-snapshot" in step.get("run", "")
        ] == ["gps-snapshot"]
        uploads = [
            s["with"]["name"]
            for s in jobs["gps-snapshot"]["steps"]
            if s.get("uses", "").startswith("actions/upload-artifact@")
        ]
        assert uploads == ["gps-snapshot"]
        for consumer in consumers:
            job = jobs[consumer]
            assert "gps-snapshot" in job["needs"]
            download = next(
                s["with"]
                for s in job["steps"]
                if s.get("uses", "").startswith("actions/download-artifact@")
            )
            assert download["name"] == "gps-snapshot"
            checks = [
                s["run"]
                for s in job["steps"]
                if s.get("run", "").startswith(
                    ("uv run jktz-validate", "uv run jktz-render-otwory")
                )
            ]
            assert checks and all("--gps-snapshot" in command for command in checks)

        package = jobs[consumers[-1]]["steps"]
        gate = next(s for s in package if s.get("run", "").startswith("uv run jktz-validate"))
        build = next(s for s in package if s.get("run", "").startswith("uv run jktz-build-zip"))
        assert "--export-version" in gate["run"]
        assert package.index(gate) < package.index(build)
