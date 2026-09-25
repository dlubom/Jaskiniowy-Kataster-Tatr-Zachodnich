"""P03 audit contract against native P01 files and narrowly mutated records."""

from __future__ import annotations

import hashlib
import json
import math
import struct
from importlib.metadata import version
from pathlib import Path

import pytest

from jktz.pockettopo.grouping import Exclusion, RepeatConfirmation
from jktz.pockettopo.parser import ParseError, ParseLimits
from jktz.pockettopo.report import ProcessingPlan, prepare_conversion

EVIDENCE = Path(__file__).resolve().parents[1] / "doc/pockettopo/evidence"
CASES = sorted((EVIDENCE / "p01/cases").iterdir())
REPEAT_MANIFEST = json.loads((EVIDENCE / "repeat-candidates/manifest.json").read_text())
CONFIRMATION = "Native P01 pockettopo_fixtures.cs:167-169 explicitly defines repeat A1/A2/A3"


def _native(name: str) -> tuple[bytes, dict]:
    case = EVIDENCE / "p01/cases" / name
    return next(case.glob("*.top")).read_bytes(), json.loads((case / "expected.json").read_text())


def _raw_oracle(value):
    if isinstance(value, list):
        return [_raw_oracle(item) for item in value]
    if isinstance(value, dict):
        if "raw" in value:
            return {"raw": value["raw"]}
        return {key: _raw_oracle(item) for key, item in value.items()}
    return value


def _plan(data: bytes, *, confirmations=(), exclusions=()) -> ProcessingPlan:
    return ProcessingPlan(hashlib.sha256(data).hexdigest(), confirmations, exclusions)


def _string(value: str) -> bytes:
    encoded = value.encode("utf-8")
    length = len(encoded)
    prefix = bytearray()
    while length >= 128:
        prefix.append((length & 127) | 128)
        length >>= 7
    return bytes(prefix) + bytes([length]) + encoded


def _shot_bytes(shot: dict) -> bytes:
    body = struct.pack(
        "<iiihhBBh",
        shot["from_id"]["raw"],
        shot["to_id"]["raw"],
        shot["distance_mm"],
        shot["azimuth_raw"],
        shot["inclination_raw"],
        shot["flags"],
        shot["roll_raw"],
        shot["trip_index"],
    )
    return body + (_string(shot["comment"]) if shot["flags"] & 2 else b"")


def _replace_shot(data: bytes, oracle: dict, index: int, **changes) -> bytes:
    original = oracle["source"]["shots"][index]
    needle = _shot_bytes(original)
    assert data.count(needle) == 1
    return data.replace(needle, _shot_bytes({**original, **changes}), 1)


@pytest.mark.parametrize("case", CASES, ids=lambda path: path.name)
def test_source_document_preserves_every_native_raw_field_and_drawing_kind(case: Path) -> None:
    data = next(case.glob("*.top")).read_bytes()
    expected = json.loads((case / "expected.json").read_text())
    source, report = prepare_conversion(data)
    # Round-trip through strict JSON: tuples may become lists, integers must not
    # become floats, and neither NaN nor Infinity may enter a durable report.
    saved = json.loads(json.dumps(source, ensure_ascii=False, allow_nan=False))
    json.dumps(report, ensure_ascii=False, allow_nan=False)
    expected_records = _raw_oracle(expected["source"])
    expected_records.pop("header_hex")
    expected_records.pop("trailing_hex")
    expected_records["ending"] = "zero_trailer"
    assert saved["records"] == expected_records
    assert source["schema_version"] == report["schema_version"] == 1
    assert (
        source["provenance"]
        == report["provenance"]
        == {
            "sha256": expected["source_SHA256"],
            "bytes": len(data),
            "input_format": "PocketTopo v3",
            "tool": "jktz-release-tools",
            "tool_version": version("jktz-release-tools"),
            "algorithm_version": "p03-1",
        }
    )
    assert next(case.glob("*.top")).read_bytes() == data


