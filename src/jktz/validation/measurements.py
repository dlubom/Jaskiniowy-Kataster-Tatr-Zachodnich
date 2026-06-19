from __future__ import annotations

import re

_DATE_DIRECTIVE_RE = re.compile(r"^\s*#date\b", re.IGNORECASE)
_UNITS_DIRECTIVE_RE = re.compile(r"^\s*#units\b", re.IGNORECASE)
_DECL_DIRECTIVE_RE = re.compile(r"^\s*#units\b.*\bDECL\s*=", re.IGNORECASE)
_ORDER_RE = re.compile(r"\border\s*=\s*([A-Z]+)", re.IGNORECASE)
_RECT_RE = re.compile(r"\brect\b", re.IGNORECASE)


def has_dated_or_declared_active_shots(text: str) -> bool:
    has_orientation_state = False
    distance_token_index = 2
    is_rectangular = False
    in_block_comment = False
    for raw_line in text.splitlines():
        line = raw_line.split(";", 1)[0].strip()
        if not line:
            continue
        if in_block_comment:
            if line.startswith("#]"):
                in_block_comment = False
            continue
        if line.startswith("#["):
            in_block_comment = "#]" not in line[2:]
            continue
        if _DATE_DIRECTIVE_RE.match(line):
            has_orientation_state = True
            continue
        if _UNITS_DIRECTIVE_RE.match(line):
            if _DECL_DIRECTIVE_RE.match(line):
                has_orientation_state = True
            if _ORDER_RE.search(line):
                is_rectangular = bool(_RECT_RE.search(line))
                distance_token_index = _distance_token_index(line)
            continue
        if line.startswith("#"):
            continue
        if is_rectangular:
            continue
        tokens = line.split()
        if len(tokens) <= distance_token_index:
            continue
        distance = _as_float(tokens[distance_token_index])
        if distance is None:
            continue
        if distance == 0:
            continue
        if not has_orientation_state:
            return False
    return True


def _distance_token_index(units_line: str) -> int:
    match = _ORDER_RE.search(units_line)
    if match is None:
        return 2
    order = match.group(1).upper()
    if "D" not in order:
        return 2
    return 2 + order.index("D")


def _as_float(value: str) -> float | None:
    try:
        return float(value)
    except ValueError:
        return None
