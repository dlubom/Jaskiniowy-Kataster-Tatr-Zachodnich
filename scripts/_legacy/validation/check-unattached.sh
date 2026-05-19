#!/usr/bin/env bash
# Checks the cavern compile log for survey stations not attached to a fixed
# point. Reads the log path from $1 (defaults to cavern_output.txt).
set -euo pipefail

LOG="${1:-cavern_output.txt}"

if grep -qE "not attached to a (fixed|control) point" "${LOG}"; then
    echo "ERROR: Cavern detected survey stations not attached to a fixed point:"
    sed -n '/not attached to a .* point/,/^$/p' "${LOG}"
    exit 1
fi
