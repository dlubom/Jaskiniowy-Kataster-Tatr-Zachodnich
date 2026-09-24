from __future__ import annotations

import pytest

from jktz.validation.measurements import has_dated_or_declared_active_shots


def test_active_shot_scanner_requires_date_or_decl_for_nonzero_shots() -> None:
    assert has_dated_or_declared_active_shots("#date 2004-06-19\n0\t1\t1.0\t90\t0\n")
    assert has_dated_or_declared_active_shots("#Units DECL=0.819D\n0\t1\t1.0\t90\t0\n")
    assert has_dated_or_declared_active_shots("0\t1\t0\t0\t0\n")
    assert has_dated_or_declared_active_shots(";0\t1\t1.0\t90\t0\n")
    assert not has_dated_or_declared_active_shots("0\t1\t1.0\t90\t0\n")


def test_active_shot_scanner_ignores_date_inside_block_comment() -> None:
    text = "#[ disabled\n#date 2004-06-19\n#]\n0\t1\t1.0\t90\t0\n"

    assert not has_dated_or_declared_active_shots(text)


def test_active_shot_scanner_ignores_shots_inside_block_comment() -> None:
    text = "#[ deferred\n0\t1\t1.0\t90\t0\n#]\n"

    assert has_dated_or_declared_active_shots(text)


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


@pytest.mark.parametrize(
    "text",
    [
        "#units rect order=NEU\n0 1 1 2 3\n#units CT\n1 2 10 90 0\n",
        "#units DECL=0\n#units reset\n0 1 10 90 0\n",
        "#units save DECL=0\n0 1 10 90 0\n#units restore\n1 2 10 90 0\n",
        "#units rect order=NEU\n#units save CT DECL=0\n0 1 10 90 0\n"
        "#units restore\n#units CT\n1 2 10 90 0\n",
        "#units rect=0 order=DAV\n0 1 10 90 0\n",
        "#units order=AVD\n#units order=NEU\n0 1 0 0 10\n",
        "#units order=NEU order=AVD\n0 1 0 0 10\n",
    ],
)
def test_units_state_changes_cannot_hide_undeclared_compass_shots(text: str) -> None:
    assert not has_dated_or_declared_active_shots(text)


@pytest.mark.parametrize(
    "text",
    [
        "#units rect\n0 1 1 2 3\n",
        "#units rect order=NEU\n#units order=DAV\n0 1 1 2 3\n",
        "#units DECL=0\n#units save reset rect\n0 1 1 2 3\n#units restore\n1 2 10 90 0\n",
        "#units rect order=NEU\n#units save CT DECL=0\n0 1 10 90 0\n#units restore\n1 2 1 2 3\n",
        "#date 2004-06-19\n#units save reset\n#units save DECL=1\n0 1 10 90 0\n"
        "#units restore\n#units restore\n1 2 10 90 0\n",
    ],
)
def test_units_state_restores_orientation_and_keeps_rectangular_order_separate(text: str) -> None:
    assert has_dated_or_declared_active_shots(text)


@pytest.mark.parametrize(
    "prefix",
    [
        "\n; comment\n",
        "#[#]\n",
        "#date 2004-06-19\n#units reset\n",
        "#prefix Cave\n",
        "0 <1,2,3,4>\n",
        "0 1 -- 90 0\n",
        "0 1 0 0 0\n",
    ],
)
def test_scanner_reaches_undeclared_shot_after_non_survey_or_zero_rows(prefix: str) -> None:
    assert not has_dated_or_declared_active_shots(prefix + "1 2 3 90 0\n")


def test_fixed_coordinates_are_not_compass_measurements() -> None:
    assert has_dated_or_declared_active_shots("#fix A 10 20 30\n")
