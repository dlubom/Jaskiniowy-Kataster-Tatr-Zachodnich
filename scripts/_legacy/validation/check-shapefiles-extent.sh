#!/usr/bin/env bash
# Checks that each generated shapefile's geographic extent (reprojected from
# UTM 34N to WGS84) falls inside the Tatra Mountains extent.
#
# Usage: check-shapefiles-extent.sh <VERSION> <OUTDIR>
set -euo pipefail

# shellcheck source=tatra-extent.sh
source "$(dirname "$0")/tatra-extent.sh"

VERSION="${1:?VERSION required}"
OUTDIR="${2:?OUTDIR required}"

check_shp_extent() {
    local shp=$1
    local extent_line
    extent_line=$(ogrinfo -ro -al -so "$shp" | grep -m1 '^Extent:' || true)
    if [ -z "$extent_line" ]; then
        echo "  WARN: no extent reported for $shp"
        return 0
    fi
    local coords xmin ymin xmax ymax
    coords=$(echo "$extent_line" | sed -E 's/Extent:[[:space:]]*\(//; s/\)[[:space:]]*-[[:space:]]*\(/ /; s/\)//; s/,//g')
    read -r xmin ymin xmax ymax <<< "$coords"

    local lonlat lon_min lat_min lon_max lat_max
    lonlat=$(printf '%s %s\n%s %s\n%s %s\n%s %s\n' \
                "$xmin" "$ymin" "$xmax" "$ymin" "$xmin" "$ymax" "$xmax" "$ymax" \
             | gdaltransform -s_srs EPSG:32634 -t_srs '+proj=longlat +datum=WGS84' \
             | awk '
                 NR == 1 { lonmn=lonmx=$1; latmn=latmx=$2; next }
                 { if ($1<lonmn) lonmn=$1; if ($1>lonmx) lonmx=$1;
                   if ($2<latmn) latmn=$2; if ($2>latmx) latmx=$2 }
                 END { printf "%s %s %s %s\n", lonmn, latmn, lonmx, latmx }')
    read -r lon_min lat_min lon_max lat_max <<< "$lonlat"

    awk -v shp="$shp" \
        -v lon_min="$lon_min" -v lon_max="$lon_max" \
        -v lat_min="$lat_min" -v lat_max="$lat_max" \
        -v LONMIN="$TATRA_LON_MIN" -v LONMAX="$TATRA_LON_MAX" \
        -v LATMIN="$TATRA_LAT_MIN" -v LATMAX="$TATRA_LAT_MAX" '
        BEGIN {
            err = ""
            if (lon_min < LONMIN || lon_max > LONMAX)
                err = err sprintf("    %s: lon %.6f .. %.6f outside [%.2f, %.2f]\n",
                                  shp, lon_min, lon_max, LONMIN, LONMAX)
            if (lat_min < LATMIN || lat_max > LATMAX)
                err = err sprintf("    %s: lat %.6f .. %.6f outside [%.2f, %.2f]\n",
                                  shp, lat_min, lat_max, LATMIN, LATMAX)
            if (err != "") { printf "%s", err; exit 1 }
        }'
}

extent_bad=0
for shp in "${OUTDIR}/JKTZ-${VERSION}-all.shp" "${OUTDIR}/caves/"*.shp; do
    [ -f "$shp" ] || continue
    check_shp_extent "$shp" || extent_bad=1
done
if [ "$extent_bad" -ne 0 ]; then
    echo ""
    echo "ERROR: Shapefiles have features outside the Tatra Mountains extent."
    exit 1
fi
echo "  Shapefile extents inside Tatras (lon [${TATRA_LON_MIN}, ${TATRA_LON_MAX}], lat [${TATRA_LAT_MIN}, ${TATRA_LAT_MAX}]): Passed ✔"
