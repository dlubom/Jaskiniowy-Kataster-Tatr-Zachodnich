"""Grouping requires an explicit complete plan, never geometrical similarity."""

from __future__ import annotations

import signal
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from jktz.pockettopo.grouping import (
    Exclusion,
    RecordGroup,
    RepeatConfirmation,
    make_groups,
    shot_kind,
    shot_problem,
)
from jktz.pockettopo.model import Drawing, Mapping, Point, Shot, StationId, TopFile, Trip
from jktz.pockettopo.parser import read_top

UNDEFINED = StationId(-2147483648)
PLAIN_ZERO = StationId(-2147483647)
A = StationId(0)
B = StationId(1)
C = StationId(2)
BASE = Shot(A, B, 1000, 0, 0, 0, 0, 0, None)


@pytest.fixture(autouse=True)
def grouping_terminates_promptly():
    """Tiny plans must finish, including when traversal stops making progress.

    Mutation campaigns run on POSIX. Windows still runs all behavior tests,
    without the POSIX timer; no production timeout policy is introduced.
    """
    if not hasattr(signal, "setitimer"):
        yield
        return

    def fail_on_nontermination(_signum, _frame):
        raise AssertionError("Grouping tiny fixtures must terminate within one second")

    previous_handler = signal.signal(signal.SIGALRM, fail_on_nontermination)
    previous_timer = signal.setitimer(signal.ITIMER_REAL, 1.0)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous_handler)
        signal.setitimer(signal.ITIMER_REAL, *previous_timer)


def source(*shots: Shot) -> TopFile:
    mapping = Mapping(Point(0, 0), 500)
    drawing = Drawing(mapping, ())
    return TopFile(
        (Trip(0, "session one", 0), Trip(0, "session two", 0)),
        tuple(shots),
        (),
        mapping,
        drawing,
        drawing,
        "eof",
    )


def test_no_implicit_grouping_and_no_records_disappear() -> None:
    shots = (
        BASE,
        BASE,
        replace(BASE, from_id=B, to_id=A),
        replace(BASE, to_id=UNDEFINED),
        replace(BASE, distance_mm=0),
        replace(BASE, distance_mm=-1),
        replace(BASE, trip_index=-1),
    )
    original = source(*shots)
    expected = tuple(RecordGroup((index,)) for index in range(7))
    assert make_groups(original) == expected
    assert make_groups(original, exclusions=(Exclusion(1, "separate survey"),)) == expected
    assert original == source(*shots)
    assert make_groups(source()) == ()


def test_explicit_groups_follow_source_order_and_keep_evidence_verbatim() -> None:
    reverse = replace(BASE, from_id=B, to_id=A, inclination_raw=1000, flags=1)
    records = source(BASE, reverse, BASE, BASE, BASE, BASE, BASE, BASE)
    confirmations = (
        RepeatConfirmation((4, 5, 6), " Author's field notes: 4–6\n "),
        RepeatConfirmation((0, 1), "repeat pair"),
    )
    expected = (
        RecordGroup((0, 1), "repeat pair"),
        RecordGroup((2,)),
        RecordGroup((3,)),
        RecordGroup((4, 5, 6), " Author's field notes: 4–6\n "),
        RecordGroup((7,)),
    )
    assert make_groups(records, confirmations, (Exclusion(3, "bad instrument"),)) == expected
    assert tuple(index for group in expected for index in group.indices) == tuple(range(8))
    assert records.shots[1] == reverse
    assert confirmations[0].indices == (4, 5, 6)


@pytest.mark.parametrize(
    "plan", [RepeatConfirmation((0, 1), "source"), Exclusion(0, "reason"), RecordGroup((0,))]
)
def test_plans_are_frozen(plan) -> None:
    field = "index" if isinstance(plan, Exclusion) else "indices"
    with pytest.raises(FrozenInstanceError):
        setattr(plan, field, 99)


@pytest.mark.parametrize("inclination", [-16384, -16383, 0, 16383, 16384])
@pytest.mark.parametrize("distance", [1, 1000])
def test_valid_leg_range_boundaries(inclination: int, distance: int) -> None:
    shot = replace(BASE, inclination_raw=inclination, distance_mm=distance)
    assert shot_problem(shot) is None
    assert shot_kind(shot) == "leg"
    assert make_groups(source(shot, shot), (RepeatConfirmation((0, 1), "field book"),)) == (
        RecordGroup((0, 1), "field book"),
    )


