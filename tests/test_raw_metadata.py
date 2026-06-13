from __future__ import annotations

from pathlib import Path

import pytest

from jktz.metadata.errors import MetadataError
from jktz.metadata.raw import (
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
    with pytest.raises(MetadataError, match="Licencja źródłowa"):
        parse_raw_metadata(
            Path("_RAW/01/README.md"),
            RAW_README.replace("- **Licencja źródłowa:** nieznane\n", ""),
        )


def test_parse_raw_metadata_rejects_duplicate_field() -> None:
    text = RAW_README.replace(
        "- **Status materiału:** dostępny\n",
        "- **Status materiału:** dostępny\n- **Status materiału:** częściowy\n",
    )

    with pytest.raises(MetadataError, match="duplicate RAW field Status materiału"):
        parse_raw_metadata(Path("_RAW/01/README.md"), text)


def test_parse_raw_metadata_contents_stop_at_next_heading() -> None:
    text = RAW_README.replace(
        "## Zawartość\n\n- `source.xlsx` - arkusz z pomiarami\n",
        "## Zawartość\n\n## Uwagi\n\n- `source.xlsx` - arkusz z pomiarami\n",
    )

    with pytest.raises(MetadataError, match="missing ## Zawartość items"):
        parse_raw_metadata(Path("_RAW/01/README.md"), text)


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
