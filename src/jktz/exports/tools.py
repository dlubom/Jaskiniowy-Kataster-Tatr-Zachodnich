from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


class ExternalToolError(RuntimeError):
    """An external Survex/GDAL binary either failed or is missing from PATH."""


def _missing_tool_msg(tool: str) -> str:
    return (
        f"External tool '{tool}' not found on PATH. "
        f"Install Survex/GDAL natively or run via /docker-validate or /docker-exports."
    )


def _resolve(tool: str) -> str:
    """Resolve ``tool`` to an absolute path via PATH lookup, or raise.

    Survex's Windows binaries (``survexport.exe``, ``aven.exe``) are launcher
    wrappers that locate their real ``_.exe`` sibling via ``dirname(argv[0])``.
    Invoking them by bare name means ``argv[0]`` is just the name and the
    wrapper can't find its sibling. Passing the absolute path here makes
    ``argv[0]`` absolute on every platform and resolution is always correct.
    """
    resolved = shutil.which(tool)
    if resolved is None:
        raise ExternalToolError(_missing_tool_msg(tool))
    return resolved


def _stream_subprocess(
    cmd: list[str],
    cwd: Path | None = None,
    log_to: Path | None = None,
) -> None:
    """Run ``cmd``, streaming its combined stdout/stderr through ``sys.stdout``.

    Routing the output through Python's text stream (rather than subprocess
    inheriting our fd 1 or writing direct bytes to ``sys.stdout.buffer``) is
    what lets ``_indent_stdout`` in the orchestrator catch every line and
    prefix it. Optionally also tees the raw bytes to ``log_to`` (used for the
    cavern log that the unattached-station check later greps).
    """
    cmd = [_resolve(cmd[0]), *cmd[1:]]
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=str(cwd) if cwd else None,
        bufsize=0,
    )
    assert proc.stdout is not None

    logf = log_to.open("wb") if log_to is not None else None
    try:
        for chunk in iter(lambda: proc.stdout.read(4096), b""):
            if logf is not None:
                logf.write(chunk)
            sys.stdout.write(chunk.decode("utf-8", errors="replace"))
            sys.stdout.flush()
    finally:
        if logf is not None:
            logf.close()

    ret = proc.wait()
    if ret != 0:
        raise ExternalToolError(f"{Path(cmd[0]).name} failed with exit code {ret}")


def cavern(
    args: list[str],
    cwd: Path | None = None,
    log_to: Path | None = None,
) -> None:
    """Run Survex's ``cavern`` to compile a .wpj or .svx project file."""
    _stream_subprocess(["cavern", *args], cwd=cwd, log_to=log_to)


def survexport(args: list[str], cwd: Path | None = None) -> None:
    """Run Survex's ``survexport`` to export .3d into DXF/CSV/etc."""
    _stream_subprocess(["survexport", *args], cwd=cwd)


def ogr2ogr(args: list[str], cwd: Path | None = None) -> None:
    """Run GDAL's ``ogr2ogr`` to convert between vector formats."""
    _stream_subprocess(["ogr2ogr", *args], cwd=cwd)
