from __future__ import annotations

import hashlib
import io
import json
import sqlite3
import urllib.error
import urllib.request
from contextlib import closing

import pytest

from jktz.entrances.render import render_entrances
from jktz.gps_catalog import download_snapshot, effective_cave_id, load_snapshot, read_catalogue


def write_manifest(directory):
    manifest = {
        "repo": "owner/gps",
        "tag": "preview-49",
        "release_id": None,
        "assets": {
            name: {"sha256": hashlib.sha256((directory / name).read_bytes()).hexdigest()}
            for name in ("best-measurements.csv", "katalog.gpkg")
        },
    }
    (directory / "snapshot.json").write_text(json.dumps(manifest), encoding="utf-8")
    return manifest


def update_database(directory, sql):
    with closing(sqlite3.connect(directory / "katalog.gpkg")) as connection:
        connection.executescript(sql)
    write_manifest(directory)


@pytest.fixture
def snapshot_directory(tmp_path):
    directory = tmp_path / "GPS #1"
    directory.mkdir()
    (directory / "best-measurements.csv").write_text(
        "object_id,cave_id,system_cave_id,lon,lat,elevation_m\n"
        "MLZ-0068,C-0648,C-0295,19.9,49.2,1730\n"
        "KSZ-0112,,,19.8,49.3,1300\n",
        encoding="utf-8",
    )
    update_database(
        directory,
        """
        CREATE TABLE caves (
            fid INTEGER PRIMARY KEY,
            cave_id TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            system_cave_id TEXT REFERENCES caves(cave_id)
        );
        CREATE TABLE objects (
            fid INTEGER PRIMARY KEY,
            object_id TEXT NOT NULL UNIQUE,
            name TEXT,
            cave_id TEXT REFERENCES caves(cave_id),
            category TEXT NOT NULL
        );
        INSERT INTO caves VALUES
            (1, 'C-0295', 'Jaskinia Wielka Śnieżna', NULL),
            (2, 'C-0648', 'Jaskinia Śnieżna', 'C-0295'),
            (3, 'C-12345', 'Część systemu', 'C-0648');
        INSERT INTO objects VALUES
            (1, 'MLZ-0068', 'Jaskinia Śnieżna', 'C-0648', 'jaskinia_otwor'),
            (2, 'KSZ-0112', NULL, NULL, 'punkt_terenowy'),
            (3, 'LEJ-0002', NULL, 'C-12345', 'jaskinia_otwor');
        """,
    )
    return directory


def test_catalogue_contains_system_without_object(snapshot_directory, monkeypatch):
    def unexpected_network(*args, **kwargs):
        pytest.fail("The offline snapshot accessed the network")

    monkeypatch.setattr(urllib.request, "urlopen", unexpected_network)
    snapshot = load_snapshot(snapshot_directory)
    catalogue = read_catalogue(snapshot)

    assert snapshot.repo == "owner/gps"
    assert snapshot.tag == "preview-49"
    assert snapshot.release_id is None
    assert catalogue.caves["C-0295"].name == "Jaskinia Wielka Śnieżna"
    assert catalogue.caves["C-0295"].system_cave_id is None
    assert all(obj.cave_id != "C-0295" for obj in catalogue.objects.values())
    assert catalogue.objects["MLZ-0068"].cave_id == "C-0648"
    assert catalogue.objects["MLZ-0068"].category == "jaskinia_otwor"
    assert catalogue.objects["KSZ-0112"].cave_id is None
    assert catalogue.objects["KSZ-0112"].name is None
    assert catalogue.objects["LEJ-0002"].cave_id == "C-12345"
    assert effective_cave_id("C-0295", catalogue) == "C-0295"
    assert effective_cave_id("C-0648", catalogue) == "C-0295"
    assert effective_cave_id("C-12345", catalogue) == "C-0295"
    with pytest.raises(ValueError, match="C-9999"):
        effective_cave_id("C-9999", catalogue)

    template = snapshot_directory / "template"
    output = snapshot_directory / "OTWORY.SRV"
    template.write_text("{{ gps_fix('Sniezna:0', 'MLZ-0068') }}\n", encoding="utf-8")
    render_entrances(template_path=template, output_path=output, csv_path=snapshot.csv_path)
    assert output.read_text(encoding="utf-8") == "#fix\tSniezna:0\tE19.9\tN49.2\t1730m\n"
    assert load_snapshot(snapshot_directory) == snapshot


