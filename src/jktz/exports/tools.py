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


def _run_capturing(cmd: list[str], cwd: Path | None = None) -> None:
    """Run cmd to completion, inheriting stdout/stderr. Raise on non-zero exit."""
    cmd = [_resolve(cmd[0]), *cmd[1:]]
    try:
        subprocess.run(cmd, check=True, cwd=str(cwd) if cwd else None)
    except subprocess.CalledProcessError as exc:
        raise ExternalToolError(
            f"{Path(cmd[0]).name} failed with exit code {exc.returncode}"
        ) from exc


def _run_tee(cmd: list[str], log_path: Path, cwd: Path | None = None) -> None:
    """Run cmd, stream combined stdout+stderr to our stdout AND a log file.

    Matches the bash idiom ``cmd 2>&1 | tee log.txt`` — used for cavern so the
    cavern log is both visible live and saved for the unattached-station check.
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
    with log_path.open("wb") as logf:
        for chunk in iter(lambda: proc.stdout.read(4096), b""):
            sys.stdout.buffer.write(chunk)
            sys.stdout.flush()
            logf.write(chunk)
    ret = proc.wait()
    if ret != 0:
        raise ExternalToolError(f"{Path(cmd[0]).name} failed with exit code {ret}")


def cavern(
    args: list[str],
    cwd: Path | None = None,
    log_to: Path | None = None,
) -> None:
    """Run Survex's ``cavern`` to compile a .wpj or .svx project file."""
    cmd = ["cavern", *args]
    if log_to is not None:
        _run_tee(cmd, log_to, cwd=cwd)
    else:
        _run_capturing(cmd, cwd=cwd)


def survexport(args: list[str], cwd: Path | None = None) -> None:
    """Run Survex's ``survexport`` to export .3d into DXF/CSV/etc."""
    _run_capturing(["survexport", *args], cwd=cwd)


def ogr2ogr(args: list[str], cwd: Path | None = None) -> None:
    """Run GDAL's ``ogr2ogr`` to convert between vector formats."""
    _run_capturing(["ogr2ogr", *args], cwd=cwd)
