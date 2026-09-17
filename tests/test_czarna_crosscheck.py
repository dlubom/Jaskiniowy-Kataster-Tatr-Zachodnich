import hashlib
import json
from copy import deepcopy
from pathlib import Path

import pytest

from jktz.czarna_crosscheck import (
    CAVE,
    FIELDS,
    PAIRS,
    arithmetic,
    audit,
    check_checkpoints,
    compare_model,
    cumulative,
    parse_srv,
    written_dh_bounds,
)


def row(start="0", end="1", **values):
    return {
        "from": start,
        "to": end,
        "line": 1,
        "values": {**dict(D=5, A=90, V=0, Lh=5, dh=0), **values},
        "uncertain_fields": [],
        "alternatives": {},
    }


def test_degree_math_sign_and_pythagorean_check():
    result = arithmetic(dict(D=10, A=32, V=-30, Lh=8.66, dh=-5))
    assert result["calculated_dh"] == pytest.approx(-5)
    assert result["calculated_Lh"] == pytest.approx(8.660254037844386)
    assert result["norm_distance_from_aux"] == pytest.approx(9.999779997579946)
    assert all(result["strict_rounding_0_005m"].values())
    assert result["azimuth_testable"] is False
    assert result == arithmetic(dict(D=10, A=222, V=-30, Lh=8.66, dh=-5))


def test_literal_source_error_not_silently_fixed():
    result = arithmetic(dict(D=6.7, A=91, V=35, Lh=6.46, dh=3.84))
    assert result["within_0_05m"] == {"Lh": False, "dh": True}
    assert result["residual_scan_minus_calculated"]["Lh"] == pytest.approx(0.971681303263755)


def test_uncertain_fields_are_excluded_equally_and_alternatives_separate():
    ref = row()
    ref["uncertain_fields"] = ["A"]
    candidate = row(A=10, D=4)
    candidate["alternatives"] = {"D": [5]}
    result = compare_model([candidate], [ref])
    assert result["counts"] == dict(assessed=4, wrong=1, including_alternatives=4, correct=3)
    assert result["mismatches"][0]["field"] == "D"
    assert result["mismatches"][0]["correct_in_alternatives"] is True


def test_missing_topology_and_duplicates_do_not_inflate_score():
    ref = row("19", "20")
    wrong_pair = row("18", "20")
    comparison = compare_model([wrong_pair, deepcopy(wrong_pair)], [ref])
    assert comparison["counts"] == dict(assessed=5, missing=5)
    assert comparison["pairs_unique"] == 1
    assert comparison["extra_pairs"] == [["18", "20"]]
    first, second = row(D=4), row(D=5)
    second["line"] = 10
    result = compare_model([first, second], [row()])
    assert result["counts"]["assessed"] == 5
    assert result["counts"]["wrong"] == 1
    assert result["repeat_conflicts"][0]["repeat_conflicts"][0]["line"] == 10


def test_branch_cumulative_and_checkpoint_intervals():
    rows = [row(start, end, D=1, V=90, Lh=0, dh=1) for start, end in PAIRS]
    sums = cumulative(rows, "dh")
    assert sums["76"] == 76
    assert sums["6"] == 6
    assert sums["a"] == 7
    assert sums["b"] == 8
    checks = check_checkpoints(
        rows, [dict(station="b", value=8, previous_station="a", previous_value=7)]
    )
    assert checks[0]["residual_written"] == 0
    assert checks[0]["interval_residual"] == 0
    assert checks[0]["sum_trig_dh"] == pytest.approx(8)


def test_vertical_blank_azimuth_is_correct_not_missing():
    ref = row(A=None, V=-90, D=10, Lh=0, dh=-10)
    assert compare_model([ref], [ref])["counts"]["correct"] == len(FIELDS)
    assert arithmetic(ref["values"])["strict_rounding_0_005m"]["Lh"]


def test_original_codex_uncertainty_is_not_lost_in_scoring():
    snapshot = (
        Path(__file__).resolve().parents[1] / CAVE / "KONTROLA_RACHUNKOW/CODEX_PIERWOTNY.SRV.txt"
    )
    original = parse_srv(snapshot.read_text(encoding="utf-8"))
    assert original[29]["alternatives"] == {"D": [13.6]}
    assert original[39]["alternatives"] == {"A": [75.0]}
    assert original[49]["alternatives"] == {"A": [88.0]}
    assert original[71]["alternatives"] == {"V": [1.0]}
    ref = deepcopy(original)
    for r in ref:
        r["uncertain_fields"] = []
    ref[39]["values"]["A"] = 75
    scored = compare_model(original, ref)
    assert scored["counts"]["correct"] == 389
    assert scored["counts"]["including_alternatives"] == 390


def test_interval_bounds_cancel_shared_prefix_not_independent_endpoints():
    rows = [row(start, end, D=1, V=90, Lh=0, dh=1) for start, end in PAIRS]
    rows[0]["alternatives"] = {"dh": [-100]}
    rows[76]["alternatives"] = {"dh": [2]}
    assert written_dh_bounds(rows, "a", "6") == [1, 2]
    assert written_dh_bounds(rows, "b", "a") == [1, 1]
    with pytest.raises(ValueError, match="single directed path"):
        written_dh_bounds(rows, "b", "76")


def test_missing_auxiliary_is_not_a_confirmed_arithmetic_conflict():
    result = arithmetic(dict(D=1, V=0, Lh=None, dh=0))
    assert result["status"] == "missing_auxiliary"
    assert result["within_0_05m"]["Lh"] is None


def test_stale_reviewed_source_stops_before_producing_a_new_report(tmp_path):
    source = tmp_path / "source.txt"
    source.write_bytes(b"changed")
    reference = tmp_path / "reference.json"
    reference.write_text(
        json.dumps(
            {
                "reviewed_sources": [
                    {"path": "source.txt", "sha256": hashlib.sha256(b"original").hexdigest()}
                ]
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Reviewed source changed"):
        audit(tmp_path, reference)
