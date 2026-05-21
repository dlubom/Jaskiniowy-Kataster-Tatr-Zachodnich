from __future__ import annotations

import re
from pathlib import Path

from jktz.reporting import CheckFailed
from jktz.validation._utils import srv_files

_PREFIX_DOT_RE = re.compile(r"^#prefix.*\.")


def check(root: Path = Path("Poligony")) -> None:
    """No ``#prefix`` / ``#prefix2`` / ``#prefix3`` value may contain a ``.``.

    Use the multi-level ``#prefix`` directives instead. Excludes ``_RAW/``.
    """
    matches: list[str] = []
    for path in srv_files(root):
        text = path.read_text(encoding="latin-1")
        for line_num, line in enumerate(text.splitlines(), start=1):
            if _PREFIX_DOT_RE.match(line):
                matches.append(f"{path.as_posix()}:{line_num}:{line}")
    if matches:
        raise CheckFailed(
            "ERROR: #prefix directives must not contain '.' "
            "(use #prefix3, #prefix2 and #prefix directives for prefix levels).\n\n"
            + "\n".join(matches)
        )
