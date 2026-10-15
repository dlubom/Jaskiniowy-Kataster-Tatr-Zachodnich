"""JKTZ consumes the published executable; it never decodes TOP bytes itself."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import zipfile
from pathlib import Path

import pytest

EVIDENCE = Path(__file__).parent / "fixtures/pockettopo"
REPOSITORY = Path(__file__).parents[1]
CASES = sorted((EVIDENCE / "p01/cases").iterdir())


@pytest.fixture
def exporter() -> str:
    executable = os.environ.get("POCKETTOPO_EXPORTER") or shutil.which("pockettopo-exporter")
    if executable is None:
        if os.environ.get("JKTZ_REQUIRE_POCKETTOPO_EXPORTER") == "1":
            pytest.fail("pockettopo-exporter executable is required")
        pytest.skip("Install the published pockettopo-exporter executable")
    return executable


def run(exporter: str, *arguments: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [exporter, *(str(argument) for argument in arguments)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )


def test_frozen_fixture_manifest_is_complete_and_matches_hashes() -> None:
    entries = [
        line.split("  ", 1)
        for line in (EVIDENCE / "SHA256SUMS").read_text(encoding="ascii").splitlines()
    ]
    expected = {name: digest for digest, name in entries}
    assert len(expected) == len(entries)
    actual = {
        path.relative_to(EVIDENCE).as_posix()
        for path in EVIDENCE.rglob("*")
        if path.is_file() and path.name not in {"README.md", "SHA256SUMS"}
    }
    assert actual == set(expected)
    for name, digest in expected.items():
        assert hashlib.sha256((EVIDENCE / name).read_bytes()).hexdigest() == digest, name


@pytest.mark.parametrize("case", CASES, ids=lambda path: path.name)
def test_binary_preserves_native_fixture_rows_and_accounts_for_drawings(exporter, case):
    source = next(case.glob("*.top"))
    before = source.read_bytes()
    expected = json.loads((case / "expected.json").read_text(encoding="utf-8"))
    inspected = run(exporter, "inspect", source, "--json")
    processed = run(exporter, "process", source, "--json")
    assert inspected.returncode == processed.returncode == 0, inspected.stderr + processed.stderr
    inspection, processing = json.loads(inspected.stdout), json.loads(processed.stdout)
    assert inspection["source"]["sha256"] == expected["source_SHA256"]
    assert processing["source"] == inspection["source"]
    assert inspection["complete"] and inspection["supported"]
    assert inspection["accounting"]["unparsed_bytes"] == 0
    assert len(processing["rows"]) == len(expected["source"]["shots"])
    for row, shot in zip(processing["rows"], expected["source"]["shots"]):
        for end in ("from", "to"):
            identity = shot[end + "_id"]
            assert row[end]["raw"] == identity["raw"] & 0xFFFFFFFF
            assert row[end]["display"] == (identity["text"] or "")
        for field in ("distance_mm", "azimuth", "inclination", "roll"):
            original = field if field == "distance_mm" else field + "_raw"
            assert row[field + "_raw"] == shot[original]
        assert row["flags_raw"] == shot["flags"]
        assert row["trip_index_raw"] == shot["trip_index"]
        assert row["comment"] == (shot["comment"] or "")
    for view, original in (("plan", "outline"), ("side", "sideview")):
        assert inspection[view]["elements"] == len(expected["source"][original]["elements"])
    members = [member["row_index"] for group in processing["groups"] for member in group["members"]]
    assert sorted(members) == list(range(len(processing["rows"])))
    assert source.read_bytes() == before


def test_text_report_keeps_trip_ticks_and_auto_declination(exporter, tmp_path):
    case = EVIDENCE / "p01/cases/api-trips-ids"
    source = next(case.glob("*.top"))
    expected = json.loads((case / "expected.json").read_text(encoding="utf-8"))
    destination = tmp_path / "text"
    result = run(exporter, "export", source, "--format", "text", "--output", destination)
    assert result.returncode == 0, result.stderr
    report = json.loads((destination / "report.json").read_text(encoding="utf-8"))
    trips = [record for record in report["records"] if record["kind"] == "trip"]
    assert [trip["raw"] for trip in trips] == [
        {"ticks": trip["ticks"], "declination_raw": trip["declination_raw"]}
        for trip in expected["source"]["trips"]
    ]
    text = (destination / "survey.txt").read_bytes()
    assert report["source_sha256"] == expected["source_SHA256"]
    assert report["text_sha256"] == hashlib.sha256(text).hexdigest()
    assert any(loss["code"] == "trip_date_and_declination" for loss in report["losses"])


@pytest.mark.parametrize("format", ["srv", "svx"])
def test_measurement_exports_trace_every_repeat_reverse_and_splay(exporter, tmp_path, format):
    source = EVIDENCE / "p01/cases/api-cardinal/api-cardinal.top"
    before = source.read_bytes()
    processed = run(exporter, "process", source, "--json")
    assert processed.returncode == 0, processed.stderr
    processing = json.loads(processed.stdout)
    assert any(len(group["members"]) > 1 for group in processing["groups"])
    assert any(member["reversed"] for group in processing["groups"] for member in group["members"])
    assert any(group["kind"] == "splay" for group in processing["groups"])
    destination = tmp_path / format
    result = run(exporter, "export", source, "--format", format, "--output", destination)
    assert result.returncode == 0, result.stderr
    report = json.loads((destination / "report.json").read_text(encoding="utf-8"))
    assert report["source_sha256"] == hashlib.sha256(before).hexdigest()
    assert [row["index"] for row in report["measurements"]] == list(range(len(processing["rows"])))
    assert (
        report["output_sha256"]
        == hashlib.sha256((destination / ("survey." + format)).read_bytes()).hexdigest()
    )
    assert source.read_bytes() == before


@pytest.mark.parametrize("view", ["plan", "side"])
def test_drawings_are_exported_by_binary_with_source_provenance(exporter, tmp_path, view):
    source = EVIDENCE / "p01/cases/api-drawings/api-drawings.top"
    before = source.read_bytes()
    destination = tmp_path / view
    result = run(
        exporter, "export", source, "--format", "dxf", "--output", destination, "--view", view
    )
    assert result.returncode == 0, result.stderr
    report = json.loads((destination / "report.json").read_text(encoding="utf-8"))
    assert report["source_sha256"] == hashlib.sha256(before).hexdigest()
    assert b"POLYLINE" in (destination / "survey.dxf").read_bytes()
    assert source.read_bytes() == before


def test_binary_rejects_truncation_and_existing_destination(exporter, tmp_path):
    source = tmp_path / "truncated.top"
    source.write_bytes(b"Top\x03")
    destination = tmp_path / "result"
    inspected = run(exporter, "inspect", source, "--json")
    assert inspected.returncode == 1
    assert not json.loads(inspected.stdout)["complete"]
    failed = run(exporter, "export", source, "--format", "text", "--output", destination)
    assert failed.returncode != 0 and not destination.exists()
    assert source.read_bytes() == b"Top\x03"
    source = EVIDENCE / "p01/cases/api-cardinal/api-cardinal.top"
    destination.mkdir()
    marker = destination / "keep.txt"
    marker.write_bytes(b"keep")
    refused = run(exporter, "export", source, "--format", "text", "--output", destination)
    assert refused.returncode != 0
    assert list(destination.iterdir()) == [marker]
    assert marker.read_bytes() == b"keep"


def test_archival_reserved_id_remains_anonymous_in_real_source(exporter, tmp_path):
    archive = REPOSITORY / (
        "Poligony/D_Malej_Laki/Przechod-Kotliny/Syst_W_Snieznej/sniezna/"
        "_RAW/03/W.Sniezna-partie_przemkowe.zip"
    )
    before = hashlib.sha256(archive.read_bytes()).hexdigest()
    with zipfile.ZipFile(archive) as package:
        original = package.read("Przemko2/przemko2.top")
    source = tmp_path / "przemko2.top"
    source.write_bytes(original)
    result = run(exporter, "process", source, "--json")
    assert result.returncode == 0, result.stderr
    row = json.loads(result.stdout)["rows"][112]
    assert row["to"] == {"raw": 0x800FFFFF, "native": -2, "display": ""}
    assert source.read_bytes() == original
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == before
