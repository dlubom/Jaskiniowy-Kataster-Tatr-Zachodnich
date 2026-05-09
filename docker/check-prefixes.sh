#!/usr/bin/env bash
# Checks that no #prefix / #prefix2 / #prefix3 directive contains a "." in the
# prefix value. Excludes _RAW/.
set -euo pipefail

invalid_prefixes=$(LC_ALL=C grep -rn --include='*.SRV' --exclude-dir='_RAW' \
        '^#prefix.*\.' \
        Poligony/ || true)

if [ -n "$invalid_prefixes" ]; then
    echo "ERROR: #prefix directives must not contain '.' (use #prefix3, #prefix2 and #prefix directives for prefix levels)."
    echo ""
    echo "$invalid_prefixes"
    exit 1
fi
  