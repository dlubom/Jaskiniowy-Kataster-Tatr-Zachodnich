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
EXPORTS_BASEDIR="exports"
EXPORTS_VERSION="validate"
EXPORTS_OUTDIR="${EXPORTS_BASEDIR}/JKTZ-${EXPORTS_VERSION}"
trap 'rm -rf "${EXPORTS_BASEDIR}"' EXIT

echo "=== Validation Started ==="

echo "[1/5] Checking SRV file naming..."
bash docker/check-naming.sh
echo "      OK"

echo "[2/5] Checking for invalid directives..."
bash docker/check-directives.sh
echo "      OK"

echo "[3/5] Compiling with cavern..."
cavern KATASTER.wpj 2>&1 | tee "${CAVERN_LOG}"

echo "[4/5] Checking for unattached stations..."
if grep -qE "not attached to a (fixed|control) point" "${CAVERN_LOG}"; then
    echo "ERROR: Cavern detected survey stations not attached to a fixed point:"
    sed -n '/not attached to a .* point/,/^$/p' "${CAVERN_LOG}"
    exit 1
fi

echo "[5/5] Checking exports..."
echo ""
bash docker/exports.sh "${EXPORTS_VERSION}" "${EXPORTS_BASEDIR}" 2>&1 | sed 's/^/                   /'

echo ""
echo "Checking for empty .shp files..."
echo ""
bad=$(find "${EXPORTS_OUTDIR}" -type f -name "*.shp" -size 100c)
if [ -n "$bad" ]; then
  echo "ERROR: Detected empty Shapefiles:"
  echo "  $bad"
  exit 1
fi 
  

echo ""
echo "=== Validation Passed ✔ ===" 	
