from __future__ import annotations

import io
from pathlib import Path
from unittest.mock import Mock

import pytest

from jktz.cli import build_zip, exports, validate
from jktz.exports.tools import ExternalToolError
from jktz.reporting import CheckFailed


@pytest.mark.parametrize(
    ("failure", "result", "message", "stream"),
    [
        (None, 0, "Validation Passed", "out"),
        (CheckFailed("bad survey"), 1, "bad survey", "out"),
        (ExternalToolError("missing cavern"), 1, "ERROR: missing cavern", "err"),
    ],
)
def test_validation_cli_status_and_error_channel(
    monkeypatch, capsys, failure, result, message, stream
):
    run = Mock(side_effect=failure)
    monkeypatch.setattr(validate, "run_validation", run)

    assert validate.main() == result

    run.assert_called_once_with()
    output = capsys.readouterr()
    assert message in getattr(output, stream)
    assert ("Validation Passed" in output.out) == (failure is None)


def test_validate_configures_supported_streams_and_accepts_stringio(monkeypatch):
    stream = Mock()
    monkeypatch.setattr(validate.sys, "stdout", stream)
    monkeypatch.setattr(validate.sys, "stderr", io.StringIO())

    validate._reconfigure_streams_utf8()

    stream.reconfigure.assert_called_once_with(
        encoding="utf-8", errors="replace", line_buffering=True
    )


@pytest.mark.parametrize(
    ("args", "version", "outdir"),
    [([], "local", Path("exports")), (["v1.2.3", "other"], "v1.2.3", Path("other"))],
)
def test_exports_cli_passes_requested_destination(monkeypatch, args, version, outdir):
    monkeypatch.setattr("sys.argv", ["jktz-exports", *args])
    run = Mock()
    monkeypatch.setattr(exports.pipeline, "run_exports", run)

    assert exports.main() == 0

    run.assert_called_once_with(version=version, outdir=outdir)


def test_exports_cli_reports_external_failure(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["jktz-exports"])
    monkeypatch.setattr(
        exports.pipeline, "run_exports", Mock(side_effect=ExternalToolError("broken"))
    )

    assert exports.main() == 1
    assert capsys.readouterr().err == "ERROR: broken\n"


@pytest.mark.parametrize("destination", [None, "custom.zip"])
def test_zip_cli_preserves_version_and_optional_destination(monkeypatch, destination):
    args = ["jktz-build-zip", "v1.2.3"] + ([destination] if destination else [])
    monkeypatch.setattr("sys.argv", args)
    build = Mock()
    monkeypatch.setattr(build_zip, "build_release_zip", build)

    assert build_zip.main() == 0

    build.assert_called_once_with(
        version="v1.2.3", zip_path=Path(destination) if destination else None
    )


def test_zip_cli_requires_version_before_building(monkeypatch):
    monkeypatch.setattr("sys.argv", ["jktz-build-zip"])
    build = Mock()
    monkeypatch.setattr(build_zip, "build_release_zip", build)

    with pytest.raises(SystemExit) as result:
        build_zip.main()

    assert result.value.code == 2
    build.assert_not_called()
