from __future__ import annotations

import os
import re
import shlex
import zipfile
from pathlib import Path

import pytest

from jktz.cli import build_zip, release_metadata

WORKFLOWS = Path(__file__).parents[1] / ".github" / "workflows"


def _step(workflow: str, name: str) -> str:
    match = re.search(
        rf"^      - name: {re.escape(name)}\n.*?(?=^      - |\Z)",
        workflow,
        re.MULTILINE | re.DOTALL,
    )
    assert match, f"Missing workflow step: {name}"
    return match.group()


def _run_line(step: str) -> str:
    match = re.search(r"^        run: (.+)$", step, re.MULTILINE)
    assert match, "Expected a single CLI command"
    return match.group(1)


def test_release_publishes_matching_version_notes_and_archive_after_validation() -> None:
    workflow = (WORKFLOWS / "release.yml").read_text(encoding="utf-8")
    ordered_steps = [
        "Validate Python tooling",
        "Run mutation gate",
        "Prepare release metadata",
        "Check rendered entrance snapshot",
        "Install Survex",
        "Build exports",
        "Build release ZIP",
        "Create GitHub Release",
    ]
    positions = [workflow.index(_step(workflow, name)) for name in ordered_steps]
    assert positions == sorted(positions)
    assert 'echo "VERSION=${GITHUB_REF_NAME}"' in _step(workflow, "Extract version from tag")
    version = "${{ steps.version.outputs.VERSION }}"
    assert f"RELEASE_VERSION: {version}" in _step(workflow, "Prepare release metadata")
    assert _run_line(_step(workflow, "Check rendered entrance snapshot")) == (
        "uv run jktz-render-otwory --check"
    )
    assert _run_line(_step(workflow, "Build exports")) == f"uv run jktz-exports {version}"
    assert _run_line(_step(workflow, "Build release ZIP")) == f"uv run jktz-build-zip {version}"
    publish = _step(workflow, "Create GitHub Release")
    assert "uses: softprops/action-gh-release@v2" in publish
    assert "body_path: release_notes.md" in publish
    assert f"files: |\n            JKTZ-{version}.zip" in publish


def test_pr_package_keeps_version_render_upload_and_link_contract() -> None:
    workflow = (WORKFLOWS / "validate.yml").read_text(encoding="utf-8")
    job = workflow.split("\n  pr-release-package:\n", 1)[1]
    assert "if: github.event_name == 'pull_request'" in job
    assert "needs: [python-tools, mutation-tests, validate]" in job
    ordered_steps = [
        "Compute package version",
        "Set version in INFO.txt",
        "Render latest entrance fixes",
        "Install Survex",
        "Build exports",
        "Build PR release ZIP",
        "Upload PR release ZIP",
        "Add package link to job summary",
        "Link package in pull request",
    ]
    positions = [job.index(_step(job, name)) for name in ordered_steps]
    assert positions == sorted(positions)
    compute = _step(job, "Compute package version")
    assert 'short_sha="${GITHUB_SHA::7}"' in compute
    assert 'version="pr-${{ github.event.pull_request.number }}-${short_sha}"' in compute
    assert 'echo "version=${version}" >> "$GITHUB_OUTPUT"' in compute
    assert 'echo "zip=JKTZ-${version}.zip" >> "$GITHUB_OUTPUT"' in compute
    version = "${{ steps.package.outputs.version }}"
    assert f"PACKAGE_VERSION: {version}" in _step(job, "Set version in INFO.txt")
    assert _run_line(_step(job, "Render latest entrance fixes")) == "uv run jktz-render-otwory"
    assert _run_line(_step(job, "Build exports")) == f"uv run jktz-exports {version}"
    assert _run_line(_step(job, "Build PR release ZIP")) == f"uv run jktz-build-zip {version}"
    upload = _step(job, "Upload PR release ZIP")
    assert "uses: actions/upload-artifact@v4" in upload
    assert "name: ${{ steps.package.outputs.zip }}" in upload
    assert "path: ${{ steps.package.outputs.zip }}" in upload
    assert "if-no-files-found: error" in upload
    assert "retention-days: 14" in upload
    for name in ("Add package link to job summary", "Link package in pull request"):
        link = _step(job, name)
        assert "${{ steps.upload.outputs.artifact-url }}" in link
        assert "${{ steps.package.outputs.version }}" in link
        assert "${{ steps.package.outputs.zip }}" in link
    comment = _step(job, "Link package in pull request")
    assert "if: github.event.pull_request.head.repo.full_name == github.repository" in comment
    assert "continue-on-error: true" in comment
    assert "action-gh-release" not in job


