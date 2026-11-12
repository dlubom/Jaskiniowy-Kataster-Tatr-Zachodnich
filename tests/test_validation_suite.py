from __future__ import annotations

import io
import sys
from pathlib import Path, PureWindowsPath
from unittest.mock import Mock

import pytest

from jktz.entrances.render import RenderError, RenderResult
from jktz.gps_catalog import GpsSnapshot
from jktz.reporting import CheckFailed
from jktz.validation import suite
from jktz.validation.suite import (
    ValidationContext,
    ValidationStep,
    run_steps,
    run_validation,
    validation_steps,
)


@pytest.fixture
def fake_snapshot(tmp_path, monkeypatch):
    snapshot = GpsSnapshot("owner/gps", "v1", 1, tmp_path / "csv", tmp_path / "gpkg", "a", "b")
    monkeypatch.setattr(suite, "download_snapshot", Mock(return_value=snapshot))
    return snapshot


def test_validation_contract_orders_checks(tmp_path: Path, fake_snapshot) -> None:
    context = ValidationContext(
        cavern_log=tmp_path / "cavern.log",
        exports_dir=tmp_path / "exports",
    )

    steps = validation_steps(context, fake_snapshot)

    assert len(steps) == 14
    assert steps[0].heading == "Checking SRV filenames format"
    assert steps[-1].heading == "Checking exports"


def test_run_steps_derives_progress_total_from_collection(capsys) -> None:
    calls: list[str] = []
    steps = (
        ValidationStep("First", "First", lambda: calls.append("first")),
        ValidationStep("Second", None, lambda: calls.append("second")),
    )

    run_steps(steps)

    assert calls == ["first", "second"]
    assert capsys.readouterr().out == ("[1/2] First...\n      First: Passed ✔\n[2/2] Second...\n")


def test_run_validation_removes_exports_after_failure(
    tmp_path: Path, monkeypatch, fake_snapshot
) -> None:
    exports_dir = tmp_path / "exports"
    context = ValidationContext(
        cavern_log=tmp_path / "cavern.log",
        exports_dir=exports_dir,
    )

    def failing_steps(
        _context: ValidationContext, _snapshot: GpsSnapshot
    ) -> tuple[ValidationStep, ...]:
        def fail() -> None:
            exports_dir.mkdir()
            (exports_dir / "partial.shp").write_bytes(b"partial")
            raise RuntimeError("boom")

        return (ValidationStep("Fail", None, fail),)

    monkeypatch.setattr("jktz.validation.suite.validation_steps", failing_steps)

    try:
        run_validation(context)
    except RuntimeError as exc:
        assert str(exc) == "boom"
    else:
        raise AssertionError("run_validation should propagate validation failures")

    assert not exports_dir.exists()


def test_validation_preserves_existing_export_directory(tmp_path, monkeypatch):
    exports = tmp_path / "validate-exports"
    exports.mkdir()
    retained = exports / "previous-survey.shp"
    retained.write_bytes(b"previous export")
    monkeypatch.chdir(tmp_path)
    steps = Mock(side_effect=CheckFailed("unrelated early failure"))
    monkeypatch.setattr(suite, "validation_steps", steps)

    with pytest.raises(CheckFailed):
        run_validation()

    assert retained.read_bytes() == b"previous export"
    steps.assert_not_called()


def test_rendered_entrances_check_uses_package_api(monkeypatch, capsys, fake_snapshot) -> None:
    def fake_render(*, check: bool, csv_path: Path) -> RenderResult:
        assert check is True
        assert csv_path == fake_snapshot.csv_path
        return RenderResult(
            output=PureWindowsPath("Poligony/OTWORY.SRV"),
            source="gps-kataster@v1",
            gps_fixes=87,
        )

    monkeypatch.setattr(suite, "render_entrances", fake_render)

    suite._check_rendered_entrances(fake_snapshot)

    assert capsys.readouterr().out == (
        "Checked Poligony/OTWORY.SRV from gps-kataster@v1\nGPS fixes: 87\n"
    )


