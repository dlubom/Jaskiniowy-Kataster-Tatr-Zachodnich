from __future__ import annotations

import io
import json
import re
import urllib.error
from pathlib import Path, PureWindowsPath

import pytest

from jktz.cli import render_otwory
from jktz.entrances import render
from jktz.entrances.render import RenderError, RenderResult

REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_TEMPLATE = REPO_ROOT / "Poligony" / "OTWORY.SRV.j2"
GPS_FIX_CALL_RE = re.compile(r"{{ gps_fix\('([^']+)', '([^']+)'(?:, suffix='[^']+')?\) }}")
ACTIVE_GPS_FIX_CALL_RE = re.compile(
    r"^{{ gps_fix\('([^']+)', '([^']+)'(?:, suffix='[^']+')?\) }}$",
    re.MULTILINE,
)
COMMENTED_GPS_FIX_CALL_RE = re.compile(
    r"^;\s+{{ gps_fix\('([^']+)', '([^']+)'(?:, suffix='[^']+')?\) }}$",
    re.MULTILINE,
)
ENTRANCE_FLAG_RE = re.compile(r"^#flag\t([^\t]+)\t/ENTRANCE$", re.MULTILINE)


@pytest.fixture(autouse=True)
def offline_renderer(monkeypatch):
    """A missing download mock is a test failure, including inside mutant runs."""

    def unexpected_network(*_args, **_kwargs):
        raise AssertionError("Renderer tests must not use the network")

    monkeypatch.setattr(render.urllib.request, "urlopen", unexpected_network)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)


def test_renderer_cli_prints_portable_output_path(monkeypatch, capsys) -> None:
    def fake_render(**_kwargs) -> RenderResult:
        return RenderResult(
            output=PureWindowsPath("Poligony/OTWORY.SRV"),
            source="gps-kataster@v1",
            gps_fixes=87,
        )

    monkeypatch.setattr(render_otwory, "render_entrances", fake_render)

    return_code = render_otwory.main(["--check"])

    assert return_code == 0
    assert capsys.readouterr().out == (
        "Checked Poligony/OTWORY.SRV from gps-kataster@v1\nGPS fixes: 87\n"
    )


def test_renderer_writes_fix_from_template_object_id(tmp_path: Path, capsys) -> None:
    template = tmp_path / "OTWORY.SRV.j2"
    output = tmp_path / "OTWORY.SRV"
    measurements = tmp_path / "best-measurements.csv"
    template.write_text("{{ gps_fix('Cave:0', 'OBJ-1') }}\n", encoding="utf-8")
    measurements.write_text(
        "object_id,lon,lat,elevation_m\nOBJ-1,19.1,49.2,123.4\n",
        encoding="utf-8",
    )

    return_code = render_otwory.main(
        [
            "--template",
            str(template),
            "--csv",
            str(measurements),
            "--output",
            str(output),
        ],
    )
    captured = capsys.readouterr()

    assert return_code == 0, captured.err
    assert output.read_text(encoding="utf-8") == "#fix\tCave:0\tE19.1\tN49.2\t123.4m\n"
    assert "GPS fixes: 1" in captured.out


def test_renderer_fails_when_required_measurement_value_is_empty(tmp_path: Path, capsys) -> None:
    template = tmp_path / "OTWORY.SRV.j2"
    output = tmp_path / "OTWORY.SRV"
    measurements = tmp_path / "best-measurements.csv"
    template.write_text("{{ gps_fix('Cave:0', 'OBJ-1') }}\n", encoding="utf-8")
    measurements.write_text(
        "object_id,lon,lat,elevation_m\nOBJ-1,19.1,49.2,\n",
        encoding="utf-8",
    )

    return_code = render_otwory.main(
        [
            "--template",
            str(template),
            "--csv",
            str(measurements),
            "--output",
            str(output),
        ],
    )
    captured = capsys.readouterr()

    assert return_code == 1
    assert "OBJ-1 has empty elevation_m" in captured.err
    assert not output.exists()


def test_renderer_check_passes_when_output_is_current(tmp_path: Path, capsys) -> None:
    template = tmp_path / "OTWORY.SRV.j2"
    output = tmp_path / "OTWORY.SRV"
    measurements = tmp_path / "best-measurements.csv"
    template.write_text("{{ gps_fix('Cave:0', 'OBJ-1') }}\n", encoding="utf-8")
    measurements.write_text(
        "object_id,lon,lat,elevation_m\nOBJ-1,19.1,49.2,123.4\n",
        encoding="utf-8",
    )
    output.write_text("#fix\tCave:0\tE19.1\tN49.2\t123.4m\n", encoding="utf-8")

    return_code = render_otwory.main(
        [
            "--template",
            str(template),
            "--csv",
            str(measurements),
            "--output",
            str(output),
            "--check",
        ],
    )
    captured = capsys.readouterr()

    assert return_code == 0, captured.err
    assert output.read_text(encoding="utf-8") == "#fix\tCave:0\tE19.1\tN49.2\t123.4m\n"
    assert "Checked" in captured.out


