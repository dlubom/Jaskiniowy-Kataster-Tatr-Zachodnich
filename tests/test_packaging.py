from __future__ import annotations

import zipfile
from pathlib import Path

from jktz.packaging import EXCLUDE_PATTERNS, build_release_zip, is_excluded


def test_is_excluded_matches_known_patterns() -> None:
    assert is_excluded(".git/config")
    assert is_excluded(".github/workflows/validate.yml")
    assert is_excluded("scripts/render_otwory_from_gps.py")
    assert is_excluded("src/jktz/cli/validate.py")
    assert is_excluded("tests/test_packaging.py")
    assert is_excluded("doc/Walls_manual.md")
    assert is_excluded("Poligony/OTWORY.SRV.j2")
    assert is_excluded("Poligony/D_Bystra/Cave/_RAW/original.svx")
    assert is_excluded("Poligony/Whatever.NTA")
    assert is_excluded("KATASTER.wrl")
    assert is_excluded("JKTZ-v1.2.6.zip")
    assert is_excluded("cavern_output.txt")
    assert is_excluded("uv.lock")
    assert is_excluded("pyproject.toml")
    assert is_excluded(".idea/workspace.xml")
    assert is_excluded(".vscode/settings.json")
    assert is_excluded(".gitattributes")
    assert is_excluded(".pre-commit-config.yaml")
    assert is_excluded("survex-1.4.21/configure")
    assert is_excluded("survex-1.4.21/src/cavern.c")
    assert is_excluded("survex-1.4.21.tar.gz")


def test_is_excluded_keeps_real_data_files() -> None:
    assert not is_excluded("KATASTER.wpj")
    assert not is_excluded("README.md")
    assert not is_excluded("CHANGELOG.md")
    assert not is_excluded("LICENCE")
    assert not is_excluded("INFO.txt")
    assert not is_excluded("Poligony/OTWORY.SRV")
    assert not is_excluded("Poligony/D_Bystra/Goryczkowa/GORYC_S.SRV")
    assert not is_excluded("Powierzchnia/something.svx")


def test_excludes_use_posix_separators_on_windows_paths() -> None:
    # On Windows the relative path uses backslashes; is_excluded must normalize.
    assert is_excluded(r".git\config")
    assert is_excluded(r"scripts\render_otwory_from_gps.py")


def test_build_release_zip_includes_data_and_excludes_tooling(tmp_path: Path) -> None:
    # Arrange: build a minimal fake workspace under tmp_path.
    (tmp_path / "Poligony" / "D_Bystra").mkdir(parents=True)
    (tmp_path / "Poligony" / "D_Bystra" / "GORYC_S.SRV").write_text("survey data")
    (tmp_path / "Poligony" / "OTWORY.SRV").write_text("#fix Cave:0 E19.9 N49.25 1500m")
    (tmp_path / "Poligony" / "OTWORY.SRV.j2").write_text("template - excluded")
    (tmp_path / "KATASTER.wpj").write_text("project file")
    (tmp_path / "README.md").write_text("readme")
    (tmp_path / "INFO.txt").write_text("info")

    # Files that must NOT make it into the ZIP:
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "HEAD").write_text("ref: refs/heads/main")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "render_otwory_from_gps.py").write_text("py")
    (tmp_path / "src" / "jktz").mkdir(parents=True)
    (tmp_path / "src" / "jktz" / "__init__.py").write_text("")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_x.py").write_text("py")
    (tmp_path / "pyproject.toml").write_text("[project]")
    (tmp_path / "uv.lock").write_text("")
    (tmp_path / "CLAUDE.md").write_text("instructions")
    (tmp_path / "cavern_output.txt").write_text("log")
    (tmp_path / "previous.NTA").write_bytes(b"\x00" * 10)
    (tmp_path / "KATASTER.wrl").write_text("vrml")
    raw_dir = tmp_path / "Poligony" / "D_Bystra" / "_RAW"
    raw_dir.mkdir()
    (raw_dir / "raw.txt").write_text("raw data not for release")
    (tmp_path / "JKTZ-v0.zip").write_bytes(b"PK\x05\x06" + b"\x00" * 18)  # empty zip

    zip_path = tmp_path / "JKTZ-v1.zip"

    # Act
    result = build_release_zip(version="v1", zip_path=zip_path, root=tmp_path)

    # Assert
    assert result == zip_path
    assert zip_path.exists()
    with zipfile.ZipFile(zip_path) as zf:
        names = set(zf.namelist())

    # Included
    assert "KATASTER.wpj" in names
    assert "README.md" in names
    assert "INFO.txt" in names
    assert "Poligony/OTWORY.SRV" in names
    assert "Poligony/D_Bystra/GORYC_S.SRV" in names

    # Excluded
    assert ".git/HEAD" not in names
    assert "scripts/render_otwory_from_gps.py" not in names
    assert "src/jktz/__init__.py" not in names
    assert "tests/test_x.py" not in names
    assert "pyproject.toml" not in names
    assert "uv.lock" not in names
    assert "CLAUDE.md" not in names
    assert "cavern_output.txt" not in names
    assert "previous.NTA" not in names
    assert "KATASTER.wrl" not in names
    assert "Poligony/D_Bystra/_RAW/raw.txt" not in names
    assert "Poligony/OTWORY.SRV.j2" not in names
    assert "JKTZ-v0.zip" not in names


def test_build_release_zip_overwrites_existing_target(tmp_path: Path) -> None:
    (tmp_path / "KATASTER.wpj").write_text("project")
    zip_path = tmp_path / "JKTZ-v1.zip"
    zip_path.write_bytes(b"stale-bytes")
    build_release_zip(version="v1", zip_path=zip_path, root=tmp_path)
    with zipfile.ZipFile(zip_path) as zf:
        assert "KATASTER.wpj" in zf.namelist()


def test_default_zip_path_is_jktz_version_zip(tmp_path: Path) -> None:
    (tmp_path / "KATASTER.wpj").write_text("project")
    result = build_release_zip(version="v2.3.4", zip_path=None, root=tmp_path)
    assert result.name == "JKTZ-v2.3.4.zip"
    assert result.parent.resolve() == tmp_path.resolve()


def test_exclude_patterns_is_immutable_tuple() -> None:
    assert isinstance(EXCLUDE_PATTERNS, tuple)
    assert "src/*" in EXCLUDE_PATTERNS
    assert "scripts/*" in EXCLUDE_PATTERNS
    assert "tests/*" in EXCLUDE_PATTERNS
