#!/usr/bin/env bash
# =============================================================================
# validate.sh — full validation pipeline for local Docker use.
#
# Runs all checks and compiles KATASTER.wpj with cavern.
# Mirrors the Linux job in GitHub Actions validate.yml.
#
# Usage (from repo root):
#   docker run --rm -v "$(pwd):/project" jktz-survex bash scripts/validation/validate.sh
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
    bash scripts/validation/check-naming.sh
    echo "      SRV file naming: Passed ✔"
} 2>&1 | tee -a "${CAVERN_LOG}"

{
    echo "[2/7] Checking for invalid directives..."
    bash scripts/validation/check-directives.sh
    echo "      Invalid directives: Passed ✔"
} 2>&1 | tee -a "${CAVERN_LOG}"

{
    echo "[3/7] Checking #prefix values..."
    bash scripts/validation/check-prefixes.sh
    echo "      #prefix values: Passed ✔"
} 2>&1 | tee -a "${CAVERN_LOG}"

{
    echo "[4/7] Checking entrance coordinates are inside Tatras extent..."
    bash scripts/validation/check-coordinates.sh
    echo "      Entrance coordinates in Tatras extent: Passed ✔"
} 2>&1 | tee -a "${CAVERN_LOG}"

echo "[5/7] Compiling with cavern..."
cavern KATASTER.wpj 2>&1 | tee -a "${CAVERN_LOG}"

{
    echo "[6/7] Checking for unattached stations..."
    bash scripts/validation/check-unattached.sh "${CAVERN_LOG}"
    echo "      Unattached stations: Passed ✔"
} 2>&1 | tee -a "${CAVERN_LOG}"

{
    echo "[7/7] Checking exports..."
    bash scripts/validation/check-exports.sh "${EXPORTS_VERSION}" "${EXPORTS_OUTDIR}"
    echo "      Exports: Passed ✔"
} 2>&1 | tee -a "${CAVERN_LOG}"

echo ""
echo "=== Validation Passed ✔ ==="
