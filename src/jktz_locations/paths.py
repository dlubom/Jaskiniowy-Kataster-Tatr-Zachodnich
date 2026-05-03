"""Path helpers for the repository-local tooling."""

from __future__ import annotations

from pathlib import Path
from typing import Optional


def locations_root(path: Optional[Path] = None) -> Path:
    """Resolve the Lokalizacje root from either repo root or the directory itself."""
    candidate = Path.cwd() if path is None else path
    if candidate.name != "Lokalizacje" and (candidate / "Lokalizacje").is_dir():
        candidate = candidate / "Lokalizacje"
    return candidate.resolve()


def default_export_dir(root: Path) -> Path:
    """Default output directory kept under git-ignored exports/."""
    repo_root = root.parent if root.name == "Lokalizacje" else root
    return repo_root / "exports" / "lokalizacje"