def test_rendered_entrances_check_wraps_renderer_errors(monkeypatch, fake_snapshot) -> None:
    def fail(*, check: bool, csv_path: Path) -> RenderResult:
        raise RenderError("snapshot is stale")

    monkeypatch.setattr(suite, "render_entrances", fail)

    with pytest.raises(CheckFailed, match="entrance snapshot check failed: snapshot is stale"):
        suite._check_rendered_entrances(fake_snapshot)


def test_indentation_handles_partial_writes_and_preserves_stream_interface():
    target = io.StringIO()
    stream = suite._IndentingStream(target, "> ")

    assert stream.write("") == 0
    stream.write("first")
    stream.write(" line\nsecond\n")
    stream.write("third\r")
    stream.write("fourth")
    stream.flush()

    assert target.getvalue() == "> first line\n> second\n> third\r> fourth"
    assert stream.getvalue() == target.getvalue()


def test_indentation_restores_stdout_when_export_fails():
    original = sys.stdout

    with pytest.raises(RuntimeError, match="export failed"), suite._indent_stdout():
        raise RuntimeError("export failed")

    assert sys.stdout is original


def test_exports_run_before_artifact_checks_with_shared_destination(tmp_path, monkeypatch, capsys):
    context = ValidationContext(exports_dir=tmp_path / "artifacts", exports_version="custom")
    calls = []

    def export(**kwargs):
        calls.append(("export", kwargs))
        print("compiler output")

    monkeypatch.setattr(suite.pipeline, "run_exports", export)
    for name in ("empty_shapefiles", "shapefiles_count", "shapefiles_extent"):
        monkeypatch.setattr(
            getattr(suite, name),
            "check",
            lambda _name=name, **kwargs: calls.append((_name, kwargs)),
        )

    suite._check_exports(context)

    assert calls == [
        ("export", {"version": "custom", "outdir": context.exports_dir}),
        ("empty_shapefiles", {"outdir": context.exports_dir}),
        ("shapefiles_count", {"outdir": context.exports_dir, "version": "custom"}),
        ("shapefiles_extent", {"outdir": context.exports_dir, "version": "custom"}),
    ]
    assert capsys.readouterr().out == "                   compiler output\n"


def test_validation_contract_compiles_then_checks_the_same_log(
    tmp_path, monkeypatch, fake_snapshot
):
    context = ValidationContext(cavern_log=tmp_path / "compile.txt")
    compile_project = Mock()
    unattached = Mock()
    warnings = Mock()
    exports = Mock()
    references = Mock()
    monkeypatch.setattr(suite.exports_tools, "cavern", compile_project)
    monkeypatch.setattr(suite.unattached, "check", unattached)
    monkeypatch.setattr(suite.cavern_warnings, "check", warnings)
    monkeypatch.setattr(suite, "_check_exports", exports)

    monkeypatch.setattr(suite.catalogue, "check_compiled_references", references)

    for step in validation_steps(context, fake_snapshot)[9:]:
        step.check()

    compile_project.assert_called_once_with(["KATASTER.wpj"], log_to=context.cavern_log)
    unattached.assert_called_once_with(log_path=context.cavern_log)
    warnings.assert_called_once_with(log_path=context.cavern_log)
    references.assert_called_once_with(Path("KATASTER.3d"), {})
    exports.assert_called_once_with(context)


@pytest.mark.parametrize("create_exports", [False, True])
def test_successful_default_validation_cleans_only_its_temporary_exports(
    tmp_path, monkeypatch, create_exports, fake_snapshot
):
    monkeypatch.chdir(tmp_path)
    retained = tmp_path / "retained.txt"
    retained.write_text("keep")
    contexts = []

    def steps(context, snapshot):
        contexts.append(context)

        def generate():
            if create_exports:
                context.exports_dir.mkdir()
                (context.exports_dir / "generated.txt").write_text("remove")

        return (ValidationStep("Generate", None, generate),)

    monkeypatch.setattr(suite, "validation_steps", steps)

    run_validation()

    assert contexts == [ValidationContext()]
    assert not (tmp_path / "validate-exports").exists()
    assert retained.read_text() == "keep"


