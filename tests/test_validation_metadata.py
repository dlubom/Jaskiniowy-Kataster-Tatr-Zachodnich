from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from jktz.reporting import CheckFailed
from jktz.validation import metadata


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    )


def _raw_readme(status: str = "dostępny") -> str:
    item = "`source.xlsx` - arkusz" if status != "niedostępny" else "Brak materiałów źródłowych."
    return (
        "# Cave - source package\n\n"
        f"- **Status materiału:** {status}\n"
        "- **Pochodzenie danych:** J. Nowak\n"
        "- **Autorzy pomiarów:** J. Nowak\n"
        "- **Daty pomiarów:** 2004-06-19\n"
        "- **Data pozyskania:** 2013-11-26\n"
        "- **Dodał do _RAW:** Dariusz Lubomski\n"
        "- **Licencja źródłowa:** nieznane\n"
        "- **Kompletność:** pełny pomiar\n\n"
        "## Zawartość\n\n"
        f"- {item}\n"
    )


def _srv(source_ref: str = "_RAW/01", body: str = "#date 2004-06-19\n0\t1\t1.0\t90\t0\n") -> str:
    return (
        "#[\n"
        'CAVE_ID         "T.D-04.01"\n'
        'CAVE_NAME       "Zbojecka Dziura"\n'
        'SURVEY_ID       "ZBDZIU"\n'
        'SURVEY_NAME     "Zbojecka Dziura"\n'
        'UPDATE_DATE     "2026-06-05"\n'
        'PROJECT_NAME    "Kataster jaskin tatrzanskich"\n'
        'COORDINATOR     "Dariusz Lubomski"\n'
        'COORDINATOR_EMAIL "darek.lubomski@gmail.com"\n'
        f'SOURCE_REF      "{source_ref}"\n'
        'LICENSE         "http://creativecommons.org/licenses/by-sa/4.0/"\n'
        "\n"
        'TEAM            "J. Nowak"\n'
        'INSTRUMENT      "nieznane"\n'
        'SURVEY_DATE     "2004-06-19"\n'
        'SURVEY_GRADE    "BCRA:5D"\n'
        'PROCESSING      "konwersja z arkusza"\n'
        "#]\n\n" + body
    )


def test_metadata_check_passes_for_valid_srv_and_raw(tmp_path: Path) -> None:
    cave = tmp_path / "Poligony" / "Cave"
    raw = cave / "_RAW" / "01"
    raw.mkdir(parents=True)
    (raw / "README.md").write_text(_raw_readme(), encoding="utf-8")
    (raw / "source.xlsx").write_text("raw", encoding="utf-8")
    (cave / "CAVE.SRV").write_text(_srv(), encoding="utf-8")

    metadata.check(root=tmp_path / "Poligony")


def test_metadata_check_reports_all_errors(tmp_path: Path) -> None:
    cave = tmp_path / "Poligony" / "Cave"
    raw = cave / "_RAW" / "01"
    raw.mkdir(parents=True)
    (raw / "README.md").write_text(
        _raw_readme().replace("- **Licencja źródłowa:** nieznane\n", ""), encoding="utf-8"
    )
    (raw / "loose.txt").write_text("raw", encoding="utf-8")
    (cave / "BAD.SRV").write_text("#prefix Cave\n0\t1\t1.0\t90\t0\n", encoding="utf-8")
    (cave / "CAVE.SRV").write_text(_srv(body="0\t1\t1.0\t90\t0\n"), encoding="utf-8")

    with pytest.raises(CheckFailed) as excinfo:
        metadata.check(root=tmp_path / "Poligony")

    msg = str(excinfo.value)
    assert "BAD.SRV" in msg
    assert "must start with #[" in msg
    assert "Licencja źródłowa" in msg
    assert "active shot without #date or DECL" in msg


def test_metadata_check_allows_parent_source_ref(tmp_path: Path) -> None:
    system = tmp_path / "Poligony" / "System"
    section = system / "Section"
    raw = system / "_RAW" / "02"
    raw.mkdir(parents=True)
    section.mkdir(parents=True)
    (raw / "README.md").write_text(_raw_readme(), encoding="utf-8")
    (raw / "source.svx").write_text("raw", encoding="utf-8")
    (section / "SECTION.SRV").write_text(_srv(source_ref="../_RAW/02"), encoding="utf-8")

    metadata.check(root=tmp_path / "Poligony")


def test_metadata_check_ignores_raw_otwory_and_powierzchnia_via_active_path_gate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path
    poligony = root / "Poligony"
    raw = poligony / "Cave" / "_RAW" / "01"
    raw.mkdir(parents=True)
    (raw / "README.md").write_text(_raw_readme(), encoding="utf-8")
    (raw / "ORIG.SRV").write_text("0\t1\t1.0\t90\t0\n", encoding="utf-8")
    (poligony / "OTWORY.SRV").write_text("#fix Cave:0 E19.9 N49.2 1000m\n", encoding="utf-8")
    surface = root / "Powierzchnia" / "Teren_10x10" / "POZIOM.SRV"
    surface.parent.mkdir(parents=True)
    surface.write_text("0\t1\t1.0\t90\t0\n", encoding="utf-8")

    checked_paths: list[Path] = []
    original_is_active_srv_path = metadata.is_active_srv_path

    def recording_is_active_srv_path(path: Path) -> bool:
        checked_paths.append(path)
        return original_is_active_srv_path(path)

    monkeypatch.setattr(metadata, "is_active_srv_path", recording_is_active_srv_path)

    metadata.check(root=root)

    assert Path("Poligony/Cave/_RAW/01/ORIG.SRV") in checked_paths
    assert Path("Poligony/OTWORY.SRV") in checked_paths
    assert Path("Powierzchnia/Teren_10x10/POZIOM.SRV") in checked_paths


def test_metadata_check_rejects_direct_material_under_raw(tmp_path: Path) -> None:
    root = tmp_path / "Poligony"
    raw = root / "Cave" / "_RAW"
    raw.mkdir(parents=True)
    (raw / "ORIG.SRV").write_text("0\t1\t1.0\t90\t0\n", encoding="utf-8")

    with pytest.raises(CheckFailed) as excinfo:
        metadata.check(root=root)

    msg = str(excinfo.value)
    assert "ORIG.SRV" in msg
    assert "material left directly under _RAW" in msg


def test_metadata_check_allows_ignored_untracked_material_under_raw(tmp_path: Path) -> None:
    _git(tmp_path, "init")
    (tmp_path / ".gitignore").write_text("*.err\n", encoding="utf-8")
    raw = tmp_path / "Poligony" / "Cave" / "_RAW"
    raw.mkdir(parents=True)
    (raw / "generated.err").write_text("generated", encoding="utf-8")

    metadata.check(root=tmp_path / "Poligony")


def test_metadata_check_rejects_ignored_tracked_material_under_raw(tmp_path: Path) -> None:
    _git(tmp_path, "init")
    (tmp_path / ".gitignore").write_text("*.err\n", encoding="utf-8")
    raw = tmp_path / "Poligony" / "Cave" / "_RAW"
    raw.mkdir(parents=True)
    generated = raw / "generated.err"
    generated.write_text("generated", encoding="utf-8")
    _git(tmp_path, "add", "--force", str(generated))

    with pytest.raises(CheckFailed) as excinfo:
        metadata.check(root=tmp_path / "Poligony")

    msg = str(excinfo.value)
    assert "generated.err" in msg
    assert "material left directly under _RAW" in msg