@pytest.mark.parametrize(
    ("filename", "metadata_step", "version", "version_env", "build_step", "build_expr"),
    [
        (
            "release.yml",
            "Prepare release metadata",
            "v1.2.3",
            "RELEASE_VERSION",
            "Build release ZIP",
            "${{ steps.version.outputs.VERSION }}",
        ),
        (
            "validate.yml",
            "Set version in INFO.txt",
            "pr-127-a1b2c3d",
            "PACKAGE_VERSION",
            "Build PR release ZIP",
            "${{ steps.package.outputs.version }}",
        ),
    ],
)
def test_workflow_metadata_commands_produce_complete_versioned_package(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    filename: str,
    metadata_step: str,
    version: str,
    version_env: str,
    build_step: str,
    build_expr: str,
) -> None:
    workflow = (WORKFLOWS / filename).read_text(encoding="utf-8")
    info = b"JKTZ __VERSION__\r\nLegacy author: \xb3\xf3\r\n"
    changelog = (
        b"## [Unreleased]\n\n## [v1.2.3]\n\n    example\n\n"
        b"## Release details\n- Complete body.\n\n## [v1.2.2]\nOld.\n"
    )
    included = {
        "INFO.txt": info,
        "CHANGELOG.md": changelog,
        "KATASTER.wpj": b".BOOK Cave\r\n",
        "README.md": b"Instructions\n",
        "LICENCE": b"CC BY-SA 4.0\n",
        "Poligony/OTWORY.SRV": b"#fix Cave:0 E19.9 N49.2 1500m\n",
        "Poligony/Cave/CAVE.SRV": b"0 1 2 90 0\r\n; legacy \xb3\r\n",
        "Powierzchnia/terrain.svx": b"*begin terrain\n*end terrain\n",
        f"exports/JKTZ-{version}.3d": b"3D fixture\x00\xff",
        f"exports/JKTZ-{version}.dxf": b"DXF fixture\r\n",
        f"exports/JKTZ-{version}-all.shp": b"all caves fixture\x00",
        "exports/caves/Cave.shp": b"cave fixture\x00",
        "exports/caves/Cave.dbf": b"attributes fixture\x00",
        "exports/caves/Cave.shx": b"index fixture\x00",
        "exports/caves/Cave.prj": b"EPSG:32634 fixture",
    }
    excluded = {
        ".github/workflows/release.yml",
        ".agents/skills/example/SKILL.md",
        "src/jktz/tool.py",
        "tests/test_tool.py",
        "Poligony/OTWORY.SRV.j2",
        "Poligony/Cave/_RAW/01/source.svx",
        "logs/quality/coverage.json",
        "mutants/src/jktz/tool.py",
        "htmlcov/index.html",
        ".coverage",
        "JKTZ-old.zip",
    }
    originals = {**included, **dict.fromkeys(excluded, b"excluded fixture\x00\xff")}
    for relative, content in originals.items():
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv(version_env, version)

    metadata_command = os.path.expandvars(_run_line(_step(workflow, metadata_step)))
    metadata_args = shlex.split(metadata_command)
    assert metadata_args[:3] == ["uv", "run", "jktz-release-metadata"]
    assert release_metadata.main(metadata_args[3:]) == 0
    notes = tmp_path / "release_notes.md"
    if filename == "release.yml":
        assert notes.read_bytes() == b"    example\n\n## Release details\n- Complete body.\n"
    else:
        assert not notes.exists()

    build_command = _run_line(_step(workflow, build_step)).replace(build_expr, version)
    build_args = shlex.split(build_command)
    assert build_args[:3] == ["uv", "run", "jktz-build-zip"]
    monkeypatch.setattr("sys.argv", build_args[2:])
    assert build_zip.main() == 0

    included["INFO.txt"] = info.replace(b"__VERSION__", version.encode("ascii"))
    with zipfile.ZipFile(tmp_path / f"JKTZ-{version}.zip") as archive:
        assert len(archive.namelist()) == len(included)
        assert set(archive.namelist()) == set(included)
        assert {name: archive.read(name) for name in archive.namelist()} == included
    for relative, original in originals.items():
        expected = included["INFO.txt"] if relative == "INFO.txt" else original
        assert (tmp_path / relative).read_bytes() == expected, relative
