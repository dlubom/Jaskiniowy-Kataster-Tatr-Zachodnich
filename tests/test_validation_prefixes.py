from __future__ import annotations

from pathlib import Path

import pytest

from jktz.reporting import CheckFailed
from jktz.validation import prefixes


def test_passes_with_dot_free_prefix(tmp_path: Path) -> None:
    (tmp_path / "OK.SRV").write_text("#prefix Marmurowa\n#prefix2 WielkaSniezna\n")
    prefixes.check(root=tmp_path)


def test_fails_on_prefix_with_dot(tmp_path: Path) -> None:
    (tmp_path / "BAD.SRV").write_text("#prefix Cave.Section\n")
    with pytest.raises(CheckFailed, match=r"#prefix directives must not contain '\.'"):
        prefixes.check(root=tmp_path)


def test_fails_on_prefix2_with_dot(tmp_path: Path) -> None:
    (tmp_path / "BAD.SRV").write_text("#prefix2 System.Sub\n")
    with pytest.raises(CheckFailed):
        prefixes.check(root=tmp_path)


def test_ignores_raw_subtree(tmp_path: Path) -> None:
    raw = tmp_path / "Cave" / "_RAW"
    raw.mkdir(parents=True)
    (raw / "ORIG.SRV").write_text("#prefix Original.With.Dots\n")
    prefixes.check(root=tmp_path)


@pytest.mark.parametrize("directive", ["#PREFIX", " #Prefix1", "\t#PREFIX2", "#Prefix3"])
def test_rejects_dots_in_case_insensitive_indented_prefix_directives(tmp_path, directive):
    (tmp_path / "BAD.SRV").write_text(f"{directive} Cave.Section\n")

    with pytest.raises(CheckFailed, match="#prefix directives"):
        prefixes.check(root=tmp_path)


def test_comment_punctuation_does_not_make_a_prefix_invalid(tmp_path):
    (tmp_path / "OK.SRV").write_text("#prefix Cave ; Cave name.\n#prefix2 ; reset prefix.\n")

    prefixes.check(root=tmp_path)


def test_ignores_prefix_inside_block_comment_but_checks_after_block(tmp_path):
    path = tmp_path / "CAVE.SRV"
    text = "#[\n#prefix Cave.Section\n#]\n"
    path.write_text(text + "#prefix Cave\n")
    prefixes.check(root=tmp_path)

    path.write_text(text + "#prefix Cave.Section\n")
    with pytest.raises(CheckFailed, match=r"CAVE.SRV:4"):
        prefixes.check(root=tmp_path)
