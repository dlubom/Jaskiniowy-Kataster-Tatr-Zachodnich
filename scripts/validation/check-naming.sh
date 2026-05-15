#!/usr/bin/env bash
# Checks that no .srv files (lowercase) exist outside _RAW/ directories.
set -euo pipefail

invalid_files_extension=$(find Poligony -name "*.srv" -not -path "*/_RAW/*" -type f)
if [ -n "$invalid_files_extension" ]; then
    echo "ERROR: Lowercase .srv files found (should be .SRV):"
    echo "$invalid_files_extension"
    exit 1
fi
