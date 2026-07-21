from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).parents[1]


def test_scripts_directory_contains_only_pre_install_bootstrap() -> None:
    scripts = {path.name for path in (REPO_ROOT / "scripts").glob("*.py")}

    assert scripts == {"initial-setup.py"}


def test_contributor_docs_explain_bootstrap_and_installed_tools_boundary() -> None:
    contributing = (REPO_ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")

    assert "python scripts/initial-setup.py" in contributing
    assert "src/jktz/" in contributing
    assert "uv run jktz-*" in contributing
