#!/usr/bin/env python3
"""Render Poligony/OTWORY.SRV from GPS best-measurements release data.

The template intentionally uses a tiny Jinja-compatible subset:
``{{ gps_fix(...) }}`` calls.  Keeping the renderer dependency-free matters for
the release workflow, where this script runs before Survex compiles the project.
"""

from __future__ import annotations

import argparse
import ast
import csv
import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_TEMPLATE = Path("Poligony/OTWORY.SRV.j2")
DEFAULT_OUTPUT = Path("Poligony/OTWORY.SRV")
DEFAULT_GITHUB_REPO = "dlubom/gps-kataster-obiektow-tatr"
BEST_MEASUREMENTS_ASSET = "best-measurements.csv"
GPS_FIX_RE = re.compile(r"{{\s*gps_fix\((.*?)\)\s*}}")


@dataclass(frozen=True)
class ReleaseAsset:
    """Downloaded release asset with provenance for logging."""

    path: Path
    source: str


@dataclass
class RenderStats:
    """Counters reported after rendering."""

    gps_fixes: int = 0


class RenderError(ValueError):
    """Raised when the template or input data cannot be rendered safely."""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render Poligony/OTWORY.SRV from gps-kataster latest best measurements."
    )
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--csv",
        type=Path,
        help="Use an already downloaded best-measurements.csv instead of GitHub latest.",
    )
    parser.add_argument(
        "--github-repo",
        default=DEFAULT_GITHUB_REPO,
        help="GitHub repository to read latest release from, as owner/repo.",
    )
    args = parser.parse_args(argv)

    try:
        with tempfile.TemporaryDirectory(prefix="jktz-gps-") as tmp_dir:
            asset = (
                ReleaseAsset(path=args.csv, source=str(args.csv))
                if args.csv is not None
                else _download_latest_best_measurements(args.github_repo, Path(tmp_dir))
            )
            measurements = _load_best_measurements(asset.path)
            template = args.template.read_text(encoding="utf-8")
            rendered, stats = _render_template(
                template,
                measurements=measurements,
            )
            args.output.write_text(rendered, encoding="utf-8")
    except RenderError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"Rendered {args.output} from {asset.source}")
    print(f"GPS fixes: {stats.gps_fixes}")
    return 0


def _download_latest_best_measurements(github_repo: str, tmp_dir: Path) -> ReleaseAsset:
    api_url = f"https://api.github.com/repos/{github_repo}/releases/latest"
    release = _read_json(api_url)
    assets = release.get("assets")
    if not isinstance(assets, list):
        raise RenderError(f"GitHub latest release for {github_repo} has no asset list.")

    asset = next(
        (
            item
            for item in assets
            if isinstance(item, dict) and item.get("name") == BEST_MEASUREMENTS_ASSET
        ),
        None,
    )
    if asset is None:
        tag = release.get("tag_name", "latest")
        raise RenderError(f"{github_repo} release {tag} has no {BEST_MEASUREMENTS_ASSET} asset.")

    download_url = _required_str(asset, "browser_download_url")
    output_path = tmp_dir / BEST_MEASUREMENTS_ASSET
    request = _request(download_url)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            output_path.write_bytes(response.read())
    except urllib.error.URLError as exc:
        raise RenderError(
            f"Cannot download {BEST_MEASUREMENTS_ASSET} from {download_url}: {exc}"
        ) from exc
    return ReleaseAsset(
        path=output_path, source=f"{github_repo}@{release.get('tag_name', 'latest')}"
    )


def _read_json(url: str) -> dict[str, Any]:
    request = _request(url)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = response.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise RenderError(f"Cannot read {url}: {exc}") from exc
    try:
        value = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise RenderError(f"Expected JSON from {url}: {exc}") from exc
    if not isinstance(value, dict):
        raise RenderError(f"Expected JSON object from {url}.")
    return value


def _request(url: str) -> urllib.request.Request:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "JKTZ-release-renderer",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return urllib.request.Request(url, headers=headers)


