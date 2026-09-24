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


def test_contributor_docs_explain_bootstrap_and_installed_tools_boundary() -> None:
    contributing = (REPO_ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")

    assert "python scripts/initial-setup.py" in contributing
    assert "src/jktz/" in contributing
    assert "uv run jktz-*" in contributing
