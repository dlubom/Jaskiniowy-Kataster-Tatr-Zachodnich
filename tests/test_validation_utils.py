from __future__ import annotations

from pathlib import Path

from jktz.validation._utils import is_raw_path, non_raw_paths


def test_is_raw_path_matches_complete_raw_segment() -> None:
    assert is_raw_path(Path("Poligony/Cave/_RAW/01/SOURCE.SRV"))
    assert not is_raw_path(Path("Poligony/Cave/_RAW_EXPORT/SOURCE.SRV"))


def test_non_raw_paths_excludes_entire_raw_subtree(tmp_path: Path) -> None:
    active = tmp_path / "Cave" / "ACTIVE.SRV"
    source = tmp_path / "Cave" / "_RAW" / "01" / "SOURCE.SRV"
    active.parent.mkdir(parents=True)
    source.parent.mkdir(parents=True)
    active.write_text("")
    source.write_text("")

    assert set(non_raw_paths(tmp_path, "*.SRV")) == {active}
