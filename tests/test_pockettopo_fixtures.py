"""Independent P01 native application inputs, frozen before the P02 parser existed."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from jktz.pockettopo import ParseError, parse_bytes, read_top

EVIDENCE = Path(__file__).resolve().parent / "fixtures/pockettopo"
CASES = sorted((EVIDENCE / "p01/cases").iterdir())
REPEAT_MANIFEST = json.loads((EVIDENCE / "repeat-candidates/manifest.json").read_text())


def test_frozen_fixture_manifest_is_complete_and_matches_hashes() -> None:
    entries = [
        line.split("  ", 1)
        for line in (EVIDENCE / "SHA256SUMS").read_text(encoding="ascii").splitlines()
    ]
    expected = {name: digest for digest, name in entries}
    assert len(expected) == len(entries), "Duplicate fixture path in SHA256SUMS"
    actual = {
        path.relative_to(EVIDENCE).as_posix()
        for path in EVIDENCE.rglob("*")
        if path.is_file() and path.name not in {"README.md", "SHA256SUMS"}
    }
    assert actual == set(expected), "Fixture inventory changed; preserve every regression case"
    for name, digest in expected.items():
        assert hashlib.sha256((EVIDENCE / name).read_bytes()).hexdigest() == digest, name


def assert_record(actual: object, expected: object) -> None:
    """Compare literal oracle leaves, including type, order and empty collections."""
    if isinstance(expected, dict):
        for field, value in expected.items():
            assert_record(getattr(actual, field), value)
    elif isinstance(expected, list):
        assert isinstance(actual, tuple)
        assert len(actual) == len(expected)
        for item, value in zip(actual, expected):
            assert_record(item, value)
    else:
        assert type(actual) is type(expected)
        assert actual == expected


@pytest.mark.parametrize("case", CASES, ids=lambda path: path.name)
def test_every_native_fixture_field_and_vertex(case: Path) -> None:
    expected = json.loads((case / "expected.json").read_text(encoding="utf-8"))
    source = next(case.glob("*.top"))
    before = source.read_bytes()
    assert hashlib.sha256(before).hexdigest() == expected["source_SHA256"]

    parsed = read_top(source)

    fields = dict(expected["source"])
    assert before[:4].hex() == fields.pop("header_hex") == "546f7003"
    assert fields.pop("trailing_hex") == "00000000"
    assert parsed.ending == "zero_trailer"
    assert_record(parsed, fields)
    assert parse_bytes(before) == parsed
    assert source.read_bytes() == before


@pytest.mark.parametrize("case", CASES, ids=lambda path: path.name)
def test_every_truncation_of_native_records_fails_without_modifying_input(case: Path) -> None:
    source = next(case.glob("*.top"))
    before = source.read_bytes()
    schema_end = len(before) - 4
    for end in range(schema_end):
        with pytest.raises(ParseError):
            parse_bytes(before[:end])
    assert parse_bytes(before[:schema_end]).ending == "eof"
    for count in (1, 2, 3):
        with pytest.raises(ParseError):
            parse_bytes(before[: schema_end + count])
    assert source.read_bytes() == before


@pytest.mark.parametrize("entry", REPEAT_MANIFEST, ids=lambda entry: entry["file"])
def test_real_sources_match_separately_audited_records(entry: dict) -> None:
    source = EVIDENCE / "repeat-candidates" / entry["file"]
    before = source.read_bytes()
    expected = json.loads((source.parent / "source-records.json").read_text(encoding="utf-8"))
    assert len(before) == entry["bytes"]
    assert hashlib.sha256(before).hexdigest() == entry["sha256"]
    parsed = read_top(source)

    # This older inspector includes derived float values. Only its raw fields
    # are the P02 oracle; angle calculations belong to P03.
    for trip in expected["trips"]:
        for key in tuple(trip):
            if key not in {"ticks", "declination_raw", "comment"}:
                del trip[key]
    for shot in expected["shots"]:
        for key in ("azimuth_unsigned", "azimuth_degrees", "inclination_degrees", "roll_degrees"):
            shot.pop(key, None)
    assert_record(
        parsed,
        {
            key: expected[key]
            for key in ("trips", "shots", "references", "overview", "outline", "sideview")
        },
    )
    assert parsed.ending == "zero_trailer"
    assert source.read_bytes() == before
