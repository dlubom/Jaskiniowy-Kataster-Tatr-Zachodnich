"""Observable atomic publication, failure recovery and package provenance."""

from __future__ import annotations

import ctypes
import errno
import hashlib
import io
import json
import os
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest

from jktz.pockettopo import package
from jktz.pockettopo.drawings import export_drawings
from jktz.pockettopo.parser import DEFAULT_LIMITS

EVIDENCE = Path(__file__).resolve().parents[1] / "doc/pockettopo/evidence"
SOURCE = next((EVIDENCE / "p01/cases/api-drawings").glob("*.top"))


@pytest.fixture
def fast_tools(monkeypatch):
    # P05 tests validate rendering itself. These tests inject only that costly
    # external boundary, while preserving real parsing, reports and SVG content.
    def drawings(data, **kwargs):
        kwargs.pop("resvg_path")
        result = export_drawings(data, **kwargs)
        png = (EVIDENCE / "p05/examples/api-drawings/plan-sketch.png").read_bytes()
        result.pngs.update(dict.fromkeys(package.VARIANTS, png))
        result.report["completeness"]["png_drawings_created"] = 4
        return result

    monkeypatch.setattr(package, "export_drawings", drawings)
    monkeypatch.setattr(package, "validate_surveys", lambda *a, **k: {"complete": True})


