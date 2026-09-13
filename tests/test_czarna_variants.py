from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import pytest

from jktz.cli import czarna_warianty
from jktz.czarna_variants import (
    Shot,
    SurveyContractError,
    analyze_survey,
    parse_survey,
    shot_vector,
)
from jktz.metadata.errors import MetadataError
from jktz.metadata.srv import default_metadata, format_srv_metadata


@pytest.fixture
def survey_text() -> str:
    metadata = default_metadata(
        cave_id="T.E-09.12",
        cave_name="Czarna",
        survey_id="TEST",
        survey_name="Synthetic sensitivity fixture",
        source_refs=["_RAW/02"],
        update_date="2026-09-12",
    )
    special = {
        29: "13.80 90 0",
        39: "10 25 0",
        49: "5 68 60",
        57: "10 -- -90",
        71: "20 0 -1",
    }
    lines = [
        "#prefix2 Czarna",
        "#prefix CiagSkany",
        "#units meters order=DAV",
        "#units A=D V=D DECL=0",
    ]
    lines.extend(f"{i} {i + 1} {special.get(i, '1 0 0')}" for i in range(76))
    lines.extend(["6 a 100 0 0", "a b 200 90 0"])
    return format_srv_metadata(metadata) + "\n".join(lines) + "\n"


@pytest.mark.parametrize(
    ("shot", "expected"),
    [
        (Shot(5, 0, 0), (0, 5, 0)),
        (Shot(5, 90, 0), (5, 0, 0)),
        (Shot(5, 180, 0), (0, -5, 0)),
        (Shot(5, 270, 0), (-5, 0, 0)),
        (Shot(5 * math.sqrt(2), 90, 45), (5, 0, 5)),
        (Shot(10, 180, -30), (0, -5 * math.sqrt(3), -5)),
        (Shot(7, None, 90), (0, 0, 7)),
        (Shot(7, None, -90), (0, 0, -7)),
    ],
)
def test_vector_uses_cave_compass_orientation_and_signed_inclination(shot, expected) -> None:
    assert shot_vector(shot) == pytest.approx(expected, abs=1e-12)


def test_variant_effects_are_local_and_branch_is_not_the_endpoint(tmp_path, survey_text) -> None:
    source = tmp_path / "survey.SRV"
    source.write_text(survey_text)
    report = analyze_survey(source)
    variants = {item["id"]: item for item in report["variants"]}
    assert len(variants) == 16
    assert report["input"]["sha256"] == hashlib.sha256(source.read_bytes()).hexdigest()
    assert report["baseline"]["main_length_m"] == pytest.approx(129.8)
    assert variants["1000"]["delta_m"] == pytest.approx({"E": -0.2, "N": 0, "Z": 0})
    assert variants["1000"]["main_length_m"] == pytest.approx(129.6)
    # A 50-degree rotation of a horizontal 10 m leg has this chord length.
    assert variants["0100"]["delta_3d_m"] == pytest.approx(20 * math.sin(math.radians(25)))
    # Here the 60-degree inclined 5 m leg has a 2.5 m horizontal projection.
    assert variants["0010"]["delta_horizontal_m"] == pytest.approx(5 * math.sin(math.radians(10)))
    assert variants["0010"]["delta_m"]["Z"] == 0
    assert variants["0001"]["delta_m"] == pytest.approx(
        {"E": 0, "N": 0, "Z": 40 * math.sin(math.radians(1))}
    )
    assert len(report["single_alternative_effects"]) == 4
    for axis in ("E", "N", "Z"):
        assert variants["1111"]["delta_m"][axis] == pytest.approx(
            sum(item["delta_m"][axis] for item in report["single_alternative_effects"])
        )
    farthest = report["farthest_pair"]
    assert farthest["delta_3d_m"] >= max(item["delta_3d_m"] for item in variants.values())
    assert farthest["from_variant"] != farthest["to_variant"]
    # Moving the disconnected end of the branch must not move station 76.
    source.write_text(survey_text.replace("a b 200 90 0", "a b 900 180 30"))
    changed = analyze_survey(source)
    assert changed["variants"] == report["variants"]
    assert changed["input"]["sha256"] != report["input"]["sha256"]


