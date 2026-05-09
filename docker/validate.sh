#!/usr/bin/env bash
# =============================================================================
# validate.sh — full validation pipeline for local Docker use.
#
# Runs all checks and compiles KATASTER.wpj with cavern.
# Mirrors the Linux job in GitHub Actions validate.yml.
#
# Usage (from repo root):
#   docker run --rm -v "$(pwd):/project" jktz-survex bash docker/validate.sh
# =============================================================================
set -euo pipefail

CAVERN_LOG="cavern_output.txt"
EXPORTS_OUTDIR="validate-exports"
EXPORTS_VERSION="validate"
trap 'rm -rf "${EXPORTS_OUTDIR}"' EXIT

: > "${CAVERN_LOG}"

echo "=== Validation Started ==="

{
    echo "[1/6] Checking SRV file naming..."
    bash docker/check-naming.sh
    echo "      OK"
} 2>&1 | tee -a "${CAVERN_LOG}"

{
    echo "[2/6] Checking for invalid directives..."
    bash docker/check-directives.sh
    echo "      OK"
} 2>&1 | tee -a "${CAVERN_LOG}"

{
    echo "[3/6] Checking #prefix values..."
    bash docker/check-prefixes.sh
    echo "      OK"
} 2>&1 | tee -a "${CAVERN_LOG}"

echo "[4/6] Compiling with cavern..."
cavern KATASTER.wpj 2>&1 | tee -a "${CAVERN_LOG}"

{
    echo "[5/6] Checking for unattached stations..."
    bash docker/check-unattached.sh "${CAVERN_LOG}"
    echo "      OK"
} 2>&1 | tee -a "${CAVERN_LOG}"

echo "[6/6] Checking exports..."
echo ""
bash docker/exports.sh "${EXPORTS_VERSION}" "${EXPORTS_OUTDIR}" 2>&1 | tee -a "${CAVERN_LOG}" | sed 's/^/                   /'

echo ""
echo "Checking for empty .shp files..."
echo ""
EMPTY_SHAPEFILES=$(find "${EXPORTS_OUTDIR}" -type f -name "*.shp" -size 100c)
if [ -n "$EMPTY_SHAPEFILES" ]; then
  echo "ERROR: Detected empty Shapefiles:"
  echo "  $EMPTY_SHAPEFILES"
  exit 1
fi


echo ""
echo "=== Validation Passed ✔ ==="
