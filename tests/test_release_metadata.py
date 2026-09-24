from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from jktz.cli.release_metadata import extract_release_notes, main, prepare_release_metadata


@pytest.mark.parametrize("newline", [b"\n", b"\r\n"])
def test_info_version_preserves_encoding_and_newlines(tmp_path: Path, newline: bytes) -> None:
    original = newline.join([b"Title __VERSION__", b"legacy: \xb3\xf3", b""])
    info = tmp_path / "INFO.txt"
    info.write_bytes(original)

    prepare_release_metadata("pr-123-a1b2c3d", tmp_path)

    assert info.read_bytes() == original.replace(b"__VERSION__", b"pr-123-a1b2c3d")


def test_extracts_literal_version_until_next_release_heading() -> None:
    changelog = (
        "# Changelog\n\n## [Unreleased]\n\n## [v1x2x3]\nWrong release\n\n"
        "## [v1.2.3] - 2026-09-24\n\n### Fixed\n- Poprawiono źródła.\n\n"
        "## Other heading\nMore details for this release\n\n"
        "## [v1.2.2]\nNot part of this release\n"
    )

    assert extract_release_notes(changelog, "v1.2.3") == (
        "### Fixed\n- Poprawiono źródła.\n\n## Other heading\nMore details for this release\n"
    )


def test_extracts_final_section_with_crlf_and_no_final_newline() -> None:
    assert extract_release_notes("## [v1]\r\n\r\nLast release", "v1") == "Last release\n"


def test_release_notes_preserve_markdown_indentation_and_line_breaks() -> None:
    changelog = "## [v1]\n\n    indented code\nlast line with a hard break  \n\n## [v0]\nOld\n"

    assert extract_release_notes(changelog, "v1") == (
        "    indented code\nlast line with a hard break  \n"
    )


@pytest.mark.parametrize(
    "changelog",
    [
        "## [v2]\nAnother release\n",
        "## [v1]\n \t\n## [v0]\nEarlier release\n",
        "## [v1]\nFirst\n## [v1]\nDuplicate\n",
    ],
)
def test_invalid_notes_leave_info_and_existing_notes_untouched(
    tmp_path: Path, changelog: str
) -> None:
    info = tmp_path / "INFO.txt"
    info.write_bytes(b"Title __VERSION__\r\n")
    (tmp_path / "CHANGELOG.md").write_text(changelog, encoding="utf-8")
    notes = tmp_path / "release_notes.md"
    notes.write_bytes(b"previous notes\n")

    with pytest.raises(ValueError):
        prepare_release_metadata("v1", tmp_path, notes)

    assert info.read_bytes() == b"Title __VERSION__\r\n"
    assert notes.read_bytes() == b"previous notes\n"


@pytest.mark.parametrize("info", [b"No marker", b"__VERSION__ __VERSION__"])
def test_missing_or_duplicate_info_marker_is_an_error(tmp_path: Path, info: bytes) -> None:
    (tmp_path / "INFO.txt").write_bytes(info)
    with pytest.raises(ValueError, match="exactly one"):
        prepare_release_metadata("v1", tmp_path)
    assert (tmp_path / "INFO.txt").read_bytes() == info


@pytest.mark.parametrize("version", ["", "v1\nVERSION=x", "../v1", "vęrsion", "v1/2", "v1 2"])
def test_invalid_version_is_rejected_before_reading_files(tmp_path: Path, version: str) -> None:
    with pytest.raises(ValueError, match="ASCII version label"):
        prepare_release_metadata(version, tmp_path)


@pytest.mark.parametrize("output", ["INFO.txt", "CHANGELOG.md"])
def test_notes_cannot_overwrite_source_files(tmp_path: Path, output: str) -> None:
    (tmp_path / "INFO.txt").write_bytes(b"__VERSION__")
    (tmp_path / "CHANGELOG.md").write_text("## [v1]\nNotes\n", encoding="utf-8")
    with pytest.raises(ValueError, match="must not overwrite"):
        prepare_release_metadata("v1", tmp_path, tmp_path / output)
    assert (tmp_path / "INFO.txt").read_bytes() == b"__VERSION__"
    assert (tmp_path / "CHANGELOG.md").read_text(encoding="utf-8") == "## [v1]\nNotes\n"