def test_catalogue_opens_sqlite_read_only(snapshot_directory, monkeypatch):
    snapshot = load_snapshot(snapshot_directory)
    before = snapshot.gpkg_path.read_bytes()
    connect = sqlite3.connect

    def check_connection(*args, **kwargs):
        connection = connect(*args, **kwargs)
        with pytest.raises(sqlite3.OperationalError, match="readonly"):
            connection.execute("DELETE FROM caves")
        return connection

    monkeypatch.setattr(sqlite3, "connect", check_connection)

    assert read_catalogue(snapshot).caves["C-0295"].cave_id == "C-0295"
    assert snapshot.gpkg_path.read_bytes() == before
    assert not list(snapshot_directory.glob("katalog.gpkg-*"))


def test_snapshot_resolves_release_once(tmp_path, snapshot_directory, monkeypatch):
    csv_bytes = (snapshot_directory / "best-measurements.csv").read_bytes()
    gpkg_bytes = (snapshot_directory / "katalog.gpkg").read_bytes()
    first_csv = "https://github.com/owner/gps/releases/download/v1/best-measurements.csv"
    first_gpkg = "https://github.com/owner/gps/releases/download/v1/katalog.gpkg"
    first_release = {
        "tag_name": "v1",
        "id": 123,
        "assets": [
            {"id": 1, "name": "best-measurements.csv", "browser_download_url": first_csv},
            {
                "id": 2,
                "name": "katalog.gpkg",
                "browser_download_url": first_gpkg,
                "digest": f"sha256:{hashlib.sha256(gpkg_bytes).hexdigest()}",
            },
        ],
    }
    second_release = {
        "tag_name": "v2",
        "id": 124,
        "assets": [
            dict(
                asset,
                id=asset["id"] + 2,
                browser_download_url=asset["browser_download_url"].replace("/v1/", "/v2/"),
            )
            for asset in first_release["assets"]
        ],
    }
    releases = iter([first_release, second_release])
    requests = []

    def urlopen(request, *, timeout):
        requests.append(request)
        if request.full_url.endswith("/releases/latest"):
            return io.BytesIO(json.dumps(next(releases)).encode())
        return io.BytesIO({first_csv: csv_bytes, first_gpkg: gpkg_bytes}[request.full_url])

    monkeypatch.setenv("GITHUB_TOKEN", "test-token")
    monkeypatch.setattr(urllib.request, "urlopen", urlopen)
    destination = tmp_path / "snapshot"
    destination.mkdir()

    snapshot = download_snapshot("owner/gps", destination)

    assert [req.full_url for req in requests] == [
        "https://api.github.com/repos/owner/gps/releases/latest",
        first_csv,
        first_gpkg,
    ]
    assert [req.get_header("Authorization") for req in requests] == [
        "Bearer test-token",
        None,
        None,
    ]
    assert "Authorization" in requests[0].unredirected_hdrs
    assert snapshot.tag == "v1"
    assert snapshot.release_id == 123
    assert snapshot.csv_path.read_bytes() == csv_bytes
    assert snapshot.gpkg_path.read_bytes() == gpkg_bytes
    assert snapshot.csv_sha256 == hashlib.sha256(csv_bytes).hexdigest()
    assert snapshot.gpkg_sha256 == hashlib.sha256(gpkg_bytes).hexdigest()
    manifest = json.loads((destination / "snapshot.json").read_text(encoding="utf-8"))
    assert manifest["assets"]["katalog.gpkg"]["id"] == 2
    assert manifest["assets"]["best-measurements.csv"]["id"] == 1
    assert load_snapshot(destination) == snapshot
    assert read_catalogue(snapshot).objects["MLZ-0068"].cave_id == "C-0648"


