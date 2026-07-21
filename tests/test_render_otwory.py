from __future__ import annotations

import re
from pathlib import Path, PureWindowsPath

from jktz.cli import render_otwory
from jktz.entrances.render import RenderResult

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
