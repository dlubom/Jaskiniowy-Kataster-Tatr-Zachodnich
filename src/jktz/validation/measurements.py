from __future__ import annotations

import re
from dataclasses import dataclass, replace

_DATE_DIRECTIVE_RE = re.compile(r"^\s*#date\b", re.IGNORECASE)
_UNITS_DIRECTIVE_RE = re.compile(r"^\s*#units\b", re.IGNORECASE)
_DECL_DIRECTIVE_RE = re.compile(r"^\s*#units\b.*\bDECL\s*=", re.IGNORECASE)
_ORDER_RE = re.compile(r"\border\s*=\s*([A-Z]+)", re.IGNORECASE)
_UNITS_KEYWORD_RE = re.compile(r"(?<!\S)(SAVE|RESET|RESTORE|CT|RECT)(?!\S)", re.IGNORECASE)


@dataclass(frozen=True)
class _UnitsState:
    has_orientation: bool = False
    distance_index: int = 2
    rectangular: bool = False


def has_dated_or_declared_active_shots(text: str) -> bool:
    state = _UnitsState()
    saved_states: list[_UnitsState] = []
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
            state = replace(state, has_orientation=True)
            continue
        if _UNITS_DIRECTIVE_RE.match(line):
            state = _apply_units(line, state, saved_states)
            continue
        if line.startswith("#"):
            continue
        if state.rectangular:
            continue
        tokens = line.split()
        if len(tokens) <= state.distance_index:
            continue
        distance = _as_float(tokens[state.distance_index])
        if distance is None:
            continue
        if distance == 0:
            continue
        if not state.has_orientation:
            return False
    return True


def _apply_units(line: str, state: _UnitsState, saved_states: list[_UnitsState]) -> _UnitsState:
    # Walls saves before applying other parameters; RESET clears declination too.
    keywords = [keyword.upper() for keyword in _UNITS_KEYWORD_RE.findall(line)]
    if "SAVE" in keywords:
        saved_states.append(state)
    if "RESET" in keywords:
        state = _UnitsState()
    if "RESTORE" in keywords and saved_states:
        state = saved_states.pop()
    if _DECL_DIRECTIVE_RE.match(line):
        state = replace(state, has_orientation=True)
    for keyword in keywords:
        if keyword in {"CT", "RECT"}:
            state = replace(state, rectangular=keyword == "RECT")
    # CT and RECT orders are independent and can coexist on one directive.
    for order in _ORDER_RE.findall(line.upper()):
        if "D" in order:
            state = replace(state, distance_index=2 + order.index("D"))
    return state


def _as_float(value: str) -> float | None:
    try:
        return float(value)
    except ValueError:
        return None
