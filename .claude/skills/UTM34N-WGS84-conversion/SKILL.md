# Skill: UTM34N-WGS84-conversion

Converts coordinates between WGS84 UTM Zone 34N (EPSG:32634) and WGS84 geographic
(EPSG:4326), in either direction.

UTM Zone 34N is the projection used by the JKTZ shapefile and `.3d` exports
(see `exports/caves/*.prj`). This skill is the bridge between:

- Station coordinates pulled from a compiled survey
  (`survexport --csv <file>.3d`, which prints `Easting,Northing,Altitude,Station Name`)
- The WGS84 lon/lat values required by Walls `#fix` directives in `Poligony/OTWORY.SRV`

## When to use

- You need to re-anchor a cave on a specific computed station (e.g. dropping a bad
  surface shot and fixing the actual entrance instead).
- You need to sanity-check a `#fix` line against the UTM coordinates shown in the
  shapefile / 3D export.
- Round-trip verification after editing a fix.

## Usage

```
/UTM34N-WGS84-conversion to-wgs84 <easting> <northing> [<elevation>]
/UTM34N-WGS84-conversion to-utm   <lon>     <lat>      [<elevation>]
```

Examples:

```
# Resolve UTM coordinates of station MietusiaWyznia:ot_0 (from survexport --csv)
# back to WGS84 lon/lat for an OTWORY.SRV #fix line:
/UTM34N-WGS84-conversion to-wgs84 419557.06 5455328.95 1391.87

# Sanity-check an existing #fix (lon, lat, elev) against the UTM export:
/UTM34N-WGS84-conversion to-utm 19.8947380569 49.2454436384 1391.87
```

## Steps

1. Run the conversion script:
   ```bash
   python3 .claude/skills/UTM34N-WGS84-conversion/utm34n_wgs84.py to-wgs84 <E> <N> [<elev>]
   python3 .claude/skills/UTM34N-WGS84-conversion/utm34n_wgs84.py to-utm <lon> <lat> [<elev>]
   ```

2. Show the output to the user:
   - `to-wgs84` prints `lon=...  lat=...` and a ready-to-paste `#fix STATION E... N... <elev>m` line.
   - `to-utm` prints `easting=...  northing=...` for cross-checking against the shapefile / `.3d` export.

3. Warnings are printed to stderr if either input or output lies outside the
   Tatra Mountains bounding box (helps catch swapped or wrong-zone inputs).

4. If `pyproj` is not installed, the script will print install instructions
   (`pip3 install pyproj`).

## Functions (for reuse in other scripts)

The script exposes two functions:

- `utm34n_to_wgs84(easting, northing, elevation=None) -> (lon, lat, elevation)`
- `wgs84_to_utm34n(lon, lat, elevation=None) -> (easting, northing, elevation)`

Elevation is passed through unchanged (UTM and geographic share the same vertical
datum here).

## Related workflow: pulling a station's coordinates from a compiled 3D

```bash
survexport --csv exports/JKTZ-mietusie.3d /tmp/positions.csv
grep '<station_name>' /tmp/positions.csv
# -> Easting,Northing,Altitude in UTM34N
# Feed those numbers into `to-wgs84` to get the lon/lat for a #fix line.
```

## Dependencies

Requires `pyproj`:

```bash
pip3 install pyproj
```
