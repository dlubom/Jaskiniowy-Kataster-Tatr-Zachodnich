#!/usr/bin/env python3
"""Convert coordinates between WGS84 UTM Zone 34N (EPSG:32634) and WGS84 geographic (EPSG:4326).

UTM Zone 34N is the projection used by the JKTZ shapefile/3D exports
(see exports/caves/*.prj). This script enables round-trips between the
station coordinates printed by `survexport --csv` (UTM34N easting / northing / altitude)
and the WGS84 lon/lat values expected by Walls `#fix` directives.

Usage:
    python3 utm34n_wgs84.py to-wgs84 <easting> <northing> [<elevation>]
    python3 utm34n_wgs84.py to-utm   <lon>     <lat>      [<elevation>]

Examples:
    # UTM34N -> WGS84 (e.g. ot_0 of Mietusia Wyznia from the 3D export)
    python3 utm34n_wgs84.py to-wgs84 419557.06 5455328.95 1391.87

    # WGS84 -> UTM34N (e.g. an existing #fix line)
    python3 utm34n_wgs84.py to-utm 19.8947380569 49.2454436384 1391.87
"""
import sys

try:
    from pyproj import Transformer
except ImportError:
    print("Error: pyproj is not installed.", file=sys.stderr)
    print("Install it with:  pip3 install pyproj", file=sys.stderr)
    sys.exit(1)

# UTM34N ranges for the Tatra Mountains region
TATRA_E_MIN, TATRA_E_MAX = 410_000, 450_000
TATRA_N_MIN, TATRA_N_MAX = 5_440_000, 5_475_000

# WGS84 bounding box for the Tatra Mountains (PL + SK)
TATRA_LAT_MIN, TATRA_LAT_MAX = 49.15, 49.30
TATRA_LON_MIN, TATRA_LON_MAX = 19.75, 20.15


def utm34n_to_wgs84(easting, northing, elevation=None):
    """Convert UTM Zone 34N (EPSG:32634) easting/northing to WGS84 lon/lat.

    Args:
        easting: UTM34N easting in meters
        northing: UTM34N northing in meters
        elevation: optional elevation in meters, passed through unchanged

    Returns:
        (lon, lat, elevation) tuple. elevation is None if not provided.
    """
    tr = Transformer.from_crs(32634, 4326, always_xy=True)
    lon, lat = tr.transform(easting, northing)
    return lon, lat, elevation


def wgs84_to_utm34n(lon, lat, elevation=None):
    """Convert WGS84 lon/lat (EPSG:4326) to UTM Zone 34N easting/northing.

    Args:
        lon: WGS84 longitude in decimal degrees
        lat: WGS84 latitude in decimal degrees
        elevation: optional elevation in meters, passed through unchanged

    Returns:
        (easting, northing, elevation) tuple. elevation is None if not provided.
    """
    tr = Transformer.from_crs(4326, 32634, always_xy=True)
    easting, northing = tr.transform(lon, lat)
    return easting, northing, elevation


def _warn_utm(easting, northing):
    warnings = []
    if not (TATRA_E_MIN <= easting <= TATRA_E_MAX):
        warnings.append(
            f"WARNING: easting={easting} outside Tatra UTM34N range "
            f"({TATRA_E_MIN}-{TATRA_E_MAX})"
        )
    if not (TATRA_N_MIN <= northing <= TATRA_N_MAX):
        warnings.append(
            f"WARNING: northing={northing} outside Tatra UTM34N range "
            f"({TATRA_N_MIN}-{TATRA_N_MAX})"
        )
    return warnings


def _warn_wgs84(lon, lat):
    warnings = []
    if not (TATRA_LON_MIN <= lon <= TATRA_LON_MAX):
        warnings.append(
            f"WARNING: lon={lon} outside Tatra range "
            f"({TATRA_LON_MIN}-{TATRA_LON_MAX})"
        )
    if not (TATRA_LAT_MIN <= lat <= TATRA_LAT_MAX):
        warnings.append(
            f"WARNING: lat={lat} outside Tatra range "
            f"({TATRA_LAT_MIN}-{TATRA_LAT_MAX})"
        )
    return warnings


def _usage_and_exit():
    print(__doc__.strip(), file=sys.stderr)
    sys.exit(1)


def main():
    if len(sys.argv) < 4:
        _usage_and_exit()

    direction = sys.argv[1]
    a = float(sys.argv[2])
    b = float(sys.argv[3])
    elev = sys.argv[4] if len(sys.argv) > 4 else None

    if direction == "to-wgs84":
        for w in _warn_utm(a, b):
            print(w, file=sys.stderr)
        lon, lat, _ = utm34n_to_wgs84(a, b, elev)
        for w in _warn_wgs84(lon, lat):
            print(w, file=sys.stderr)
        elev_str = f"  elev={elev}" if elev else ""
        print(f"lon={lon:.10f}  lat={lat:.10f}{elev_str}")
        elev_fix = f"\t{elev}m" if elev else ""
        print(f"#fix\tSTATION\tE{lon:.10f}\tN{lat:.10f}{elev_fix}")
    elif direction == "to-utm":
        # a=lon, b=lat
        for w in _warn_wgs84(a, b):
            print(w, file=sys.stderr)
        easting, northing, _ = wgs84_to_utm34n(a, b, elev)
        for w in _warn_utm(easting, northing):
            print(w, file=sys.stderr)
        elev_str = f"  elev={elev}" if elev else ""
        print(f"easting={easting:.2f}  northing={northing:.2f}{elev_str}")
    else:
        print(f"Error: unknown direction '{direction}'. Use 'to-wgs84' or 'to-utm'.",
              file=sys.stderr)
        _usage_and_exit()


if __name__ == "__main__":
    main()