@pytest.mark.parametrize("asset", ["best-measurements.csv", "katalog.gpkg"])
def test_snapshot_rejects_hash_mismatch(snapshot_directory, asset):
    path = snapshot_directory / asset
    modified = path.read_bytes() + b"changed"
    path.write_bytes(modified)

    with pytest.raises(ValueError, match=rf"{asset}.*SHA-256"):
        load_snapshot(snapshot_directory)

    assert path.read_bytes() == modified


@pytest.mark.parametrize(
    ("key", "value", "error"),
    [
        ("tag", " ", "non-empty repo and tag"),
        ("release_id", True, "positive GitHub ID"),
        ("assets", [], "asset checksums"),
        ("assets", {"best-measurements.csv": {"sha256": "missing-digest"}}, "SHA-256"),
    ],
)
def test_snapshot_rejects_invalid_manifest(snapshot_directory, key, value, error):
    manifest = write_manifest(snapshot_directory)
    manifest[key] = value
    (snapshot_directory / "snapshot.json").write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match=error):
        load_snapshot(snapshot_directory)


@pytest.mark.parametrize("filename", ["snapshot.json", "katalog.gpkg"])
def test_snapshot_rejects_missing_input_without_creating_it(snapshot_directory, filename):
    path = snapshot_directory / filename
    path.unlink()

    with pytest.raises(ValueError, match=filename):
        load_snapshot(snapshot_directory)

    assert not path.exists()


@pytest.mark.parametrize("table", ["caves", "objects"])
def test_catalogue_rejects_missing_tables(snapshot_directory, table):
    update_database(snapshot_directory, f"DROP TABLE {table};")

    with pytest.raises(ValueError, match=table):
        read_catalogue(load_snapshot(snapshot_directory))


@pytest.mark.parametrize(
    ("change", "error"),
    [
        ("UPDATE caves SET system_cave_id = 'C-9999' WHERE cave_id = 'C-0648';", "C-9999"),
        ("UPDATE caves SET system_cave_id = 'C-0648' WHERE cave_id = 'C-0295';", "cycle"),
        ("UPDATE caves SET system_cave_id = cave_id WHERE cave_id = 'C-0648';", "cycle"),
        ("UPDATE objects SET cave_id = 'C-9999' WHERE object_id = 'MLZ-0068';", "C-9999"),
    ],
)
def test_catalogue_rejects_dangling_or_cyclic_system(snapshot_directory, change, error):
    update_database(snapshot_directory, change)

    with pytest.raises(ValueError, match=error):
        read_catalogue(load_snapshot(snapshot_directory))


@pytest.mark.parametrize(
    ("change", "error"),
    [
        ("ALTER TABLE caves RENAME COLUMN fid TO other_id;", "fid"),
        ("ALTER TABLE objects RENAME COLUMN category TO other;", "category"),
        ("UPDATE caves SET cave_id = 'T.X-00.01' WHERE cave_id = 'C-0295';", "T.X-00.01"),
        ("UPDATE caves SET system_cave_id = '' WHERE cave_id = 'C-0648';", "system_cave_id"),
        ("UPDATE objects SET object_id = '' WHERE object_id = 'MLZ-0068';", "object_id"),
        ("UPDATE objects SET cave_id = '' WHERE object_id = 'MLZ-0068';", "cave_id"),
        (
            "CREATE TABLE duplicates AS SELECT * FROM caves; "
            "INSERT INTO duplicates SELECT * FROM caves WHERE cave_id = 'C-0295'; "
            "DROP TABLE caves; ALTER TABLE duplicates RENAME TO caves;",
            "duplicate cave_id C-0295",
        ),
        (
            "CREATE TABLE duplicates AS SELECT * FROM objects; "
            "INSERT INTO duplicates SELECT * FROM objects WHERE object_id = 'MLZ-0068'; "
            "DROP TABLE objects; ALTER TABLE duplicates RENAME TO objects;",
            "duplicate object_id MLZ-0068",
        ),
    ],
)
def test_catalogue_rejects_invalid_columns_or_ids(snapshot_directory, change, error):
    update_database(snapshot_directory, change)

    with pytest.raises(ValueError, match=error):
        read_catalogue(load_snapshot(snapshot_directory))


