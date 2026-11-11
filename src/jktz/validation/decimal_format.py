from __future__ import annotations

import re
from pathlib import Path

from jktz.reporting import CheckFailed
from jktz.validation._utils import active_lines, srv_files

_LRUD_RE = re.compile(r"<[^>]*>")
_DECIMAL_COMMA_RE = re.compile(r"\d,\d")


def check(root: Path = Path("Poligony")) -> None:
    """Numeric measurement fields must use ``.`` as decimal separator.

    Walls treats ``,`` as whitespace, silently shifting every subsequent field.
    Comments (``;...``) and LRUD blocks (``<...>``) are stripped before scanning.
    Excludes ``_RAW/``.
    """
    errors: list[str] = []
    for path in srv_files(root):
        text = path.read_text(encoding="latin-1")
        for line_num, raw_line in active_lines(text):
            cleaned = _LRUD_RE.sub("", raw_line)
            if _DECIMAL_COMMA_RE.search(cleaned):
                errors.append(f"  {path.as_posix()}:{line_num}  {raw_line}")
    if errors:
        raise CheckFailed(
            "ERROR: decimal comma found in numeric field "
            "(Walls treats ',' as whitespace):\n" + "\n".join(errors)
        )
