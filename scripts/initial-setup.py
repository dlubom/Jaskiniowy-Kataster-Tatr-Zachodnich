"""One-shot developer setup for Jaskiniowy Kataster Tatr Zachodnich.

Run after cloning the repository:

    python scripts/initial-setup.py

Uses only the Python standard library; all project work is delegated to `uv`
subprocesses, so this script does not need to live inside the project venv.

What it does:
  1. Verifies `uv` is on PATH (hard fail with install link otherwise).
  2. Installs Python tooling via `uv sync --locked` (ruff, pytest,
     pre-commit, and the jktz-* CLI commands).
  3. Installs pre-commit and pre-push git hooks (see
     .pre-commit-config.yaml).
  4. Warns about missing optional system tools (cavern, ogr2ogr, docker)
     but does not fail the setup. These are needed for the pre-push hook
     (`uv run jktz-validate`) and the /docker-* skills.

Idempotent: safe to re-run any time.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Enable ANSI escape sequence processing on Windows (10+) consoles. The empty
# os.system call flips the VT-processing flag on stdout without printing
# anything. POSIX terminals already understand the codes natively.
if os.name == "nt":
    os.system("")

# Honour https://no-color.org/ and disable colors when stdout isn't a TTY
# (e.g. piped output, CI logs).
_USE_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _USE_COLOR else text


def _red(text: str) -> str:
    return _c("31", text)


def _green(text: str) -> str:
    return _c("32", text)


def _yellow(text: str) -> str:
    return _c("33", text)


SYSTEM_TOOLS = [
    (
        "cavern",
        "Survex (needed for `uv run jktz-validate`, the pre-push hook). "
        "Install: https://survex.com/download.html",
    ),
    (
        "ogr2ogr",
        "GDAL (needed for the exports step of `jktz-validate`). "
        "Windows: conda-forge or OSGeo4W. macOS: `brew install gdal`. "
        "Linux: `apt install gdal-bin`.",
    ),
    (
        "docker",
        "Docker (optional, enables /docker-validate and /docker-exports "
        "as a fallback if cavern/GDAL aren't installed locally).",
    ),
]


def _has(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def _run(args: list[str]) -> None:
    print(f"$ {' '.join(args)}")
    subprocess.run(args, cwd=REPO_ROOT, check=True)


def main() -> int:
    print("=== JKTZ developer setup ===\n")

    print("[1/4] Checking required tool: uv")
    if not _has("uv"):
        print(f"  {_red('[MISSING]')} uv is required.")
        print("           Install from https://docs.astral.sh/uv/getting-started/installation/")
        print("           Then re-run: python scripts/initial-setup.py")
        return 1
    print(f"  {_green('[OK]')} uv found\n")

    print("[2/4] Installing Python tooling (uv sync --locked)")
    _run(["uv", "sync", "--locked"])
    print()

    print("[3/4] Installing pre-commit / pre-push git hooks")
    _run(
        [
            "uv",
            "run",
            "pre-commit",
            "install",
            "--hook-type",
            "pre-commit",
            "--hook-type",
            "pre-push",
        ]
    )
    print()

    print("[4/4] Checking optional system tools")
    missing: list[str] = []
    for cmd, hint in SYSTEM_TOOLS:
        if _has(cmd):
            print(f"  {_green('[OK]     ')} {cmd}")
        else:
            print(f"  {_red('[MISSING]')} {cmd} -- {hint}")
            missing.append(cmd)

    print("\n=== Setup complete ===\n")
    print("From now on:")
    print("  * `git commit` runs ruff format + ruff check --fix + pytest")
    print(
        "    If ruff modifies a file, the commit fails. Re-stage with "
        "`git add -u` and commit again."
    )
    print(
        "  * `git push` runs `uv run jktz-validate` (full cavern compile + "
        "exports check, can take a few minutes)."
    )

    if missing:
        print()
        print(_yellow("NOTE: missing system tool(s): " + ", ".join(missing) + "."))
        if "cavern" in missing or "ogr2ogr" in missing:
            print(
                _yellow(
                    "      The pre-push hook will fail until these are installed. "
                    "Use `git push --no-verify` to bypass intentionally."
                )
            )

    return 0


if __name__ == "__main__":
    sys.exit(main())
