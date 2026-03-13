#!/usr/bin/env bash
# survex-stats.sh — compile a Survex .svx file with cavern and print statistics
#
# Requires: cavern (Survex) available on PATH.
#
# Usage:
#   ./survex-stats.sh <path/to/file.svx>
#
# Example:
#   ./survex-stats.sh "Poligony/D_Mietusia/M_Swistowka/Mietusia_Wyznia/_RAW/mietusia_wyznia.svx"

set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <path/to/file.svx>" >&2
    exit 1
fi

SVX="$1"

if [[ ! -f "$SVX" ]]; then
    echo "Error: file not found: $SVX" >&2
    exit 1
fi

if ! command -v cavern &>/dev/null; then
    echo "Error: 'cavern' not found on PATH. Install Survex and add it to PATH." >&2
    exit 1
fi

TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

echo "=== Compiling: $SVX ==="
echo ""

# Run from SVX file's directory so *include paths resolve correctly
SVX_DIR=$(dirname "$SVX")
SVX_FILE=$(basename "$SVX")

cavern --no-auxiliary-files -o "$TMPDIR/out" "$SVX_DIR/$SVX_FILE" 2>&1 \
    | grep -v "^CPU time"

echo ""
echo "=== Done ==="
