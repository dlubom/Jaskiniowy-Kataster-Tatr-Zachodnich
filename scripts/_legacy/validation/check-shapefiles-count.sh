#!/usr/bin/env bash
# Checks that the feature count in the whole-project shapefile equals the
# sum of per-cave shapefile feature counts (no features lost or duplicated
# during the per-cave split).
#
# Usage: check-shapefiles-count.sh <VERSION> <OUTDIR>
set -euo pipefail

VERSION="${1:?VERSION required}"
OUTDIR="${2:?OUTDIR required}"

ALL_SHP="${OUTDIR}/JKTZ-${VERSION}-all.shp"
ALL_COUNT=$(ogrinfo -ro -al -so "$ALL_SHP" | awk '/^Feature Count:/ {print $3; exit}')

SUM_COUNT=0
BREAKDOWN=""
for shp in "${OUTDIR}/caves/"*.shp; do
    cave=$(basename "$shp" .shp)
    count=$(ogrinfo -ro -al -so "$shp" | awk '/^Feature Count:/ {print $3; exit}')
    SUM_COUNT=$((SUM_COUNT + count))
    BREAKDOWN="${BREAKDOWN}    ${cave}: ${count}"$'\n'
done

if [ "$ALL_COUNT" -ne "$SUM_COUNT" ]; then
    echo "ERROR: Feature count mismatch between whole-project and per-cave shapefiles:"
    echo "  Whole-project (JKTZ-${VERSION}-all.shp): ${ALL_COUNT}"
    echo "  Sum of per-cave shapefiles:                      ${SUM_COUNT}"
    echo "  Difference (all - sum):                          $((ALL_COUNT - SUM_COUNT))"
    echo ""
    echo "  Per-cave breakdown:"
    printf '%s' "$BREAKDOWN"
    exit 1
fi

CAVE_COUNT=$(find "${OUTDIR}/caves" -type f -name "*.shp" | wc -l)
echo "  Shapefile feature counts (whole=${ALL_COUNT}, sum=${SUM_COUNT} across ${CAVE_COUNT} caves): Passed ✔"