def _load_best_measurements(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        required = {"object_id", "lon", "lat", "elevation_m"}
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            missing = ", ".join(sorted(required.difference(reader.fieldnames or ())))
            raise RenderError(f"{path} is missing required columns: {missing}")
        rows = {row["object_id"]: row for row in reader if row.get("object_id")}
    if not rows:
        raise RenderError(f"{path} has no best-measurements rows.")
    return rows


def _render_template(
    template: str,
    *,
    measurements: dict[str, dict[str, str]],
) -> tuple[str, RenderStats]:
    stats = RenderStats()

    def replace(match: re.Match[str]) -> str:
        args, kwargs = _parse_gps_fix_args(match.group(1))
        try:
            return _gps_fix(
                *args,
                measurements=measurements,
                stats=stats,
                **kwargs,
            )
        except TypeError as exc:
            raise RenderError(f"Invalid gps_fix arguments: {match.group(0)}") from exc

    rendered = GPS_FIX_RE.sub(replace, template)
    return rendered, stats


def _parse_gps_fix_args(source: str) -> tuple[list[Any], dict[str, Any]]:
    try:
        expression = ast.parse(f"gps_fix({source})", mode="eval").body
    except SyntaxError as exc:
        raise RenderError(f"Invalid gps_fix template expression: {source}") from exc
    if not isinstance(expression, ast.Call) or not isinstance(expression.func, ast.Name):
        raise RenderError(f"Invalid gps_fix template expression: {source}")
    args = [_literal(node, source=source) for node in expression.args]
    kwargs = {
        keyword.arg: _literal(keyword.value, source=source)
        for keyword in expression.keywords
        if keyword.arg is not None
    }
    return args, kwargs


def _literal(node: ast.AST, *, source: str) -> Any:
    try:
        return ast.literal_eval(node)
    except ValueError as exc:
        raise RenderError(f"gps_fix accepts only literal arguments: {source}") from exc


def _gps_fix(
    station_id: str,
    object_id: str,
    *,
    measurements: dict[str, dict[str, str]],
    stats: RenderStats,
    suffix: str = "",
) -> str:
    if not isinstance(station_id, str) or not station_id:
        raise RenderError(f"Invalid gps_fix station_id: {station_id!r}")
    if not isinstance(object_id, str) or not object_id:
        raise RenderError(f"Invalid gps_fix object_id for {station_id}: {object_id!r}")
    row = measurements.get(object_id)
    if row is None:
        raise RenderError(f"{station_id} maps to {object_id}, missing in best-measurements.csv.")

    lon = _required_measurement_value(row, "lon", object_id=object_id)
    lat = _required_measurement_value(row, "lat", object_id=object_id)
    elevation = _required_measurement_value(row, "elevation_m", object_id=object_id)

    stats.gps_fixes += 1
    return _format_fix(station_id, lon, lat, elevation, suffix)


def _format_fix(station_id: str, lon: str, lat: str, elevation_m: str, suffix: str) -> str:
    lon = _decimal_text(lon, label=f"{station_id} lon")
    lat = _decimal_text(lat, label=f"{station_id} lat")
    elevation_m = _decimal_text(elevation_m, label=f"{station_id} elevation_m")
    return f"#fix\t{station_id}\tE{lon}\tN{lat}\t{elevation_m}m{suffix}"


def _required_measurement_value(row: dict[str, str], key: str, *, object_id: str) -> str:
    value = row.get(key, "").strip()
    if not value:
        raise RenderError(f"{object_id} has empty {key} in best-measurements.csv.")
    return value


def _decimal_text(value: object, *, label: str) -> str:
    text = str(value).strip()
    if not re.fullmatch(r"-?\d+(?:\.\d+)?", text):
        raise RenderError(f"{label} is not a decimal number: {text!r}")
    return text


def _required_str(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise RenderError(f"GitHub release asset missing {key}.")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
