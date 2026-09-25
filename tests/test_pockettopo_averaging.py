"""Independent numerical contracts for confirmed PocketTopo reading groups."""

import math
import sys
from dataclasses import FrozenInstanceError, replace

import pytest

from jktz.pockettopo.averaging import (
    Average,
    NormalizedReading,
    average_readings,
    normalize_reading,
    validate_min_resultant,
)
from jktz.pockettopo.model import Shot, StationId


def _shot(**changes: object) -> Shot:
    return replace(
        Shot(StationId(-2147483647), StationId(-2147483646), 1234, 0, 0, 0, 0, 0, None),
        **changes,
    )


def _reading(azimuth: float, distance: float = 2.0, inclination: float = 0.0) -> NormalizedReading:
    return NormalizedReading(distance, azimuth, inclination, False)


@pytest.mark.parametrize(
    ("raw", "degrees"),
    [
        (0, 0.0),
        (1, 360 / 65536),
        (16384, 90.0),
        (-32768, 180.0),
        (-16384, 270.0),
        (-1, 360 - 360 / 65536),
    ],
)
def test_raw_signed_azimuth_bits_use_65536_units(raw: int, degrees: float) -> None:
    result = normalize_reading(_shot(azimuth_raw=raw, inclination_raw=1))
    assert result == NormalizedReading(1.234, degrees, 360 / 65536, False)


@pytest.mark.parametrize(("raw", "degrees"), [(-16384, -90.0), (0, 0.0), (16384, 90.0)])
def test_inclination_includes_both_vertical_endpoints(raw: int, degrees: float) -> None:
    assert normalize_reading(_shot(inclination_raw=raw)).inclination_deg == degrees


@pytest.mark.parametrize(
    ("raw", "expected"), [(0, 180.0), (16384, 270.0), (-32768, 0.0), (-16384, 90.0)]
)
def test_explicit_reversal_normalizes_azimuth_and_signed_inclination(
    raw: int, expected: float
) -> None:
    shot = _shot(azimuth_raw=raw, inclination_raw=2048, flags=1)
    result = normalize_reading(shot, reverse=True)
    assert result == NormalizedReading(1.234, expected, -11.25, True)
    assert shot.azimuth_raw == raw
    assert shot.inclination_raw == 2048
    assert shot.flags == 1


def test_flip_does_not_reverse_measurements_and_zero_distance_is_valid() -> None:
    assert normalize_reading(_shot(distance_mm=0, flags=1, azimuth_raw=4096)) == NormalizedReading(
        0.0, 22.5, 0.0, False
    )


@pytest.mark.parametrize(
    "changes", [{"distance_mm": -1}, {"inclination_raw": -16385}, {"inclination_raw": 16385}]
)
def test_raw_nonphysical_measurements_are_rejected_without_source_mutation(changes: dict) -> None:
    shot = _shot(**changes)
    before = replace(shot)
    with pytest.raises(ValueError):
        normalize_reading(shot)
    assert shot == before


def test_north_crossing_has_canonical_zero_and_shortest_deviation() -> None:
    result = average_readings((_reading(358, 1, -10), _reading(2, 3, 10)))
    assert result.count == 2
    assert result.azimuth_deg == 0.0
    assert result.distance_m == 2
    assert result.inclination_deg == 0
    assert result.resultant_length == pytest.approx(math.cos(math.radians(2)), abs=1e-15)
    assert result.azimuth_max_deviation_deg == 2
    assert result.distance_spread_m == 2
    assert result.inclination_spread_deg == 20


@pytest.mark.parametrize("angle", [1e-13, 359.9999999999999, -0.001, 361.25, -719.0])
def test_singleton_preserves_near_north_without_arbitrary_rounding(angle: float) -> None:
    result = average_readings((_reading(angle, 1.234567, -12.34567),))
    assert result.azimuth_deg == pytest.approx(angle % 360, abs=1e-14)
    assert result.azimuth_deg != 0
    assert result.distance_m == 1.234567
    assert result.inclination_deg == -12.34567
    assert result.resultant_length == pytest.approx(1.0, abs=1e-15)
    assert result.azimuth_max_deviation_deg == pytest.approx(0.0, abs=1e-13)
    assert result.distance_spread_m == 0
    assert result.inclination_spread_deg == 0


