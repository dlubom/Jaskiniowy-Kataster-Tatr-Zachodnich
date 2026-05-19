from __future__ import annotations

import re
from pathlib import Path

from jktz.reporting import CheckFailed
from jktz.validation.constants import (
    TATRA_ELEV_MAX,
    TATRA_ELEV_MIN,
    TATRA_LAT_MAX,
    TATRA_LAT_MIN,
    TATRA_LON_MAX,
    TATRA_LON_MIN,
)

_FIX_RE = re.compile(r"^#fix[ \t]+(\S+)\s+(.*)$")
_LON_RE = re.compile(r"^E(-?[0-9].*)$")
_LAT_RE = re.compile(r"^N(-?[0-9].*)$")
_ELEV_RE = re.compile(r"^(-?[0-9].*?)m$")


def _parse_float(s: str) -> float | None:
    try:
        return float(s)
    except ValueError:
        return None


def check(otwory_path: Path = Path("Poligony/OTWORY.SRV")) -> None:
    """Every ``#fix`` entry in OTWORY.SRV must lie inside the Tatras extent.

    Catches swapped lat/lon, decimal-magnitude errors, wrong-region coordinates
    (e.g. unconverted PUWG-1992 meters), and feet-vs-meters elevation mistakes.
    """
    errors: list[str] = []
    text = otwory_path.read_text(encoding="latin-1")
    for line_num, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.rstrip("\r")
        m = _FIX_RE.match(line)
        if not m:
            continue
        station = m.group(1)
        fields = m.group(2).split()
        lon: float | None = None
        lat: float | None = None
        elev: float | None = None
        for field in fields:
            if (fm := _LON_RE.match(field)) and lon is None:
                lon = _parse_float(fm.group(1))
            elif (fm := _LAT_RE.match(field)) and lat is None:
                lat = _parse_float(fm.group(1))
            elif (fm := _ELEV_RE.match(field)) and elev is None:
                elev = _parse_float(fm.group(1))

        msgs: list[str] = []
        if lon is None:
            msgs.append("    missing longitude (E<value>)")
        elif lon < TATRA_LON_MIN or lon > TATRA_LON_MAX:
            msgs.append(f"    lon {lon:.6f} outside [{TATRA_LON_MIN:.2f}, {TATRA_LON_MAX:.2f}]")

        if lat is None:
            msgs.append("    missing latitude (N<value>)")
        elif lat < TATRA_LAT_MIN or lat > TATRA_LAT_MAX:
            msgs.append(f"    lat {lat:.6f} outside [{TATRA_LAT_MIN:.2f}, {TATRA_LAT_MAX:.2f}]")

        if elev is None:
            msgs.append("    missing elevation (<value>m)")
        elif elev < TATRA_ELEV_MIN or elev > TATRA_ELEV_MAX:
            msgs.append(
                f"    elevation {elev:.2f} m outside [{TATRA_ELEV_MIN}, {TATRA_ELEV_MAX}] m"
            )

        if msgs:
            errors.append(f"  {otwory_path.as_posix()}:{line_num}  {station}")
            errors.extend(msgs)

    if errors:
        raise CheckFailed("ERROR: #fix entries with invalid coordinates:\n" + "\n".join(errors))
