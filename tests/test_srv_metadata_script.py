from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_srv_metadata():
    script = Path(__file__).resolve().parents[1] / "scripts" / "srv_metadata.py"
    spec = importlib.util.spec_from_file_location("srv_metadata", script)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


srv_metadata = _load_srv_metadata()


def test_replace_or_insert_metadata_preserves_body() -> None:
    original = "#prefix Cave\n#date 2004-06-19\n0\t1\t1.0\t90\t0\n"
    metadata = srv_metadata.default_metadata(
        cave_id="T.X-00.00",
        cave_name="Cave",
        survey_id="CAVE",
        survey_name="Cave",
        source_refs=["_RAW/01"],
        update_date="2026-06-05",
    )

    updated = srv_metadata.replace_or_insert_metadata(original, metadata)

    assert updated.startswith("#[\n")
    assert updated.endswith("#date 2004-06-19\n0\t1\t1.0\t90\t0\n")
    assert srv_metadata.replace_or_insert_metadata(updated, metadata) == updated


def test_append_processing_is_idempotent() -> None:
    metadata = srv_metadata.default_metadata(
        cave_id="T.X-00.00",
        cave_name="Cave",
        survey_id="CAVE",
        survey_name="Cave",
        source_refs=["_RAW/01"],
        update_date="2026-06-05",
    )

    updated = srv_metadata.append_processing(metadata, "usredniono pomiary przod/tyl")
    updated_again = srv_metadata.append_processing(updated, "usredniono pomiary przod/tyl")

    assert updated.repeated["PROCESSING"].count("usredniono pomiary przod/tyl") == 1
    assert updated_again == updated


def test_canonical_raw_readme_for_missing_materials() -> None:
    text = srv_metadata.canonical_raw_readme(
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

    hashes = srv_metadata.material_hashes(tmp_path)

    assert len(hashes) == 1
    assert hashes[0].path.as_posix().endswith("source.srv")
