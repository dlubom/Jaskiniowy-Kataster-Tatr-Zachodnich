from __future__ import annotations

from pathlib import Path

from jktz.validation._utils import active_lines, is_raw_path, non_raw_paths


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


def test_active_lines_ignore_metadata_and_comments_and_keep_line_numbers():
    text = (
        '#[\nCAVE_NAME "Test"\n#]\n\n; comment\n'
        " #[ ignored\n#]\n  #prefix Cave ; annotation\n"
        "#[ disabled\n0 1 1,5 90 0\n; #]\n#]\n0 1 1.5 90 0\n"
    )

    assert list(active_lines(text)) == [(8, "#prefix Cave"), (13, "0 1 1.5 90 0")]


def test_nested_blocks_only_end_after_matching_outer_close():
    text = "#[ outer\n#[ inner\n#prefix HiddenInner\n#]\n#prefix HiddenOuter\n#]\n#prefix Active\n"

    assert list(active_lines(text)) == [(7, "#prefix Active")]


def test_comment_close_must_start_its_own_line():
    text = "#[ opening text #]\n#prefix Hidden\n#]\n#prefix Active\n"

    assert list(active_lines(text)) == [(4, "#prefix Active")]
