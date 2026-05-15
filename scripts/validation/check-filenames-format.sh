#!/usr/bin/env bash
# Checks that every `.SRV` file has an UPPERCASE basename and an UPPERCASE
# `.SRV` extension. Cavern on case-sensitive filesystems (Linux) only tries
# lowercase, Initial-cap, and ALL-UPPERCASE filename variants when resolving
# `.NAME` references in `.wpj` paths (CLAUDE.md:62) — keeping every name in
# the all-uppercase form is the project's documented convention.
#
# Non-letter characters (digits, `_`, `-`) are allowed and ignored by the
# case check. Excludes _RAW/ — originals are preserved verbatim.
#
# Usage: check-filenames-format.sh
set -euo pipefail

# Phase 1: lowercase extension (.srv)
lowercase_extensions=$(LC_ALL=C find Poligony/ -name '*.srv' -not -path '*/_RAW/*' -type f \
  | sed 's|^|  |')

# Phase 2: .SRV extension but basename contains a lowercase ASCII letter
lowercase_basenames=$(LC_ALL=C find Poligony/ -name '*.SRV' -not -path '*/_RAW/*' -type f \
  | LC_ALL=C awk -F/ '
      { base = $NF; sub(/\.SRV$/, "", base)
        if (base ~ /[a-z]/) printf "  %s\n", $0 }')

if [ -n "$lowercase_extensions" ] || [ -n "$lowercase_basenames" ]; then
    echo "ERROR: SRV filename format violation (basename and .SRV must be UPPERCASE, per CLAUDE.md:62):"
    [ -n "$lowercase_extensions" ] && echo "$lowercase_extensions"
    [ -n "$lowercase_basenames" ]  && echo "$lowercase_basenames"
    exit 1
fi
