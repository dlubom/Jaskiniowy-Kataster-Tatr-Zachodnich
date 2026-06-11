from __future__ import annotations

from pathlib import Path

from jktz.metadata_errors import MetadataError
from jktz.raw_metadata import parse_raw_readme
from jktz.reporting import CheckFailed
from jktz.srv_metadata import (
    is_active_srv_path,
    parse_srv_metadata,
    resolve_source_ref,
)
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


def _check_raw_root(raw_dir: Path, errors: list[str]) -> None:
    children = sorted(raw_dir.iterdir())
    numbered_packages = [child for child in children if _is_numbered_package_dir(child)]

    for child in children:
        if child.name == "README.md" or _is_numbered_package_dir(child):
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
        parsed = parse_raw_readme(readme, readme.read_text(encoding="utf-8"))
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

    for raw_dir in sorted(scan_root.rglob("_RAW")):
        if raw_dir.is_dir():
            _check_raw_root(raw_dir, errors)

    for path in sorted(scan_root.rglob("*.SRV")):
        _check_srv(path, scan_root, poligony_root, errors)

    if errors:
        raise CheckFailed("ERROR: SRV metadata contract violation:\n" + "\n".join(errors))
