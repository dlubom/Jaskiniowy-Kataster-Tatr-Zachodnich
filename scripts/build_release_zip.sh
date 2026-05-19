#!/usr/bin/env bash
# Build the user-facing JKTZ ZIP package from the current workspace.
#
# Usage:
#   scripts/build_release_zip.sh <VERSION> [ZIP_PATH]
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
    echo "usage: $0 <VERSION> [ZIP_PATH]" >&2
    exit 2
fi

VERSION="$1"
ZIP_PATH="${2:-JKTZ-${VERSION}.zip}"

rm -f "${ZIP_PATH}"

zip -qr "${ZIP_PATH}" . \
    -x ".git/*" \
    -x ".github/*" \
    -x ".claude/*" \
    -x ".venv/*" \
    -x ".pytest_cache/*" \
    -x ".ruff_cache/*" \
    -x ".playwright-mcp/*" \
    -x "docker/*" \
    -x ".gitignore" \
    -x "CLAUDE.md" \
    -x "pyproject.toml" \
    -x "uv.lock" \
    -x "doc/*" \
    -x "scripts/*" \
    -x "tests/*" \
    -x "Poligony/OTWORY.SRV.j2" \
    -x "logs/*" \
    -x "*/_RAW/*" \
    -x "*.DS_Store" \
    -x "KATASTER/*" \
    -x "*.nta" \
    -x "*.ntn" \
    -x "*.ntv" \
    -x "*.nts" \
    -x "*.ntp" \
    -x "*.NTA" \
    -x "*.NTN" \
    -x "*.NTV" \
    -x "*.NTS" \
    -x "*.NTP" \
    -x "*.wrl" \
    -x "*.log" \
    -x "*.lst" \
    -x "web/*" \
    -x "survex-src/*" \
    -x "validate-exports/*" \
    -x "cavern_output.txt" \
    -x "release_notes.md" \
    -x "JKTZ-*.zip"
