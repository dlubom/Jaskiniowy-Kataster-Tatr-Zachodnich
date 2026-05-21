#!/usr/bin/env bash
# Checks that no invalid #< directives exist in SRV files.
set -euo pipefail

if grep -r --include='*.SRV' '#<' Poligony/; then
    echo "ERROR: Invalid #< directive found"
    exit 1
fi
