#!/usr/bin/env bash
# Checks that #fix entrance coordinates in Poligony/OTWORY.SRV fall within
# the Tatra Mountains extent and that elevations are realistic.
#
# Catches: swapped lat/lon, decimal-magnitude errors, wrong-region coords
# (e.g. PUWG-1992 meters left unconverted), feet-vs-meters elevation.
set -euo pipefail

# shellcheck source=tatra-extent.sh
source "$(dirname "$0")/tatra-extent.sh"

OTWORY="Poligony/OTWORY.SRV"

errors=$(LC_ALL=C awk \
    -v lonmin="$TATRA_LON_MIN" -v lonmax="$TATRA_LON_MAX" \
    -v latmin="$TATRA_LAT_MIN" -v latmax="$TATRA_LAT_MAX" \
    -v elevmin="$TATRA_ELEV_MIN" -v elevmax="$TATRA_ELEV_MAX" '
    { sub(/\r$/, "") }   # tolerate CRLF line endings (Windows checkouts)
    /^#fix[ \t]/ {
        station = $2
        lon = ""; lat = ""; elev = ""
        for (i = 3; i <= NF; i++) {
            if ($i ~ /^E-?[0-9]/)        lon  = substr($i, 2) + 0
            else if ($i ~ /^N-?[0-9]/)   lat  = substr($i, 2) + 0
            else if ($i ~ /^-?[0-9].*m$/) {
                e = $i; sub(/m$/, "", e); elev = e + 0
            }
        }
        msg = ""
        if (lon == "")
            msg = msg "    missing longitude (E<value>)\n"
        else if (lon < lonmin || lon > lonmax)
            msg = msg sprintf("    lon %.6f outside [%.2f, %.2f]\n", lon, lonmin, lonmax)

        if (lat == "")
            msg = msg "    missing latitude (N<value>)\n"
        else if (lat < latmin || lat > latmax)
            msg = msg sprintf("    lat %.6f outside [%.2f, %.2f]\n", lat, latmin, latmax)

        if (elev == "")
            msg = msg "    missing elevation (<value>m)\n"
        else if (elev < elevmin || elev > elevmax)
            msg = msg sprintf("    elevation %.2f m outside [%d, %d] m\n", elev, elevmin, elevmax)
        if (msg != "")
            printf "  %s:%d  %s\n%s", FILENAME, NR, station, msg
    }
' "$OTWORY")

if [ -n "$errors" ]; then
    echo "ERROR: #fix entries with invalid coordinates:"
    echo "$errors"
    exit 1
fi
