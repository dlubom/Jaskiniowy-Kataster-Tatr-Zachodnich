#!/usr/bin/env bash
# Checks that no generated .shp file is empty (an empty shapefile header is
# exactly 100 bytes).
#
# Usage: check-empty-shapefiles.sh <OUTDIR>
set -euo pipefail

OUTDIR="${1:?OUTDIR required}"

EMPTY_SHAPEFILES=$(find "${OUTDIR}" -type f -name "*.shp" -size 100c)
if [ -n "$EMPTY_SHAPEFILES" ]; then
    echo "ERROR: Detected empty Shapefiles:"
    echo "  $EMPTY_SHAPEFILES"
    exit 1
fi
