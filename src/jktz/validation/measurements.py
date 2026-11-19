from __future__ import annotations

import re
from dataclasses import dataclass, replace

from jktz.validation._utils import (
    LRUD_RE,
    UNITS_DIRECTIVE_RE,
    active_lines,
    without_inline_comment,
)

_DATE_DIRECTIVE_RE = re.compile(r"^\s*#date\b", re.IGNORECASE)
_MACRO_REFERENCE_RE = re.compile(r"\$\(([^)]+)\)")
_MACRO_DEFINITION_RE = re.compile(
    r'(?<![^\s,])\$([^\s,=;]+)(?:\s*=\s*(?:"((?:[^"]|"")*)"|([^\s,;]+)))?'
)
_DECL_OPTION_RE = re.compile(r"(?<!\S)DECL\s*=", re.IGNORECASE)
_ORDER_RE = re.compile(r"(?<!\S)O(?:RDER)?\s*=\s*([A-Z]+)", re.IGNORECASE)
_UNITS_KEYWORD_RE = re.compile(r"(?<!\S)(SAVE|RESET|RESTORE|CT|RECT)(?!\S)", re.IGNORECASE)


@dataclass(frozen=True)
class _UnitsState:
    has_orientation: bool = False
    distance_index: int = 2
    rectangular: bool = False


def has_dated_or_declared_active_shots(text: str) -> bool:
    state = _UnitsState()
    saved_states: list[_UnitsState] = []
    macros: dict[str, str] = {}
    for _line_num, line in active_lines(text):
        if _DATE_DIRECTIVE_RE.match(line):
            state = replace(state, has_orientation=True)
            continue
        if UNITS_DIRECTIVE_RE.match(line):
            state = _apply_units(_units_options(line, macros), state, saved_states)
            continue
        if line.startswith("#"):
            continue
        if state.rectangular:
            continue
        readings = LRUD_RE.split(line, maxsplit=1)[0]
        tokens = readings.replace(",", " ").split()
        if len(tokens) <= state.distance_index:
            continue
        distance = _distance_value(tokens[state.distance_index])
        if distance is None:
            continue
        if distance == 0:
            continue
        if not state.has_orientation:
            return False
    return True


def _units_options(line: str, macros: dict[str, str]) -> str:
    # Walls expands references before processing any definitions on this line.
    expanded = _MACRO_REFERENCE_RE.sub(lambda ref: macros.get(ref[1], ""), line)
    options = without_inline_comment(expanded)
    for name, quoted, bare in _MACRO_DEFINITION_RE.findall(options):
        macros[name] = quoted.replace('""', '"') or bare
    return _MACRO_DEFINITION_RE.sub("", options).replace(",", " ")


def _apply_units(line: str, state: _UnitsState, saved_states: list[_UnitsState]) -> _UnitsState:
    # Walls saves before applying other parameters; RESET clears declination too.
    keywords = [keyword.upper() for keyword in _UNITS_KEYWORD_RE.findall(line)]
    if "SAVE" in keywords:
        saved_states.append(state)
    if "RESET" in keywords:
        state = _UnitsState()
    if "RESTORE" in keywords and saved_states:
        state = saved_states.pop()
    if _DECL_OPTION_RE.search(line):
        state = replace(state, has_orientation=True)
    for keyword in keywords:
        if keyword in {"CT", "RECT"}:
            state = replace(state, rectangular=keyword == "RECT")
    # CT and RECT orders are independent and can coexist on one directive.
    for order in _ORDER_RE.findall(line.upper()):
        if "D" in order:
            state = replace(state, distance_index=2 + order.index("D"))
    return state


def _distance_value(value: str) -> float | None:
    """Read enough of Walls length syntax to distinguish zero from active shots."""
    try:
        if value[-1:].upper() in {"M", "F"}:
            value = value[:-1]
        if "i" in value.lower():
            feet, inches = value.lower().split("i", 1)
            return float(feet or "0") * 12 + float(inches or "0")
        return float(value)
    except ValueError:
        return None
