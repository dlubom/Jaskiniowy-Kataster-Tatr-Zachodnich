#!/usr/bin/env bash
# Checks for non-ASCII bytes anywhere in SRV-land:
#   1. Filenames and directory names under Poligony/ (excluding _RAW)
#   2. Content of *.SRV files (excluding _RAW)
#
# Polish/Slovak diacritics and other non-ASCII characters are disallowed
# in `.wpj` paths, `.SRV` filenames, and survey text content (CLAUDE.md:128)
# because Walls' file paths and survey text rely on a restricted character
# set. Use ASCII equivalents instead (CLAUDE.md:129: a->a, c->c, l->l, etc.).
#
# Excludes _RAW/ — originals are preserved verbatim (CLAUDE.md:204).
#
# Implementation note: uses an awk byte-mapping scan rather than a
# bracket-expression grep (CLAUDE.md:162 recipe), because the bracket
# expression fails in some Git-Bash + locale combinations with an
# "Unmatched [" parser error. The awk version is portable.
#
# Usage: check-non-ascii.sh
set -euo pipefail

# Phase 1: scan basenames of every path under Poligony/ (files + dirs),
# excluding _RAW and its contents. Reports the offending byte position
# inside the basename so the user knows which path component to rename.
non_ascii_paths=$(LC_ALL=C find Poligony/ ! -path '*/_RAW' ! -path '*/_RAW/*' \
  | LC_ALL=C awk '
      BEGIN { for (i = 0; i <= 255; i++) ord[sprintf("%c", i)] = i }
      {
          base = $0; sub(/.*\//, "", base)
          for (i = 1; i <= length(base); i++) {
              v = ord[substr(base, i, 1)]
              if (v == 9 || v == 13) continue
              if (v < 32 || v > 126) {
                  printf "  %s  byte 0x%02x at col %d (path)\n", $0, v, i
                  next
              }
          }
      }')

# Phase 2: scan content of *.SRV files.
non_ascii_content=$(LC_ALL=C find Poligony/ -name '*.SRV' -not -path '*/_RAW/*' -print0 \
  | LC_ALL=C xargs -0 awk '
      BEGIN { for (i = 0; i <= 255; i++) ord[sprintf("%c", i)] = i }
      {
          for (i = 1; i <= length($0); i++) {
              v = ord[substr($0, i, 1)]
              if (v == 9 || v == 13) continue          # TAB, CR
              if (v < 32 || v > 126) {
                  printf "  %s:%d  byte 0x%02x at col %d\n", FILENAME, FNR, v, i
                  next                                  # one report per line
              }
          }
      }')

if [ -n "$non_ascii_paths" ] || [ -n "$non_ascii_content" ]; then
    echo "ERROR: non-ASCII byte(s) found in SRV files or paths (use ASCII equivalents per CLAUDE.md):"
    [ -n "$non_ascii_paths" ]   && echo "$non_ascii_paths"
    [ -n "$non_ascii_content" ] && echo "$non_ascii_content"
    exit 1
fi
