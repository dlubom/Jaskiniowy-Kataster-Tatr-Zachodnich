from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from jktz.czarna_variants import DEFAULT_INPUT, SurveyContractError, analyze_survey
from jktz.metadata.errors import MetadataError
from jktz.metadata.io import atomic_write


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Czarna: wrazliwosc na 4 odczyty; bez wyboru poprawnego wariantu i bez GNSS."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.input.resolve() == args.output.resolve():
            raise SurveyContractError("input and output must be different files")
        result = analyze_survey(args.input)
        encoded = (json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode(
            "utf-8"
        )
        atomic_write(args.output, encoded)
    except (OSError, UnicodeError, MetadataError, SurveyContractError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Zapisano 16 wariantow do {args.output}. Analiza wrazliwosci, bez oceny GNSS.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
