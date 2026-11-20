"""Build CaveView entrance names from the Walls notes in OTWORY.SRV."""

import argparse
import json
import re
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    notes = re.findall(
        r"^[ \t]*#note[ \t]+(\S+)[ \t]+/([^\n;]+)",
        args.source.read_text(encoding="ascii"),
        re.MULTILINE | re.IGNORECASE,
    )
    entrances = {station: {"name": name.strip()} for station, name in notes}
    args.output.write_text(json.dumps({"entrances": entrances}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
