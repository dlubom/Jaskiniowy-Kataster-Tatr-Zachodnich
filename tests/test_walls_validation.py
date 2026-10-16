from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from jktz.walls import EXTENSIONS, validate


def project(root):
    root.mkdir(exist_ok=True)
    (root / "KATASTER.wpj").write_text(
        ".BOOK Test\n.NAME KATASTER\n.SURVEY Data\n.NAME DATA\n.ENDBOOK\n"
    )
    (root / "DATA.SRV").write_text("#units meters order=DAV\na b 1 0 0\n")
    return root / "KATASTER.wpj"


def runner(monkeypatch, action="ok"):
    def run(command, **kwargs):
        work = Path(kwargs["cwd"])
        if action == "timeout":
            raise OSError("Cannot launch driver")
        output = work / "KATASTER"
        output.mkdir()
        for ext in EXTENSIONS:
            if action != "missing" or ext != "NTV":
                (output / f"KATASTER.{ext}").write_bytes(b"fresh")
        if action == "warning":
            (output / "KATASTER.LOG").write_text("Warning: duplicate fix")
        if action == "changed":
            (work / "DATA.SRV").write_text("modified")
        return SimpleNamespace(
            returncode=20 if action == "error" else 0,
            stderr="",
            stdout="COMPILE_COMPLETE\n" if action != "false-success" else "launched\n",
        )

    monkeypatch.setattr("jktz.walls.subprocess.run", run)


def invoke(tmp_path, monkeypatch, action="ok"):
    source = project(tmp_path / "source")
    exe = tmp_path / "Walls32.exe"
    exe.write_bytes(b"compiler")
    driver = tmp_path / "driver.exe"
    driver.write_bytes(b"driver")
    runner(monkeypatch, action)
    report = validate(source, exe, driver, tmp_path / "evidence")
    return report


def test_success_keeps_fresh_evidence_and_preserves_sources(tmp_path, monkeypatch):
    source = project(tmp_path / "source")
    old = source.parent / "KATASTER"
    old.mkdir()
    (old / "KATASTER.NTV").write_bytes(b"user artifact")
    raw = source.parent / "_RAW"
    raw.mkdir()
    (raw / "original.SRV").write_bytes(b"original")
    report = invoke(tmp_path, monkeypatch)
    assert report["status"] == "PASS"
    assert len(report["artifacts"]) == 5
    assert report["inputs_unchanged"]
    assert len(report["inputs"]) == 2
    assert (old / "KATASTER.NTV").read_bytes() == b"user artifact"
    assert json.loads((tmp_path / "evidence" / "result.json").read_text()) == report


@pytest.mark.parametrize(
    "action", ["missing", "warning", "changed", "error", "false-success", "timeout"]
)
def test_never_passes_incomplete_warning_changed_or_failed_run(tmp_path, monkeypatch, action):
    report = invoke(tmp_path, monkeypatch, action)
    assert report["status"] == "FAIL"
    assert report["reason"]
    assert (tmp_path / "evidence" / "result.json").is_file()


def test_evidence_must_be_new(tmp_path, monkeypatch):
    (tmp_path / "evidence").mkdir()
    with pytest.raises(FileExistsError):
        invoke(tmp_path, monkeypatch)


@pytest.mark.parametrize("unsafe", ["C:\\outside", "..\\outside", "/outside"])
def test_rejects_external_paths_before_launch(tmp_path, monkeypatch, unsafe):
    source = project(tmp_path / "source")
    source.write_text(source.read_text().replace(".NAME DATA", f".PATH {unsafe}\n.NAME DATA"))
    with pytest.raises(ValueError, match="path"):
        validate(source, source, source, tmp_path / "evidence")


def test_missing_referenced_source_is_not_silently_skipped(tmp_path, monkeypatch):
    source = project(tmp_path / "source")
    (source.parent / "DATA.SRV").unlink()
    with pytest.raises(ValueError, match="Missing referenced"):
        validate(source, source, source, tmp_path / "evidence")


