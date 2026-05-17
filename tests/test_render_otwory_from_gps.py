from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "render_otwory_from_gps.py"
PROJECT_TEMPLATE = REPO_ROOT / "Poligony" / "OTWORY.SRV.j2"
PROJECT_SRV = REPO_ROOT / "Poligony" / "OTWORY.SRV"


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


def test_project_template_embeds_object_ids_for_every_fix() -> None:
    template = PROJECT_TEMPLATE.read_text(encoding="utf-8")
    source_fix_count = sum(
        1
        for line in PROJECT_SRV.read_text(encoding="utf-8").splitlines()
        if line.startswith("#fix\t")
    )
    calls = re.findall(
        r"{{ gps_fix\('([^']+)', '([^']+)'(?:, suffix='[^']+')?\) }}",
        template,
    )

    assert len(calls) == source_fix_count == 87
    assert all(station and object_id for station, object_id in calls)
    assert "fallback" not in template.lower()
    assert ("BandziochKom:136", "LEJ-0002") in calls
    assert ("Wysoka7Progow:W7-200", "KSW-0153") in calls
