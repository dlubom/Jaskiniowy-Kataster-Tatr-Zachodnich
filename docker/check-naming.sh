#!/usr/bin/env bash
# Checks that no .srv files (lowercase) exist outside _RAW/ directories.
set -euo pipefail

bad=$(find Poligony -name "*.srv" -not -path "*/_RAW/*" -type f)
if [ -n "$bad" ]; then
    echo "ERROR: Lowercase .srv files found (should be .SRV):"
    echo "$bad"
    exit 1
fi
