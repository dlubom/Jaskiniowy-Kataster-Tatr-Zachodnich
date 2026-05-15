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
    echo "[1/6] Checking SRV file naming..."
    bash scripts/validation/check-naming.sh
    echo "      OK"
} 2>&1 | tee -a "${CAVERN_LOG}"

{
    echo "[2/6] Checking for invalid directives..."
    bash scripts/validation/check-directives.sh
    echo "      OK"
} 2>&1 | tee -a "${CAVERN_LOG}"

{
    echo "[3/6] Checking #prefix values..."
    bash scripts/validation/check-prefixes.sh
    echo "      OK"
} 2>&1 | tee -a "${CAVERN_LOG}"

echo "[4/6] Compiling with cavern..."
cavern KATASTER.wpj 2>&1 | tee -a "${CAVERN_LOG}"

{
    echo "[5/6] Checking for unattached stations..."
    bash scripts/validation/check-unattached.sh "${CAVERN_LOG}"
    echo "      OK"
} 2>&1 | tee -a "${CAVERN_LOG}"

{
    echo "[6/6] Checking exports..."
    bash scripts/validation/check-exports.sh "${EXPORTS_VERSION}" "${EXPORTS_OUTDIR}"
    echo "      OK"
} 2>&1 | tee -a "${CAVERN_LOG}"

echo ""
echo "=== Validation Passed ✔ ==="
