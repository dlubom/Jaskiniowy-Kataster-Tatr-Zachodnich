"""Sensitivity of the four unresolved readings in Czarna's isolated scan survey.

This deliberately accepts only the current, uncorrected DAV survey contract.
It neither chooses readings nor compares coordinates with GNSS.
"""

from __future__ import annotations

import hashlib
import itertools
import math
import re
from collections.abc import Iterable
from dataclasses import dataclass, replace
from pathlib import Path

from jktz.metadata.srv import parse_srv_metadata

DEFAULT_INPUT = Path("Poligony/D_Koscieliska/Organy/Czarna/CZ_GL_R.SRV")
_NUMBER = re.compile(r"[+-]?\d+(?:\.\d+)?")
_HEADERS = {
    ("#prefix2", "Czarna"),
    ("#prefix", "CiagSkany"),
    ("#units", "meters", "order=DAV"),
    ("#units", "A=D", "V=D", "DECL=0"),
}
_MAIN_PAIRS = tuple((str(i), str(i + 1)) for i in range(76))
_EXPECTED_PAIRS = set(_MAIN_PAIRS) | {("6", "a"), ("a", "b")}


class SurveyContractError(ValueError):
    """The input no longer satisfies this diagnostic's narrow assumptions."""


@dataclass(frozen=True)
class Shot:
    distance: float
    azimuth: float | None
    inclination: float


@dataclass(frozen=True)
class UncertainReading:
    start: str
    end: str
    field: str
    attribute: str
    baseline: float
    alternative: float

    def describe(self) -> dict:
        return {
            "from": self.start,
            "to": self.end,
            "field": self.field,
            "baseline": self.baseline,
            "alternative": self.alternative,
        }


READINGS = (
    UncertainReading("29", "30", "D", "distance", 13.80, 13.60),
    UncertainReading("39", "40", "A", "azimuth", 25.0, 75.0),
    UncertainReading("49", "50", "A", "azimuth", 68.0, 88.0),
    UncertainReading("71", "72", "V", "inclination", -1.0, 1.0),
)


def _number(token: str, location: str) -> float:
    if not _NUMBER.fullmatch(token):
        raise SurveyContractError(f"{location}: unsupported numeric value {token!r}")
    value = float(token)
    if not math.isfinite(value):
        raise SurveyContractError(f"{location}: non-finite value")
    return value


def parse_survey(text: str, path: Path) -> dict[tuple[str, str], Shot]:
    """Reject unsupported directives, topology, units, or changed baseline readings."""
    metadata = parse_srv_metadata(path, text)
    if metadata.single["CAVE_ID"] != "T.E-09.12":
        raise SurveyContractError(f"{path}: expected Czarna CAVE_ID T.E-09.12")
    if metadata.repeated["SURVEY_DATE"] != ["nieznane"]:
        raise SurveyContractError(f"{path}: expected unknown survey date; reassess orientation")
    headers: set[tuple[str, ...]] = set()
    shots: dict[tuple[str, str], Shot] = {}
    body_lines = metadata.body.splitlines()
    line_offset = len(text.splitlines()) - len(body_lines)
    for line_number, line in enumerate(body_lines, line_offset + 1):
        tokens = line.split(";", 1)[0].split()
        if not tokens:
            continue
        location = f"{path}:{line_number}"
        if tokens[0].startswith("#"):
            header = tuple(tokens)
            if header not in _HEADERS or header in headers or shots:
                raise SurveyContractError(f"{location}: unsupported, repeated or late directive")
            headers.add(header)
            continue
        if headers != _HEADERS:
            raise SurveyContractError(f"{location}: incomplete Czarna DAV/DECL=0 header")
        if len(tokens) != 5:
            raise SurveyContractError(f"{location}: expected exactly FROM TO D A V")
        pair = (tokens[0], tokens[1])
        if pair not in _EXPECTED_PAIRS or pair in shots:
            raise SurveyContractError(f"{location}: unexpected or repeated station pair {pair}")
        distance = _number(tokens[2], location)
        inclination = _number(tokens[4], location)
        azimuth = None if tokens[3] == "--" else _number(tokens[3], location)
        if distance <= 0 or not -90 <= inclination <= 90:
            raise SurveyContractError(f"{location}: invalid distance or inclination")
        if azimuth is None and abs(inclination) != 90:
            raise SurveyContractError(f"{location}: missing azimuth is allowed only for a vertical")
        if azimuth is not None and not 0 <= azimuth < 360:
            raise SurveyContractError(f"{location}: azimuth outside [0, 360)")
        shots[pair] = Shot(distance, azimuth, inclination)
    if headers != _HEADERS or set(shots) != _EXPECTED_PAIRS:
        raise SurveyContractError(f"{path}: expected all 78 shots: 0-76 plus 6-a-b, without gaps")
    for reading in READINGS:
        value = getattr(shots[(reading.start, reading.end)], reading.attribute)
        if value != reading.baseline:
            raise SurveyContractError(
                f"{path}: baseline changed for {reading.start}-{reading.end} {reading.field}; "
                "review the diagnostic's alternatives before running"
            )
    return shots


