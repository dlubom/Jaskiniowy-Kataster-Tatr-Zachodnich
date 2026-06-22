from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

from jktz.metadata.io import atomic_write, encode_srv, read_srv


def test_srv_latin1_round_trip_preserves_every_byte(tmp_path: Path) -> None:
    path = tmp_path / "CAVE.SRV"
    original = b"#prefix Cave\n; legacy byte: \x9c\n0\t1\t1.0\t90\t0\n"
    path.write_bytes(original)

    text = read_srv(path)

    assert encode_srv(text) == original


def test_atomic_write_replaces_content_without_leaving_temporary_file(tmp_path: Path) -> None:
    path = tmp_path / "CAVE.SRV"
    path.write_bytes(b"before")

    atomic_write(path, b"after")

    assert path.read_bytes() == b"after"
    assert list(tmp_path.iterdir()) == [path]


def test_atomic_write_preserves_existing_file_mode(tmp_path: Path) -> None:
    if os.name == "nt":
        pytest.skip("Windows does not preserve POSIX permission bits")

    path = tmp_path / "CAVE.SRV"
    path.write_bytes(b"before")
    path.chmod(0o640)

    atomic_write(path, b"after")

    assert stat.S_IMODE(path.stat().st_mode) == 0o640


def test_atomic_write_creates_parent_directories(tmp_path: Path) -> None:
    path = tmp_path / "Cave" / "_RAW" / "01" / "README.md"

    atomic_write(path, "zażółć\n".encode())

    assert path.read_text(encoding="utf-8") == "zażółć\n"
