from __future__ import annotations

import pytest

from jktz.validation.measurements import has_dated_or_declared_active_shots


def test_active_shot_scanner_requires_date_or_decl_for_nonzero_shots() -> None:
    assert has_dated_or_declared_active_shots("#date 2004-06-19\n0\t1\t1.0\t90\t0\n")
    assert has_dated_or_declared_active_shots("#Units DECL=0.819D\n0\t1\t1.0\t90\t0\n")
    assert has_dated_or_declared_active_shots("0\t1\t0\t0\t0\n")
    assert has_dated_or_declared_active_shots(";0\t1\t1.0\t90\t0\n")
    assert not has_dated_or_declared_active_shots("0\t1\t1.0\t90\t0\n")


@pytest.mark.parametrize("order", ["DAV", "DVA"])
def test_active_shot_scanner_reads_distance_from_third_token_for_dav_and_dva(order: str) -> None:
    assert not has_dated_or_declared_active_shots(
        f"#units meters order={order}\n0\t1\t1.0\t90\t0\n"
    )
    assert has_dated_or_declared_active_shots(
        f"#units meters order={order}\n#date 2004-06-19\n0\t1\t1.0\t90\t0\n"
    )


def test_active_shot_scanner_reads_distance_from_fifth_token_for_avd() -> None:
    text = "#units meters order=AVD\n0\t1\t0\t0\t1.0\n"

    assert not has_dated_or_declared_active_shots(text)
    assert has_dated_or_declared_active_shots("#date 2004-06-19\n" + text)


def test_active_shot_scanner_keeps_zero_shots_allowed_for_unit_orders() -> None:
    assert has_dated_or_declared_active_shots("#units meters order=DAV\n0\t1\t0\t90\t0\n")
    assert has_dated_or_declared_active_shots("#units meters order=AVD\n0\t1\t90\t0\t0\n")


def test_active_shot_scanner_ignores_rectangular_delta_rows() -> None:
    assert has_dated_or_declared_active_shots("#units meters rect Order=NEU\n0\t1\t1.0\t2.0\t3.0\n")


def test_active_shot_scanner_preserves_order_across_units_without_order() -> None:
    assert not has_dated_or_declared_active_shots(
        "#units meters order=AVD\n#units A=D V=D\n0\t1\t0\t0\t1.0\n"
    )
