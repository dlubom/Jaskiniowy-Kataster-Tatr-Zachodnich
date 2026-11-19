from __future__ import annotations

import fnmatch
import os
import stat
import tempfile
import zipfile
from collections.abc import Iterator
from pathlib import Path

# Single source of truth for what stays out of the release ZIP. Patterns use
# POSIX-style separators and are matched against each file's path relative to
# the project root via fnmatch (where `*` matches `/` — same as zip's -x).
#
# This is the canonical release-content contract. `src/*` and the other
# tooling paths are intentionally excluded from the user-facing data archive.
EXCLUDE_PATTERNS: tuple[str, ...] = (
    ".git",
    ".git/*",
    ".github/*",
    ".claude/*",
    ".agents/*",
    ".codex/*",
    ".verification/*",
    ".venv/*",
    ".pytest_cache/*",
    ".coverage*",
    "htmlcov/*",
    "mutants/*",
    ".ruff_cache/*",
    ".playwright-mcp/*",
    ".idea/*",
    ".vscode/*",
    "docker/*",
    ".gitignore",
    ".gitattributes",
    ".pre-commit-config.yaml",
    "AGENTS.md",
    "CONTRIBUTING.md",
    "pyproject.toml",
    "uv.lock",
    "doc/*",
    "docs/*",
    "scripts/*",
    "src/*",
    "tests/*",
    "Poligony/OTWORY.SRV.j2",
    "logs/*",
    "*/_RAW/*",
    "*.DS_Store",
    "KATASTER/*",
    "*.[Nn][Tt][AaNnPpSsVvWw]",
    "*.[Nn][Tt][Aa][CcDdEeSs]",
    "*.[Ww][Rr][Ll]",
    "*.[Ll][Oo][Gg]",
    "*.[Ll][Ss][Tt]",
    "web/*",
    "survex-src/*",
    "validate-exports/*",
    "cavern_output.txt",
    "release_notes.md",
    "JKTZ-*.zip",
    "*/JKTZ-*.zip",
)


def is_excluded(rel_path: str, patterns: tuple[str, ...] = EXCLUDE_PATTERNS) -> bool:
    """Return True if rel_path matches any exclude pattern."""
    rel_path = rel_path.replace("\\", "/")
    return any(fnmatch.fnmatch(rel_path, p) for p in patterns)


def _raise_walk_error(error: OSError) -> None:
    raise error


def _release_files(root: Path) -> Iterator[Path]:
    for directory, dirs, names in os.walk(root, onerror=_raise_walk_error):
        parent = Path(directory).relative_to(root)
        dirs[:] = [name for name in dirs if not is_excluded((parent / name).as_posix() + "/")]
        for name in names:
            relative = parent / name
            if not is_excluded(relative.as_posix()):
                yield relative


def build_release_zip(
    version: str,
    zip_path: Path | None = None,
    root: Path = Path("."),
) -> Path:
    """Build the user-facing JKTZ release ZIP from the workspace at ``root``.

    Returns the absolute path of the produced ZIP. Replaces the target only
    after every input has been archived and the ZIP has been closed.
    """
    root = Path(root).resolve()
    if zip_path is None:
        zip_path = root / f"JKTZ-{version}.zip"
    else:
        zip_path = Path(zip_path).resolve()

    files = sorted(_release_files(root))
    with tempfile.TemporaryDirectory(dir=zip_path.parent) as directory:
        staged = Path(directory) / "JKTZ-pending.zip"
        with zipfile.ZipFile(staged, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for relative in files:
                file = root / relative
                if file.resolve() != zip_path and stat.S_ISREG(file.stat().st_mode):
                    archive.write(file, arcname=relative.as_posix())
        staged.replace(zip_path)

    print(f"=== Built {zip_path.as_posix()} with {len(archive.infolist())} files ===")
    return zip_path