def test_validation_stops_at_first_failure_without_success_message(capsys):
    later = Mock()
    steps = [
        ValidationStep("Invalid", "Invalid", Mock(side_effect=CheckFailed("bad data"))),
        ValidationStep("Later", "Later", later),
    ]

    with pytest.raises(CheckFailed, match="bad data"):
        run_steps(steps)

    later.assert_not_called()
    assert capsys.readouterr().out == "[1/2] Invalid...\n"


@pytest.fixture
def gps_project(tmp_path, monkeypatch):
    from test_gps_catalog import update_database
    from test_validation_metadata import _raw_readme

    from jktz.entrances.render import render_entrances
    from jktz.metadata.srv import default_metadata, replace_or_insert_metadata

    monkeypatch.chdir(tmp_path)
    directory = tmp_path / "GPS #1"
    directory.mkdir()
    csv_path = directory / "best-measurements.csv"
    csv_path.write_text(
        "object_id,cave_id,system_cave_id,lon,lat,elevation_m\n"
        "MLW-0001,C-0001,,19.9,49.2,1730\n"
        "MLW-0002,C-0001,,19.8,49.3,1300\n",
        encoding="utf-8",
    )
    update_database(
        directory,
        """
        CREATE TABLE caves (fid INTEGER PRIMARY KEY, cave_id TEXT, name TEXT, system_cave_id TEXT);
        CREATE TABLE objects (
            fid INTEGER PRIMARY KEY, object_id TEXT, name TEXT, cave_id TEXT, category TEXT
        );
        INSERT INTO caves VALUES (1, 'C-0001', 'Cave', NULL);
        INSERT INTO objects VALUES (1, 'MLW-0001', NULL, 'C-0001', 'jaskinia_otwor'),
                                   (2, 'MLW-0002', NULL, 'C-0001', 'jaskinia_otwor');
        """,
    )
    from jktz.entrances.render import DEFAULT_OUTPUT, DEFAULT_TEMPLATE

    DEFAULT_TEMPLATE.parent.mkdir()
    DEFAULT_TEMPLATE.write_text(
        "{{ gps_fix('Fixture:0', 'MLW-0001') }}\n; {{ gps_fix('Fixture:0', 'MLW-0002') }}\n",
        encoding="utf-8",
    )
    render_entrances(csv_path=csv_path)
    cave = Path("Poligony/Fixture")
    (cave / "_RAW/01").mkdir(parents=True)
    (cave / "_RAW/01/README.md").write_text(_raw_readme("niedostępny"), encoding="utf-8")
    survey = cave / "FIXTURE.SRV"
    survey.write_text(
        replace_or_insert_metadata(
            "#prefix Fixture\n#units meters order=DAV\n#date 2020-01-01\n0 1 10 0 0\n",
            default_metadata(
                survey_kind="underground",
                update_date="2026-11-12",
                cave_id="C-0001",
                cave_name="Fixture",
                survey_id="FIXTURE",
                survey_name="Fixture",
                source_refs=["_RAW/01"],
                object_refs=["Fixture:0=MLW-0001", "Fixture:1=MLW-0002"],
            ),
        ),
        encoding="utf-8",
    )
    compiler = Mock()
    export = Mock()
    monkeypatch.setattr(suite.exports_tools, "cavern", compiler)
    monkeypatch.setattr(suite, "_check_exports", export)
    monkeypatch.setattr(suite.unattached, "check", Mock())
    monkeypatch.setattr(suite.cavern_warnings, "check", Mock())

    def export_stations(args):
        assert compiler.called
        assert Path(args[-2]).name == "KATASTER.3d"
        assert "--csv" in args
        Path(args[-1]).write_bytes(
            b"Easting,Northing,Altitude,Station Name\r\n0,0,0,Fixture:0\r\n0,0,0,Fixture:1\r\n"
        )

    monkeypatch.setattr(suite.exports_tools, "survexport", Mock(side_effect=export_stations))
    return directory, survey, DEFAULT_OUTPUT, compiler, export