@pytest.mark.parametrize(
    ("changes", "kind", "problem"),
    [
        ({"distance_mm": 0}, "zero_link", None),
        ({"from_id": PLAIN_ZERO}, "leg", None),
        ({"from_id": PLAIN_ZERO, "to_id": A, "distance_mm": 0}, "zero_link", None),
        ({"from_id": UNDEFINED}, "splay", None),
        ({"to_id": UNDEFINED}, "splay", None),
        ({"from_id": UNDEFINED, "flags": 1}, "splay", None),
        ({"distance_mm": -1}, "invalid", "negative_distance"),
        ({"inclination_raw": -16385}, "invalid", "inclination_out_of_range"),
        ({"inclination_raw": 16385}, "invalid", "inclination_out_of_range"),
        ({"from_id": UNDEFINED, "to_id": UNDEFINED}, "invalid", "both_stations_undefined"),
        ({"from_id": A, "to_id": A}, "invalid", "self_shot"),
        ({"from_id": A, "to_id": A, "distance_mm": 0}, "invalid", "self_link"),
        ({"from_id": UNDEFINED, "distance_mm": 0}, "invalid", "zero_unnamed_shot"),
        ({"to_id": UNDEFINED, "distance_mm": 0}, "invalid", "zero_unnamed_shot"),
    ],
)
def test_shot_categories_and_explicit_invalid_reasons(
    changes: dict, kind: str, problem: str
) -> None:
    shot = replace(BASE, **changes)
    assert shot_kind(shot) == kind
    assert shot_problem(shot) == problem
    assert make_groups(source(shot)) == (RecordGroup((0,)),)


@pytest.mark.parametrize("bad", [True, False, 0.0, "0", None, -1, 2])
def test_invalid_confirmation_indices_fail_before_record_access(bad) -> None:
    with pytest.raises(ValueError, match="^record_index_must_be_an_in_range_integer$"):
        make_groups(source(BASE, BASE), (RepeatConfirmation((0, bad), "source"),))


@pytest.mark.parametrize("bad", [True, False, 0.0, "0", None, -1, 2])
def test_invalid_exclusion_indices_fail(bad) -> None:
    with pytest.raises(ValueError, match="^record_index_must_be_an_in_range_integer$"):
        make_groups(source(BASE, BASE), exclusions=(Exclusion(bad, "reason"),))


@pytest.mark.parametrize("bad", [(), (0,), [0, 1], None, "01"])
def test_confirmations_require_immutable_multiple_indices(bad) -> None:
    with pytest.raises(
        ValueError, match="^repeat_indices_must_be_a_tuple_with_at_least_two_records$"
    ):
        make_groups(source(BASE, BASE), (RepeatConfirmation(bad, "source"),))


@pytest.mark.parametrize("indices", [(0, 2), (1, 0), (0, 0), (0, 1, 1), (0, 2, 1)])
def test_nonconsecutive_or_unsorted_series_fail(indices: tuple[int, ...]) -> None:
    with pytest.raises(ValueError, match="^repeat_indices_must_be_sorted_and_consecutive$"):
        make_groups(source(BASE, BASE, BASE), (RepeatConfirmation(indices, "source"),))


@pytest.mark.parametrize("text", ["", " \t\n", None, 1, True])
def test_evidence_and_exclusion_reasons_must_be_nonblank_strings(text) -> None:
    with pytest.raises(ValueError, match="^repeat_evidence_must_be_nonblank_text$"):
        make_groups(source(BASE, BASE), (RepeatConfirmation((0, 1), text),))
    with pytest.raises(ValueError, match="^exclusion_reason_must_be_nonblank_text$"):
        make_groups(source(BASE), exclusions=(Exclusion(0, text),))


