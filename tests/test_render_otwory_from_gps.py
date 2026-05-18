from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "render_otwory_from_gps.py"
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


def test_renderer_writes_fix_from_template_object_id(tmp_path: Path) -> None:
    template = tmp_path / "OTWORY.SRV.j2"
    output = tmp_path / "OTWORY.SRV"
    measurements = tmp_path / "best-measurements.csv"
    template.write_text("{{ gps_fix('Cave:0', 'OBJ-1') }}\n", encoding="utf-8")
    measurements.write_text(
        "object_id,lon,lat,elevation_m\nOBJ-1,19.1,49.2,123.4\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--template",
            str(template),
            "--csv",
            str(measurements),
            "--output",
            str(output),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert output.read_text(encoding="utf-8") == "#fix\tCave:0\tE19.1\tN49.2\t123.4m\n"
    assert "GPS fixes: 1" in result.stdout


def test_renderer_fails_when_required_measurement_value_is_empty(tmp_path: Path) -> None:
    template = tmp_path / "OTWORY.SRV.j2"
    output = tmp_path / "OTWORY.SRV"
    measurements = tmp_path / "best-measurements.csv"
    template.write_text("{{ gps_fix('Cave:0', 'OBJ-1') }}\n", encoding="utf-8")
    measurements.write_text(
        "object_id,lon,lat,elevation_m\nOBJ-1,19.1,49.2,\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--template",
            str(template),
            "--csv",
            str(measurements),
            "--output",
            str(output),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "OBJ-1 has empty elevation_m" in result.stderr
    assert not output.exists()


def test_renderer_keeps_commented_gps_fix_commented(tmp_path: Path) -> None:
    template = tmp_path / "OTWORY.SRV.j2"
    output = tmp_path / "OTWORY.SRV"
    measurements = tmp_path / "best-measurements.csv"
    template.write_text("; {{ gps_fix('Cave:0', 'OBJ-1') }}\n", encoding="utf-8")
    measurements.write_text(
        "object_id,lon,lat,elevation_m\nOBJ-1,19.1,49.2,123.4\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--template",
            str(template),
            "--csv",
            str(measurements),
            "--output",
            str(output),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
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
