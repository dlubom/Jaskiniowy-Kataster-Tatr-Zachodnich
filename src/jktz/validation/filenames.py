from __future__ import annotations

from pathlib import Path

from jktz.reporting import CheckFailed


def check(root: Path = Path("Poligony")) -> None:
    """Every ``.SRV`` file must have an UPPERCASE basename and ``.SRV`` extension.

    Cavern on case-sensitive filesystems (Linux) only tries lowercase,
    Initial-cap, and ALL-UPPERCASE filename variants when resolving ``.NAME``
    references in ``.wpj`` paths (CLAUDE.md:62). Excludes ``_RAW/``.
    """
    lowercase_extensions: list[str] = []
    lowercase_basenames: list[str] = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if "_RAW" in path.parts:
            continue
        if path.suffix == ".srv":
            lowercase_extensions.append(f"  {path.as_posix()}")
        elif path.suffix == ".SRV":
            base = path.stem
            if any("a" <= c <= "z" for c in base):
                lowercase_basenames.append(f"  {path.as_posix()}")

    if lowercase_extensions or lowercase_basenames:
        lines = [
            "ERROR: SRV filename format violation "
            "(basename and .SRV must be UPPERCASE, per CLAUDE.md:62):"
        ]
        lines.extend(lowercase_extensions)
        lines.extend(lowercase_basenames)
        raise CheckFailed("\n".join(lines))