def test_explicit_native_repeats_normalize_backshot_and_trace_all_source_records() -> None:
    data, oracle = _native("api-cardinal")
    confirmation = RepeatConfirmation((4, 5, 6), CONFIRMATION)
    source, report = prepare_conversion(data, plan=_plan(data, confirmations=(confirmation,)))
    assert [group["source_indices"] for group in report["groups"]] == [
        (0,),
        (1,),
        (2,),
        (3,),
        (4, 5, 6),
        (7,),
        (8,),
        (9,),
        (10,),
    ]
    group = report["groups"][4]
    assert group["confirmation_evidence"] == CONFIRMATION
    assert group["status"] == "ready"
    assert (group["from_raw"], group["to_raw"]) == (-2147483643, -2147483642)
    assert group["average"] == pytest.approx(
        {
            "count": 3,
            "distance_m": 5,
            "azimuth_deg": 0,
            "inclination_deg": 1820 * 360 / 65536,
            "resultant_length": (1 + 2 * math.cos(math.radians(364 * 360 / 65536))) / 3,
            "azimuth_max_deviation_deg": 364 * 360 / 65536,
            "distance_spread_m": 0,
            "inclination_spread_deg": 0,
        },
        abs=1e-12,
    )
    assert [row["reversed"] for row in group["normalized_readings"]] == [False, False, True]
    assert [row["source_index"] for row in group["normalized_readings"]] == [4, 5, 6]
    assert [row["azimuth_deg"] for row in group["normalized_readings"]] == [
        360 - 364 * 360 / 65536,
        364 * 360 / 65536,
        0,
    ]
    trace = report["record_trace"]
    assert [row["source_index"] for row in trace] == list(range(11))
    assert [row["group_id"] for row in trace] == [0, 1, 2, 3, 4, 4, 4, 5, 6, 7, 8]
    for row, original in zip(trace, oracle["source"]["shots"]):
        assert row["comment"] == original["comment"]
        assert row["flags"] == original["flags"]
        assert row["roll_raw"] == original["roll_raw"]
        assert row["flipped"] is bool(original["flags"] & 1)
        confirmed = row["source_index"] in (4, 5, 6)
        assert row["disposition"] == ("averaged_member" if confirmed else "retained_single")
        assert row["reason"] == ("explicit_repeat_confirmation" if confirmed else "not_averaged")
    assert source["records"]["shots"][6]["inclination_raw"] == -1820
    assert report["completeness"] == {
        "source_decode": "complete",
        "source_shots": 11,
        "traced_shots": 11,
        "ready_measurements": 9,
        "held_shots": 0,
        "exports_created": False,
        "conversion_complete": False,
    }


@pytest.mark.parametrize("entry", REPEAT_MANIFEST, ids=lambda entry: entry["file"])
def test_real_repeat_candidates_remain_separate_without_independent_confirmation(
    entry: dict,
) -> None:
    data = (EVIDENCE / "repeat-candidates" / entry["file"]).read_bytes()
    source, report = prepare_conversion(data)
    count = len(source["records"]["shots"])
    assert [group["source_indices"] for group in report["groups"]] == [(i,) for i in range(count)]
    assert [row["source_index"] for row in report["record_trace"]] == list(range(count))
    # Each independently audited source starts with the same zero-length
    # unnamed record. It must survive as held evidence, not become a vector.
    assert report["record_trace"][0]["disposition"] == "invalid"
    assert report["record_trace"][0]["reason"] == "zero_unnamed_shot"
    assert all(row["disposition"] == "retained_single" for row in report["record_trace"][1:])
    assert all(group["confirmation_evidence"] is None for group in report["groups"])
    assert report["plan"]["confirmations"] == ()
    assert report["completeness"]["ready_measurements"] == count - 1
    assert report["completeness"]["held_shots"] == 1


def test_even_named_native_repeat_fixture_is_not_automatically_averaged() -> None:
    data, _ = _native("api-cardinal")
    _, report = prepare_conversion(data)
    assert len(report["groups"]) == 11
    assert all(group["average"]["count"] == 1 for group in report["groups"])
    assert report["settings"]["repeat_policy"] == "explicit_source_pinned_confirmation_only"


def test_station_map_keeps_plain_zero_distinct_and_defers_target_names() -> None:
    data, _ = _native("api-trips-ids")
    _, report = prepare_conversion(data)
    assert [(row["raw"], row["kind"], row["source_text"]) for row in report["station_map"]] == [
        (-2147483647, "plain", "0"),
        (0, "major.minor", "0.0"),
        (851967, "major.minor", "12.65535"),
        (851968, "major.minor", "13.0"),
    ]
    for row in report["station_map"]:
        assert row["walls_name"] is row["survex_name"] is None
        assert row["status"] == "target_mapping_deferred_p04"


