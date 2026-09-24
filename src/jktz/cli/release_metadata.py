from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from jktz.metadata.io import atomic_write


def extract_release_notes(changelog: str, version: str) -> str:
    """Extract exactly one nonempty, literal version section from the changelog."""
    headings = list(re.finditer(r"^##[ \t]+\[([^\]\r\n]+)\][^\r\n]*", changelog, re.MULTILINE))
    matches = [heading for heading in headings if heading.group(1) == version]
    if len(matches) != 1:
        raise ValueError(f"CHANGELOG.md must contain exactly one section for {version}")
    start = matches[0].end()
    following = re.search(r"^##(?:[ \t]|$)", changelog[start:], re.MULTILINE)
    end = start + following.start() if following else len(changelog)
    notes = changelog[start:end].strip()
    if not notes:
        raise ValueError(f"Release notes for {version} are empty")
    return notes + "\n"


def prepare_release_metadata(version: str, root: Path, notes_path: Path | None = None) -> None:
    """Validate inputs before replacing the INFO marker and optional release notes."""
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._+-]*", version) is None:
        raise ValueError("Version must be a nonempty ASCII version label")
    info_path = root / "INFO.txt"
    info = info_path.read_bytes()
    marker = b"__VERSION__"
    if info.count(marker) != 1:
        raise ValueError("INFO.txt must contain exactly one __VERSION__ marker")
    notes = None
    if notes_path is not None:
        notes = extract_release_notes((root / "CHANGELOG.md").read_text(encoding="utf-8"), version)
        if notes_path.resolve() in {info_path.resolve(), (root / "CHANGELOG.md").resolve()}:
            raise ValueError("Release notes output must not overwrite INFO.txt or CHANGELOG.md")
    atomic_write(info_path, info.replace(marker, version.encode("ascii")))
    if notes is not None:
        atomic_write(notes_path, notes.encode("utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare INFO.txt and optional release notes.")
    parser.add_argument("version")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--notes", type=Path, help="Write the matching CHANGELOG.md section here")
    args = parser.parse_args(argv)
    try:
        prepare_release_metadata(args.version, args.root, args.notes)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"Prepared release metadata for {args.version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
