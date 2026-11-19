from __future__ import annotations

import io
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest

from jktz.exports import tools


def test_missing_binary_fails_before_starting_process(monkeypatch):
    monkeypatch.setattr(tools.shutil, "which", lambda name: None)
    start = Mock()
    monkeypatch.setattr(tools.subprocess, "Popen", start)

    with pytest.raises(tools.ExternalToolError, match="'cavern' not found on PATH"):
        tools.cavern(["KATASTER.wpj"])

    start.assert_not_called()


@pytest.mark.parametrize("returncode", [0, 7])
def test_cavern_streams_combined_output_and_keeps_raw_log(
    tmp_path, monkeypatch, capsys, returncode
):
    executable = str(tmp_path / "Survex tools" / "cavern.exe")
    monkeypatch.setattr(tools.shutil, "which", lambda name: executable)
    data = b"x" * 4095 + "ł\nlegacy ".encode() + b"\xff\n"
    process = MagicMock(stdout=io.BytesIO(data), returncode=returncode)
    process.__enter__.return_value = process
    start = Mock(return_value=process)
    monkeypatch.setattr(tools.subprocess, "Popen", start)
    logfile = tmp_path / "cavern.log"

    if returncode:
        with pytest.raises(tools.ExternalToolError, match="cavern.exe failed with exit code 7"):
            tools.cavern(["KATASTER.wpj"], cwd=tmp_path, log_to=logfile)
    else:
        tools.cavern(["KATASTER.wpj"], cwd=tmp_path, log_to=logfile)

    start.assert_called_once_with(
        [executable, "KATASTER.wpj"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=str(tmp_path),
        bufsize=0,
    )
    process.__exit__.assert_called_once()
    assert capsys.readouterr().out == data.decode("utf-8", errors="replace")
    assert logfile.read_bytes() == data


def test_unwritable_log_does_not_start_compilation(tmp_path, monkeypatch):
    monkeypatch.setattr(tools.shutil, "which", lambda name: name)
    start = Mock()
    monkeypatch.setattr(tools.subprocess, "Popen", start)
    with pytest.raises(OSError):
        tools.cavern(["KATASTER.wpj"], log_to=tmp_path / "absent" / "output.log")
    start.assert_not_called()


@pytest.mark.parametrize("name", ["survexport", "ogr2ogr"])
def test_export_wrappers_resolve_the_binary_and_forward_arguments(monkeypatch, capsys, name):
    executable = str(Path("/tools") / name)
    which = Mock(return_value=executable)
    monkeypatch.setattr(tools.shutil, "which", which)
    process = MagicMock(stdout=io.BytesIO(b"done\n"), returncode=0)
    process.__enter__.return_value = process
    start = Mock(return_value=process)
    monkeypatch.setattr(tools.subprocess, "Popen", start)

    getattr(tools, name)(["--help"])

    which.assert_called_once_with(name)
    assert start.call_args.args[0] == [executable, "--help"]
    assert start.call_args.kwargs["cwd"] is None
    assert capsys.readouterr().out == "done\n"
