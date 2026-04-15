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

echo "[1/4] Checking SRV file naming..."
bash docker/check-naming.sh
echo "      OK"

echo "[2/4] Checking for invalid directives..."
bash docker/check-directives.sh
echo "      OK"

echo "[3/4] Compiling with cavern..."
cavern KATASTER.wpj 2>&1 | tee "${CAVERN_LOG}"

echo "[4/4] Checking for unattached stations..."
if grep -qE "not attached to a (fixed|control) point" "${CAVERN_LOG}"; then
    echo "ERROR: Cavern detected survey stations not attached to a fixed point:"
    sed -n '/not attached to a .* point/,/^$/p' "${CAVERN_LOG}"
    exit 1
fi

echo ""
echo "=== Validation OK ==="