def test_renderer_check_fails_when_output_is_stale(tmp_path: Path, capsys) -> None:
    template = tmp_path / "OTWORY.SRV.j2"
    output = tmp_path / "OTWORY.SRV"
    measurements = tmp_path / "best-measurements.csv"
    template.write_text("{{ gps_fix('Cave:0', 'OBJ-1') }}\n", encoding="utf-8")
    measurements.write_text(
        "object_id,lon,lat,elevation_m\nOBJ-1,19.1,49.2,123.4\n",
        encoding="utf-8",
    )
    output.write_text("#fix\tCave:0\tE19.0\tN49.2\t123.4m\n", encoding="utf-8")

    return_code = render_otwory.main(
        [
            "--template",
            str(template),
            "--csv",
            str(measurements),
            "--output",
            str(output),
            "--check",
        ],
    )
    captured = capsys.readouterr()

    assert return_code == 1
    assert "is not up to date" in captured.err
    assert "---" in captured.err
    assert "+#fix\tCave:0\tE19.1\tN49.2\t123.4m" in captured.err
    assert output.read_text(encoding="utf-8") == "#fix\tCave:0\tE19.0\tN49.2\t123.4m\n"


def test_renderer_keeps_commented_gps_fix_commented(tmp_path: Path, capsys) -> None:
    template = tmp_path / "OTWORY.SRV.j2"
    output = tmp_path / "OTWORY.SRV"
    measurements = tmp_path / "best-measurements.csv"
    template.write_text("; {{ gps_fix('Cave:0', 'OBJ-1') }}\n", encoding="utf-8")
    measurements.write_text(
        "object_id,lon,lat,elevation_m\nOBJ-1,19.1,49.2,123.4\n",
        encoding="utf-8",
    )

    return_code = render_otwory.main(
        [
            "--template",
            str(template),
            "--csv",
            str(measurements),
            "--output",
            str(output),
        ],
    )
    captured = capsys.readouterr()

    assert return_code == 0, captured.err
    assert output.read_text(encoding="utf-8") == "; #fix\tCave:0\tE19.1\tN49.2\t123.4m\n"


def test_project_template_embeds_unique_object_ids_for_gps_fixes() -> None:
    template = PROJECT_TEMPLATE.read_text(encoding="utf-8")
    calls = GPS_FIX_CALL_RE.findall(template)
    gps_fix_stations = {station for station, _object_id in calls}
    gps_fix_object_ids = [object_id for _station, object_id in calls]
    entrance_stations = set(ENTRANCE_FLAG_RE.findall(template))

    assert calls
    assert all(station and object_id for station, object_id in calls)
    assert len(gps_fix_stations) == len(calls)
    assert len(set(gps_fix_object_ids)) == len(gps_fix_object_ids)
    assert gps_fix_stations <= entrance_stations
    assert not re.search(r"(?m)^#fix\t", template)
    assert "fallback" not in template.lower()


def test_project_template_uses_only_reviewed_gnss_for_active_wysoka_fix() -> None:
    template = PROJECT_TEMPLATE.read_text(encoding="utf-8")
    active_wysoka_calls = [
        call
        for call in ACTIVE_GPS_FIX_CALL_RE.findall(template)
        if call[0].startswith("Wysoka7Progow:")
    ]
    commented_wysoka_calls = {
        call
        for call in COMMENTED_GPS_FIX_CALL_RE.findall(template)
        if call[0].startswith("Wysoka7Progow:")
    }

    assert active_wysoka_calls == [("Wysoka7Progow:W7-0", "KSW-0189")]
    assert commented_wysoka_calls == {
        ("Wysoka7Progow:W7-200", "KSW-0153"),
        ("Wysoka7Progow:W7-500", "KSW-0123"),
    }


def test_project_template_keeps_ziobrowa_second_entrance_unconstrained() -> None:
    template = PROJECT_TEMPLATE.read_text(encoding="utf-8")
    active_calls = set(ACTIVE_GPS_FIX_CALL_RE.findall(template))
    commented_calls = set(COMMENTED_GPS_FIX_CALL_RE.findall(template))

    assert ("Ziobrowa:5.24", "KSW-0177") not in active_calls
    assert ("Ziobrowa:5.24", "KSW-0177") in commented_calls
    assert "Walls/Survex policzyl ten otwor z sieci pomiarowej" in template


