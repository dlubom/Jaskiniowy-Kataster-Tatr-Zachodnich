"""P06 CLI serialization, option forwarding and distinct completion/error exits."""

from __future__ import annotations

import hashlib
import json
import os
import runpy
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from jktz.cli import pockettopo
from jktz.pockettopo import CorrectionOverride, CorrectionPolicy, ProcessingPlan, RepeatConfirmation
from jktz.pockettopo.drawings import DrawingSettings, RenderingError
from jktz.pockettopo.export import export_surveys

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "doc/pockettopo/evidence/p01/cases"
CARDINAL = CASES / "api-cardinal/api-cardinal.top"
UNICODE = CASES / "api-trips-ids/api-trips-ids.top"


@pytest.mark.parametrize("case", ["api-trips-ids", "api-drawings", "api-references"])
def test_inspect_prints_complete_source_and_report_json(case, capsys):
    source = CASES / case / f"{case}.top"
    before = source.read_bytes()
    assert pockettopo.main(["inspect", str(source)]) == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    document = json.loads(captured.out)
    exported = export_surveys(before)
    limitations = document["report"].pop("limitations")
    library_limitations = exported.report.pop("limitations")
    assert limitations[:-1] == library_limitations[:-1]
    assert limitations[-1] == (
        "Inspection only: drawings, compilation and package publication have not run."
    )
    assert not document["report"]["completeness"]["conversion_complete"]
    assert document == json.loads(
        json.dumps(
            {
                "source": exported.source_document,
                "report": exported.report,
            }
        )
    )
    expected = json.loads((source.parent / "expected.json").read_text(encoding="utf-8"))
    assert document["source"]["records"]["trips"] == expected["source"]["trips"]
    assert document["source"]["provenance"]["sha256"] == hashlib.sha256(before).hexdigest()
    assert all(trip["used_date"] is None for trip in document["report"]["trips"])
    assert source.read_bytes() == before


def test_inspect_uses_pinned_decisions_and_explicit_resultant_threshold(tmp_path, capsys):
    digest = hashlib.sha256(CARDINAL.read_bytes()).hexdigest()
    decisions = tmp_path / "decisions.json"
    decisions.write_text(
        json.dumps(
            {
                "source_sha256": digest,
                "confirmations": [{"indices": [4, 5, 6], "reason": "independent fixture evidence"}],
            }
        )
    )
    assert (
        pockettopo.main(
            [
                "inspect",
                str(CARDINAL),
                "--decisions",
                str(decisions),
                "--min-resultant",
                "0.0001",
            ]
        )
        == 0
    )
    document = json.loads(capsys.readouterr().out)
    assert document["report"]["completeness"]["exported_measurements"] == 9
    assert document["report"]["groups"][4]["source_indices"] == [4, 5, 6]
    assert document["report"]["settings"]["min_resultant"] == 0.0001


@pytest.mark.parametrize(
    "case", ["missing_source", "invalid_source", "missing_decisions", "bad_decisions"]
)
def test_inspect_errors_have_exit_one_without_partial_stdout(tmp_path, capsys, case):
    source = tmp_path / "source.top"
    source.write_bytes(CARDINAL.read_bytes())
    arguments = ["inspect", str(source)]
    if case == "missing_source":
        source.unlink()
    elif case == "invalid_source":
        source.write_bytes(b"Top\x03")
    else:
        decisions = tmp_path / "decisions.json"
        if case == "bad_decisions":
            decisions.write_text("{")
        arguments += ["--decisions", str(decisions)]
    assert pockettopo.main(arguments) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith("ERROR: ")
    assert "Traceback" not in captured.err