def test_nested_books_and_survey_paths(tmp_path):
    from jktz.walls import referenced_files

    path = tmp_path / "tree.wpj"
    path.write_text(
        ".BOOK Root\n.NAME ROOT\n.BOOK Branch\n.PATH one\\two\n"
        ".SURVEY Leaf\n.PATH three\n.NAME SHOTS\n.ENDBOOK\n"
        ".SURVEY Info\n.NAME INFO.txt\n.ENDBOOK\n"
    )
    assert referenced_files(path) == ["one/two/three/SHOTS.SRV", "INFO.txt"]


def test_rejects_linked_source(tmp_path, monkeypatch):
    from jktz.walls import source_files

    source = project(tmp_path / "source")
    target = tmp_path / "outside.SRV"
    target.write_text("outside")
    (source.parent / "LINK.SRV").symlink_to(target)
    with pytest.raises(ValueError, match="Unsafe source path"):
        source_files(source.parent)


@pytest.mark.parametrize("content", ["", ".BOOK Root\n.NAME one/two\n"])
def test_invalid_root_name(tmp_path, content):
    from jktz.walls import project_name

    path = tmp_path / "bad.wpj"
    path.write_text(content)
    with pytest.raises(ValueError, match="root .NAME"):
        project_name(path)


def test_wine_paths_and_command(tmp_path, monkeypatch):
    from jktz.walls import windows_path

    assert windows_path(Path("/tmp/file"), "wine").startswith("Z:")


def test_cli_success_failure_and_invalid_options(tmp_path, monkeypatch, capsys):
    from jktz.cli import walls_validate

    args = ["--walls", "Walls32.exe", "--driver", "driver.exe", "--output", str(tmp_path)]
    for status, expected in [("PASS", 0), ("FAIL", 1)]:
        monkeypatch.setattr(
            walls_validate,
            "validate",
            lambda *a, status=status, **kw: dict(status=status, reason=["detail"]),
        )
        assert walls_validate.main(args) == expected

    def failure(*a, **kw):
        raise OSError("missing compiler")

    monkeypatch.setattr(walls_validate, "validate", failure)
    assert walls_validate.main(args) == 1
    monkeypatch.delenv("WINEPREFIX", raising=False)
    for extra in [["--timeout", "0"], ["--wine", "wine"]]:
        with pytest.raises(SystemExit) as exc:
            walls_validate.main(args + extra)
        assert exc.value.code == 2
    assert "missing compiler" in capsys.readouterr().out


def test_snapshot_contains_only_wpj_references_not_prior_test_evidence(tmp_path, monkeypatch):
    source = project(tmp_path / "source")
    evidence = source.parent / "logs" / "fixtures"
    evidence.mkdir(parents=True)
    (evidence / "old.SRV").write_text("test fixture")
    (source.parent / "UNUSED.SRV").write_text("unreferenced")
    report = invoke(tmp_path, monkeypatch)
    assert report["status"] == "PASS"
    assert set(report["inputs"]) == {"KATASTER.wpj", "DATA.SRV"}


def test_external_timeout_keeps_partial_diagnostics(tmp_path, monkeypatch):
    import subprocess

    source = project(tmp_path / "source")

    def timeout(*a, **kw):
        raise subprocess.TimeoutExpired("driver", 5, output=b"partial driver evidence")

    monkeypatch.setattr("jktz.walls.subprocess.run", timeout)
    report = validate(source, source, source, tmp_path / "evidence")
    assert report["status"] == "FAIL"
    assert "partial driver evidence" in (tmp_path / "evidence" / "driver.log").read_text()


def test_path_after_endbook_applies_to_closed_book(tmp_path):
    from jktz.walls import referenced_files

    path = tmp_path / "tree.wpj"
    path.write_text(
        ".BOOK Root\n.NAME ROOT\n.BOOK Branch\n.NAME BRANCH\n"
        ".SURVEY A\n.NAME A\n.SURVEY B\n.NAME B\n"
        ".ENDBOOK\n.PATH nested\n.ENDBOOK\n"
    )
    assert referenced_files(path) == ["nested/A.SRV", "nested/B.SRV"]
