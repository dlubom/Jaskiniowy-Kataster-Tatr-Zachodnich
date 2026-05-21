#!/usr/bin/env bash
# =============================================================================
# validate.sh — full validation pipeline for local Docker use.
#
# Runs all checks and compiles KATASTER.wpj with cavern.
# Mirrors the Linux job in GitHub Actions validate.yml.
#
# Usage (from repo root):
#   docker run --rm -v "$(pwd):/project" jktz-survex bash scripts/_legacy/validation/validate.sh
# =============================================================================
set -euo pipefail

CAVERN_LOG="cavern_output.txt"
EXPORTS_OUTDIR="validate-exports"
EXPORTS_VERSION="validate"
trap 'rm -rf "${EXPORTS_OUTDIR}"' EXIT

: > "${CAVERN_LOG}"

echo "=== Validation Started ==="

{
    echo "[1/10] Checking SRV filenames format..."
    bash scripts/_legacy/validation/check-filenames-format.sh
    echo "      SRV filenames format: Passed ✔"
} 2>&1 | tee -a "${CAVERN_LOG}"

{
    echo "[2/10] Checking for invalid directives..."
    bash scripts/_legacy/validation/check-directives.sh
    echo "      Invalid directives: Passed ✔"
} 2>&1 | tee -a "${CAVERN_LOG}"

{
    echo "[3/10] Checking decimal format in numeric fields..."
    bash scripts/_legacy/validation/check-decimal-format.sh
    echo "      Decimal format: Passed ✔"
} 2>&1 | tee -a "${CAVERN_LOG}"

{
    echo "[4/10] Checking for non-ASCII bytes in SRV files..."
    bash scripts/_legacy/validation/check-non-ascii.sh
    echo "      Non-ASCII bytes: Passed ✔"
} 2>&1 | tee -a "${CAVERN_LOG}"

{
    echo "[5/10] Checking #prefix values..."
    bash scripts/_legacy/validation/check-prefixes.sh
    echo "      #prefix values: Passed ✔"
} 2>&1 | tee -a "${CAVERN_LOG}"

{
    echo "[6/10] Checking rendered entrance snapshot..."
    python3 scripts/render_otwory_from_gps.py --check
    echo "      OK"
} 2>&1 | tee -a "${CAVERN_LOG}"

{
    echo "[7/10] Checking entrance coordinates are inside Tatras extent..."
    bash scripts/_legacy/validation/check-coordinates.sh
    echo "      Entrance coordinates in Tatras extent: Passed ✔"
} 2>&1 | tee -a "${CAVERN_LOG}"

echo "[8/10] Compiling with cavern..."
cavern KATASTER.wpj 2>&1 | tee -a "${CAVERN_LOG}"

{
    echo "[9/10] Checking for unattached stations..."
    bash scripts/_legacy/validation/check-unattached.sh "${CAVERN_LOG}"
    echo "      Unattached stations: Passed ✔"
} 2>&1 | tee -a "${CAVERN_LOG}"

{
    echo "[10/10] Checking exports..."
    bash scripts/_legacy/validation/check-exports.sh "${EXPORTS_VERSION}" "${EXPORTS_OUTDIR}"
    echo "      Exports: Passed ✔"
} 2>&1 | tee -a "${CAVERN_LOG}"

echo ""
echo "=== Validation Passed ✔ ==="