def test_station_map_includes_stations_only_present_in_references() -> None:
    data, _ = _native("api-references")
    needle = struct.pack("<iqqi", -2147483647, 6000000003, 7000000004, 1500250)
    replacement = struct.pack("<iqqi", -2147483547, 6000000003, 7000000004, 1500250)
    assert data.count(needle) == 1
    _, report = prepare_conversion(data.replace(needle, replacement))
    assert [row["source_text"] for row in report["station_map"]] == ["0", "1", "100"]


def test_station_map_includes_stations_only_present_in_each_drawing() -> None:
    data, _ = _native("api-drawings")
    for y, station in ((-6000, -2147483547), (6000, 0)):
        needle = struct.pack("<Biiii", 3, -5000, y, -2147483646, -1)
        replacement = struct.pack("<Biiii", 3, -5000, y, station, -1)
        assert data.count(needle) == 1
        data = data.replace(needle, replacement)
    source, report = prepare_conversion(data)
    assert [row["source_text"] for row in report["station_map"]] == ["0", "1", "2", "100", "0.0"]
    for name in ("outline", "sideview"):
        assert report["drawings"][name] == {
            "elements": 10,
            "status": "retained_not_exported",
            "mapping_applied": False,
        }
        assert source["records"][name]["elements"][-1]["kind"] == "xsection"


def test_absent_empty_multiline_comments_and_exact_ticks_survive_json() -> None:
    data, oracle = _native("api-trips-ids")
    comments = [None, "", "Pierwszy wiersz\nZażółć\r\nTrzeci\x00koniec"]
    for index, comment in enumerate(comments):
        flags = 0 if comment is None else 2
        data = _replace_shot(data, oracle, index, flags=flags, comment=comment)
    source, report = prepare_conversion(data)
    source, report = json.loads(json.dumps((source, report), ensure_ascii=False, allow_nan=False))
    assert [row["comment"] for row in source["records"]["shots"][:3]] == comments
    assert [row["comment"] for row in report["record_trace"][:3]] == comments
    ticks = [630822816000000007, 639259776000000009, 639260640000000001]
    assert [row["ticks"] for row in source["records"]["trips"]] == ticks
    assert [row["source_ticks"] for row in report["trips"]] == ticks
    assert all(type(row["source_ticks"]) is int for row in report["trips"])


def test_changed_source_bytes_reject_previously_pinned_plan() -> None:
    data, oracle = _native("api-cardinal")
    plan = _plan(data, confirmations=(RepeatConfirmation((4, 5, 6), CONFIRMATION),))
    changed = _replace_shot(data, oracle, 0, distance_mm=10001)
    with pytest.raises(ValueError, match="source_sha256"):
        prepare_conversion(changed, plan=plan)


def test_excluded_record_stays_in_source_group_trace_and_plan_with_reason() -> None:
    data, oracle = _native("api-cardinal")
    reason = "Instrument operator documented this as a practice reading"
    source, report = prepare_conversion(data, plan=_plan(data, exclusions=(Exclusion(5, reason),)))
    group = report["groups"][5]
    assert (group["status"], group["reason"], group["average"], group["normalized_readings"]) == (
        "excluded",
        reason,
        None,
        [],
    )
    assert group["source_indices"] == (5,)
    assert report["record_trace"][5]["disposition"] == "excluded"
    assert report["record_trace"][5]["reason"] == reason
    assert report["plan"]["exclusions"] == ({"index": 5, "reason": reason},)
    assert source["records"]["shots"][5]["comment"] == oracle["source"]["shots"][5]["comment"]
    assert report["completeness"]["source_shots"] == report["completeness"]["traced_shots"] == 11
    assert report["completeness"]["held_shots"] == 1
    assert report["completeness"]["ready_measurements"] == 10


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"distance_mm": -1}, "negative_distance"),
        ({"inclination_raw": 16385}, "inclination_out_of_range"),
        (
            {"from_id": {"raw": -2147483648}, "to_id": {"raw": -2147483648}},
            "both_stations_undefined",
        ),
    ],
)
def test_invalid_geometry_is_retained_with_reason_and_without_an_average(
    changes: dict, reason: str
) -> None:
    data, oracle = _native("api-cardinal")
    data = _replace_shot(data, oracle, 0, **changes)
    source, report = prepare_conversion(data)
    group = report["groups"][0]
    assert group["status"] == group["kind"] == "invalid"
    assert group["reason"] == reason
    assert group["average"] is None
    assert group["normalized_readings"] == []
    assert report["record_trace"][0]["disposition"] == "invalid"
    assert report["record_trace"][0]["reason"] == reason
    assert report["completeness"]["held_shots"] == 1
    for key, value in changes.items():
        assert source["records"]["shots"][0][key] == value


