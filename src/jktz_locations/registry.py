"""YAML registry loading utilities."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import yaml


@dataclass(frozen=True)
class RegistryObject:
    path: Path
    data: dict[str, Any]

    @property
    def object_id(self) -> str:
        return str(self.data.get("id", ""))


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def normalize_object(data: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(data)
    for key in ("systems", "observations", "related_source_records"):
        if normalized.get(key) is None:
            normalized[key] = []
    if normalized.get("cave") is None:
        normalized["cave"] = {}
    if normalized.get("source_ids") is None:
        normalized["source_ids"] = {}
    return normalized


def load_yaml(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if loaded is None:
        return {}
    if not isinstance(loaded, dict):
        raise ValueError("YAML root must be a mapping")
    return normalize_object(loaded)


def object_files(root: Path) -> list[Path]:
    return sorted((root / "rejestr" / "obiekty").glob("JKTZ-OBJ-*.yaml"))


def load_objects(root: Path) -> list[RegistryObject]:
    return [RegistryObject(path=path, data=load_yaml(path)) for path in object_files(root)]


def observations(obj: RegistryObject) -> list[dict[str, Any]]:
    return [item for item in as_list(obj.data.get("observations")) if isinstance(item, dict)]


def related_source_records(obj: RegistryObject) -> list[dict[str, Any]]:
    return [item for item in as_list(obj.data.get("related_source_records")) if isinstance(item, dict)]


def current_observation(obj: RegistryObject) -> Optional[dict[str, Any]]:
    current_id = str(obj.data.get("current_observation_id", ""))
    for observation in observations(obj):
        if str(observation.get("id", "")) == current_id:
            return observation
    return None


def iter_observation_ids(objects: Iterable[RegistryObject]) -> Iterable[tuple[str, Path]]:
    for obj in objects:
        for observation in observations(obj):
            yield str(observation.get("id", "")), obj.path
