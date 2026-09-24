from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def bootstrap():
    path = Path(__file__).parents[1] / "scripts" / "initial-setup.py"
    spec = importlib.util.spec_from_file_location("initial_setup", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_bootstrap_missing_uv_does_not_install(bootstrap, monkeypatch, capsys):
    monkeypatch.setattr(bootstrap.shutil, "which", lambda command: None)
    commands = []
    monkeypatch.setattr(bootstrap.subprocess, "run", lambda *a, **kw: commands.append(a))

    assert bootstrap.main() == 1

    assert commands == []
    assert "uv is required" in capsys.readouterr().out


@pytest.mark.parametrize("missing", [set(), {"docker"}, {"cavern", "ogr2ogr"}])
def test_bootstrap_installs_locked_dependencies_and_both_hooks(
    bootstrap, monkeypatch, capsys, missing
):
    monkeypatch.setattr(
        bootstrap.shutil, "which", lambda command: None if command in missing else f"/bin/{command}"
    )
    commands = []
    monkeypatch.setattr(
        bootstrap.subprocess, "run", lambda args, **kwargs: commands.append((args, kwargs))
    )

    assert bootstrap.main() == 0

    assert commands == [
        (["uv", "sync", "--locked"], {"cwd": bootstrap.REPO_ROOT, "check": True}),
        (
            [
                "uv",
                "run",
                "pre-commit",
                "install",
                "--hook-type",
                "pre-commit",
                "--hook-type",
                "pre-push",
            ],
            {"cwd": bootstrap.REPO_ROOT, "check": True},
        ),
    ]
    output = capsys.readouterr().out
    assert ("NOTE: missing system tool(s):" in output) == bool(missing)
    assert ("pre-push hook will fail" in output) == bool(missing & {"cavern", "ogr2ogr"})


def test_failed_dependency_install_stops_before_hooks(bootstrap, monkeypatch):
    monkeypatch.setattr(bootstrap.shutil, "which", lambda command: f"/bin/{command}")
    commands = []

    def fail(args, **kwargs):
        commands.append(args)
        raise subprocess.CalledProcessError(7, args)

    monkeypatch.setattr(bootstrap.subprocess, "run", fail)

    with pytest.raises(subprocess.CalledProcessError) as failure:
        bootstrap.main()

    assert failure.value.returncode == 7
    assert commands == [["uv", "sync", "--locked"]]


def test_color_is_optional(bootstrap, monkeypatch):
    monkeypatch.setattr(bootstrap, "_USE_COLOR", True)
    assert bootstrap._yellow("warning") == "\033[33mwarning\033[0m"
    monkeypatch.setattr(bootstrap, "_USE_COLOR", False)
    assert bootstrap._yellow("warning") == "warning"
