#!/usr/bin/env python3
"""Convert coordinates from Polish EPSG:2180 (PUWG 1992) to WGS84 (EPSG:4326).

Polish geodetic convention: X = northing, Y = easting (opposite to common intuition).
The script validates that inputs and output fall within the Tatra Mountains region.

Usage:
    python3 gnss_to_wgs84.py <X_northing> <Y_easting> [<elevation>]

Example (from a GNSS report in uklad 1992):
    python3 gnss_to_wgs84.py 152168.79 564375.07 1486.69

Output:
    lat=49.23364130  lon=19.88454604  elev=1486.69
    #fix	STATION	E19.88454604	N49.23364130	1486.69
"""
import sys

try:
    from pyproj import Transformer
except ImportError:
    print("Error: pyproj is not installed.", file=sys.stderr)
    print("Install it with:  pip3 install pyproj", file=sys.stderr)
    sys.exit(1)

# EPSG:2180 ranges for the Tatra Mountains region
# X (northing): ~140 000 - 170 000
# Y (easting):  ~550 000 - 580 000
TATRA_X_MIN, TATRA_X_MAX = 140_000, 170_000
TATRA_Y_MIN, TATRA_Y_MAX = 550_000, 580_000

# WGS84 extent for the Tatra Mountains (PL + SK)
TATRA_LAT_MIN, TATRA_LAT_MAX = 49.15, 49.30
TATRA_LON_MIN, TATRA_LON_MAX = 19.75, 20.15


def validate_input(x, y):
    """Warn if X/Y look swapped or out of Tatra range."""
    warnings = []

    x_ok = TATRA_X_MIN <= x <= TATRA_X_MAX
    y_ok = TATRA_Y_MIN <= y <= TATRA_Y_MAX

    if not x_ok and not y_ok:
        # Maybe both are completely out of range
        x_as_y = TATRA_Y_MIN <= x <= TATRA_Y_MAX
        y_as_x = TATRA_X_MIN <= y <= TATRA_X_MAX
        if x_as_y and y_as_x:
            warnings.append(
                f"WARNING: X/Y look SWAPPED! X={x} is in easting range, Y={y} is in northing range.\n"
                f"  Expected: X (northing) ~ {TATRA_X_MIN}-{TATRA_X_MAX}, Y (easting) ~ {TATRA_Y_MIN}-{TATRA_Y_MAX}\n"
                f"  Try: python3 gnss_to_wgs84.py {y} {x}"
            )
        else:
            warnings.append(
                f"WARNING: coordinates out of Tatra range for EPSG:2180.\n"
                f"  X={x} (expected northing ~ {TATRA_X_MIN}-{TATRA_X_MAX})\n"
                f"  Y={y} (expected easting ~ {TATRA_Y_MIN}-{TATRA_Y_MAX})"
            )
    elif not x_ok:
        warnings.append(
            f"WARNING: X={x} outside Tatra northing range ({TATRA_X_MIN}-{TATRA_X_MAX})"
        )
    elif not y_ok:
        warnings.append(
            f"WARNING: Y={y} outside Tatra easting range ({TATRA_Y_MIN}-{TATRA_Y_MAX})"
        )

    return warnings


def validate_output(lat, lon):
    """Warn if WGS84 result is outside the Tatra Mountains."""
    if not (TATRA_LAT_MIN <= lat <= TATRA_LAT_MAX and TATRA_LON_MIN <= lon <= TATRA_LON_MAX):
        return [
            f"WARNING: result ({lat:.6f}N, {lon:.6f}E) is outside the Tatra Mountains!\n"
            f"  Expected: lat {TATRA_LAT_MIN}-{TATRA_LAT_MAX}, lon {TATRA_LON_MIN}-{TATRA_LON_MAX}"
        ]
    return []


def convert(x_northing, y_easting):
    tr = Transformer.from_crs(2180, 4326, always_xy=True)
    lon, lat = tr.transform(y_easting, x_northing)
    return lat, lon


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 gnss_to_wgs84.py <X_northing> <Y_easting> [<elevation>]")
        print()
        print("  X = northing from GNSS report (e.g. 152168.79)")
        print("  Y = easting from GNSS report (e.g. 564375.07)")
        print()
        print("  Polish geodetic convention: X = northing, Y = easting")
        print("  (opposite to common X=horizontal, Y=vertical intuition)")
        sys.exit(1)

    x = float(sys.argv[1])
    y = float(sys.argv[2])
    elev = sys.argv[3] if len(sys.argv) > 3 else None

    # Validate input (EPSG:2180 range)
    for w in validate_input(x, y):
        print(w, file=sys.stderr)

    lat, lon = convert(x, y)

    # Validate output (WGS84 Tatra extent)
    for w in validate_output(lat, lon):
        print(w, file=sys.stderr)

    elev_str = f"  elev={elev}" if elev else ""
    print(f"lat={lat:.8f}  lon={lon:.8f}{elev_str}")

    elev_fix = f"\t{elev}" if elev else ""
    print(f"#fix\tSTATION\tE{lon:.8f}\tN{lat:.8f}{elev_fix}")


if __name__ == "__main__":
    main()
