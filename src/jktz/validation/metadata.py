from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path, PurePosixPath

from jktz.metadata.errors import MetadataError
from jktz.metadata.raw import parse_raw_metadata
from jktz.metadata.srv import (
    is_active_srv_path,
    parse_srv_metadata,
    resolve_source_ref,
)
from jktz.reporting import CheckFailed
from jktz.validation.measurements import has_dated_or_declared_active_shots

_INVENTORY_ITEM_RE = re.compile(r"^`([^`]+)`(?:\s.*)?$")
_NO_SOURCE_MATERIAL = "Brak materiałów źródłowych."


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


def _raw_package_material(package: Path) -> list[Path]:
    control_paths = {package / "README.md", package / ".gitignore"}
    return [
        path
        for path in sorted(package.rglob("*"))
        if path not in control_paths and (path.is_file() or path.is_symlink())
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
        _check_raw_package(package, ignored_untracked, errors)


def _inventory_path(item: str) -> PurePosixPath | None:
    if item == _NO_SOURCE_MATERIAL:
        return None
    match = _INVENTORY_ITEM_RE.match(item)
    if match is None:
        raise ValueError("inventory item must start with a path in backticks")
    value = match.group(1)
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError(f"unsafe RAW inventory path {value!r}")
    return path


def _is_covered_by_inventory(path: PurePosixPath, declared: list[PurePosixPath]) -> bool:
    return any(path == item or path.is_relative_to(item) for item in declared)


def _check_raw_inventory(
    package: Path,
    content_items: list[str],
    material: list[Path],
    errors: list[str],
) -> None:
    readme = package / "README.md"
    declared: list[PurePosixPath] = []
    for item in content_items:
        try:
            inventory_path = _inventory_path(item)
        except ValueError as exc:
            errors.append(f"  {readme.as_posix()}: {exc}")
            continue
        if inventory_path is None:
            continue
        candidate = package.joinpath(*inventory_path.parts)
        if not candidate.exists() and not candidate.is_symlink():
            errors.append(
                f"  {readme.as_posix()}: declared RAW inventory path "
                f"{inventory_path.as_posix()!r} does not exist"
            )
            continue
        declared.append(inventory_path)

    for path in material:
        relative = PurePosixPath(path.relative_to(package).as_posix())
        if not _is_covered_by_inventory(relative, declared):
            errors.append(
                f"  {readme.as_posix()}: material missing from RAW inventory: {relative.as_posix()}"
            )


def _check_raw_package(
    package: Path,
    ignored_untracked: set[Path],
    errors: list[str],
) -> None:
    readme = package / "README.md"
    if not readme.exists():
        errors.append(f"  {readme.as_posix()}: missing RAW package README.md")
        return

    try:
        parsed = parse_raw_metadata(readme, readme.read_text(encoding="utf-8"))
    except MetadataError as exc:
        errors.append(f"  {exc}")
        return

    material = [
        path
        for path in _raw_package_material(package)
        if _lexical_absolute(path) not in ignored_untracked
    ]
    status = parsed.fields["Status materiału"]
    if status == "niedostępny":
        if material:
            errors.append(f"  {package.as_posix()}: unavailable RAW package contains material")
        if parsed.content_items != [_NO_SOURCE_MATERIAL]:
            errors.append(
                f"  {readme.as_posix()}: unavailable RAW package must declare {_NO_SOURCE_MATERIAL}"
            )
        return

    if not material:
        errors.append(f"  {package.as_posix()}: empty RAW package must have status niedostępny")
        return

    if _NO_SOURCE_MATERIAL in parsed.content_items:
        errors.append(f"  {readme.as_posix()}: available RAW package declares no source material")

    _check_raw_inventory(package, parsed.content_items, material, errors)


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
    raw_packages = [
        child
        for raw_dir in raw_dirs
        for child in sorted(raw_dir.iterdir())
        if _is_numbered_package_dir(child)
    ]
    raw_package_material = [
        path for package in raw_packages for path in _raw_package_material(package)
    ]
    ignored_untracked = _git_ignored_untracked(
        raw_root_material + raw_package_material,
        scan_root,
    )
    for raw_dir in raw_dirs:
        _check_raw_root(raw_dir, ignored_untracked, errors)

    for path in sorted(scan_root.rglob("*.SRV")):
        _check_srv(path, scan_root, poligony_root, errors)

    if errors:
        raise CheckFailed("ERROR: SRV metadata contract violation:\n" + "\n".join(errors))
