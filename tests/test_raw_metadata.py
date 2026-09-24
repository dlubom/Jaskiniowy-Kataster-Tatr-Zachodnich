from __future__ import annotations

from pathlib import Path

import pytest

from jktz.metadata.errors import MetadataError
from jktz.metadata.raw import (
    MaterialHash,
    RawMetadata,
    format_raw_metadata,
    material_hashes,
    parse_raw_metadata,
)

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


def test_parse_raw_metadata_contract() -> None:
    parsed = parse_raw_metadata(Path("_RAW/01/README.md"), RAW_README)

    assert isinstance(parsed, RawMetadata)
    assert parsed.fields["Status materiału"] == "dostępny"
    assert parsed.content_items == ["`source.xlsx` - arkusz z pomiarami"]


def test_parse_raw_metadata_rejects_missing_field() -> None:
    with pytest.raises(MetadataError) as exc_info:
        parse_raw_metadata(
            Path("_RAW/01/README.md"),
            RAW_README.replace("- **Licencja źródłowa:** nieznane\n", ""),
        )

    assert str(exc_info.value) == ("_RAW/01/README.md missing RAW field(s): 'Licencja źródłowa'")


def test_parse_raw_metadata_rejects_duplicate_field() -> None:
    text = RAW_README.replace(
        "- **Status materiału:** dostępny\n",
        "- **Status materiału:** dostępny\n- **Status materiału:** częściowy\n",
    )

    with pytest.raises(MetadataError) as exc_info:
        parse_raw_metadata(Path("_RAW/01/README.md"), text)

    assert str(exc_info.value) == ("_RAW/01/README.md duplicate RAW field 'Status materiału'")


def test_parse_raw_metadata_rejects_invalid_status() -> None:
    text = RAW_README.replace(
        "- **Status materiału:** dostępny\n",
        "- **Status materiału:** uszkodzony\n",
    )

    with pytest.raises(MetadataError) as exc_info:
        parse_raw_metadata(Path("_RAW/01/README.md"), text)

    assert str(exc_info.value) == (
        "_RAW/01/README.md invalid value for RAW field 'Status materiału': 'uszkodzony'"
    )


def test_parse_raw_metadata_contents_stop_at_next_heading() -> None:
    text = RAW_README.replace(
        "## Zawartość\n\n- `source.xlsx` - arkusz z pomiarami\n",
        "## Zawartość\n\n"
        "- `source.xlsx` - arkusz z pomiarami\n\n"
        "## Uwagi\n\n"
        "- `notes.txt` - ten wpis nie należy do inwentarza\n",
    )

    parsed = parse_raw_metadata(Path("_RAW/01/README.md"), text)

    assert parsed.content_items == ["`source.xlsx` - arkusz z pomiarami"]


def test_parse_raw_metadata_rejects_empty_contents() -> None:
    text = RAW_README.replace("- `source.xlsx` - arkusz z pomiarami\n", "")

    with pytest.raises(MetadataError) as exc_info:
        parse_raw_metadata(Path("_RAW/01/README.md"), text)

    assert str(exc_info.value) == (
        "_RAW/01/README.md section '## Zawartość' must contain at least one item"
    )


def test_format_raw_metadata_for_missing_materials() -> None:
    text = format_raw_metadata(
        title="Cave - missing source package",
        status="niedostępny",
        origin="nieznane",
        authors="nieznane",
        dates="nieznane",
        acquired="nieznane",
        added_by="nieznane",
        license_value="nieznane",
        completeness="brak materiałów źródłowych",
        contents=["Brak materiałów źródłowych."],
    )

    assert "- **Status materiału:** niedostępny" in text
    assert "## Zawartość" in text
    assert "- Brak materiałów źródłowych." in text


def test_material_hashes_skip_readmes(tmp_path: Path) -> None:
    raw = tmp_path / "_RAW" / "01"
    raw.mkdir(parents=True)
    (raw / "README.md").write_text("metadata")
    (raw / "source.srv").write_text("raw")

    hashes = material_hashes(tmp_path)

    assert len(hashes) == 1
    assert hashes[0].path.as_posix().endswith("source.srv")