def test_antipodal_confirmation_is_unresolved_and_remains_strict_json() -> None:
    data, oracle = _native("api-cardinal")
    data = _replace_shot(data, oracle, 4, azimuth_raw=0)
    data = _replace_shot(data, oracle, 5, azimuth_raw=-32768)
    plan = _plan(data, confirmations=(RepeatConfirmation((4, 5), "Synthetic antipodal test"),))
    _, report = prepare_conversion(data, plan=plan)
    group = report["groups"][4]
    assert (group["status"], group["reason"]) == ("unresolved", "undefined_circular_mean")
    assert group["average"]["count"] == 2
    assert group["average"]["azimuth_deg"] is None
    assert group["average"]["azimuth_max_deviation_deg"] is None
    assert group["average"]["resultant_length"] < 1e-12
    assert [row["disposition"] for row in report["record_trace"][4:6]] == ["unresolved"] * 2
    assert report["completeness"]["held_shots"] == 2
    json.dumps(report, allow_nan=False)


def test_reported_custom_ambiguity_threshold_is_applied_to_confirmed_measurements() -> None:
    data, _ = _native("api-cardinal")
    plan = _plan(data, confirmations=(RepeatConfirmation((4, 5, 6), CONFIRMATION),))
    _, report = prepare_conversion(data, plan=plan, min_resultant=0.9999)
    group = report["groups"][4]
    assert report["settings"]["min_resultant"] == 0.9999
    assert group["status"] == "unresolved"
    assert group["average"]["resultant_length"] < 0.9999
    assert group["average"]["azimuth_deg"] is None
    assert report["completeness"]["held_shots"] == 3
    assert report["completeness"]["ready_measurements"] == 8


def test_reverse_splay_is_oriented_from_known_station_without_changing_source() -> None:
    data, oracle = _native("api-cardinal")
    data = _replace_shot(
        data,
        oracle,
        9,
        from_id={"raw": -2147483648},
        to_id={"raw": -2147483640},
    )
    source, report = prepare_conversion(data)
    group = report["groups"][9]
    assert group["kind"] == "splay"
    assert (group["from_raw"], group["to_raw"]) == (-2147483640, -2147483648)
    assert group["normalized_readings"][0] == {
        "source_index": 9,
        "distance_m": 1.234,
        "azimuth_deg": 225,
        "inclination_deg": 3641 * 360 / 65536,
        "reversed": True,
    }
    assert source["records"]["shots"][9]["from_id"]["raw"] == -2147483648
    assert source["records"]["shots"][9]["inclination_raw"] == -3641


def test_vertical_zero_missing_trip_and_mixed_flip_are_explicit_warnings() -> None:
    data, oracle = _native("api-cardinal")
    data = _replace_shot(data, oracle, 5, flags=3)
    plan = _plan(data, confirmations=(RepeatConfirmation((4, 5, 6), CONFIRMATION),))
    _, report = prepare_conversion(data, plan=plan)
    assert report["groups"][4]["warnings"] == ["mixed_flip_preserved_for_drawing_review"]
    assert [row["reversed"] for row in report["groups"][4]["normalized_readings"]] == [
        False,
        False,
        True,
    ]
    assert report["groups"][5]["warnings"] == ["vertical_azimuth_not_geometrically_determined"]
    assert report["groups"][6]["warnings"] == ["vertical_azimuth_not_geometrically_determined"]
    assert report["groups"][8]["warnings"] == ["zero_link_angles_have_no_geometric_effect"]
    assert report["groups"][8]["kind"] == "zero_link"
    missing_data, _ = _native("api-trips-ids")
    _, missing_report = prepare_conversion(missing_data)
    assert missing_report["groups"][3]["warnings"] == ["missing_trip"]
    assert missing_report["groups"][3]["trip_index"] == -1


