"""Protect model evidence against silent correction and inflated vote counts."""

from __future__ import annotations

import hashlib
from collections import Counter
from pathlib import Path

import pytest

from jktz.czarna_model_readings import FIELDS, read_model

TRANSCRIPTS = (
    Path(__file__).resolve().parents[1] / "Poligony/D_Koscieliska/Organy/Czarna/ODCZYTY_MODELI"
)


@pytest.mark.parametrize("model", ["gemini_flash_3.8", "gemini_pro", "claude_opus_5"])
def test_archived_photographs_remain_traceable_without_duplicate_votes(model):
    path = TRANSCRIPTS / f"{model}.md"
    result = read_model(path)
    rows = result["rows"]
    assert result["model"] == model
    assert result["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert len(rows) == 115
    assert len({(row["from"], row["to"]) for row in rows}) == 78
    assert Counter(row["duplicate_of_line"] is None for row in rows) == {True: 78, False: 37}
    assert len({row["photo"] for row in rows}) == 3
    lines = path.read_text().splitlines()
    first_by_pair = {}
    for row in rows:
        pair = (row["from"], row["to"])
        assert row["raw"] == lines[row["line"] - 1]
        assert row["duplicate_of_line"] == first_by_pair.get(pair)
        first_by_pair.setdefault(pair, row["line"])
        assert tuple(row["raw_fields"]) == FIELDS
        assert tuple(row["values"]) == FIELDS
        assert tuple(row["alternatives"]) == FIELDS
    for aggregate in result["aggregates"]:
        assert aggregate["raw"] == lines[aggregate["line"] - 1]


def test_pro_station_typo_is_evidence_not_silently_repaired():
    rows = read_model(TRANSCRIPTS / "gemini_pro.md")["rows"]
    assert any(row["from"] == "18" and row["to"] == "20" for row in rows)
    assert not any(row["from"] == "19" and row["to"] == "20" for row in rows)


def test_opus_primary_and_alternative_do_not_leak_between_photographs():
    rows = read_model(TRANSCRIPTS / "claude_opus_5.md")["rows"]
    readings = [row for row in rows if (row["from"], row["to"]) == ("74", "75")]
    assert [row["values"]["D"] for row in readings] == [12.0, 12.0]
    assert [row["alternatives"]["D"] for row in readings] == [[17.0], []]
    assert all("D" in row["uncertain_fields"] for row in readings)
    assert readings[1]["duplicate_of_line"] == readings[0]["line"]
    assert readings[0]["raw_fields"]["D"] == "12,00 [? 17,00]"


def test_flash_correction_is_an_alternative_not_a_replacement():
    rows = read_model(TRANSCRIPTS / "gemini_flash_3.8.md")["rows"]
    row = next(row for row in rows if (row["from"], row["to"]) == ("24", "25"))
    assert row["values"]["D"] == 21.1
    assert row["alternatives"]["D"] == [11.1]
    assert "D" in row["uncertain_fields"]
    assert row["raw_fields"]["D"] == r"21,10 \[? skorygowane na 11,10\]"
    first = rows[0]
    assert first["values"]["dh"] == -10.84
    assert first["alternatives"]["dh"] == [-10.74]


def test_comments_do_not_mark_numeric_fields_uncertain():
    rows = read_model(TRANSCRIPTS / "claude_opus_5.md")["rows"]
    row = next(row for row in rows if (row["from"], row["to"]) == ("6", "7"))
    assert "?" in row["raw_extra_fields"][0]
    assert row["uncertain_fields"] == []


@pytest.mark.parametrize(
    ("raw", "value", "alternatives", "uncertain"),
    [
        ("+ 0,5°", 0.5, [], False),
        ("− 0,5", -0.5, [], False),
        (r"\-0,5 \[? +0,5\]", -0.5, [0.5], True),
        ("±0,5", 0.5, [-0.5], True),
        ("+/- 0,5", 0.5, [-0.5], True),
        ("-/+ 0,5", -0.5, [0.5], True),
        ("5,2 / 5,7", 5.2, [5.7], True),
        ("5,2 [? 5,7 / 6,1]", 5.2, [5.7, 6.1], True),
        ("5,2 [? możliwe: 5,7]", 5.2, [5.7], True),
        ("5,2 [? odczyt z 2 zdjęć]", 5.2, [], True),
        ("5,2 (odczyt wiersza 25)", 5.2, [], False),
        ("nieczytelne (wiersz 25)", None, [], True),
        ("[? 5,2]", None, [5.2], True),
        ("—", None, [], False),
        ("--", None, [], False),
        ("brak", None, [], False),
        ("", None, [], False),
    ],
)
def test_field_formats_preserve_only_explicit_readings(
    tmp_path, raw, value, alternatives, uncertain
):
    path = tmp_path / "reading.md"
    path.write_text(f"| 0 | 1 | 90 | {raw} | 10 | 9 | -1 |\n")
    row = read_model(path)["rows"][0]
    assert row["raw_fields"]["V"] == raw
    assert row["values"]["V"] == value
    assert row["alternatives"]["V"] == alternatives
    assert ("V" in row["uncertain_fields"]) is uncertain


def test_missing_azimuth_is_not_zero_and_aggregate_rows_are_not_shots():
    result = read_model(TRANSCRIPTS / "claude_opus_5.md")
    row = next(row for row in result["rows"] if (row["from"], row["to"]) == ("57", "58"))
    assert row["values"]["A"] is None
    assert row["values"]["V"] == -90
    assert row["alternatives"]["A"] == []
    assert any("+74,23" in item["raw"] for item in result["aggregates"])
    assert any("+16,42" in item["raw"] for item in result["aggregates"])
    assert any("−61,95" in item["raw"] for item in result["aggregates"])


def test_pro_aggregate_continuation_and_cumulative_margin_are_retained():
    result = read_model(TRANSCRIPTS / "gemini_pro.md")
    assert any("- 16,42" in item["raw"] for item in result["aggregates"])
    assert any("52(+57,42)" in item["raw"] for item in result["aggregates"])


def test_short_numeric_row_does_not_disappear(tmp_path):
    path = tmp_path / "reading.md"
    path.write_text("| 0 | 1 | 90 | -2 | 10 |\n")
    row = read_model(path)["rows"][0]
    assert row["values"] == {"D": 10.0, "A": 90.0, "V": -2.0, "Lh": None, "dh": None}