def test_cli_prepares_info_and_notes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "INFO.txt").write_bytes(b"Version: __VERSION__\n")
    (tmp_path / "CHANGELOG.md").write_text("## [v1]\n\nRelease notes\n", encoding="utf-8")
    notes = tmp_path / "release_notes.md"

    assert main(["v1", "--root", str(tmp_path), "--notes", str(notes)]) == 0

    assert (tmp_path / "INFO.txt").read_bytes() == b"Version: v1\n"
    assert notes.read_bytes() == b"Release notes\n"
    assert "Prepared release metadata for v1" in capsys.readouterr().out


def test_cli_reports_missing_input(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["v1", "--root", str(tmp_path)]) == 1
    assert "error:" in capsys.readouterr().err


@pytest.mark.skipif(os.name == "nt" and shutil.which("awk") is None, reason="awk absent on Windows")
def test_all_repository_release_sections_match_legacy_awk(tmp_path: Path) -> None:
    # Exact awk program from release.yml before migration (commit 0c3e806).
    # The old NOTES=$(awk ...); echo "$NOTES" normalizes trailing LF only.
    # Legacy release ran on Linux. Normalize an autocrlf checkout before
    # comparing it; separate tests cover CRLF inputs and byte preservation.
    changelog = (Path(__file__).parents[1] / "CHANGELOG.md").read_text(encoding="utf-8")
    source = tmp_path / "CHANGELOG.md"
    source.write_bytes(changelog.encode("utf-8"))
    # Only tags matching the workflow's v* trigger are release inputs;
    # Unreleased may legitimately be empty after publishing a version.
    versions = re.findall(r"^## \[(v[^\]]+)\]", changelog, re.MULTILINE)
    assert versions

    for version in versions:
        program = (
            r"/^## \[" + version + r"\]/{found=1; next} "
            r"found && /^## \[/{exit} found{print}"
        )
        legacy = subprocess.run(
            ["awk", program, str(source)], check=True, capture_output=True
        ).stdout
        legacy_notes = legacy.rstrip(b"\n") + b"\n"
        current = extract_release_notes(changelog, version).encode("utf-8")
        # Only empty leading lines are intentionally omitted. Every content
        # byte, including Markdown indentation and trailing spaces, must agree.
        assert current == legacy_notes.lstrip(b"\n"), version


@pytest.mark.skipif(os.name == "nt" and shutil.which("awk") is None, reason="awk absent on Windows")
def test_markdown_headings_inside_notes_match_legacy_awk(tmp_path: Path) -> None:
    changelog = (
        "## [v1]\n\n    indented code\n\n## Migration details\n"
        "Do not lose this paragraph.\n\n## [v0]\nPrevious release.\n"
    )
    source = tmp_path / "CHANGELOG.md"
    source.write_bytes(changelog.encode("utf-8"))
    program = r"/^## \[v1\]/{found=1; next} found && /^## \[/{exit} found{print}"
    legacy = subprocess.run(["awk", program, str(source)], check=True, capture_output=True).stdout

    assert extract_release_notes(changelog, "v1").encode("utf-8") == (
        legacy.rstrip(b"\n").lstrip(b"\n") + b"\n"
    )


@pytest.mark.skipif(os.name == "nt" and shutil.which("sed") is None, reason="sed absent on Windows")
def test_release_and_pr_info_bytes_match_legacy_sed(tmp_path: Path) -> None:
    root = Path(__file__).parents[1]
    # Replay the original Linux checkout, not Windows sed's CRLF translation.
    # The separate LF/CRLF preservation test checks native input byte stability.
    original = (root / "INFO.txt").read_bytes().replace(b"\r\n", b"\n")
    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    versions = re.findall(r"^## \[(v[^\]]+)\]", changelog, re.MULTILINE)
    versions.append("pr-127-a1b2c3d")
    info = tmp_path / "INFO.txt"

    for version in versions:
        info.write_bytes(original)
        # Reading stdout is equivalent to old sed -i without platform-specific
        # BSD/GNU in-place flags. Only this temporary copy is passed to sed.
        legacy = subprocess.run(
            ["sed", f"s/__VERSION__/{version}/", str(info)], check=True, capture_output=True
        ).stdout

        prepare_release_metadata(version, tmp_path)

        assert info.read_bytes() == legacy, version
