#!/usr/bin/env bash
# Generates exports via exports.sh and runs all export validations:
#   - check-empty-shapefiles.sh  — no zero-feature .shp files
#   - check-shapefiles-count.sh  — whole-project features == sum of per-cave features
#   - check-shapefiles-extent.sh — every shapefile's extent is inside the Tatras
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
bash scripts/validation/check-empty-shapefiles.sh "${OUTDIR}"

echo ""
echo "Checking shapefile feature-count consistency (all vs sum-of-caves)..."
echo ""
bash scripts/validation/check-shapefiles-count.sh "${VERSION}" "${OUTDIR}"

echo ""
echo "Checking shapefile geographic extent (Tatras only)..."
echo ""
bash scripts/validation/check-shapefiles-extent.sh "${VERSION}" "${OUTDIR}"
