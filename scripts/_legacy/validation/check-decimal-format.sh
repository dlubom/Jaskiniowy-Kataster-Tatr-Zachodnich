#!/usr/bin/env bash
# Checks for decimal commas in numeric measurement fields. Walls treats
# `,` as whitespace, silently shifting every subsequent field — almost
# always a typo for `.`.
#
# Comments (everything after `;` on a line) are stripped before scanning,
# so commas in human-readable notes don't trigger.
#
# LRUD blocks (<L,R,U,D>) are stripped and intentionally NOT validated
# beyond removal — Walls accepts many LRUD shapes (4 or 5 numeric fields,
# optional trailing C/c flag, comma or whitespace separators, `--` for
# missing dimensions). A decimal-comma typo inside single-digit LRUD
# values (e.g. <1,5,2,0> meant as <1.5,2.0>) is indistinguishable from
# four valid integers without context, so any check here would have
# unavoidable false negatives.
#
# Usage: check-decimal-format.sh
set -euo pipefail

invalid_decimal_separators=$(LC_ALL=C find Poligony/ -name '*.SRV' -not -path '*/_RAW/*' -print0 \
  | LC_ALL=C xargs -0 awk '
      { sub(/\r$/, "") }                    # CRLF tolerance
      { line = $0
        sub(/;.*/, "", line)                # strip trailing comment
        gsub(/<[^>]*>/, "", line) }         # strip LRUD blocks <L,R,U,D>
      line ~ /[0-9],[0-9]/ {
          printf "  %s:%d  %s\n", FILENAME, FNR, $0
      }')

if [ -n "$invalid_decimal_separators" ]; then
    echo "ERROR: decimal comma found in numeric field (Walls treats ',' as whitespace):"
    echo "$invalid_decimal_separators"
    exit 1
fi