@pytest.mark.parametrize(
    ("rows", "error"),
    [
        ("OBJ-1,19.1,49.2,123.4\nOBJ-1,19.2,49.3,234.5\n", "duplicate object_id OBJ-1"),
        ("OBJ-1,19.1,49.2\n", "OBJ-1 has empty elevation_m"),
    ],
)
def test_invalid_csv_fails_cleanly_without_replacing_snapshot(
    tmp_path: Path, capsys, rows: str, error: str
) -> None:
    template = tmp_path / "OTWORY.SRV.j2"
    output = tmp_path / "OTWORY.SRV"
    measurements = tmp_path / "best-measurements.csv"
    template.write_text("{{ gps_fix('Cave:0', 'OBJ-1') }}\n", encoding="utf-8")
    measurements.write_text("object_id,lon,lat,elevation_m\n" + rows, encoding="utf-8")
    output.write_bytes(b"previous reviewed snapshot\n")

    return_code = render_otwory.main(
        ["--template", str(template), "--csv", str(measurements), "--output", str(output)]
    )

    assert return_code == 1
    assert error in capsys.readouterr().err
    assert output.read_bytes() == b"previous reviewed snapshot\n"


@pytest.mark.parametrize(
    ("csv_text", "error"),
    [
        ("", "missing required columns"),
        ("object_id,lon,lat\nOBJ-1,19.1,49.2\n", "elevation_m"),
        ("object_id,lon,lat,elevation_m\n", "no best-measurements rows"),
        ("object_id,lon,lat,elevation_m\n,19.1,49.2,1000\n", "no best-measurements rows"),
        ("object_id,lon,lat,elevation_m\nOBJ-2,19.1,49.2,1000\n", "missing in"),
    ],
)
def test_renderer_rejects_missing_source_data(tmp_path, csv_text, error):
    template = tmp_path / "template"
    measurements = tmp_path / "measurements.csv"
    output = tmp_path / "output"
    template.write_text("{{ gps_fix('Cave:0', 'OBJ-1') }}")
    measurements.write_text(csv_text)

    with pytest.raises(RenderError, match=error):
        render.render_entrances(template_path=template, csv_path=measurements, output_path=output)

    assert not output.exists()


@pytest.mark.parametrize(
    "expression",
    [
        "'Cave:0'",
        "'', 'OBJ-1'",
        "12, 'OBJ-1'",
        "'Cave:0', ''",
        "'Cave:0', 12",
        "'Cave:0', 'OBJ-1', unexpected=True",
        "'Cave:0', 'OBJ-1', suffix=unknown_name",
        "'Cave:0', 'OBJ-1', suffix=",
        "'Cave:0', 'OBJ-1', suffix=str('bad')",
    ],
)
def test_renderer_rejects_invalid_or_executable_template_arguments(tmp_path, expression):
    template = tmp_path / "template"
    measurements = tmp_path / "measurements.csv"
    output = tmp_path / "output"
    template.write_text("{{ gps_fix(" + expression + ") }}")
    measurements.write_text("object_id,lon,lat,elevation_m\nOBJ-1,19.1,49.2,1000\n")

    with pytest.raises(RenderError):
        render.render_entrances(template_path=template, csv_path=measurements, output_path=output)

    assert not output.exists()


@pytest.mark.parametrize("value", ["nan", "inf", "1e3", "49,2"])
def test_renderer_rejects_non_decimal_coordinates(tmp_path, value):
    template = tmp_path / "template"
    measurements = tmp_path / "measurements.csv"
    output = tmp_path / "output"
    template.write_text("{{ gps_fix('Cave:0', 'OBJ-1') }}")
    measurements.write_text(f'object_id,lon,lat,elevation_m\nOBJ-1,19.1,"{value}",1000\n')

    with pytest.raises(RenderError, match="not a decimal number"):
        render.render_entrances(template_path=template, csv_path=measurements, output_path=output)

    assert not output.exists()


