from __future__ import annotations

import fnmatch
import zipfile
from pathlib import Path

# Single source of truth for what stays out of the release ZIP. Patterns use
# POSIX-style separators and are matched against each file's path relative to
# the project root via fnmatch (where `*` matches `/` — same as zip's -x).
#
# This is the canonical release-content contract. `src/*` and the other
# tooling paths are intentionally excluded from the user-facing data archive.
EXCLUDE_PATTERNS: tuple[str, ...] = (
    ".git/*",
    ".github/*",
    ".claude/*",
    ".venv/*",
    ".pytest_cache/*",
    ".ruff_cache/*",
    ".playwright-mcp/*",
    ".idea/*",
    ".vscode/*",
    "docker/*",
    ".gitignore",
    ".gitattributes",
    ".pre-commit-config.yaml",
    "CLAUDE.md",
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
    "*.nta",
    "*.ntn",
    "*.ntv",
    "*.nts",
    "*.ntp",
    "*.NTA",
    "*.NTN",
    "*.NTV",
    "*.NTS",
    "*.NTP",
    "*.wrl",
    "*.log",
    "*.lst",
    "web/*",
    "survex-src/*",
    "validate-exports/*",
    "cavern_output.txt",
    "release_notes.md",
    "JKTZ-*.zip",
)


def is_excluded(rel_path: str, patterns: tuple[str, ...] = EXCLUDE_PATTERNS) -> bool:
    """Return True if rel_path matches any exclude pattern."""
    rel_path = rel_path.replace("\\", "/")
    return any(fnmatch.fnmatch(rel_path, p) for p in patterns)


def build_release_zip(
    version: str,
    zip_path: Path | None = None,
    root: Path = Path("."),
) -> Path:
    """Build the user-facing JKTZ release ZIP from the workspace at ``root``.

    Returns the absolute path of the produced ZIP. Overwrites any existing file
    at the target path.
    """
    root = Path(root).resolve()
    if zip_path is None:
        zip_path = root / f"JKTZ-{version}.zip"
    else:
        zip_path = Path(zip_path)
    if zip_path.exists():
        zip_path.unlink()

    included = 0
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file in sorted(root.rglob("*")):
            if not file.is_file():
                continue
            rel = file.relative_to(root).as_posix()
            if is_excluded(rel):
                continue
            zf.write(file, arcname=rel)
            included += 1

    print(f"=== Built {zip_path.as_posix()} with {included} files ===")
    return zip_path