@pytest.mark.parametrize(
    ("csv_text", "error"),
    [
        ("object_id,cave_id\nMLZ-0068,C-0648\n", "system_cave_id"),
        (
            "object_id,cave_id,cave_id,system_cave_id\nMLZ-0068,C-9999,C-0648,C-0295\n",
            "duplicate column cave_id",
        ),
        ("object_id,cave_id,system_cave_id\nMLZ-0068,C-0648\n", "system_cave_id"),
        ("object_id,cave_id,system_cave_id\nMLZ-0068,C-0295,C-0295\n", "cave_id"),
        ("object_id,cave_id,system_cave_id\nMLZ-0068,C-0648,\n", "system_cave_id"),
        ("object_id,cave_id,system_cave_id\nMLZ-9999,C-0648,C-0295\n", "MLZ-9999"),
        (
            "object_id,cave_id,system_cave_id\nMLZ-0068,C-0648,C-0295\nMLZ-0068,C-0648,C-0295\n",
            "duplicate object_id MLZ-0068",
        ),
    ],
)
def test_catalogue_rejects_inconsistent_best(snapshot_directory, csv_text, error):
    (snapshot_directory / "best-measurements.csv").write_text(csv_text, encoding="utf-8")
    write_manifest(snapshot_directory)

    with pytest.raises(ValueError, match=error):
        read_catalogue(load_snapshot(snapshot_directory))


@pytest.mark.parametrize(
    ("tag", "error"),
    [
        ("missing-gpkg", "katalog.gpkg"),
        ("failed-download", "Cannot download katalog.gpkg"),
        ("wrong-digest", "katalog.gpkg.*SHA-256"),
        ("occupied-directory", "snapshot"),
    ],
)
def test_download_failure_preserves_existing_inputs(tmp_path, monkeypatch, tag, error):
    destination = tmp_path / "snapshot"
    destination.mkdir()
    user_input = destination / "best-measurements.csv"
    if tag == "occupied-directory":
        user_input.write_bytes(b"existing CSV")
    csv_url = "https://example.test/best-measurements.csv"
    gpkg_url = "https://example.test/katalog.gpkg"
    release = {
        "tag_name": tag,
        "id": 123,
        "assets": [{"id": 1, "name": "best-measurements.csv", "browser_download_url": csv_url}],
    }
    if tag != "missing-gpkg":
        release["assets"].append(
            {
                "id": 2,
                "name": "katalog.gpkg",
                "browser_download_url": gpkg_url,
                "digest": f"sha256:{'0' * 64}",
            }
        )

    def urlopen(request, *, timeout):
        if request.full_url.endswith("/releases/latest"):
            return io.BytesIO(json.dumps(release).encode())
        if request.full_url == csv_url:
            return io.BytesIO(b"new CSV")
        if tag == "failed-download":
            raise urllib.error.URLError("network failure")
        return io.BytesIO(b"new GPKG")

    monkeypatch.setattr(urllib.request, "urlopen", urlopen)

    with pytest.raises((ValueError, OSError), match=error):
        download_snapshot("owner/gps", destination)

    if tag == "occupied-directory":
        assert list(destination.iterdir()) == [user_input]
        assert user_input.read_bytes() == b"existing CSV"
    else:
        assert list(destination.iterdir()) == []
