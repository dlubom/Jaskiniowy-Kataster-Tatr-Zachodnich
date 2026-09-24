from __future__ import annotations

import io
import subprocess
from pathlib import Path
from unittest.mock import Mock

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
    process = Mock(stdout=io.BytesIO(b"station\nlegacy \xff\n"))
    process.wait.return_value = returncode
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
    process.wait.assert_called_once_with()
    assert capsys.readouterr().out == "station\nlegacy \ufffd\n"
    assert logfile.read_bytes() == b"station\nlegacy \xff\n"


@pytest.mark.parametrize("name", ["survexport", "ogr2ogr"])
def test_export_wrappers_resolve_the_binary_and_forward_arguments(monkeypatch, capsys, name):
    executable = str(Path("/tools") / name)
    which = Mock(return_value=executable)
    monkeypatch.setattr(tools.shutil, "which", which)
    process = Mock(stdout=io.BytesIO(b"done\n"))
    process.wait.return_value = 0
    start = Mock(return_value=process)
    monkeypatch.setattr(tools.subprocess, "Popen", start)

    getattr(tools, name)(["--help"])

    which.assert_called_once_with(name)
    assert start.call_args.args[0] == [executable, "--help"]
    assert start.call_args.kwargs["cwd"] is None
    assert capsys.readouterr().out == "done\n"
