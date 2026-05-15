#!/usr/bin/env bash
# Generates exports via exports.sh and validates them: checks for empty
# shapefiles and feature-count consistency between the whole-project shapefile
# and the sum of per-cave shapefiles.
#
# Usage: check-exports.sh <VERSION> <OUTDIR>
set -euo pipefail

VERSION="${1:?VERSION required}"
OUTDIR="${2:?OUTDIR required}"

echo ""
bash scripts/exports/exports.sh "${VERSION}" "${OUTDIR}" 2>&1 | sed 's/^/                   /'

echo ""
echo "Checking for empty .shp files..."
echo ""
EMPTY_SHAPEFILES=$(find "${OUTDIR}" -type f -name "*.shp" -size 100c)
if [ -n "$EMPTY_SHAPEFILES" ]; then
  echo "ERROR: Detected empty Shapefiles:"
  echo "  $EMPTY_SHAPEFILES"
  exit 1
fi

echo ""
echo "Checking shapefile feature-count consistency (all vs sum-of-caves)..."
echo ""

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
echo "  OK: ${ALL_COUNT} features (whole-project) == ${SUM_COUNT} features (sum across ${CAVE_COUNT} caves)"
