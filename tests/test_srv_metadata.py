from __future__ import annotations

from pathlib import Path

import pytest

from jktz.metadata.errors import MetadataError
from jktz.metadata.srv import (
    SrvMetadata,
    append_processing,
    default_metadata,
    format_srv_metadata,
    is_active_srv_path,
    parse_srv_metadata,
    replace_or_insert_metadata,
    resolve_source_ref,
)

VALID_BLOCK = """#[
CAVE_ID         "T.D-04.01"
CAVE_NAME       "Zbojecka Dziura"
SURVEY_ID       "ZBDZIU"
SURVEY_NAME     "Zbojecka Dziura"
UPDATE_DATE     "2026-06-05"
PROJECT_NAME    "Kataster jaskin tatrzanskich"
COORDINATOR     "Dariusz Lubomski"
COORDINATOR_EMAIL "darek.lubomski@gmail.com"
SOURCE_REF      "_RAW/01"
SOURCE_REF      "../_RAW/02"
LICENSE         "http://creativecommons.org/licenses/by-sa/4.0/"

TEAM            "J. Nowak"
TEAM            "J. Slusarczyk"
INSTRUMENT      "nieznane"
SURVEY_DATE     "2004-06-19"
SURVEY_GRADE    "BCRA:5D"
PROCESSING      "konwersja z arkusza"
#]

#prefix ZbojeckaDziura
0\t1\t13.30\t297\t-19
"""


def test_parse_srv_metadata_with_repeated_fields() -> None:
    parsed = parse_srv_metadata(Path("Poligony/Cave/CAVE.SRV"), VALID_BLOCK)

    assert parsed.single["CAVE_ID"] == "T.D-04.01"
    assert parsed.single["SURVEY_NAME"] == "Zbojecka Dziura"
    assert parsed.single["SURVEY_GRADE"] == "BCRA:5D"
    assert parsed.repeated["SOURCE_REF"] == ["_RAW/01", "../_RAW/02"]
    assert parsed.repeated["TEAM"] == ["J. Nowak", "J. Slusarczyk"]
    assert parsed.body.startswith("#prefix ZbojeckaDziura")


def test_format_srv_metadata_is_canonical_and_parseable() -> None:
    metadata = SrvMetadata(
        single={
            "CAVE_ID": "T.D-04.01",
            "CAVE_NAME": "Zbojecka Dziura",
            "SURVEY_ID": "ZBDZIU",
            "SURVEY_NAME": "Zbojecka Dziura",
            "UPDATE_DATE": "2026-06-05",
            "PROJECT_NAME": "Kataster jaskin tatrzanskich",
            "COORDINATOR": "Dariusz Lubomski",
            "COORDINATOR_EMAIL": "darek.lubomski@gmail.com",
            "LICENSE": "http://creativecommons.org/licenses/by-sa/4.0/",
            "SURVEY_GRADE": "BCRA:5D",
        },
        repeated={
            "SOURCE_REF": ["_RAW/01"],
            "TEAM": ["J. Nowak"],
            "INSTRUMENT": ["nieznane"],
            "SURVEY_DATE": ["2004-06-19"],
            "PROCESSING": ["konwersja z arkusza"],
        },
        body="",
    )

    text = format_srv_metadata(metadata)

    assert text.startswith("#[\n")
    assert 'CAVE_ID         "T.D-04.01"' in text
    assert 'SOURCE_REF      "_RAW/01"' in text
    assert (
        'LICENSE         "http://creativecommons.org/licenses/by-sa/4.0/"\n\n'
        'TEAM            "J. Nowak"'
    ) in text
    assert text.endswith("#]\n\n")
    assert parse_srv_metadata(Path("Poligony/Cave/CAVE.SRV"), text).single["CAVE_ID"] == "T.D-04.01"


def test_rejects_missing_opening_metadata_block() -> None:
    with pytest.raises(MetadataError, match="must start with #\\["):
        parse_srv_metadata(Path("Poligony/Cave/CAVE.SRV"), "#prefix Cave\n")


