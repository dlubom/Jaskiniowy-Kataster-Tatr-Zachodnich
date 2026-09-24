---
name: utm34n-wgs84
description: Convert between WGS84 UTM zone 34N and geographic coordinates to check survey exports and entrance locations.
---

Converts coordinates between WGS84 UTM Zone 34N (EPSG:32634) and WGS84 geographic
(EPSG:4326), in either direction.

UTM Zone 34N is the projection used by the JKTZ shapefile and `.3d` exports
(see `exports/caves/*.prj`). This skill is the bridge between:

- Station coordinates pulled from a compiled survey
  (`survexport --csv <file>.3d`, which prints `Easting,Northing,Altitude,Station Name`)
- The WGS84 lon/lat values required by Walls `#fix` directives in `Poligony/OTWORY.SRV`

## When to use

- You need to compare a computed station location with independently sourced
  entrance coordinates, without inferring a new anchor from the model.
- You need to sanity-check a `#fix` line against the UTM coordinates shown in the
  shapefile / 3D export.
- Round-trip verification after editing a fix.

## Usage

```
$utm34n-wgs84 to-wgs84 <easting> <northing> [<elevation>]
$utm34n-wgs84 to-utm   <lon>     <lat>      [<elevation>]
```

Examples:

```
# Resolve UTM coordinates of station MietusiaWyznia:ot_0 (from survexport --csv)
# back to WGS84 lon/lat for a coordinate comparison:
$utm34n-wgs84 to-wgs84 419557.06 5455328.95 1391.87

# Sanity-check an existing #fix (lon, lat, elev) against the UTM export:
$utm34n-wgs84 to-utm 19.8947380569 49.2454436384 1391.87
```

## Steps

1. Run the conversion script:
   ```bash
   uv run python .agents/skills/utm34n-wgs84/utm34n_wgs84.py to-wgs84 <E> <N> [<elev>]
   uv run python .agents/skills/utm34n-wgs84/utm34n_wgs84.py to-utm <lon> <lat> [<elev>]
   ```

2. Show the output to the user:
   - `to-wgs84` prints `lon=...  lat=...` and a illustrative `#fix STATION E... N... <elev>m` line.
   - `to-utm` prints `easting=...  northing=...` for cross-checking against the shapefile / `.3d` export.

3. Warnings are printed to stderr if either input or output lies outside the
   Tatra Mountains bounding box (helps catch swapped or wrong-zone inputs).

4. If `pyproj` is not installed, the script will print install instructions
   (`uv sync --locked`).

## Functions (for reuse in other scripts)

The script exposes two functions:

- `utm34n_to_wgs84(easting, northing, elevation=None) -> (lon, lat, elevation)`
- `wgs84_to_utm34n(lon, lat, elevation=None) -> (easting, northing, elevation)`

Elevation is passed through unchanged. These horizontal CRS conversions do not
transform or establish the vertical datum; verify the height reference separately.

## Related workflow: pulling a station's coordinates from a compiled 3D

```bash
survexport --csv exports/JKTZ-mietusie.3d /tmp/positions.csv
grep '<station_name>' /tmp/positions.csv
# -> Easting,Northing,Altitude in UTM34N
# Feed those numbers into `to-wgs84` to compare lon/lat with the independently sourced entrance fix.
```

## Dependencies

Requires `pyproj`:

```bash
uv sync --locked
```

## Entrance provenance

Conversion output is a coordinate check, not a new authoritative entrance fix.
Do not paste it into the generated `Poligony/OTWORY.SRV`: active fixes come from
GPS object mappings in `Poligony/OTWORY.SRV.j2`. Preserve the source CRS and
height reference, and use the GPS project's workflow for approved updates.