@pytest.mark.parametrize("value", ["nan", "inf", "-1", "2"])
def test_invalid_threshold_is_reported_as_a_user_error(value, capsys):
    assert pockettopo.main(["inspect", str(CARDINAL), f"--min-resultant={value}"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "ERROR:" in captured.err


@pytest.mark.parametrize("complete,exit_code", [(True, 0), (False, 2)])
def test_convert_reports_absolute_package_paths_and_completion_status(
    tmp_path,
    monkeypatch,
    capsys,
    complete,
    exit_code,
):
    calls = []
    completeness = {"conversion_complete": complete, "held_shots": 0 if complete else 1}

    def convert(source, output, **options):
        calls.append((source, output, options))
        return {"completeness": completeness}

    monkeypatch.setattr(pockettopo, "convert_package", convert)
    monkeypatch.delenv("RESVG", raising=False)
    monkeypatch.chdir(tmp_path)
    assert pockettopo.main(["convert", str(CARDINAL), "--output", "result"]) == exit_code
    captured = capsys.readouterr()
    assert json.loads(captured.out) == {
        "output": str((tmp_path / "result").resolve()),
        "report": str((tmp_path / "result/conversion-report.json").resolve()),
        "completeness": completeness,
    }
    assert calls == [
        (
            CARDINAL,
            Path("result"),
            {
                "plan": None,
                "correction_policy": None,
                "min_resultant": 1e-12,
                "settings": DrawingSettings(),
                "resvg_path": "resvg",
                "cavern": "cavern",
                "dump3d": "dump3d",
            },
        )
    ]
    if complete:
        assert captured.err == ""
    else:
        assert "INCOMPLETE: package saved" in captured.err
        assert "conversion-report.json" in captured.err


@pytest.mark.parametrize(
    "background,expected_background", [("transparent", None), ("#123abc", "#123abc")]
)
def test_convert_forwards_all_options_and_decisions(
    tmp_path,
    monkeypatch,
    capsys,
    background,
    expected_background,
):
    digest = hashlib.sha256(CARDINAL.read_bytes()).hexdigest()
    decisions = tmp_path / "decisions.json"
    decisions.write_text(
        json.dumps(
            {
                "source_sha256": digest,
                "confirmations": [{"indices": [4, 5, 6], "reason": "verified repeat"}],
                "corrections": [{"trip_index": 0, "degrees": 2.5, "reason": "verified correction"}],
            }
        )
    )
    output = tmp_path / "package"
    calls = []

    def convert(source, destination, **options):
        calls.append((source, destination, options))
        return {"completeness": {"conversion_complete": True}}

    monkeypatch.setattr(pockettopo, "convert_package", convert)
    monkeypatch.setenv("RESVG", "environment-renderer")
    assert (
        pockettopo.main(
            [
                "convert",
                str(CARDINAL),
                "--output",
                str(output),
                "--decisions",
                str(decisions),
                "--resvg",
                "chosen-renderer",
                "--cavern",
                "chosen-cavern",
                "--dump3d",
                "chosen-dump3d",
                "--pixels-per-metre",
                "72.5",
                "--background",
                background,
                "--min-resultant",
                "0.25",
            ]
        )
        == 0
    )
    assert calls == [
        (
            CARDINAL,
            output,
            {
                "plan": ProcessingPlan(digest, (RepeatConfirmation((4, 5, 6), "verified repeat"),)),
                "correction_policy": CorrectionPolicy(
                    digest, (CorrectionOverride(0, 2.5, "verified correction"),)
                ),
                "min_resultant": 0.25,
                "settings": DrawingSettings(pixels_per_metre=72.5, background=expected_background),
                "resvg_path": "chosen-renderer",
                "cavern": "chosen-cavern",
                "dump3d": "chosen-dump3d",
            },
        )
    ]
    assert capsys.readouterr().err == ""


def test_resvg_environment_is_used_when_no_explicit_renderer_is_given(
    tmp_path, monkeypatch, capsys
):
    paths = []

    def convert(*args, **options):
        paths.append(options["resvg_path"])
        return {"completeness": {"conversion_complete": True}}

    monkeypatch.setenv("RESVG", "/custom renderer/resvg")
    monkeypatch.setattr(pockettopo, "convert_package", convert)
    assert pockettopo.main(["convert", str(CARDINAL), "--output", str(tmp_path / "out")]) == 0
    assert paths == ["/custom renderer/resvg"]
    assert capsys.readouterr().err == ""


@pytest.mark.parametrize(
    "error",
    [
        RenderingError("renderer failed"),
        PermissionError("write denied"),
        FileExistsError("output already exists"),
        ValueError("invalid drawing settings"),
    ],
)
def test_conversion_failures_return_exit_one_without_a_success_message(
    tmp_path,
    monkeypatch,
    capsys,
    error,
):
    def fail(*args, **options):
        raise error

    monkeypatch.setattr(pockettopo, "convert_package", fail)
    assert pockettopo.main(["convert", str(CARDINAL), "--output", str(tmp_path / "out")]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == f"ERROR: {error}\n"


@pytest.mark.parametrize(
    "arguments", [[], ["convert", str(CARDINAL)], ["inspect", str(CARDINAL), "--unknown"]]
)
def test_missing_or_unknown_arguments_are_argparse_errors(arguments, capsys):
    with pytest.raises(SystemExit) as error:
        pockettopo.main(arguments)
    assert error.value.code == 2
    assert "usage:" in capsys.readouterr().err


def test_help_documents_collision_policy_and_renderer(capsys):
    with pytest.raises(SystemExit) as error:
        pockettopo.main(["convert", "--help"])
    assert error.value.code == 0
    help_text = " ".join(capsys.readouterr().out.split())
    assert "existing paths are refused" in help_text
    assert "resvg 0.48.1" in help_text


@pytest.mark.parametrize("entrypoint", ["module", "installed"])
def test_entrypoints_emit_unicode_source_as_portable_json_under_cp1252(entrypoint):
    if entrypoint == "module":
        command = [sys.executable, "-m", "jktz.cli.pockettopo"]
    else:
        executable = shutil.which("jktz-pockettopo")
        assert executable is not None, "uv must install the declared jktz-pockettopo entrypoint"
        command = [executable]
    result = subprocess.run(
        [*command, "inspect", str(UNICODE)],
        cwd=ROOT,
        env=dict(os.environ, PYTHONIOENCODING="cp1252"),
        capture_output=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stderr.decode("cp1252")
    assert result.stderr == b""
    assert result.stdout.isascii()
    document = json.loads(result.stdout)
    assert document["source"]["records"]["trips"][1]["comment"] == "Unicode trip: Zażółć gęślą jaźń"
    assert document["report"]["trips"][1]["used_date"] is None


def test_module_main_guard_propagates_the_inspection_status(monkeypatch, capsys):
    # Execute the entrypoint guard under coverage as well as the real subprocess above.
    monkeypatch.setattr(sys, "argv", ["jktz-pockettopo", "inspect", str(CARDINAL)])
    with pytest.raises(SystemExit) as error:
        runpy.run_path(str(ROOT / "src/jktz/cli/pockettopo.py"), run_name="__main__")
    assert error.value.code == 0
    assert set(json.loads(capsys.readouterr().out)) == {"source", "report"}