def test_dates_declination_and_reference_crs_are_retained_without_inference_or_correction() -> None:
    data, oracle = _native("api-trips-ids")
    _, report = prepare_conversion(data, min_resultant=0.01)
    assert report["stage"] == "P03"
    assert report["settings"] == {
        "index_base": 0,
        "repeat_policy": "explicit_source_pinned_confirmation_only",
        "min_resultant": 0.01,
        "ambiguity_rule": "resultant_length <= min_resultant",
        "distance_mean": "arithmetic",
        "azimuth_mean": "circular_fsum",
        "inclination_mean": "signed_arithmetic_after_direction_normalization",
        "outlier_removal": False,
        "declination_applied": False,
        "date_inference": False,
        "crs_assumed": None,
    }
    for index, (trip, original) in enumerate(zip(report["trips"], oracle["source"]["trips"])):
        assert trip["index"] == index
        assert trip["source_ticks"] == original["ticks"]
        assert trip["comment"] == original["comment"]
        assert trip["date_reliability"] == "unverified_device_clock"
        assert trip["established_date"] is trip["used_date"] is trip["date_evidence"] is None
        raw = original["declination_raw"]
        assert trip["declination"] == {
            "source_raw": raw,
            "mode": "auto" if raw == -32768 else "explicit",
            "stored_degrees": None if raw == -32768 else raw * 360 / 65536,
            "applied_degrees": None,
            "status": "unresolved_auto" if raw == -32768 else "not_applied_p03",
        }
    assert report["groups"][1]["average"]["azimuth_deg"] == 90
    reference_data, _ = _native("api-references")
    _, references = prepare_conversion(reference_data)
    assert references["references"] == {
        "count": 2,
        "crs": None,
        "status": "retained_only_crs_unknown",
        "active_fixes": 0,
    }
    assert len(report["limitations"]) == 4
    assert report["completeness"]["conversion_complete"] is False


def test_empty_source_and_drawings_are_explicit_not_fabricated() -> None:
    # Minimal legal schema; native nonempty records are used by all other oracles.
    mapping = struct.pack("<iii", 0, 0, 500)
    data = b"Top\x03" + bytes(12) + mapping + mapping + b"\0" + mapping + b"\0"
    source, report = prepare_conversion(data)
    assert source["records"]["shots"] == ()
    assert source["records"]["ending"] == "eof"
    assert (
        report["groups"] == report["record_trace"] == report["station_map"] == report["trips"] == []
    )
    for name in ("outline", "sideview"):
        assert report["drawings"][name] == {
            "elements": 0,
            "status": "empty",
            "mapping_applied": False,
        }
    assert report["completeness"]["source_shots"] == report["completeness"]["traced_shots"] == 0
    assert report["completeness"]["ready_measurements"] == report["completeness"]["held_shots"] == 0
    assert report["completeness"]["conversion_complete"] is False


def test_limits_parse_errors_and_invalid_plan_produce_no_files(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    data, _ = _native("api-cardinal")
    source_path = tmp_path / "immutable.top"
    source_path.write_bytes(data)
    with pytest.raises(ParseError) as caught:
        prepare_conversion(data, limits=ParseLimits(max_bytes=len(data) - 1))
    assert (caught.value.code, caught.value.offset, caught.value.context) == (
        "resource_limit",
        0,
        "file",
    )
    with pytest.raises(ParseError):
        prepare_conversion(data[:100])
    with pytest.raises(ValueError, match="station_pair_changed"):
        prepare_conversion(
            data, plan=_plan(data, confirmations=(RepeatConfirmation((0, 1), "Bad pair"),))
        )
    source, report = prepare_conversion(data, limits=ParseLimits(max_bytes=len(data)))
    assert len(source["records"]["shots"]) == report["completeness"]["traced_shots"] == 11
    assert list(tmp_path.iterdir()) == [source_path]
    assert source_path.read_bytes() == data


@pytest.mark.parametrize("threshold", [float("nan"), float("inf"), -1, 0, 1])
def test_invalid_threshold_is_rejected_before_any_report(threshold: float) -> None:
    data, _ = _native("api-cardinal")
    with pytest.raises(ValueError, match="min_resultant"):
        prepare_conversion(data, min_resultant=threshold)