def test_rejects_unknown_field_inside_block() -> None:
    text = VALID_BLOCK.replace(
        'LICENSE         "http://creativecommons.org/licenses/by-sa/4.0/"',
        'BOGUS           "x"',
    )

    with pytest.raises(MetadataError, match="unknown field BOGUS"):
        parse_srv_metadata(Path("Poligony/Cave/CAVE.SRV"), text)


def test_rejects_duplicate_single_field() -> None:
    text = VALID_BLOCK.replace(
        'CAVE_ID         "T.D-04.01"',
        'CAVE_ID         "T.D-04.01"\nCAVE_ID         "T.D-04.02"',
    )

    with pytest.raises(MetadataError, match="duplicate single field CAVE_ID"):
        parse_srv_metadata(Path("Poligony/Cave/CAVE.SRV"), text)


def test_rejects_duplicate_survey_grade() -> None:
    text = VALID_BLOCK.replace(
        'SURVEY_GRADE    "BCRA:5D"',
        'SURVEY_GRADE    "BCRA:5D"\nSURVEY_GRADE    "BCRA:6D"',
    )

    with pytest.raises(MetadataError, match="duplicate single field SURVEY_GRADE"):
        parse_srv_metadata(Path("Poligony/Cave/CAVE.SRV"), text)


def test_rejects_unknown_structural_field_value() -> None:
    text = VALID_BLOCK.replace('SURVEY_ID       "ZBDZIU"', 'SURVEY_ID       "nieznane"')

    with pytest.raises(MetadataError, match="SURVEY_ID cannot be nieznane"):
        parse_srv_metadata(Path("Poligony/Cave/CAVE.SRV"), text)


def test_rejects_bad_date_and_grade_formats() -> None:
    bad_date = VALID_BLOCK.replace('SURVEY_DATE     "2004-06-19"', 'SURVEY_DATE     "19-06-2004"')
    with pytest.raises(MetadataError, match="SURVEY_DATE"):
        parse_srv_metadata(Path("Poligony/Cave/CAVE.SRV"), bad_date)

    bad_grade = VALID_BLOCK.replace('SURVEY_GRADE    "BCRA:5D"', 'SURVEY_GRADE    "BCRA 5D"')
    with pytest.raises(MetadataError, match="SURVEY_GRADE"):
        parse_srv_metadata(Path("Poligony/Cave/CAVE.SRV"), bad_grade)


@pytest.mark.parametrize("grade", ["BCRA:banana", "BCRA:7D", "BCRA:99"])
def test_rejects_unknown_bcra_grade(grade: str) -> None:
    text = VALID_BLOCK.replace("BCRA:5D", grade)

    with pytest.raises(MetadataError, match="SURVEY_GRADE"):
        parse_srv_metadata(Path("Poligony/Cave/CAVE.SRV"), text)


def test_accepts_named_non_bcra_grade_standard() -> None:
    text = VALID_BLOCK.replace("BCRA:5D", "UIS:2")

    parsed = parse_srv_metadata(Path("Poligony/Cave/CAVE.SRV"), text)

    assert parsed.single["SURVEY_GRADE"] == "UIS:2"


def test_rejects_impossible_full_dates() -> None:
    bad_update_date = VALID_BLOCK.replace(
        'UPDATE_DATE     "2026-06-05"', 'UPDATE_DATE     "2026-02-30"'
    )
    with pytest.raises(MetadataError, match="UPDATE_DATE"):
        parse_srv_metadata(Path("Poligony/Cave/CAVE.SRV"), bad_update_date)

    bad_survey_date = VALID_BLOCK.replace(
        'SURVEY_DATE     "2004-06-19"', 'SURVEY_DATE     "2004-02-30"'
    )
    with pytest.raises(MetadataError, match="SURVEY_DATE"):
        parse_srv_metadata(Path("Poligony/Cave/CAVE.SRV"), bad_survey_date)


