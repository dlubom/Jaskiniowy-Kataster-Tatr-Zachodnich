from __future__ import annotations

from pathlib import Path

import pytest

from jktz.metadata_contract import (
    MetadataError,
    RawReadme,
    SrvMetadata,
    format_srv_metadata,
    has_dated_or_declared_active_shots,
    is_active_srv_path,
    parse_raw_readme,
    parse_srv_metadata,
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
        },
        repeated={
            "SOURCE_REF": ["_RAW/01"],
            "TEAM": ["J. Nowak"],
            "INSTRUMENT": ["nieznane"],
            "SURVEY_DATE": ["2004-06-19"],
            "SURVEY_GRADE": ["BCRA:5D"],
            "PROCESSING": ["konwersja z arkusza"],
        },
        body="",
    )

    text = format_srv_metadata(metadata)

    assert text.startswith("#[\n")
    assert 'CAVE_ID         "T.D-04.01"' in text
    assert 'SOURCE_REF      "_RAW/01"' in text
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


RAW_README = """# Cave - source package

- **Status materiału:** dostępny
- **Pochodzenie danych:** J. Nowak
- **Autorzy pomiarów:** J. Nowak
- **Daty pomiarów:** 2004-06-19
- **Data pozyskania:** 2013-11-26
- **Dodał do _RAW:** Dariusz Lubomski
- **Licencja źródłowa:** nieznane
- **Kompletność:** pełny pomiar

## Zawartość

- `source.xlsx` - arkusz z pomiarami
"""


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


def test_parse_raw_readme_contract() -> None:
    parsed = parse_raw_readme(Path("_RAW/01/README.md"), RAW_README)

    assert isinstance(parsed, RawReadme)
    assert parsed.fields["Status materiału"] == "dostępny"
    assert parsed.content_items == ["`source.xlsx` - arkusz z pomiarami"]


def test_parse_raw_readme_rejects_missing_field() -> None:
    with pytest.raises(MetadataError, match="Licencja źródłowa"):
        parse_raw_readme(
            Path("_RAW/01/README.md"),
            RAW_README.replace("- **Licencja źródłowa:** nieznane\n", ""),
        )


def test_parse_raw_readme_rejects_duplicate_field() -> None:
    text = RAW_README.replace(
        "- **Status materiału:** dostępny\n",
        "- **Status materiału:** dostępny\n- **Status materiału:** częściowy\n",
    )

    with pytest.raises(MetadataError, match="duplicate RAW field Status materiału"):
        parse_raw_readme(Path("_RAW/01/README.md"), text)


def test_parse_raw_readme_contents_stop_at_next_heading() -> None:
    text = RAW_README.replace(
        "## Zawartość\n\n- `source.xlsx` - arkusz z pomiarami\n",
        "## Zawartość\n\n## Uwagi\n\n- `source.xlsx` - arkusz z pomiarami\n",
    )

    with pytest.raises(MetadataError, match="missing ## Zawartość items"):
        parse_raw_readme(Path("_RAW/01/README.md"), text)


def test_active_srv_scope() -> None:
    assert is_active_srv_path(Path("Poligony/Cave/CAVE.SRV"))
    assert not is_active_srv_path(Path("Poligony/OTWORY.SRV"))
    assert not is_active_srv_path(Path("Poligony/Cave/_RAW/01/source.SRV"))
    assert not is_active_srv_path(Path("Powierzchnia/Teren_10x10/POZIOM.SRV"))


def test_active_shot_scanner_requires_date_or_decl_for_nonzero_shots() -> None:
    assert has_dated_or_declared_active_shots("#date 2004-06-19\n0\t1\t1.0\t90\t0\n")
    assert has_dated_or_declared_active_shots("#Units DECL=0.819D\n0\t1\t1.0\t90\t0\n")
    assert has_dated_or_declared_active_shots("0\t1\t0\t0\t0\n")
    assert has_dated_or_declared_active_shots(";0\t1\t1.0\t90\t0\n")
    assert not has_dated_or_declared_active_shots("0\t1\t1.0\t90\t0\n")


@pytest.mark.parametrize("order", ["DAV", "DVA"])
def test_active_shot_scanner_reads_distance_from_third_token_for_dav_and_dva(order: str) -> None:
    assert not has_dated_or_declared_active_shots(
        f"#units meters order={order}\n0\t1\t1.0\t90\t0\n"
    )
    assert has_dated_or_declared_active_shots(
        f"#units meters order={order}\n#date 2004-06-19\n0\t1\t1.0\t90\t0\n"
    )


def test_active_shot_scanner_reads_distance_from_fifth_token_for_avd() -> None:
    text = "#units meters order=AVD\n0\t1\t0\t0\t1.0\n"

    assert not has_dated_or_declared_active_shots(text)
    assert has_dated_or_declared_active_shots("#date 2004-06-19\n" + text)


def test_active_shot_scanner_keeps_zero_shots_allowed_for_unit_orders() -> None:
    assert has_dated_or_declared_active_shots("#units meters order=DAV\n0\t1\t0\t90\t0\n")
    assert has_dated_or_declared_active_shots("#units meters order=AVD\n0\t1\t90\t0\t0\n")


def test_active_shot_scanner_ignores_rectangular_delta_rows() -> None:
    assert has_dated_or_declared_active_shots("#units meters rect Order=NEU\n0\t1\t1.0\t2.0\t3.0\n")


def test_active_shot_scanner_preserves_order_across_units_without_order() -> None:
    assert not has_dated_or_declared_active_shots(
        "#units meters order=AVD\n#units A=D V=D\n0\t1\t0\t0\t1.0\n"
    )