def test_duplicate_exclusions_and_overlaps_fail() -> None:
    records = source(BASE, BASE, BASE)
    with pytest.raises(ValueError, match="^duplicate_exclusion$"):
        make_groups(records, exclusions=(Exclusion(1, "first"), Exclusion(1, "second")))
    with pytest.raises(ValueError, match="^overlapping_repeat_confirmations$"):
        make_groups(
            records,
            (RepeatConfirmation((0, 1), "one"), RepeatConfirmation((1, 2), "two")),
        )
    with pytest.raises(ValueError, match="^repeat_contains_excluded_record$"):
        make_groups(records, (RepeatConfirmation((0, 1), "one"),), (Exclusion(1, "excluded"),))


@pytest.mark.parametrize(
    "changes",
    [
        {"from_id": UNDEFINED},
        {"to_id": UNDEFINED},
        {"from_id": UNDEFINED, "to_id": UNDEFINED},
        {"from_id": A, "to_id": A},
        {"distance_mm": 0},
        {"distance_mm": -1},
        {"inclination_raw": -16385},
        {"inclination_raw": 16385},
    ],
)
@pytest.mark.parametrize("position", [0, 1])
def test_nonlegs_interrupt_confirmed_group(changes: dict, position: int) -> None:
    shots = [BASE, BASE]
    shots[position] = replace(BASE, **changes)
    with pytest.raises(ValueError, match="^repeat_requires_valid_nonzero_named_legs$"):
        make_groups(source(*shots), (RepeatConfirmation((0, 1), "source"),))


@pytest.mark.parametrize("trip", [-1, -2, 2])
def test_unknown_session_cannot_confirm_repeat(trip: int) -> None:
    unknown = replace(BASE, trip_index=trip)
    with pytest.raises(ValueError, match="^repeat_requires_known_session$"):
        make_groups(source(unknown, unknown), (RepeatConfirmation((0, 1), "source"),))


@pytest.mark.parametrize("trip", [-1, 1, 2])
def test_session_changes_interrupt_group(trip: int) -> None:
    with pytest.raises(ValueError, match="^repeat_session_changed$"):
        make_groups(
            source(BASE, replace(BASE, trip_index=trip)), (RepeatConfirmation((0, 1), "x"),)
        )


@pytest.mark.parametrize(
    ("from_id", "to_id"), [(A, C), (C, B), (B, C), (PLAIN_ZERO, B), (A, PLAIN_ZERO)]
)
def test_station_identity_uses_raw_pair_including_plain_zero(from_id: StationId, to_id: StationId):
    other = replace(BASE, from_id=from_id, to_id=to_id)
    with pytest.raises(ValueError, match="^repeat_station_pair_changed$"):
        make_groups(source(BASE, other), (RepeatConfirmation((0, 1), "source"),))


def test_separated_series_remain_separate_even_if_pair_and_session_match() -> None:
    records = source(BASE, BASE, replace(BASE, to_id=UNDEFINED), BASE, BASE)
    assert make_groups(
        records, (RepeatConfirmation((0, 1), "book A"), RepeatConfirmation((3, 4), "book B"))
    ) == (RecordGroup((0, 1), "book A"), RecordGroup((2,)), RecordGroup((3, 4), "book B"))


def test_whole_plan_validation_rejects_invalid_later_entries_without_output() -> None:
    records = source(BASE, BASE, BASE, BASE)
    with pytest.raises(ValueError, match="^repeat_evidence_must_be_nonblank_text$"):
        make_groups(records, (RepeatConfirmation((0, 1), "valid"), RepeatConfirmation((2, 3), "")))
    with pytest.raises(ValueError, match="^exclusion_reason_must_be_nonblank_text$"):
        make_groups(
            records,
            (RepeatConfirmation((0, 1), "valid"),),
            (Exclusion(2, "valid"), Exclusion(3, "")),
        )
    assert records == source(BASE, BASE, BASE, BASE)


@pytest.mark.parametrize("case", ["zach0dni2", "okna", "DS201208"])
def test_real_candidates_never_become_confirmed_repeats_by_similarity(case: str) -> None:
    directory = Path(__file__).resolve().parent / "fixtures/pockettopo/repeat-candidates"
    records = read_top(next((directory / case).glob("*.top")))
    assert make_groups(records) == tuple(RecordGroup((i,)) for i in range(len(records.shots)))
