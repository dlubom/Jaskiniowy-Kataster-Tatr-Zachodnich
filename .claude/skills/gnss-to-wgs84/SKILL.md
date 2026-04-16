# Skill: gnss-to-wgs84

Converts coordinates from Polish EPSG:2180 (PUWG 1992 / "uklad 1992") to WGS84 geographic (EPSG:4326). Useful when processing GNSS survey reports that provide coordinates in the Polish national system.

## When to use

- When you receive GNSS measurement reports with coordinates in uklad 1992 (X northing, Y easting)
- When adding new cave entrance coordinates from Polish geodetic data
- When verifying or updating `#fix` directives in SRV files

## Usage

```
/gnss-to-wgs84 <X_northing> <Y_easting> [<elevation>]
```

Examples:
```
/gnss-to-wgs84 152168.79 564375.07 1486.69
/gnss-to-wgs84 153160.50 561420.30
```

## Input format

GNSS reports in uklad 1992 typically label coordinates as:
- **X** = northing (e.g. 152168.79)
- **Y** = easting (e.g. 564375.07)

Note: X/Y ordering in Polish 1992 is swapped relative to the pyproj convention — the script handles this automatically.

## Steps

1. Run the conversion script:
   ```bash
   python3 .claude/skills/gnss-to-wgs84/gnss_to_wgs84.py <X> <Y> [<elevation>]
   ```

2. Show the output to the user — it includes:
   - Decimal degrees: `lat=... lon=...`
   - Ready-to-paste `#fix` line for SRV files

3. If `pyproj` is not installed, the script will print install instructions (`pip3 install pyproj`).

## Dependencies

Requires `pyproj` Python package:
```bash
pip3 install pyproj
```
