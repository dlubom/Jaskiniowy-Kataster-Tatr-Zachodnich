#!/usr/bin/env python3
"""Convert coordinates from Polish EPSG:2180 (PUWG 1992) to WGS84 (EPSG:4326).

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


def convert(x_northing, y_easting):
    tr = Transformer.from_crs(2180, 4326, always_xy=True)
    lon, lat = tr.transform(y_easting, x_northing)
    return lat, lon


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 gnss_to_wgs84.py <X_northing> <Y_easting> [<elevation>]")
        print("  X = northing from GNSS report (e.g. 152168.79)")
        print("  Y = easting from GNSS report (e.g. 564375.07)")
        sys.exit(1)

    x = float(sys.argv[1])
    y = float(sys.argv[2])
    elev = sys.argv[3] if len(sys.argv) > 3 else None

    lat, lon = convert(x, y)

    elev_str = f"  elev={elev}" if elev else ""
    print(f"lat={lat:.8f}  lon={lon:.8f}{elev_str}")

    elev_fix = f"\t{elev}" if elev else ""
    print(f"#fix\tSTATION\tE{lon:.8f}\tN{lat:.8f}{elev_fix}")


if __name__ == "__main__":
    main()