def test_j05_validation_resolves_latest_once_for_catalogue_and_render(
    gps_project, monkeypatch, capsys
):
    import io
    import json
    import urllib.request

    from jktz.entrances.render import DEFAULT_GITHUB_REPO
    from jktz.gps_catalog import ASSET_NAMES

    directory, _, entrances, compiler, export = gps_project
    before = entrances.read_bytes()
    base = "https://example.invalid/v1/"
    assets = [
        {"id": n, "name": name, "browser_download_url": base + name}
        for n, name in enumerate(ASSET_NAMES, 1)
    ]
    latest = f"https://api.github.com/repos/{DEFAULT_GITHUB_REPO}/releases/latest"
    requests = []

    def urlopen(request, *, timeout):
        url = request.full_url
        requests.append(url)
        if url == latest:
            # A second request would see the next release.
            version = requests.count(latest)
            return io.BytesIO(
                json.dumps(
                    {
                        "id": version,
                        "tag_name": f"v{version}",
                        "assets": assets if version == 1 else [],
                    }
                ).encode()
            )
        return io.BytesIO((directory / url.removeprefix(base)).read_bytes())

    monkeypatch.setattr(urllib.request, "urlopen", urlopen)
    run_validation()

    assert requests == [latest, *(base + name for name in ASSET_NAMES)]
    assert "@v1" in capsys.readouterr().out
    assert entrances.read_bytes() == before
    compiler.assert_called_once()
    export.assert_called_once()