def test_atomic_package_manifest_source_and_all_artifacts(tmp_path, fast_tools):
    original = SOURCE.read_bytes()
    destination = tmp_path / "new"
    report = package.convert_package(SOURCE, destination)
    assert len(list(destination.iterdir())) == 12
    assert len(list(destination.glob("*.svg"))) == len(list(destination.glob("*.png"))) == 4
    assert SOURCE.read_bytes() == original
    stored = json.loads((destination / "conversion-report.json").read_bytes())
    assert stored == json.loads(package.json_bytes(report))
    source = json.loads((destination / "source.json").read_bytes())
    assert source["provenance"] == report["provenance"]
    assert source["provenance"]["sha256"] == hashlib.sha256(original).hexdigest()
    assert report["stage"] == "P06"
    assert report["completeness"]["atomic_package_created"] is True
    assert report["completeness"]["conversion_complete"] is True
    assert report["package"]["collision_policy"] == "error"
    for name, metadata in report["package"]["artifacts"].items():
        data = (destination / name).read_bytes()
        assert metadata == {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    assert list(tmp_path.iterdir()) == [destination]


def test_conversion_bounds_input_read_before_parsing(tmp_path, monkeypatch, fast_tools):
    data = SOURCE.read_bytes()
    original_open = Path.open
    read_sizes = []

    class ObservedSource(io.BytesIO):
        def read(self, size=-1):
            read_sizes.append(size)
            assert size == DEFAULT_LIMITS.max_bytes + 1
            return super().read(size)

    def observed_open(path, mode="r", *args, **kwargs):
        if path == SOURCE and mode == "rb":
            return ObservedSource(data)
        return original_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", observed_open)
    report = package.convert_package(SOURCE, tmp_path / "new")
    assert report["provenance"]["bytes"] == len(data)
    assert read_sizes == [DEFAULT_LIMITS.max_bytes + 1]


@pytest.mark.parametrize("kind", ["directory", "file", "empty", "symlink", "dangling"])
def test_any_existing_target_preserved(tmp_path, kind):
    target = tmp_path / "target"
    if kind in {"directory", "empty"}:
        target.mkdir()
        if kind == "directory":
            (target / "old").write_bytes(b"original")
    elif kind == "file":
        target.write_bytes(b"original")
    else:
        try:
            target.symlink_to(SOURCE if kind == "symlink" else tmp_path / "missing")
        except OSError:
            pytest.skip("Platform does not permit unprivileged symlinks")
    before = target.lstat()
    with pytest.raises(FileExistsError, match="collision policy"):
        package.convert_package(SOURCE, target)
    assert target.lstat() == before
    if kind == "directory":
        assert (target / "old").read_bytes() == b"original"


def test_output_in_raw_or_missing_parent_refused(tmp_path):
    raw = tmp_path / "_RAW"
    raw.mkdir()
    with pytest.raises(ValueError, match="_RAW"):
        package.convert_package(SOURCE, raw / "new")
    with pytest.raises(FileNotFoundError, match="parent"):
        package.convert_package(SOURCE, tmp_path / "absent" / "new")
    alias = tmp_path / "alias"
    try:
        alias.symlink_to(raw, target_is_directory=True)
    except OSError:
        pytest.skip("Platform does not permit unprivileged symlinks")
    with pytest.raises(ValueError, match="_RAW"):
        package.convert_package(SOURCE, alias / "new")
    assert not list(raw.iterdir())


@pytest.mark.parametrize("failure", ["write", "fsync", "rename"])
def test_write_failure_leaves_no_partial_package_or_staging(
    tmp_path, monkeypatch, fast_tools, failure
):
    original_open = Path.open
    writes = 0

    def failed_open(self, mode="r", *args, **kwargs):
        nonlocal writes
        if mode == "xb":
            writes += 1
            if writes == 4:
                raise OSError("injected disk full")
        return original_open(self, mode, *args, **kwargs)

    def fail(*args):
        raise OSError("injected disk full")

    if failure == "write":
        monkeypatch.setattr(Path, "open", failed_open)
    elif failure == "fsync":
        monkeypatch.setattr(package.os, "fsync", fail)
    else:
        monkeypatch.setattr(package, "_rename_noreplace", fail)
    with pytest.raises(OSError, match="disk full"):
        package.convert_package(SOURCE, tmp_path / "output")
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("occupied", [False, True])
def test_concurrent_target_is_not_replaced_even_if_empty(
    tmp_path, monkeypatch, fast_tools, occupied
):
    target = tmp_path / "output"
    rename = package._rename_noreplace

    def concurrent(source, destination):
        destination.mkdir()
        if occupied:
            (destination / "winner").write_bytes(b"other process")
        rename(source, destination)

    monkeypatch.setattr(package, "_rename_noreplace", concurrent)
    with pytest.raises(FileExistsError):
        package.convert_package(SOURCE, target)
    assert list(tmp_path.iterdir()) == [target]
    assert len(list(target.iterdir())) == int(occupied)
    if occupied:
        assert (target / "winner").read_bytes() == b"other process"


def test_incomplete_compilation_is_preserved_as_full_diagnostic_package(
    tmp_path, monkeypatch, fast_tools
):
    validation = {"complete": False, "failure": "missing stations"}
    monkeypatch.setattr(package, "validate_surveys", lambda *a, **k: validation)
    target = tmp_path / "output"
    report = package.convert_package(SOURCE, target)
    assert report["exports"]["validation"] == validation
    assert report["completeness"]["conversion_complete"] is False
    assert report["completeness"]["package_artifacts_complete"] is True
    assert len(list(target.iterdir())) == 12


def test_partial_drawing_set_cannot_be_published(tmp_path, monkeypatch):
    monkeypatch.setattr(
        package, "export_drawings", lambda *a, **k: SimpleNamespace(svgs={}, pngs={})
    )
    with pytest.raises(ValueError, match="all four"):
        package.convert_package(SOURCE, tmp_path / "output")
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("platform", ["darwin", "linux", "linux2", "win32", "unsupported"])
def test_platform_exclusive_rename_contract(monkeypatch, tmp_path, platform):
    calls = []

    class Operation:
        def __call__(self, *args):
            calls.append(args)
            return 0

    libc = SimpleNamespace(renamex_np=Operation(), renameat2=Operation())
    monkeypatch.setattr(package.sys, "platform", platform)
    monkeypatch.setattr(package.ctypes, "CDLL", lambda *a, **k: libc)
    monkeypatch.setattr(package.os, "rename", lambda *a: calls.append(a))
    source, target = tmp_path / "stage", tmp_path / "target"
    if platform == "unsupported":
        with pytest.raises(OSError, match="unsupported"):
            package._rename_noreplace(source, target)
        assert not calls
    else:
        package._rename_noreplace(source, target)
        if platform == "darwin":
            assert calls == [(bytes(source), bytes(target), 4)]
        elif platform.startswith("linux"):
            assert calls == [(-100, bytes(source), -100, bytes(target), 1)]
        else:
            assert calls == [(source, target)]


def test_native_rename_failure_propagates_errno(monkeypatch, tmp_path):
    class Failure:
        def __call__(self, *args):
            ctypes.set_errno(errno.EACCES)
            return -1

    monkeypatch.setattr(package.sys, "platform", "linux")
    monkeypatch.setattr(
        package.ctypes, "CDLL", lambda *a, **k: SimpleNamespace(renameat2=Failure())
    )
    with pytest.raises(PermissionError):
        package._rename_noreplace(tmp_path / "stage", tmp_path / "target")


def test_missing_atomic_primitive_fails_closed(tmp_path, monkeypatch):
    monkeypatch.setattr(package.sys, "platform", "linux")
    monkeypatch.setattr(package.ctypes, "CDLL", lambda *a, **k: SimpleNamespace())
    with pytest.raises(OSError, match="unavailable"):
        package._publish(tmp_path / "out", {"test": b"complete"})
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("case", ["api-cardinal", "gui-colors"])
def test_held_shots_and_overlay_notices_prevent_complete_claim(tmp_path, fast_tools, case):
    source = next((EVIDENCE / "p01/cases" / case).glob("*.top"))
    report = package.convert_package(source, tmp_path / "out")
    assert report["completeness"]["conversion_complete"] is False
    assert report["package"]["drawing_notices"]
    assert len(list((tmp_path / "out").iterdir())) == 12


def test_real_compiler_renderer_package(tmp_path):
    renderer = os.environ.get("RESVG") or shutil.which("resvg")
    available = renderer and shutil.which("cavern") and shutil.which("dump3d")
    if not available:
        if os.environ.get("JKTZ_REQUIRE_CAVERN") == os.environ.get("JKTZ_REQUIRE_RESVG") == "1":
            pytest.fail("Full P06 package requires resvg, cavern and dump3d")
        pytest.skip("Full P06 package requires resvg, cavern and dump3d")
    target = tmp_path / "package"
    report = package.convert_package(SOURCE, target, resvg_path=renderer)
    assert report["completeness"]["conversion_complete"] is True
    assert len(list(target.iterdir())) == 12
    for name in package.VARIANTS:
        assert (target / (name + ".png")).read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
        assert (target / (name + ".svg")).read_text(encoding="utf-8").startswith("<svg")
