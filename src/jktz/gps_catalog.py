"""Read catalogue identities from a single, checksummed GPS release or preview."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sqlite3
import tempfile
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jktz.entrances.render import (
    BEST_MEASUREMENTS_ASSET,
    _download_release_asset,
    _read_json,
    _required_str,
)

CATALOGUE_ASSET = "katalog.gpkg"
ASSET_NAMES = (BEST_MEASUREMENTS_ASSET, CATALOGUE_ASSET)
MANIFEST_NAME = "snapshot.json"
CAVE_ID = re.compile(r"C-[0-9]{4,}")
OBJECT_ID = re.compile(r"[A-Z]{2,3}-[0-9]{4,}")
SHA256 = re.compile(r"[0-9a-f]{64}")


@dataclass(frozen=True)
class GpsSnapshot:
    repo: str
    tag: str
    release_id: int | None
    csv_path: Path
    gpkg_path: Path
    csv_sha256: str
    gpkg_sha256: str


@dataclass(frozen=True)
class Cave:
    cave_id: str
    name: str
    system_cave_id: str | None


@dataclass(frozen=True)
class CatalogueObject:
    object_id: str
    name: str | None
    cave_id: str | None
    category: str


@dataclass(frozen=True)
class Catalogue:
    caves: dict[str, Cave]
    objects: dict[str, CatalogueObject]


def download_snapshot(repo: str, destination: Path) -> GpsSnapshot:
    """Fetch both assets from one release into a new or empty directory."""
    if destination.is_symlink() or (destination.exists() and any(destination.iterdir())):
        raise FileExistsError(f"GPS snapshot destination is occupied: {destination}")

    release = _read_json(f"https://api.github.com/repos/{repo}/releases/latest")
    tag = _required_str(release, "tag_name")
    release_id = _github_id(release.get("id"), f"{repo}@{tag} release")
    assets = _release_assets(release, f"{repo}@{tag}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".jktz-gps-", dir=destination.parent) as temporary:
        staging = Path(temporary)
        manifest_assets = {
            name: _download_snapshot_asset(assets[name], staging / name) for name in ASSET_NAMES
        }
        manifest = {"repo": repo, "tag": tag, "release_id": release_id, "assets": manifest_assets}
        (staging / MANIFEST_NAME).write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )
        if destination.exists():
            destination.rmdir()  # Refuses to remove files or a directory with existing inputs.
        staging.rename(destination)
    return _snapshot(destination, repo, tag, release_id, manifest_assets)


def load_snapshot(directory: Path) -> GpsSnapshot:
    """Verify the local manifest and both files without accessing GitHub.

    A preview uses its pinned provenance as the tag and a null release ID.
    The files use their release asset names, independent of the manifest contents.
    """
    path = directory / MANIFEST_NAME
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError(f"Cannot read GPS snapshot manifest {path}: {exc}") from exc

    if (
        not isinstance(manifest, dict)
        or not {"repo", "tag", "release_id", "assets"} <= manifest.keys()
    ):
        raise ValueError(f"{path} must specify repo, tag, release_id and assets.")
    repo, tag, release_id = manifest["repo"], manifest["tag"], manifest["release_id"]
    if not all(isinstance(value, str) and value.strip() for value in (repo, tag)):
        raise ValueError(f"{path} must specify non-empty repo and tag.")
    if release_id is not None:
        _github_id(release_id, str(path))
    assets = manifest["assets"]
    if not isinstance(assets, dict):
        raise ValueError(f"{path} must specify asset checksums.")
    for name in ASSET_NAMES:
        asset = assets.get(name)
        checksum = asset.get("sha256") if isinstance(asset, dict) else None
        if not isinstance(checksum, str) or SHA256.fullmatch(checksum) is None:
            raise ValueError(f"{path}: {name} must have a SHA-256 checksum.")
        _check_digest(directory / name, checksum, _sha256(directory / name))
    return _snapshot(directory, repo, tag, release_id, assets)


def _snapshot(
    directory: Path, repo: str, tag: str, release_id: int | None, assets: dict[str, Any]
) -> GpsSnapshot:
    return GpsSnapshot(
        repo=repo,
        tag=tag,
        release_id=release_id,
        csv_path=directory / BEST_MEASUREMENTS_ASSET,
        gpkg_path=directory / CATALOGUE_ASSET,
        csv_sha256=assets[BEST_MEASUREMENTS_ASSET]["sha256"],
        gpkg_sha256=assets[CATALOGUE_ASSET]["sha256"],
    )


def _release_assets(release: dict[str, Any], source: str) -> dict[str, dict[str, Any]]:
    items = release.get("assets")
    if not isinstance(items, list):
        raise ValueError(f"{source} has no asset list.")
    assets = {}
    for item in items:
        if isinstance(item, dict) and item.get("name") in ASSET_NAMES:
            name = item["name"]
            if name in assets:
                raise ValueError(f"{source} has duplicate assets named {name}.")
            assets[name] = item
    for name in ASSET_NAMES:
        if name not in assets:
            raise ValueError(f"{source} has no {name} asset.")
    return assets


def _github_id(value: object, source: str) -> int:
    if type(value) is not int or value <= 0:
        raise ValueError(f"{source} must specify a positive GitHub ID.")
    return value


def _download_snapshot_asset(asset: dict[str, Any], path: Path) -> dict[str, int | str]:
    asset_id = _github_id(asset.get("id"), path.name)
    _download_release_asset(_required_str(asset, "browser_download_url"), path)
    checksum = _sha256(path)
    if (digest := asset.get("digest")) is not None:
        _check_digest(path, digest, f"sha256:{checksum}")
    return {"id": asset_id, "sha256": checksum}


def _sha256(path: Path) -> str:
    try:
        with path.open("rb") as file:
            digest = hashlib.sha256()
            for chunk in iter(lambda: file.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise ValueError(f"Cannot checksum GPS asset {path}: {exc}") from exc
    return digest.hexdigest()


def _check_digest(path: Path, expected: object, actual: str) -> None:
    if actual != expected:
        raise ValueError(f"{path}: SHA-256 mismatch, expected {expected!r}, got {actual}.")


def read_catalogue(snapshot: GpsSnapshot) -> Catalogue:
    """Read the complete catalogue, then validate its links and the Best CSV."""
    path = snapshot.gpkg_path
    try:
        # A snapshot is a standalone, immutable file. SQLite must not create
        # sidecar files or recover a journal when reading it.
        uri = path.resolve().as_uri() + "?mode=ro&immutable=1"
        with closing(sqlite3.connect(uri, uri=True)) as connection:
            _require_catalogue_tables(connection)
            catalogue = Catalogue(_read_caves(connection), _read_objects(connection))
        for cave_id in catalogue.caves:
            effective_cave_id(cave_id, catalogue)
        for obj in catalogue.objects.values():
            if obj.cave_id is not None and obj.cave_id not in catalogue.caves:
                raise ValueError(f"objects.cave_id for {obj.object_id} references {obj.cave_id}.")
    except (sqlite3.Error, ValueError) as exc:
        raise ValueError(f"{path}: {exc}") from exc

    _check_best_links(snapshot.csv_path, catalogue)
    return catalogue


def _require_catalogue_tables(connection: sqlite3.Connection) -> None:
    tables = {
        name
        for (name,) in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name IN ('caves', 'objects')"
        )
    }
    if missing := {"caves", "objects"} - tables:
        raise ValueError(f"Missing catalogue tables: {', '.join(sorted(missing))}.")


def _read_caves(connection: sqlite3.Connection) -> dict[str, Cave]:
    caves: dict[str, Cave] = {}
    for cave_id, name, system_id in connection.execute(
        "SELECT caves.cave_id, caves.name, caves.system_cave_id FROM caves ORDER BY caves.fid"
    ):
        if not isinstance(cave_id, str) or CAVE_ID.fullmatch(cave_id) is None:
            raise ValueError(f"Invalid caves.cave_id {cave_id!r}.")
        if cave_id in caves:
            raise ValueError(f"duplicate cave_id {cave_id} in caves.")
        if not isinstance(name, str):
            raise ValueError(f"Invalid caves.name for {cave_id}: {name!r}.")
        _check_cave_reference(system_id, f"caves.system_cave_id for {cave_id}")
        caves[cave_id] = Cave(cave_id, name, system_id)
    return caves


def _read_objects(connection: sqlite3.Connection) -> dict[str, CatalogueObject]:
    objects: dict[str, CatalogueObject] = {}
    for object_id, name, cave_id, category in connection.execute(
        "SELECT objects.object_id, objects.name, objects.cave_id, objects.category "
        "FROM objects ORDER BY objects.fid"
    ):
        if not isinstance(object_id, str) or OBJECT_ID.fullmatch(object_id) is None:
            raise ValueError(f"Invalid objects.object_id {object_id!r}.")
        if object_id in objects:
            raise ValueError(f"duplicate object_id {object_id} in objects.")
        if name is not None and not isinstance(name, str):
            raise ValueError(f"Invalid objects.name for {object_id}: {name!r}.")
        if not isinstance(category, str):
            raise ValueError(f"Invalid objects.category for {object_id}: {category!r}.")
        _check_cave_reference(cave_id, f"objects.cave_id for {object_id}")
        objects[object_id] = CatalogueObject(object_id, name, cave_id, category)
    return objects


def _check_cave_reference(cave_id: object, field: str) -> None:
    if cave_id is not None and (not isinstance(cave_id, str) or CAVE_ID.fullmatch(cave_id) is None):
        raise ValueError(f"Invalid {field}: {cave_id!r}.")


def effective_cave_id(cave_id: str, catalogue: Catalogue) -> str:
    """Resolve a cave to the last cave in its chain of explicit system links."""
    start = cave_id
    visited = set()
    while cave_id not in visited:
        cave = catalogue.caves.get(cave_id)
        if cave is None:
            raise ValueError(f"Cannot resolve {start}: unknown cave_id {cave_id}.")
        if cave.system_cave_id is None:
            return cave_id
        visited.add(cave_id)
        cave_id = cave.system_cave_id
    raise ValueError(f"system_cave_id cycle from {start} at {cave_id}.")


def _check_best_links(path: Path, catalogue: Catalogue) -> None:
    required = {"object_id", "cave_id", "system_cave_id"}
    seen = set()
    with path.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames or []
        if missing := required.difference(fieldnames):
            raise ValueError(f"{path}: missing required columns: {', '.join(sorted(missing))}.")
        for field in sorted(required):
            if fieldnames.count(field) > 1:
                raise ValueError(f"{path}: duplicate column {field}.")
        for row in reader:
            location = f"{path}:{reader.line_num}"
            object_id = row["object_id"]
            obj = catalogue.objects.get(object_id)
            if obj is None:
                raise ValueError(f"{location}: unknown object_id {object_id!r}.")
            if object_id in seen:
                raise ValueError(f"{location}: duplicate object_id {object_id}.")
            seen.add(object_id)
            cave = catalogue.caves[obj.cave_id] if obj.cave_id is not None else None
            expected = {
                "cave_id": obj.cave_id,
                "system_cave_id": cave.system_cave_id if cave else None,
            }
            for field, value in expected.items():
                if row[field] != (value or ""):
                    raise ValueError(
                        f"{location}: {object_id} {field} is {row[field]!r}, expected {value!r}."
                    )