def test_renderer_downloads_named_release_asset_and_reports_provenance(tmp_path, monkeypatch):
    template = tmp_path / "template"
    output = tmp_path / "output"
    template.write_text("{{ gps_fix('Cave:0', 'OBJ-1', suffix=' /gps') }}\n")
    release = {
        "tag_name": "v1.2.3",
        "assets": [
            None,
            {"name": "other.csv"},
            {
                "name": "best-measurements.csv",
                "browser_download_url": "https://example.test/best.csv",
            },
        ],
    }
    responses = [
        json.dumps(release).encode(),
        b"\xef\xbb\xbfobject_id,lon,lat,elevation_m\nOBJ-1, 19.1 ,49.2,1000\n",
    ]
    requests = []

    def urlopen(request, *, timeout):
        requests.append((request, timeout))
        return io.BytesIO(responses.pop(0))

    monkeypatch.setenv("GITHUB_TOKEN", "test-token")
    monkeypatch.setattr(render.urllib.request, "urlopen", urlopen)

    result = render.render_entrances(
        template_path=template, output_path=output, github_repo="owner/gps"
    )

    assert output.read_text() == "#fix\tCave:0\tE19.1\tN49.2\t1000m /gps\n"
    assert result.source == "owner/gps@v1.2.3"
    assert result.gps_fixes == 1
    assert [request.full_url for request, _ in requests] == [
        "https://api.github.com/repos/owner/gps/releases/latest",
        "https://example.test/best.csv",
    ]
    assert all(timeout == 60 for _, timeout in requests)
    assert all(
        request.get_header("Authorization") == "Bearer test-token" for request, _ in requests
    )


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        (b"not json", "Expected JSON"),
        (b"[]", "Expected JSON object"),
        (b"{}", "no asset list"),
        (b'{"assets": []}', "no best-measurements.csv asset"),
        (b'{"assets": [{"name": "best-measurements.csv"}]}', "missing browser_download_url"),
    ],
)
def test_renderer_rejects_invalid_release_response(tmp_path, monkeypatch, payload, error):
    monkeypatch.setattr(
        render.urllib.request, "urlopen", lambda *_args, **_kwargs: io.BytesIO(payload)
    )

    with pytest.raises(RenderError, match=error):
        render.render_entrances(output_path=tmp_path / "output")

    assert not (tmp_path / "output").exists()


@pytest.mark.parametrize("fail_on_download", [False, True])
def test_renderer_network_failures_preserve_existing_snapshot(
    tmp_path, monkeypatch, fail_on_download
):
    output = tmp_path / "output"
    output.write_bytes(b"reviewed snapshot")

    def urlopen(request, **_kwargs):
        if fail_on_download and "/releases/latest" in request.full_url:
            return io.BytesIO(
                b'{"assets": [{"name": "best-measurements.csv", '
                b'"browser_download_url": "https://example.test/best.csv"}]}'
            )
        raise urllib.error.URLError("offline")

    monkeypatch.setattr(render.urllib.request, "urlopen", urlopen)

    with pytest.raises(RenderError, match="Cannot download" if fail_on_download else "Cannot read"):
        render.render_entrances(output_path=output)

    assert output.read_bytes() == b"reviewed snapshot"


def test_check_missing_snapshot_does_not_create_it(tmp_path):
    template = tmp_path / "template"
    measurements = tmp_path / "measurements.csv"
    output = tmp_path / "output"
    template.write_text("{{ gps_fix('Cave:0', 'OBJ-1') }}")
    measurements.write_text("object_id,lon,lat,elevation_m\nOBJ-1,19.1,49.2,1000\n")

    with pytest.raises(RenderError, match="does not exist"):
        render.render_entrances(
            template_path=template, csv_path=measurements, output_path=output, check=True
        )

    assert not output.exists()


@pytest.mark.parametrize(
    ("github_token", "gh_token", "expected_auth"),
    [
        (None, None, None),
        (None, "gh-test", "Bearer gh-test"),
        ("github-test", "gh-test", "Bearer github-test"),
    ],
)
def test_release_request_headers_support_both_token_sources(
    monkeypatch, github_token, gh_token, expected_auth
):
    if github_token:
        monkeypatch.setenv("GITHUB_TOKEN", github_token)
    if gh_token:
        monkeypatch.setenv("GH_TOKEN", gh_token)

    request = render._request("https://api.github.com/repos/owner/gps/releases/latest")

    assert request.get_header("Authorization") == expected_auth
    assert request.get_header("Accept") == "application/vnd.github+json"
    assert request.get_header("User-agent")


def test_local_csv_keeps_provenance_and_skips_unidentified_rows(tmp_path):
    template = tmp_path / "template"
    measurements = tmp_path / "measurements.csv"
    output = tmp_path / "output"
    template.write_text("{{ gps_fix('Cave:0', 'OBJ-1') }}\n")
    measurements.write_text(
        "object_id,lon,lat,elevation_m\n,19.2,49.3,1100\nOBJ-1,19.1,49.2,1000\n"
    )

    result = render.render_entrances(
        template_path=template, csv_path=measurements, output_path=output
    )

    assert result.source == str(measurements)
    assert result.output == output
    assert result.gps_fixes == 1
    assert output.read_text() == "#fix\tCave:0\tE19.1\tN49.2\t1000m\n"
