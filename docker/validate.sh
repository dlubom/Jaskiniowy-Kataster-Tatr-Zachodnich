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
    echo "[1/7] Checking SRV file naming..."
    bash docker/check-naming.sh
    echo "      OK"
} 2>&1 | tee -a "${CAVERN_LOG}"

{
    echo "[2/7] Checking for invalid directives..."
    bash docker/check-directives.sh
    echo "      OK"
} 2>&1 | tee -a "${CAVERN_LOG}"

{
    echo "[3/7] Checking #prefix values..."
    bash docker/check-prefixes.sh
    echo "      OK"
} 2>&1 | tee -a "${CAVERN_LOG}"

{
    echo "[4/7] Checking rendered entrance snapshot..."
    python3 scripts/render_otwory_from_gps.py --check
    echo "      OK"
} 2>&1 | tee -a "${CAVERN_LOG}"

echo "[5/7] Compiling with cavern..."
cavern KATASTER.wpj 2>&1 | tee -a "${CAVERN_LOG}"

{
    echo "[6/7] Checking for unattached stations..."
    bash docker/check-unattached.sh "${CAVERN_LOG}"
    echo "      OK"
} 2>&1 | tee -a "${CAVERN_LOG}"

{
    echo "[7/7] Checking exports..."
    bash docker/check-exports.sh "${EXPORTS_VERSION}" "${EXPORTS_OUTDIR}"
    echo "      OK"
} 2>&1 | tee -a "${CAVERN_LOG}"

echo ""
echo "=== Validation Passed ✔ ==="