@pytest.mark.parametrize("heading", ["## Zawartość", "## Uwagi"])
def test_only_first_inventory_section_can_supply_contents_or_metadata(heading):
    text = RAW_README + (
        f"\n{heading}\n"
        "- **Status materiału:** niedostępny\n"
        "- `other.xlsx` - an example in explanatory notes, not a source file\n"
        "## Zawartość\n"
        "- `another.xlsx` - a later inventory heading must not reopen the list\n"
    )

    parsed = parse_raw_metadata(Path("_RAW/01/README.md"), text)

    assert parsed.fields["Status materiału"] == "dostępny"
    assert parsed.content_items == ["`source.xlsx` - arkusz z pomiarami"]


@pytest.mark.parametrize("status", ["dostępny", "częściowy"])
def test_available_or_partial_package_requires_an_actual_source_inventory(status):
    text = RAW_README.replace("dostępny", status).replace(
        "`source.xlsx` - arkusz z pomiarami", "Brak materiałów źródłowych."
    )

    with pytest.raises(MetadataError, match="available package cannot have empty source inventory"):
        parse_raw_metadata(Path("_RAW/01/README.md"), text)


def test_unavailable_package_accepts_explicit_missing_materials_inventory():
    text = RAW_README.replace("dostępny", "niedostępny").replace(
        "`source.xlsx` - arkusz z pomiarami", "Brak materiałów źródłowych."
    )

    parsed = parse_raw_metadata(Path("_RAW/01/README.md"), text)

    assert parsed.fields["Status materiału"] == "niedostępny"
    assert parsed.content_items == ["Brak materiałów źródłowych."]


def test_missing_field_diagnostic_lists_every_missing_field():
    text = RAW_README.replace("- **Autorzy pomiarów:** J. Nowak\n", "").replace(
        "- **Daty pomiarów:** 2004-06-19\n", ""
    )

    with pytest.raises(MetadataError) as error:
        parse_raw_metadata(Path("_RAW/01/README.md"), text)

    assert str(error.value) == (
        "_RAW/01/README.md missing RAW field(s): 'Autorzy pomiarów', 'Daty pomiarów'"
    )


def test_formatter_produces_canonical_readme_with_all_provenance_fields():
    text = format_raw_metadata(
        title="Cave - source package",
        status="dostępny",
        origin="J. Nowak",
        authors="J. Nowak",
        dates="2004-06-19",
        acquired="2013-11-26",
        added_by="Dariusz Lubomski",
        license_value="nieznane",
        completeness="pełny pomiar",
        contents=["`source.xlsx` - arkusz z pomiarami"],
    )

    assert text == RAW_README
    parsed = parse_raw_metadata(Path("_RAW/01/README.md"), text)
    assert parsed.fields == {
        "Status materiału": "dostępny",
        "Pochodzenie danych": "J. Nowak",
        "Autorzy pomiarów": "J. Nowak",
        "Daty pomiarów": "2004-06-19",
        "Data pozyskania": "2013-11-26",
        "Dodał do _RAW": "Dariusz Lubomski",
        "Licencja źródłowa": "nieznane",
        "Kompletność": "pełny pomiar",
    }


def test_material_hashes_use_source_bytes_and_skip_unrelated_files(tmp_path):
    raw = tmp_path / "_RAW" / "01"
    raw.mkdir(parents=True)
    # This sorts before _RAW; skipping an unrelated file must not stop traversal.
    (tmp_path / "0.SRV").write_bytes(b"active survey")
    (raw / "README.md").write_text("package metadata")
    (raw / "b.dat").write_bytes(b"")
    (raw / "a.dat").write_bytes(b"abc")

    assert material_hashes(tmp_path) == [
        MaterialHash(
            path=raw / "a.dat",
            sha256="ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
        ),
        MaterialHash(
            path=raw / "b.dat",
            sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        ),
    ]
