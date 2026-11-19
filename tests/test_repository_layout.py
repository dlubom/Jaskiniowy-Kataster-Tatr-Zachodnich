from __future__ import annotations

import subprocess
from pathlib import Path

from jktz.quality import SOURCE_DIRS

REPO_ROOT = Path(__file__).parents[1]


def test_live_python_inventory_stays_inside_quality_scope() -> None:
    inventory = subprocess.check_output(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", "*.py"],
        cwd=REPO_ROOT,
        text=True,
    )
    roots = [Path(directory).parts for directory in (*SOURCE_DIRS, "tests")]
    omitted = []
    for filename in filter(None, inventory.split("\0")):
        path = Path(filename)
        # Archived source packages are preserved originals, not executable tooling.
        if "_RAW" in path.parts or not (REPO_ROOT / path).is_file():
            continue
        if not any(path.parts[: len(parts)] == parts for parts in roots):
            omitted.append(path.as_posix())

    assert not omitted, f"Python files outside the quality scope: {sorted(omitted)}"


def test_scripts_directory_contains_only_pre_install_bootstrap() -> None:
    scripts = {path.name for path in (REPO_ROOT / "scripts").glob("*.py")}

    assert scripts == {"initial-setup.py"}


def test_git_ignores_compiler_outputs_but_keeps_archival_originals(tmp_path: Path) -> None:
    user_excludes = tmp_path / "user-excludes"
    user_excludes.write_text("Thumbs.db\n")
    compiled = [
        "KATASTER/model.NTA",
        "Poligony/model.nTv",
        "survey.LOG",
        "survey.3D",
        "survey.NTW",
        "survey.ntAC",
        "survey.NTAD",
        "survey.ntae",
        "survey.NtAs",
    ]
    raw = "Poligony/example/_RAW/01"
    originals = [f"{raw}/original/{Path(path).name}" for path in compiled]
    ignored = subprocess.check_output(
        [
            "git",
            "-c",
            "core.ignorecase=false",
            "-c",
            f"core.excludesFile={user_excludes}",
            "check-ignore",
            "--no-index",
            "--",
            *compiled,
            *originals,
            "Poligony/example.SRV",
            "KATASTER/model.log",
            f"{raw}/Thumbs.db",
        ],
        cwd=REPO_ROOT,
        text=True,
    ).splitlines()

    assert ignored == [*compiled, "KATASTER/model.log", f"{raw}/Thumbs.db"]


def test_contributor_docs_explain_bootstrap_and_installed_tools_boundary() -> None:
    contributing = (REPO_ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")

    assert "python scripts/initial-setup.py" in contributing
    assert "src/jktz/" in contributing
    assert "uv run jktz-*" in contributing