def test_sub_ulp_negative_north_is_canonical_zero_rather_than_360() -> None:
    # No float in [0, 360) represents 360 - 1e-20; modulo itself yields 360.
    assert average_readings((_reading(-1e-20),)).azimuth_deg == 0.0


def test_fsum_keeps_a_tiny_sine_between_opposite_cardinal_directions() -> None:
    result = average_readings((_reading(90), _reading(1e-13), _reading(270)))
    assert result.azimuth_deg == pytest.approx(1e-13, rel=1e-14, abs=0)


def test_large_finite_azimuth_is_reduced_before_trigonometry_and_deviation() -> None:
    angle = 1e308
    result = average_readings((_reading(angle),))
    assert result.azimuth_deg == pytest.approx(angle % 360, abs=1e-13)
    assert result.azimuth_max_deviation_deg == pytest.approx(0.0, abs=1e-13)


@pytest.mark.parametrize("angles", [(0, 180), (90, 270), (30, 210), (0, 90, 180, 270)])
def test_antipodal_groups_have_no_mean_or_angular_deviation(angles: tuple[float, ...]) -> None:
    result = average_readings(tuple(_reading(angle) for angle in angles))
    assert result.azimuth_deg is None
    assert result.azimuth_max_deviation_deg is None
    assert 0 <= result.resultant_length <= 1e-12
    assert result.count == len(angles)
    assert result.distance_m == 2.0
    assert result.inclination_deg == 0


def test_nearly_antipodal_threshold_is_inclusive_and_does_not_drop_readings() -> None:
    readings = (_reading(0, 1, -30), _reading(179.9, 9, 10))
    resolved = average_readings(readings)
    threshold = resolved.resultant_length
    assert resolved.azimuth_deg == pytest.approx(89.95, abs=1e-10)
    assert resolved.azimuth_max_deviation_deg == pytest.approx(89.95, abs=1e-10)
    assert average_readings(readings, min_resultant=threshold).azimuth_deg is None
    assert (
        average_readings(readings, min_resultant=math.nextafter(threshold, 0)).azimuth_deg
        is not None
    )
    unresolved = average_readings(readings, min_resultant=0.01)
    assert unresolved.count == 2
    assert unresolved.distance_m == 5
    assert unresolved.inclination_deg == -10
    assert unresolved.distance_spread_m == 8
    assert unresolved.inclination_spread_deg == 40


def test_equal_weight_arithmetic_values_are_not_a_three_dimensional_mean() -> None:
    result = average_readings((_reading(0, 1, -60), _reading(90, 99, 30)))
    assert result.distance_m == 50
    assert result.azimuth_deg == pytest.approx(45, abs=1e-14)
    assert result.inclination_deg == -15
    assert result.resultant_length == pytest.approx(2**-0.5, abs=1e-15)
    assert result.azimuth_max_deviation_deg == pytest.approx(45, abs=1e-14)
    assert result.distance_spread_m == 98
    assert result.inclination_spread_deg == 90


@pytest.mark.parametrize("inclination", [-90, 90])
def test_vertical_readings_still_follow_the_circular_azimuth_contract(inclination: float) -> None:
    result = average_readings(
        (_reading(40, inclination=inclination), _reading(80, inclination=inclination))
    )
    assert result.azimuth_deg == pytest.approx(60, abs=1e-14)
    assert result.inclination_deg == inclination
    assert result.resultant_length == pytest.approx(math.cos(math.radians(20)), abs=1e-15)
    assert result.azimuth_max_deviation_deg == pytest.approx(20, abs=1e-14)


def test_signed_verticals_cancel_inclination_but_not_recorded_azimuth() -> None:
    result = average_readings((_reading(12, inclination=-90), _reading(12, inclination=90)))
    assert result.inclination_deg == 0
    assert result.inclination_spread_deg == 180
    assert result.azimuth_deg == pytest.approx(12)


