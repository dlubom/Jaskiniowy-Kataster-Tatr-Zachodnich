from __future__ import annotations

import argparse
from pathlib import Path

from jktz.metadata.raw import material_hashes


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage JKTZ SRV metadata helpers.")
    subparsers = parser.add_subparsers(dest="cmd", required=True)
    hash_cmd = subparsers.add_parser("hash-raw")
    hash_cmd.add_argument("root", type=Path, nargs="?", default=Path("Poligony"))
    args = parser.parse_args()

    if args.cmd == "hash-raw":
        for item in material_hashes(args.root):
            print(f"{item.sha256}  {item.path.as_posix()}")
        return 0
    raise AssertionError(args.cmd)


if __name__ == "__main__":
    raise SystemExit(main())