@pytest.mark.parametrize("survey_date", ["2004-00", "2004-13", "2004-06/2004-99"])
def test_rejects_impossible_partial_dates(survey_date: str) -> None:
    text = VALID_BLOCK.replace('SURVEY_DATE     "2004-06-19"', f'SURVEY_DATE     "{survey_date}"')

    with pytest.raises(MetadataError, match="SURVEY_DATE"):
        parse_srv_metadata(Path("Poligony/Cave/CAVE.SRV"), text)


def test_parse_srv_metadata_accepts_crlf_block_delimiters() -> None:
    text = VALID_BLOCK.replace("\n", "\r\n")

    parsed = parse_srv_metadata(Path("Poligony/Cave/CAVE.SRV"), text)

    assert parsed.single["CAVE_ID"] == "T.D-04.01"
    assert parsed.body.startswith("#prefix ZbojeckaDziura")


def test_parse_srv_metadata_accepts_closing_block_at_eof() -> None:
    text = VALID_BLOCK.split("#]\n", maxsplit=1)[0] + "#]"

    parsed = parse_srv_metadata(Path("Poligony/Cave/CAVE.SRV"), text)

    assert parsed.single["CAVE_ID"] == "T.D-04.01"
    assert parsed.body == ""


def test_resolve_source_ref_allows_sibling_and_parent_raw(tmp_path: Path) -> None:
    root = tmp_path / "Poligony"
    srv_dir = root / "System" / "Section"
    (srv_dir / "_RAW" / "01").mkdir(parents=True)
    (root / "System" / "_RAW" / "02").mkdir(parents=True)

    assert resolve_source_ref(srv_dir / "A.SRV", "_RAW/01", root) == srv_dir / "_RAW" / "01"
    assert (
        resolve_source_ref(srv_dir / "A.SRV", "../_RAW/02", root) == root / "System" / "_RAW" / "02"
    )


def test_resolve_source_ref_rejects_escape_and_non_raw_suffix(tmp_path: Path) -> None:
    root = tmp_path / "Poligony"
    srv = root / "Cave" / "A.SRV"
    srv.parent.mkdir(parents=True)

    with pytest.raises(MetadataError, match="outside Poligony"):
        resolve_source_ref(srv, "../../outside/_RAW/01", root)

    with pytest.raises(MetadataError, match="must end with _RAW/NN"):
        resolve_source_ref(srv, "sources/01", root)


def test_active_srv_scope() -> None:
    assert is_active_srv_path(Path("Poligony/Cave/CAVE.SRV"))
    assert not is_active_srv_path(Path("Poligony/OTWORY.SRV"))
    assert not is_active_srv_path(Path("Poligony/Cave/_RAW/01/source.SRV"))
    assert not is_active_srv_path(Path("Powierzchnia/Teren_10x10/POZIOM.SRV"))


def test_replace_or_insert_metadata_preserves_body() -> None:
    original = "#prefix Cave\n#date 2004-06-19\n0\t1\t1.0\t90\t0\n"
    metadata = default_metadata(
        cave_id="T.X-00.00",
        cave_name="Cave",
        survey_id="CAVE",
        survey_name="Cave",
        source_refs=["_RAW/01"],
        update_date="2026-06-05",
    )

    updated = replace_or_insert_metadata(original, metadata)

    assert updated.startswith("#[\n")
    assert updated.endswith("#date 2004-06-19\n0\t1\t1.0\t90\t0\n")
    assert replace_or_insert_metadata(updated, metadata) == updated


def test_append_processing_is_idempotent() -> None:
    metadata = default_metadata(
        cave_id="T.X-00.00",
        cave_name="Cave",
        survey_id="CAVE",
        survey_name="Cave",
        source_refs=["_RAW/01"],
        update_date="2026-06-05",
    )

    updated = append_processing(metadata, "usredniono pomiary przod/tyl")
    updated_again = append_processing(updated, "usredniono pomiary przod/tyl")

    assert updated.repeated["PROCESSING"].count("usredniono pomiary przod/tyl") == 1
    assert updated_again == updated