def test_outlier_is_retained_and_spreads_cover_every_member() -> None:
    result = average_readings((_reading(0, 1, -1), _reading(0, 2, 1), _reading(90, 300, 90)))
    assert result.count == 3
    assert result.distance_m == 101
    assert result.inclination_deg == 30
    assert result.azimuth_deg == pytest.approx(math.degrees(math.atan2(1, 2)), abs=1e-14)
    assert result.resultant_length == pytest.approx(math.sqrt(5) / 3, abs=1e-15)
    assert result.azimuth_max_deviation_deg == pytest.approx(90 - result.azimuth_deg, abs=1e-14)
    assert result.distance_spread_m == 299
    assert result.inclination_spread_deg == 91


def test_fsum_keeps_small_signed_terms_and_large_distances_do_not_overflow() -> None:
    result = average_readings(
        (
            _reading(0, sys.float_info.max, 90),
            _reading(0, sys.float_info.max, 1e-14),
            _reading(0, sys.float_info.max, -90),
        )
    )
    assert result.distance_m == sys.float_info.max
    assert result.inclination_deg == pytest.approx(1e-14 / 3, rel=1e-15, abs=0)
    assert result.distance_spread_m == 0


@pytest.mark.parametrize(
    "threshold", [float("nan"), float("inf"), -float("inf"), -1, 0, 1e-13, 1, 2, True, False]
)
def test_invalid_resultant_thresholds_are_rejected(threshold: float) -> None:
    with pytest.raises(ValueError, match="min_resultant"):
        average_readings((_reading(0),), min_resultant=threshold)
    with pytest.raises(ValueError, match="min_resultant"):
        validate_min_resultant(threshold)


def test_threshold_endpoints_and_empty_group() -> None:
    assert average_readings((_reading(0),), min_resultant=1e-12).azimuth_deg == 0
    assert average_readings((_reading(0),), min_resultant=math.nextafter(1.0, 0)).azimuth_deg == 0
    with pytest.raises(ValueError, match="at least one"):
        average_readings(())


@pytest.mark.parametrize("turns", [(0,), (0, 0, 0), (0, 1, -1), (1, -1, 0)])
def test_identical_noncardinal_directions_are_defined_at_threshold_near_one(
    turns: tuple[int, ...],
) -> None:
    angle = normalize_reading(_shot(azimuth_raw=1491)).azimuth_deg
    result = average_readings(
        tuple(_reading(angle + turn * 360) for turn in turns),
        min_resultant=math.nextafter(1.0, 0.0),
    )
    assert result.count == len(turns)
    assert result.azimuth_deg == angle
    assert result.resultant_length == 1.0
    assert result.azimuth_max_deviation_deg == 0.0


def test_different_noncardinal_directions_keep_threshold_rule_near_one() -> None:
    readings = (_reading(8.1903076171875), _reading(9.1903076171875))
    default = average_readings(readings)
    assert default.azimuth_deg == pytest.approx(8.6903076171875, abs=1e-14)
    assert default.resultant_length < math.nextafter(1.0, 0.0)
    stringent = average_readings(readings, min_resultant=math.nextafter(1.0, 0.0))
    assert stringent.resultant_length == default.resultant_length
    assert stringent.azimuth_deg is None
    assert stringent.azimuth_max_deviation_deg is None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("distance_m", -0.001),
        ("distance_m", float("nan")),
        ("distance_m", float("inf")),
        ("distance_m", -float("inf")),
        ("azimuth_deg", float("nan")),
        ("azimuth_deg", float("inf")),
        ("azimuth_deg", -float("inf")),
        ("inclination_deg", -90.00001),
        ("inclination_deg", 90.00001),
        ("inclination_deg", float("nan")),
        ("inclination_deg", float("inf")),
        ("inclination_deg", -float("inf")),
    ],
)
def test_every_reading_is_validated_before_mean(field: str, value: float) -> None:
    invalid = replace(_reading(0), **{field: value})
    with pytest.raises(ValueError, match=field):
        average_readings((_reading(0), invalid))


def test_results_and_normalized_readings_are_immutable() -> None:
    reading = _reading(45)
    result = average_readings((reading,))
    assert isinstance(result, Average)
    with pytest.raises(FrozenInstanceError):
        reading.azimuth_deg = 0  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        result.count = 2  # type: ignore[misc]
