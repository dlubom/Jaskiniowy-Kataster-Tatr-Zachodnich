from __future__ import annotations

import os
import subprocess
from pathlib import Path

from jktz.metadata.errors import MetadataError
from jktz.metadata.raw import parse_raw_metadata
from jktz.metadata.srv import (
    is_active_srv_path,
    parse_srv_metadata,
    resolve_source_ref,
)
from jktz.reporting import CheckFailed
from jktz.validation.measurements import has_dated_or_declared_active_shots


def _poligony_root(root: Path) -> Path:
    if root.name == "Poligony":
        return root
    candidate = root / "Poligony"
    if candidate.is_dir():
        return candidate
    return root


def _repo_relative(path: Path, scan_root: Path) -> Path:
    base = scan_root.parent if scan_root.name == "Poligony" else scan_root
    try:
        return path.relative_to(base)
    except ValueError:
        return path


def _is_numbered_package_dir(path: Path) -> bool:
    return path.is_dir() and len(path.name) == 2 and path.name.isdigit()


def _raw_root_material(raw_dir: Path) -> list[Path]:
    return [
        child
        for child in sorted(raw_dir.iterdir())
        if child.name != "README.md" and not _is_numbered_package_dir(child)
    ]


def _lexical_absolute(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path)))


def _git_ignored_untracked(paths: list[Path], scan_root: Path) -> set[Path]:
    absolute_paths = [_lexical_absolute(path) for path in paths]
    if not absolute_paths:
        return set()

    stdin = b"\0".join(os.fsencode(path) for path in absolute_paths) + b"\0"
    env = {key: value for key, value in os.environ.items() if not key.upper().startswith("GIT_")}
    env.update({"LANG": "C", "LC_ALL": "C"})
    try:
        result = subprocess.run(
            ["git", "-C", os.fspath(scan_root), "check-ignore", "--stdin", "-z"],
            input=stdin,
            capture_output=True,
            check=False,
            env=env,
        )
    except FileNotFoundError:
        return set()

    if result.returncode in {0, 1}:
        return {
            _lexical_absolute(Path(os.fsdecode(path)))
            for path in result.stdout.split(b"\0")
            if path
        }

    stderr = result.stderr.decode(errors="replace").strip()
    if result.returncode == 128 and (
        "not a git repository" in stderr or "must be run in a work tree" in stderr
    ):
        return set()
    detail = stderr or f"git exited with status {result.returncode}"
    raise CheckFailed(f"ERROR: git check-ignore failed: {detail}")


def _check_raw_root(raw_dir: Path, ignored_untracked: set[Path], errors: list[str]) -> None:
    numbered_packages = [
        child for child in sorted(raw_dir.iterdir()) if _is_numbered_package_dir(child)
    ]

    for child in _raw_root_material(raw_dir):
        if child in ignored_untracked:
            continue
        errors.append(f"  {child.as_posix()}: material left directly under _RAW")

    for package in numbered_packages:
        _check_raw_package(package, errors)


def _check_raw_package(package: Path, errors: list[str]) -> None:
    readme = package / "README.md"
    if not readme.exists():
        errors.append(f"  {readme.as_posix()}: missing RAW package README.md")
        return

    try:
        parsed = parse_raw_metadata(readme, readme.read_text(encoding="utf-8"))
    except MetadataError as exc:
        errors.append(f"  {exc}")
        return

    material_children = [child for child in package.iterdir() if child.name != "README.md"]
    if material_children or parsed.fields["Status materiału"] == "niedostępny":
        return

    errors.append(f"  {package.as_posix()}: empty RAW package must have status niedostępny")


def _check_srv(path: Path, scan_root: Path, poligony_root: Path, errors: list[str]) -> None:
    rel = _repo_relative(path, scan_root)
    if not is_active_srv_path(rel):
        return

    text = path.read_text(encoding="latin-1")
    try:
        parsed = parse_srv_metadata(rel, text)
    except MetadataError as exc:
        errors.append(f"  {exc}")
        return

    if not has_dated_or_declared_active_shots(parsed.body):
        errors.append(f"  {rel.as_posix()}: active shot without #date or DECL")

    for source_ref in parsed.repeated["SOURCE_REF"]:
        try:
            package = resolve_source_ref(path, source_ref, poligony_root)
        except MetadataError as exc:
            errors.append(f"  {rel.as_posix()}: {exc}")
            continue
        _check_source_ref_package(rel, source_ref, package, errors)


def _check_source_ref_package(rel: Path, source_ref: str, package: Path, errors: list[str]) -> None:
    if not package.exists():
        errors.append(f"  {rel.as_posix()}: SOURCE_REF {source_ref!r} does not exist")
        return
    if not package.is_dir():
        errors.append(f"  {rel.as_posix()}: SOURCE_REF {source_ref!r} is not a directory")
        return
    if not (package / "README.md").exists():
        errors.append(f"  {rel.as_posix()}: SOURCE_REF {source_ref!r} missing README.md")


def check(root: Path = Path("Poligony")) -> None:
    """Validate active SRV metadata blocks and normalized _RAW source packages."""
    errors: list[str] = []
    scan_root = root.resolve()
    poligony_root = _poligony_root(scan_root)

    raw_dirs = [raw_dir for raw_dir in sorted(scan_root.rglob("_RAW")) if raw_dir.is_dir()]
    raw_root_material = [child for raw_dir in raw_dirs for child in _raw_root_material(raw_dir)]
    ignored_untracked = _git_ignored_untracked(raw_root_material, scan_root)
    for raw_dir in raw_dirs:
        _check_raw_root(raw_dir, ignored_untracked, errors)

    for path in sorted(scan_root.rglob("*.SRV")):
        _check_srv(path, scan_root, poligony_root, errors)

    if errors:
        raise CheckFailed("ERROR: SRV metadata contract violation:\n" + "\n".join(errors))
