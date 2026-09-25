"""Unrounded arithmetic distance/inclination and circular azimuth means.

This module does not decide which source records are repeated readings. Callers
must establish that independently before supplying an explicitly selected group.
Vertical readings retain their recorded azimuth under the same circular rule;
neither inclination nor distance weights the azimuth mean.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from jktz.pockettopo.model import Shot


@dataclass(frozen=True)
class NormalizedReading:
    distance_m: float
    azimuth_deg: float
    inclination_deg: float
    reversed: bool


@dataclass(frozen=True)
class Average:
    count: int
    distance_m: float
    azimuth_deg: float | None
    inclination_deg: float
    resultant_length: float
    azimuth_max_deviation_deg: float | None
    distance_spread_m: float
    inclination_spread_deg: float


def _validate_reading(reading: NormalizedReading) -> None:
    if not math.isfinite(reading.distance_m) or reading.distance_m < 0:
        raise ValueError("distance_m must be finite and nonnegative")
    if not math.isfinite(reading.azimuth_deg):
        raise ValueError("azimuth_deg must be finite")
    if not math.isfinite(reading.inclination_deg) or not -90 <= reading.inclination_deg <= 90:
        raise ValueError("inclination_deg must be finite and between -90 and 90")


def _canonical_azimuth(degrees: float) -> float:
    result = degrees % 360.0
    # Floating modulo of a tiny negative atan2 result can round to exactly 360.
    # Correct that endpoint alone; never round legitimate near-north readings.
    return 0.0 if result == 360.0 else result


def validate_min_resultant(value: float) -> None:
    """Validate a circular ambiguity threshold even when no mean is needed."""
    if isinstance(value, bool) or not math.isfinite(value) or not 1e-12 <= value < 1:
        raise ValueError("min_resultant must be finite and in [1e-12, 1)")


def normalize_reading(shot: Shot, *, reverse: bool = False) -> NormalizedReading:
    """Decode the source units, optionally reversing FROM/TO, without rounding.

    The source model is left untouched. Flip is a drawing-direction flag and
    does not imply reversal. Invalid physical distance/inclination raises
    ValueError, while the parser's source record remains available for reporting.
    """
    azimuth = (shot.azimuth_raw % 65536) * 360.0 / 65536
    inclination = shot.inclination_raw * 360.0 / 65536
    if reverse:
        azimuth = (azimuth + 180.0) % 360.0
        inclination = -inclination
    reading = NormalizedReading(shot.distance_mm / 1000.0, azimuth, inclination, reverse)
    _validate_reading(reading)
    return reading


def _circular_mean(
    azimuths: tuple[float, ...], min_resultant: float
) -> tuple[float | None, float, float | None]:
    canonical = tuple(_canonical_azimuth(value) for value in azimuths)
    if all(value == canonical[0] for value in canonical):
        # Identical directions have an exact resultant of one. A trig round
        # trip can produce the float immediately below one and incorrectly
        # classify them as ambiguous at a valid threshold close to one.
        return canonical[0], 1.0, 0.0
    # Center argument reduction on north: e.g. 358/2 becomes -2/2 exactly,
    # avoiding a spurious tiny positive bearing from unequal trig roundoff.
    angles = tuple(math.radians(math.remainder(azimuth, 360.0)) for azimuth in azimuths)
    sine = math.fsum(math.sin(angle) for angle in angles)
    cosine = math.fsum(math.cos(angle) for angle in angles)
    # Clamp roundoff at the physical upper bound, not the ambiguity threshold.
    resultant = min(1.0, math.hypot(sine / len(angles), cosine / len(angles)))
    if resultant <= min_resultant:
        return None, resultant, None
    azimuth = _canonical_azimuth(math.degrees(math.atan2(sine, cosine)))
    max_deviation = max(abs(math.remainder(value % 360.0 - azimuth, 360.0)) for value in azimuths)
    return azimuth, resultant, max_deviation


def _distance_mean(distances: tuple[float, ...]) -> float:
    try:
        return math.fsum(distances) / len(distances)
    except OverflowError:
        # The public API accepts finite distances larger than the source's
        # int32 mm range. Their mean is finite even if their sum overflows.
        maximum = max(distances)
        return (math.fsum(distance / maximum for distance in distances) / len(distances)) * maximum


def average_readings(
    readings: tuple[NormalizedReading, ...], *, min_resultant: float = 1e-12
) -> Average:
    """Average every supplied reading with equal weight; never reject outliers.

    ``resultant_length`` is the circular mean vector length in [0, 1]. At or
    below ``min_resultant`` the direction and angular deviation are undefined.
    The threshold must be finite in [1e-12, 1): the floor prevents floating
    residuals from making an antipodal pair appear to have a direction, while
    the exclusive upper bound keeps identical directions well-defined. Exactly
    identical azimuths modulo 360 have an exact resultant of one, independently
    of floating trigonometric roundoff.

    Distance/inclination spreads are max-minus-min, and azimuth spread is the
    maximum shortest angular distance from the circular mean. All quantities
    are calculated before any presentation rounding.
    """
    if not readings:
        raise ValueError("at least one reading is required")
    validate_min_resultant(min_resultant)
    for reading in readings:
        _validate_reading(reading)
    count = len(readings)
    distances = tuple(reading.distance_m for reading in readings)
    inclinations = tuple(reading.inclination_deg for reading in readings)
    azimuth, resultant, deviation = _circular_mean(
        tuple(reading.azimuth_deg for reading in readings), min_resultant
    )
    return Average(
        count=count,
        distance_m=_distance_mean(distances),
        azimuth_deg=azimuth,
        inclination_deg=math.fsum(inclinations) / count,
        resultant_length=resultant,
        azimuth_max_deviation_deg=deviation,
        distance_spread_m=max(distances) - min(distances),
        inclination_spread_deg=max(inclinations) - min(inclinations),
    )