@pytest.mark.parametrize(
    ("before", "after", "message"),
    [
        ("#prefix2 Czarna", "#prefix2 Other", "directive"),
        ("#prefix CiagSkany", "#prefix Borowiec", "directive"),
        ("meters order=DAV", "feet order=DAV", "directive"),
        ("order=DAV", "order=AVD", "directive"),
        ("A=D V=D DECL=0", "A=G V=D DECL=0", "directive"),
        ("A=D V=D DECL=0", "A=D V=G DECL=0", "directive"),
        ("DECL=0", "DECL=1", "directive"),
        ("#prefix CiagSkany\n", "", "incomplete"),
        ("0 1 1 0 0", "#date 1981-01-01\n0 1 1 0 0", "directive"),
        ("0 1 1 0 0", "#fix 0 0 0 0\n0 1 1 0 0", "directive"),
        ("0 1 1 0 0", "0 1 1 0 0\n#units A=D V=D DECL=0", "directive"),
        ("0 1 1 0 0", "0 1 1 0 0 extra", "exactly"),
        ("0 1 1 0 0", "0 1 1,5 0 0", "numeric"),
        ("0 1 1 0 0", "0 1 nan 0 0", "numeric"),
        ("0 1 1 0 0", "0 1 inf 0 0", "numeric"),
        ("0 1 1 0 0", "0 1 0 0 0", "distance"),
        ("0 1 1 0 0", "0 1 -1 0 0", "distance"),
        ("0 1 1 0 0", "0 1 1 360 0", "azimuth"),
        ("0 1 1 0 0", "0 1 1 0 91", "inclination"),
        ("0 1 1 0 0", "0 1 1 -- 0", "vertical"),
        ("0 1 1 0 0", "0 1 1 - 0", "numeric"),
        ("0 1 1 0 0", "0 Other:1 1 0 0", "station pair"),
        ("0 1 1 0 0", "0 - 1 0 0", "station pair"),
        ("0 1 1 0 0", "0 1 1 0 0\n0 1 1 0 0", "repeated"),
        ("0 1 1 0 0\n", "", "78 shots"),
        ("a b 200 90 0\n", "", "78 shots"),
        ("29 30 13.80 90 0", "29 30 13.60 90 0", "baseline changed"),
        ('"T.E-09.12"', '"T.E-00.00"', "CAVE_ID"),
        ('SURVEY_DATE     "nieznane"', 'SURVEY_DATE     "1981-01-01"', "unknown survey date"),
    ],
)
def test_unsupported_inputs_are_rejected(survey_text, before, after, message) -> None:
    assert before in survey_text
    with pytest.raises(SurveyContractError, match=message):
        parse_survey(survey_text.replace(before, after), Path("example.SRV"))


def test_metadata_contract_is_not_bypassed(survey_text) -> None:
    with pytest.raises(MetadataError, match="missing metadata"):
        parse_survey(survey_text.replace('CAVE_NAME       "Czarna"\n', ""), Path("bad.SRV"))


def test_cli_output_and_failure_preserve_source_and_previous_result(tmp_path, survey_text, capsys):
    source = tmp_path / "survey.SRV"
    output = tmp_path / "results" / "variants.json"
    source.write_text(survey_text)
    original_source = source.read_bytes()
    assert czarna_warianty.main(["--input", str(source), "--output", str(output)]) == 0
    original_result = output.read_bytes()
    assert len(json.loads(original_result)["variants"]) == 16
    assert source.read_bytes() == original_source
    assert czarna_warianty.main(["--input", str(source), "--output", str(source)]) == 1
    assert source.read_bytes() == original_source
    source.write_text(survey_text.replace("DECL=0", "DECL=2"))
    assert czarna_warianty.main(["--input", str(source), "--output", str(output)]) == 1
    assert output.read_bytes() == original_result
    assert "ERROR:" in capsys.readouterr().err