def shot_vector(shot: Shot) -> tuple[float, float, float]:
    """Local E/N/Z in metres, angles in degrees, no declination or grid rotation."""
    if abs(shot.inclination) == 90:
        return (0.0, 0.0, math.copysign(shot.distance, shot.inclination))
    if shot.azimuth is None:
        raise SurveyContractError("non-vertical shot has no azimuth")
    a = math.radians(shot.azimuth)
    v = math.radians(shot.inclination)
    horizontal = shot.distance * math.cos(v)
    return (horizontal * math.sin(a), horizontal * math.cos(a), shot.distance * math.sin(v))


def _coordinates(values: Iterable[float]) -> dict[str, float]:
    return dict(zip(("E", "N", "Z"), values))


def _difference(endpoint: dict, origin: dict) -> dict:
    delta = {axis: endpoint[axis] - origin[axis] for axis in ("E", "N", "Z")}
    return {
        "delta_m": delta,
        "delta_horizontal_m": math.hypot(delta["E"], delta["N"]),
        "delta_3d_m": math.sqrt(math.fsum(value**2 for value in delta.values())),
    }


def analyze_survey(path: Path) -> dict:
    source = path.read_bytes()
    shots = parse_survey(source.decode("ascii"), path)
    variants = []
    for bits in itertools.product((0, 1), repeat=4):
        selected = dict(shots)
        parameters = []
        changes = []
        for bit, reading in zip(bits, READINGS):
            value = reading.alternative if bit else reading.baseline
            parameter = {
                "from": reading.start,
                "to": reading.end,
                "field": reading.field,
                "value": value,
            }
            parameters.append(parameter)
            if bit:
                changes.append(reading.describe())
                pair = (reading.start, reading.end)
                selected[pair] = replace(selected[pair], **{reading.attribute: value})
        vectors = [shot_vector(selected[pair]) for pair in _MAIN_PAIRS]
        endpoint = _coordinates(math.fsum(vector[axis] for vector in vectors) for axis in range(3))
        baseline_endpoint = variants[0]["endpoint_m"] if variants else endpoint
        variants.append(
            {
                "id": "".join(map(str, bits)),
                "parameters": parameters,
                "changes": changes,
                "main_length_m": math.fsum(selected[pair].distance for pair in _MAIN_PAIRS),
                "endpoint_m": endpoint,
                **_difference(endpoint, baseline_endpoint),
            }
        )
    pairs = [
        {
            "from_variant": first["id"],
            "to_variant": second["id"],
            **_difference(second["endpoint_m"], first["endpoint_m"]),
        }
        for first, second in itertools.combinations(variants, 2)
    ]
    return {
        "schema_version": 1,
        "purpose": "Analiza wrazliwosci; nie wybiera poprawnego odczytu i nie porownuje z GNSS.",
        "input": {"path": path.as_posix(), "sha256": hashlib.sha256(source).hexdigest()},
        "assumptions": {
            "coordinate_frame": "local E/N/Z, station 0 = (0,0,0), endpoint station 76",
            "units": "metres and degrees; DAV; DECL=0; no grid rotation or adjustment",
            "main_shots": 76,
            "excluded_branch_shots": ["6-a", "a-b"],
            "total_input_shots": len(shots),
            "variant_id": "bits follow uncertain_readings order; 0=baseline, 1=alternative",
        },
        "uncertain_readings": [reading.describe() for reading in READINGS],
        "baseline": variants[0],
        "single_alternative_effects": [item for item in variants if len(item["changes"]) == 1],
        "variants": variants,
        "farthest_pair": max(pairs, key=lambda pair: pair["delta_3d_m"]),
    }
