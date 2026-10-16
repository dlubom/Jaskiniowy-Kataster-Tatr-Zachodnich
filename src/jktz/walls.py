"""Isolated native Walls compilation; Survex validation remains a separate gate."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path, PureWindowsPath

EXTENSIONS = ("NTA", "NTN", "NTP", "NTS", "NTV")
BUILD = "v2.3.0-beta.1 2025-09-13"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_files(root: Path) -> list[Path]:
    result = []
    for directory, dirs, files in os.walk(root):
        dirs[:] = [
            d for d in dirs if not d.startswith(".") and d not in ("_RAW", "node_modules", "logs")
        ]
        for name in files:
            path = Path(directory) / name
            if path.suffix.lower() in (".srv", ".wpj") or name == "INFO.txt":
                if path.is_symlink() or not path.resolve().is_relative_to(root):
                    raise ValueError(f"Unsafe source path: {path}")
                result.append(path)
    return sorted(result)


def project_name(project: Path) -> str:
    """Reject paths escaping the isolated tree, including Windows paths on POSIX."""
    name = ""
    for line in project.read_text(encoding="cp1250").splitlines():
        fields = line.split(maxsplit=1)
        if len(fields) == 2 and fields[0].upper() in (".NAME", ".PATH"):
            value = fields[1]
            path = PureWindowsPath(value)
            if path.drive or path.root or ".." in path.parts or '"' in value:
                raise ValueError(f"Unsafe project path: {value}")
            if not name and fields[0].upper() == ".NAME":
                name = value
    if not name or len(PureWindowsPath(name).parts) != 1:
        raise ValueError("Missing or unsupported root .NAME")
    return name


def referenced_files(project: Path) -> list[str]:
    """Resolve WPJ survey paths, including detached branches, before copying."""
    books = []
    surveys = []
    current = {}
    for line in project.read_text(encoding="cp1250").splitlines():
        fields = line.split(maxsplit=1)
        directive = fields[0].upper() if fields else ""
        if directive in (".BOOK", ".SURVEY"):
            current = {"parents": list(books), ".PATH": "", ".NAME": ""}
            if directive == ".BOOK":
                books.append(current)
            else:
                surveys.append(current)
        elif directive == ".ENDBOOK":
            current = books.pop()
        elif directive in (".NAME", ".PATH") and len(fields) == 2:
            current[directive] = fields[1]
    result = []
    for survey in surveys:
        name = survey[".NAME"]
        if not PureWindowsPath(name).suffix:
            name += ".SRV"
        parts = [node[".PATH"] for node in survey["parents"]] + [survey[".PATH"], name]
        result.append(PureWindowsPath(*parts).as_posix())
    return result


def windows_path(path: Path, wine: str | None) -> str:
    return "Z:" + str(path.resolve()).replace("/", "\\") if wine else str(path.resolve())


def inspect_result(work: Path, name: str, before: dict, completed) -> tuple[dict, list[str]]:
    artifacts = {}
    errors = []
    if completed.returncode or "COMPILE_COMPLETE\n" not in completed.stdout.replace("\r\n", "\n"):
        errors.append(f"driver did not confirm completion (exit {completed.returncode})")
    for extension in EXTENSIONS:
        path = work / name / f"{name}.{extension}"
        if path.is_file() and path.stat().st_size:
            artifacts[path.relative_to(work).as_posix()] = digest(path)
        else:
            errors.append(f"missing/empty artifact: {extension}")
    for path in work.rglob("*"):
        if path.suffix.lower() == ".log" and path.stat().st_size:
            errors.append(f"Walls diagnostics: {path.relative_to(work)}")
    if any(not (work / p).is_file() or digest(work / p) != sha for p, sha in before.items()):
        errors.append("staged inputs changed")
    return artifacts, errors


def validate(
    project: Path,
    walls: Path,
    driver: Path,
    output: Path,
    *,
    wine: str | None = None,
    timeout: int = 180,
    duplicates: bool = False,
    scratch_root: Path | None = None,
) -> dict:
    project, walls, driver = project.resolve(), walls.resolve(), driver.resolve()
    root = project.parent
    name = project_name(project)
    available = {p.relative_to(root).as_posix().casefold(): p for p in source_files(root)}
    files = {project}
    for reference in referenced_files(project):
        if reference.casefold() not in available:
            raise ValueError(f"Missing referenced source in snapshot: {reference}")
        files.add(available[reference.casefold()])
    before = {p.relative_to(root).as_posix(): digest(p) for p in sorted(files)}
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    report = dict(
        status="FAIL",
        reason=[],
        inputs=before,
        inputs_unchanged=False,
        artifacts={},
        walls_build=BUILD,
        walls_sha256=digest(walls),
        driver_sha256=digest(driver),
        duplicates=duplicates,
    )
    with tempfile.TemporaryDirectory(prefix="w", dir=scratch_root) as directory:
        work = Path(directory)
        for relative in before:
            target = work / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / relative, target)
        command = ([wine] if wine else []) + [
            str(driver),
            windows_path(walls, wine),
            windows_path(work / project.name, wine),
            windows_path(work / name / name, wine),
            str(timeout),
            str(int(duplicates)),
            BUILD,
        ]
        try:
            completed = subprocess.run(
                command,
                cwd=work,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout + 30,
            )
            (output / "driver.log").write_text(
                completed.stdout + completed.stderr, encoding="utf-8"
            )
            report["artifacts"], report["reason"] = inspect_result(work, name, before, completed)
        except (OSError, subprocess.TimeoutExpired) as exc:
            report["reason"] = [str(exc)]
            details = str(exc)
            if isinstance(exc, subprocess.TimeoutExpired):
                details += f"\nstdout: {exc.stdout!r}\nstderr: {exc.stderr!r}"
            (output / "driver.log").write_text(details + "\n", encoding="utf-8")
        report["inputs_unchanged"] = all(
            p.is_file() and digest(p) == before[p.relative_to(root).as_posix()] for p in files
        ) and all((work / p).is_file() and digest(work / p) == sha for p, sha in before.items())
        if not report["inputs_unchanged"]:
            report["reason"].append("inputs changed during validation")
        shutil.copytree(work, output / "project")
    if not report["reason"]:
        report["status"] = "PASS"
    (output / "result.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report
