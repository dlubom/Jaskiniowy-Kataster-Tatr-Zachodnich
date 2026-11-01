"""Execute Linux installer shell steps against controlled runner dependencies."""

from __future__ import annotations

import os
import re
import shlex
import subprocess
from pathlib import Path

import pytest
import yaml

ACTION = Path(__file__).parents[1] / ".github/actions/install-survex/action.yml"
VERSION = "1.4.24"
pytestmark = pytest.mark.skipif(os.name == "nt", reason="Linux installer needs a POSIX shell")


def _executable(path: Path, body: str) -> None:
    path.write_text("#!/bin/sh\n" + body, encoding="utf-8")
    path.chmod(0o755)


def _expand(text: str, context: dict) -> str:
    def replace(match: re.Match) -> str:
        value = context
        for part in match.group(1).split("."):
            value = value[part]
        return str(value)

    return re.sub(r"\$\{\{\s*([\w.-]+)\s*\}\}", replace, text)


def _bash(script: str, environment: dict, directory: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", "--noprofile", "--norc", "-e", "-o", "pipefail", "-c", script],
        cwd=directory,
        env=environment,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )


def test_cached_install_uses_available_ubuntu_dependencies_without_rebuilding(tmp_path):
    commands = tmp_path / "commands"
    commands.mkdir()
    installed = tmp_path / "installed"
    github_path = tmp_path / "github-path"
    _executable(commands / "sudo", 'test "$1" = apt-get || exit 99\nexec "$@"\n')
    _executable(
        commands / "apt-get",
        """if [ "$1" = update ]; then exit 0; fi
[ "$1" = install ] && [ "$2" = -y ] || exit 98
shift 2
for package in "$@"; do
  case "$package" in
    libproj-dev|libgdal-dev|gdal-bin|libwxgtk3.2-dev|libproj25|libwxgtk3.2-1t64|build-essential) ;;
    *) echo "E: Unable to locate package $package" >&2; exit 100 ;;
  esac
done
printf '%s\\n' "$@" >> "$JKTZ_TEST_INSTALLED"
""",
    )
    for command in ("wget", "tar", "make"):
        _executable(commands / command, "echo 'Cached install tried to rebuild' >&2\nexit 97\n")
    environment = {
        **os.environ,
        "PATH": str(commands) + os.pathsep + os.environ["PATH"],
        "GITHUB_PATH": str(github_path),
        "RUNNER_TEMP": str(tmp_path),
        "JKTZ_TEST_INSTALLED": str(installed),
    }
    steps = yaml.safe_load(ACTION.read_text(encoding="utf-8"))["runs"]["steps"]
    step = next(item for item in steps if item.get("name") == "Install Survex")
    script = _expand(
        step["run"],
        {"inputs": {"version": VERSION}, "steps": {"cache": {"outputs": {"cache-hit": "true"}}}},
    )
    completed = _bash(script, environment, tmp_path)

    assert completed.returncode == 0, completed.stdout + completed.stderr
    packages = set(installed.read_text(encoding="utf-8").splitlines())
    assert {"libproj-dev", "libgdal-dev", "gdal-bin", "libwxgtk3.2-dev"} <= packages
    assert "build-essential" not in packages
    assert github_path.read_text(encoding="utf-8").splitlines() == [
        str(Path(os.environ["HOME"]) / "survex/bin")
    ]


def _cache_key(directory: Path, release: str, architecture: str) -> str:
    directory.mkdir()
    release_file = directory / "os-release"
    release_file.write_text(f'ID=ubuntu\nVERSION_ID="{release}"\n', encoding="utf-8")
    commands = directory / "commands"
    commands.mkdir()
    _executable(
        commands / "uname",
        'test "$1" = -m || exit 99\nprintf "%s\\n" "$JKTZ_TEST_ARCH"\n',
    )
    environment = {
        **os.environ,
        "PATH": str(commands) + os.pathsep + os.environ["PATH"],
        "JKTZ_TEST_ARCH": architecture,
    }
    context = {"inputs": {"version": VERSION}, "steps": {}}
    steps = yaml.safe_load(ACTION.read_text(encoding="utf-8"))["runs"]["steps"]
    for number, step in enumerate(steps):
        if step.get("uses", "").startswith("actions/cache@"):
            return _expand(step["with"]["key"], context)
        if "run" not in step:
            continue
        output = directory / f"output-{number}"
        script = _expand(step["run"], context).replace(
            "/etc/os-release", shlex.quote(str(release_file))
        )
        completed = _bash(script, {**environment, "GITHUB_OUTPUT": str(output)}, directory)
        assert completed.returncode == 0, completed.stdout + completed.stderr
        if "id" in step:
            values = dict(line.split("=", 1) for line in output.read_text().splitlines())
            context["steps"][step["id"]] = {"outputs": values}
    raise AssertionError("Installer did not request its build cache")


def test_cache_does_not_reuse_binaries_across_linux_release_or_architecture(tmp_path):
    keys = {
        (release, architecture): _cache_key(
            tmp_path / f"{release}-{architecture}", release, architecture
        )
        for release in ("24.04", "26.04")
        for architecture in ("x86_64", "aarch64")
    }

    assert len(set(keys.values())) == 4, keys
