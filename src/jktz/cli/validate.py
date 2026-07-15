from __future__ import annotations

import sys

from jktz.exports.tools import ExternalToolError
from jktz.reporting import CheckFailed
from jktz.validation.suite import run_validation


def _reconfigure_streams_utf8() -> None:
    """Keep progress output readable and timely on redirected Windows streams."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace", line_buffering=True)


def main() -> int:
    _reconfigure_streams_utf8()
    print("=== Validation Started ===")

    try:
        run_validation()
    except CheckFailed as exc:
        print(str(exc))
        return 1
    except ExternalToolError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print()
    print("=== Validation Passed ✔ ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