@pytest.mark.parametrize(
    ("error", "message", "compiled"),
    [
        ("tables", "objects", False),
        ("id", r"FIXTURE.SRV: CAVE_ID C-9999", False),
        ("binding", r"Fixture:0.*conflicting object_ids", False),
        ("station", r"Fixture:missing=MLW-0002.*missing from compiler output", True),
        ("station_csv", "Station Name", True),
        ("stale_entrances", "entrance snapshot check failed", False),
    ],
)
def test_j05_bad_snapshot_or_reference_never_publishes(
    gps_project, monkeypatch, error, message, compiled
):
    from test_gps_catalog import update_database

    from jktz.entrances.render import DEFAULT_TEMPLATE, render_entrances

    directory, survey, entrances, compiler, export = gps_project
    if error == "tables":
        update_database(directory, "DROP TABLE objects")
    elif error == "binding":
        template = DEFAULT_TEMPLATE.read_text(encoding="utf-8")
        DEFAULT_TEMPLATE.write_text(template.replace("; {{", "{{"), encoding="utf-8")
        render_entrances(csv_path=directory / "best-measurements.csv")
    elif error == "stale_entrances":
        entrances.write_bytes(b"previous OTWORY")
    elif error == "station_csv":
        monkeypatch.setattr(
            suite.exports_tools, "survexport", lambda args: Path(args[-1]).write_text("invalid\n")
        )
    else:
        old, new = ("C-0001", "C-9999") if error == "id" else ("Fixture:1", "Fixture:missing")
        survey.write_text(survey.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")
    before = entrances.read_bytes()
    from jktz.cli.validate import main

    with pytest.raises(CheckFailed, match=message):
        run_validation(ValidationContext(gps_snapshot=directory))

    assert compiler.called is compiled
    export.assert_not_called()
    assert entrances.read_bytes() == before
    assert not Path("validate-exports").exists()
    assert main(["--gps-snapshot", str(directory)]) == 1


def test_j05_snapshot_render_rejects_invalid_catalogue_before_write(gps_project, capsys):
    from test_gps_catalog import update_database

    from jktz.cli.render_otwory import main

    directory, _, entrances, *_ = gps_project
    before = entrances.read_bytes()
    update_database(directory, "DROP TABLE objects")

    assert main(["--gps-snapshot", str(directory)]) == 1
    assert "objects" in capsys.readouterr().err
    assert entrances.read_bytes() == before


@pytest.mark.parametrize("command", ["render_otwory", "validate"])
def test_j05_cli_rejects_ambiguous_gps_inputs(command, capsys):
    from jktz.cli import render_otwory, validate

    cli = {"render_otwory": render_otwory, "validate": validate}[command]
    with pytest.raises(SystemExit) as error:
        cli.main(["--csv", "best.csv", "--gps-snapshot", "snapshot"])
    assert error.value.code == 2
    assert "not allowed with argument" in capsys.readouterr().err


@pytest.mark.parametrize(
    "fault", [None, "unknown cave", "missing station", "compiler error", "coordinates"]
)
def test_j05_versioned_render_replaces_entrances_only_after_checks(
    gps_project, monkeypatch, capsys, fault
):
    from test_gps_catalog import write_manifest

    from jktz.cli import render_otwory
    from jktz.exports.tools import ExternalToolError

    directory, survey, entrances, *_ = gps_project
    original = entrances.read_bytes()
    csv = directory / "best-measurements.csv"
    csv.write_text(csv.read_text(encoding="utf-8").replace("1730", "1731"), encoding="utf-8")
    if fault == "coordinates":
        csv.write_text(csv.read_text(encoding="utf-8").replace("19.9", "99.9"), encoding="utf-8")
    write_manifest(directory)
    if fault in ("unknown cave", "missing station"):
        old, new = ("C-0001", "C-9999") if fault == "unknown cave" else ("Fixture:1", "Fixture:99")
        survey.write_text(survey.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")

    def compile_candidate(args, *, cwd, log_to):
        assert cwd != Path.cwd()
        assert (cwd / entrances).read_bytes() != original
        assert entrances.read_bytes() == original
        assert (cwd / survey).read_bytes() == survey.read_bytes()
        assert not (cwd / survey.parent / "_RAW").exists()
        assert args == ["--warnings-are-errors", "KATASTER.wpj"]
        if fault == "compiler error":
            raise ExternalToolError("synthetic compiler error")
        log_to.write_text("Compiled.", encoding="utf-8")

    compiler = Mock(side_effect=compile_candidate)
    monkeypatch.setattr(render_otwory, "cavern", compiler)
    station_export = Mock(
        side_effect=lambda args: Path(args[-1]).write_text(
            "Easting,Northing,Altitude,Station Name\n0,0,0,Fixture:0\n0,0,0,Fixture:1\n",
            encoding="utf-8",
        )
    )
    monkeypatch.setattr(suite.exports_tools, "survexport", station_export)

    assert render_otwory.main(["--gps-snapshot", str(directory)]) == int(fault is not None)
    out = capsys.readouterr()
    if fault is None:
        assert entrances.read_bytes() == original.replace(b"1730m", b"1731m")
        assert "owner/gps@preview-49" in out.out
    else:
        assert entrances.read_bytes() == original
        assert {
            "unknown cave": "C-9999",
            "missing station": "Fixture:99",
            "compiler error": "synthetic compiler error",
            "coordinates": "lon 99.900000 outside",
        }[fault] in out.err
    assert compiler.called is (fault not in ("unknown cave", "coordinates"))


def test_j05_checked_render_and_offline_validation_do_not_access_network(gps_project, monkeypatch):
    import urllib.request

    from jktz.cli import render_otwory, validate

    directory, *_ = gps_project
    request = Mock(side_effect=AssertionError("offline operation accessed the network"))
    monkeypatch.setattr(urllib.request, "urlopen", request)

    assert render_otwory.main(["--gps-snapshot", str(directory), "--check"]) == 0
    assert validate.main(["--gps-snapshot", str(directory)]) == 0
    request.assert_not_called()


@pytest.mark.parametrize("bad_input", [False, True])
def test_j05_snapshot_command_checks_downloaded_catalogue(
    gps_project, monkeypatch, capsys, bad_input
):
    from test_gps_catalog import update_database

    from jktz.cli import render_otwory
    from jktz.gps_catalog import load_snapshot

    directory, *_ = gps_project
    if bad_input:
        update_database(directory, "DROP TABLE objects")
    download = Mock(return_value=load_snapshot(directory))
    monkeypatch.setattr(render_otwory, "download_snapshot", download)
    assert render_otwory.snapshot_main(["new snapshot"]) == int(bad_input)
    download.assert_called_once()
    captured = capsys.readouterr()
    assert "Missing catalogue tables" in captured.err if bad_input else "preview-49" in captured.out


def test_j05_invalid_manifest_is_reported_before_metadata(gps_project, monkeypatch, capsys):
    from jktz.cli import validate

    directory, *_ = gps_project
    (directory / "snapshot.json").unlink()
    metadata = Mock()
    monkeypatch.setattr(suite.metadata, "check", metadata)
    assert validate.main(["--gps-snapshot", str(directory)]) == 1
    assert "Cannot read GPS snapshot manifest" in capsys.readouterr().out
    metadata.assert_not_called()


@pytest.mark.parametrize("fail_after_export", [True, False])
def test_j05_publish_only_checked_exports(gps_project, monkeypatch, fail_after_export):
    from jktz.cli import validate

    directory, *_ = gps_project

    def exports(context):
        assert context.exports_version == "pr-test"
        assert not Path("exports").exists()
        context.exports_dir.mkdir()
        (context.exports_dir / "checked.3d").write_bytes(b"compiled")
        if fail_after_export:
            raise CheckFailed("invalid export")

    monkeypatch.setattr(suite, "_check_exports", exports)
    rc = validate.main(["--gps-snapshot", str(directory), "--export-version", "pr-test"])
    assert rc == int(fail_after_export)
    assert Path("exports/checked.3d").exists() is (not fail_after_export)


def test_j05_csv_is_preview_only_for_versioned_output(gps_project, capsys):
    from jktz.cli import render_otwory, validate

    directory, _, entrances, *_ = gps_project
    before = entrances.read_bytes()
    for cli in (render_otwory, validate):
        with pytest.raises(SystemExit) as error:
            cli.main(["--csv", str(directory / "best-measurements.csv")])
        assert error.value.code == 2
        assert "complete GPS snapshot" in capsys.readouterr().err
    assert entrances.read_bytes() == before


def test_j05_online_versioned_render_downloads_full_snapshot(gps_project, monkeypatch):
    from jktz.cli import render_otwory
    from jktz.gps_catalog import load_snapshot

    directory, _, entrances, *_ = gps_project
    snapshot = load_snapshot(directory)
    download = Mock(return_value=snapshot)
    write = Mock(return_value=RenderResult(entrances, "local", 2))
    monkeypatch.setattr(render_otwory, "download_snapshot", download)
    monkeypatch.setattr(render_otwory, "_render_checked_project", write)
    assert render_otwory.main([]) == 0
    download.assert_called_once()
    write.assert_called_once()
    assert write.call_args.args[2] == snapshot.csv_path


def test_j05_nested_walls_comment_does_not_claim_a_station(gps_project):
    from jktz.entrances.render import DEFAULT_TEMPLATE, render_entrances

    directory, _, _, _, exports = gps_project
    with DEFAULT_TEMPLATE.open("a", encoding="utf-8") as template:
        template.write("#[\n#[\n#]\n{{ gps_fix('Fixture:0', 'MLW-0002') }}\n#]\n")
    render_entrances(csv_path=directory / "best-measurements.csv")
    run_validation(ValidationContext(gps_snapshot=directory))
    exports.assert_called_once()
