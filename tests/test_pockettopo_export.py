"""P04 semantic export contract, independently checked against native fixtures."""

from __future__ import annotations

import hashlib
import json
import struct
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from jktz.pockettopo import (
    CorrectionOverride,
    CorrectionPolicy,
    Exclusion,
    ParseError,
    ParseLimits,
    ProcessingPlan,
    RepeatConfirmation,
    SurveyExport,
    export_surveys,
    prepare_conversion,
)

EVIDENCE = Path(__file__).resolve().parents[1] / "doc/pockettopo/evidence"
CASES = sorted((EVIDENCE / "p01/cases").iterdir())
UNDEFINED = -2147483648
PLAIN_ZERO = -2147483647


def _string(text: str) -> bytes:
    encoded = text.encode("utf-8")
    size = len(encoded)
    prefix = bytearray()
    while size >= 128:
        prefix.append((size & 127) | 128)
        size >>= 7
    return bytes(prefix) + bytes([size]) + encoded


def _shot(
    start: int = PLAIN_ZERO,
    end: int = PLAIN_ZERO + 1,
    distance: int = 1234,
    azimuth: int = 0,
    inclination: int = 0,
    trip: int = 0,
    comment: str | None = None,
    flipped: bool = False,
) -> bytes:
    flags = int(flipped) + (2 if comment is not None else 0)
    body = struct.pack("<iiihhBBh", start, end, distance, azimuth, inclination, flags, 0, trip)
    return body + (_string(comment) if comment is not None else b"")


def _file(shots=(), declinations=(0,), trip_comment="", reference_comment=None) -> bytes:
    trips = b"".join(
        struct.pack("<q", 635573952000000000) + _string(trip_comment) + struct.pack("<h", raw)
        for raw in declinations
    )
    references = (
        b""
        if reference_comment is None
        else struct.pack("<iqqi", PLAIN_ZERO, -1234, 2345, -3456) + _string(reference_comment)
    )
    mapping = struct.pack("<iii", 0, 0, 500)
    return (
        b"Top\x03"
        + struct.pack("<i", len(declinations))
        + trips
        + struct.pack("<i", len(shots))
        + b"".join(shots)
        + struct.pack("<i", int(reference_comment is not None))
        + references
        + mapping
        + mapping
        + b"\0"
        + mapping
        + b"\0"
    )


def _policy(data, *overrides):
    return CorrectionPolicy(hashlib.sha256(data).hexdigest(), overrides)


def _plan(data, confirmations=(), exclusions=()):
    return ProcessingPlan(hashlib.sha256(data).hexdigest(), confirmations, exclusions)


def _active(text):
    return [line for line in text.splitlines() if line and not line.startswith((";", "#", "*"))]


def _native(name):
    return next((EVIDENCE / "p01/cases" / name).glob("*.top")).read_bytes()


def _comments(text, label):
    """Reassemble ASCII comment JSON independently from the exporter's helpers."""
    result = []
    accumulated = ""
    prefix = "; " + label + " "
    for line in text.splitlines():
        if line.startswith(prefix):
            counter, chunk = line[len(prefix) :].split(" ", 1)
            part, total = (int(value) for value in counter.split("/"))
            if part == 1:
                accumulated = ""
            accumulated += chunk
            if part == total:
                result.append(json.loads(accumulated))
    return result


@pytest.mark.parametrize("case", CASES, ids=lambda path: path.name)
def test_native_sources_are_lossless_ascii_audited_and_not_falsely_complete(case):
    data = next(case.glob("*.top")).read_bytes()
    before, p03 = prepare_conversion(data)
    result = export_surveys(data)
    assert isinstance(result, SurveyExport)
    assert result.source_document["records"] == before["records"]
    assert result.source_document["provenance"] == result.report["provenance"]
    assert result.report["provenance"]["sha256"] == hashlib.sha256(data).hexdigest()
    assert result.report["provenance"]["algorithm_version"] == "p04-1"
    assert result.report["stage"] == "P04"
    assert result.report["plan"] == p03["plan"]
    assert result.report["completeness"]["conversion_complete"] is False
    assert result.report["completeness"]["exports_created"] is True
    assert result.report["completeness"]["survey_texts_created"] is True
    assert result.report["references"]["active_fixes"] == 0
    assert result.report["settings"]["date_inference"] is False
    assert result.report["settings"]["crs_assumed"] is None
    assert result.report["exports"]["validation"] == "not_run_by_library"
    json.dumps(result.report, allow_nan=False)
    for text in (result.srv, result.svx):
        assert text.isascii()
        assert text.endswith("\n")
        assert max(map(len, text.splitlines())) <= 255
        assert _comments(text, "source_shot") == [
            {"index": i, **shot} for i, shot in enumerate(before["records"]["shots"])
        ]
        active_directives = [line.lower() for line in text.splitlines() if not line.startswith(";")]
        assert not any(
            line.startswith(("#date", "*date", "#fix", "*fix", "*cs")) for line in active_directives
        )
    assert next(case.glob("*.top")).read_bytes() == data
    with pytest.raises(FrozenInstanceError):
        result.srv = "changed"


def test_explicit_corrections_are_directives_with_unmodified_measurements_and_provenance():
    data = _file(
        (_shot(azimuth=16384, inclination=-8192), _shot(trip=1)),
        declinations=(1820, -1820),
    )
    result = export_surveys(data)
    assert _active(result.srv) == ["0\t1\t1.234\t90\t-45", "0\t1\t1.234\t0\t0"]
    assert _active(result.svx) == _active(result.srv)
    assert "#units DECL=9.99755859375\n" in result.srv
    assert "#units DECL=-9.99755859375\n" in result.srv
    assert "*declination 9.99755859375 degrees\n" in result.svx
    assert "*declination -9.99755859375 degrees\n" in result.svx
    for index, degrees in enumerate((9.99755859375, -9.99755859375)):
        trip = result.report["trips"][index]
        assert trip["used_date"] is trip["established_date"] is None
        assert trip["date_reliability"] == "unverified_device_clock"
        assert trip["declination"]["applied_degrees"] == degrees
        assert trip["declination"]["provenance"] == "stored_explicit"
        assert trip["declination"]["evidence"] is None
        assert trip["declination"]["status"] == "applied"
    assert result.report["settings"]["declination_applied"] is True


def test_explicit_zero_is_preserved_without_claiming_historical_verification():
    result = export_surveys(_file((_shot(),)))
    assert "#units DECL=0\n" in result.srv
    assert "*declination 0 degrees\n" in result.svx
    assert result.report["groups"][0]["export"]["declination_degrees"] == 0
    assert any("not historically verified" in item for item in result.report["limitations"])


@pytest.mark.parametrize(
    ("trip", "declinations", "reason"),
    [(0, (-32768,), "unresolved_auto"), (-1, (), "missing_trip_correction")],
)
def test_auto_and_missing_trip_are_held_with_no_implicit_zero(trip, declinations, reason):
    data = _file((_shot(trip=trip),), declinations=declinations)
    result = export_surveys(data)
    assert _active(result.srv) == _active(result.svx) == []
    assert not any(line.startswith("#units DECL=") for line in result.srv.splitlines())
    assert not any(line.startswith("*declination") for line in result.svx.splitlines())
    group = result.report["groups"][0]
    assert group["status"] == "ready"
    assert group["export"]["status"] == "held"
    assert group["export"]["reason"] == reason
    assert group["export"]["srv_line"] is group["export"]["svx_line"] is None
    assert result.report["record_trace"][0]["export"] == group["export"]
    assert result.report["completeness"]["held_shots"] == 1
    assert result.report["completeness"]["exported_source_shots"] == 0
    assert result.report["completeness"]["measurement_export_complete"] is False
    assert result.report["settings"]["declination_applied"] is False
    assert result.report["exports"]["geometry_status"] == "empty"
    if trip == 0:
        declination = result.report["trips"][0]["declination"]
        assert declination["mode"] == "auto"
        assert declination["source_raw"] == -32768
        assert declination["unresolved_reason"] == reason


@pytest.mark.parametrize(("trip", "declinations"), [(0, (-32768,)), (-1, ()), (0, (123,))])
def test_source_pinned_override_resolves_or_replaces_correction_with_evidence(trip, declinations):
    data = _file((_shot(trip=trip),), declinations=declinations)
    policy = _policy(data, CorrectionOverride(trip, -12.25, "Independent field-book reference"))
    result = export_surveys(data, correction_policy=policy)
    assert _active(result.srv) == ["0\t1\t1.234\t0\t0"]
    assert "#units DECL=-12.25\n" in result.srv
    assert "*declination -12.25 degrees\n" in result.svx
    decision = result.report["groups"][0]["export"]
    assert decision["declination_degrees"] == -12.25
    assert decision["correction_provenance"] == "source_pinned_override"
    assert decision["correction_evidence"] == "Independent field-book reference"
    assert (
        result.report["settings"]["correction_overrides"]["source_sha256"] == policy.source_sha256
    )
    assert result.report["completeness"]["measurement_export_complete"] is True
    if trip == 0:
        assert result.report["trips"][0]["declination"]["source_raw"] == declinations[0]


@pytest.mark.parametrize("degrees", [-180, 180, 0.0, -0.0, 1e-10])
def test_override_boundary_degrees_are_valid_and_negative_zero_is_not_emitted(degrees):
    data = _file((_shot(),))
    result = export_surveys(
        data, correction_policy=_policy(data, CorrectionOverride(0, degrees, "E"))
    )
    assert result.report["groups"][0]["export"]["declination_degrees"] == degrees
    assert "#units DECL=-0\n" not in result.srv


@pytest.mark.parametrize(
    "degrees",
    [
        -180.01,
        180.01,
        float("inf"),
        float("-inf"),
        float("nan"),
        True,
        "0",
        None,
        pytest.param(10**1000, id="huge_integer"),
    ],
)
def test_invalid_override_degrees_reject_entire_export(degrees):
    data = _file((_shot(),))
    with pytest.raises(ValueError, match="correction_degrees"):
        export_surveys(data, correction_policy=_policy(data, CorrectionOverride(0, degrees, "E")))


@pytest.mark.parametrize("index", [-2, 1, True, 0.0, "0", None])
def test_invalid_override_trip_indices_reject_entire_export(index):
    data = _file((_shot(),))
    with pytest.raises(ValueError, match="correction_trip_index"):
        export_surveys(data, correction_policy=_policy(data, CorrectionOverride(index, 0, "E")))


@pytest.mark.parametrize("evidence", ["", " \n\t", None, 123])
def test_override_requires_nonblank_evidence(evidence):
    data = _file((_shot(),))
    with pytest.raises(ValueError, match="correction_evidence"):
        export_surveys(data, correction_policy=_policy(data, CorrectionOverride(0, 0, evidence)))


def test_override_sha_and_duplicates_fail_without_output():
    data = _file((_shot(),))
    with pytest.raises(ValueError, match="source_sha256"):
        export_surveys(data, correction_policy=CorrectionPolicy("wrong"))
    with pytest.raises(ValueError, match="duplicate_correction_override"):
        export_surveys(
            data,
            correction_policy=_policy(
                data, CorrectionOverride(0, 0, "A"), CorrectionOverride(0, 1, "B")
            ),
        )


def test_policy_validation_is_complete_even_for_no_eligible_shots():
    data = _file()
    with pytest.raises(ValueError, match="correction_evidence"):
        export_surveys(data, correction_policy=_policy(data, CorrectionOverride(0, 0, "")))
    result = export_surveys(data, correction_policy=_policy(data))
    assert result.report["completeness"]["exported_measurements"] == 0
    assert result.report["exports"]["geometry_status"] == "empty"
    assert result.report["trips"][0]["declination"]["applied_degrees"] is None
    assert result.report["trips"][0]["declination"]["selected_degrees"] == 0


@pytest.mark.parametrize("declinations", [(0,), (-32768,), ()])
def test_zero_link_exports_constraint_even_with_unresolved_or_missing_correction(declinations):
    data = _file(
        (_shot(distance=0, azimuth=8192, inclination=16384, trip=0 if declinations else -1),),
        declinations=declinations,
    )
    result = export_surveys(data)
    assert _active(result.srv) == ["0\t1\t0\t0\t0"]
    assert "*equate 0 1\n" in result.svx
    assert _active(result.svx) == []
    decision = result.report["groups"][0]["export"]
    assert result.report["exports"]["geometry_status"] == "constraints_only"
    assert decision["reason"] == "zero_link_no_angular_correction"
    assert decision["declination_degrees"] is None
    assert result.source_document["records"]["shots"][0]["azimuth_raw"] == 8192
    assert result.report["settings"]["declination_applied"] is False


@pytest.mark.parametrize("reverse", [False, True])
def test_splays_are_anonymous_and_reverse_only_when_known_station_was_to(reverse):
    start, end = (UNDEFINED, PLAIN_ZERO) if reverse else (PLAIN_ZERO, UNDEFINED)
    result = export_surveys(
        _file((_shot(start, end, azimuth=8192, inclination=8192, flipped=True),))
    )
    values = "1.234\t225\t-45" if reverse else "1.234\t45\t45"
    assert _active(result.srv) == ["0\t-\t" + values]
    assert _active(result.svx) == ["0\t::\t" + values]
    trace = result.report["record_trace"][0]
    assert trace["flipped"] is True
    assert result.report["groups"][0]["normalized_readings"][0]["reversed"] is reverse


def test_two_splays_do_not_gain_a_shared_endpoint_identity():
    result = export_surveys(_file((_shot(end=UNDEFINED), _shot(end=UNDEFINED))))
    assert _active(result.srv) == ["0\t-\t1.234\t0\t0"] * 2
    assert _active(result.svx) == ["0\t::\t1.234\t0\t0"] * 2
    assert len(result.report["station_map"]) == 1
    assert result.report["station_map"][0]["raw"] == PLAIN_ZERO


def test_plain_zero_and_dotted_zero_are_distinct_literal_names_in_both_formats():
    result = export_surveys(_file((_shot(PLAIN_ZERO, 0),)))
    assert _active(result.srv) == _active(result.svx) == ["0\t0.0\t1.234\t0\t0"]
    assert [
        (row["source_text"], row["walls_name"], row["survex_name"])
        for row in result.report["station_map"]
    ] == [("0", "0", "0"), ("0.0", "0.0", "0.0")]
    assert "*set separator :\n" in result.svx
    assert "*set names ._-\n" in result.svx
    assert "*truncate off\n" in result.svx


@pytest.mark.parametrize(
    "raw", [-1, -2147483647 + 100000000, 2147483647, 2147418112 + 65535, (10000 << 16) + 10000]
)
def test_long_walls_names_are_reversible_unique_and_survex_preserves_literal(raw):
    result = export_surveys(_file((_shot(PLAIN_ZERO, raw),)))
    row = result.report["station_map"][1]
    alias = row["walls_name"]
    assert alias.startswith("p")
    assert len(alias) <= 8
    assert int(alias[1:], 36) == raw & 0xFFFFFFFF
    assert row["survex_name"] == row["source_text"]
    assert row["walls_mapping"] == "unsigned_raw_base36"
    assert _active(result.srv)[0].split()[1] == alias
    assert _active(result.svx)[0].split()[1] == row["source_text"]


def test_mapping_never_collides_at_eight_character_boundary_or_signed_domain():
    ids = [
        PLAIN_ZERO,
        PLAIN_ZERO + 99999999,
        PLAIN_ZERO + 100000000,
        -1,
        0,
        65535,
        9999 << 16,
        10000 << 16,
        2147483647,
    ]
    data = _file(tuple(_shot(start, end) for start, end in zip(ids, ids[1:])))
    rows = export_surveys(data).report["station_map"]
    assert len({row["walls_name"] for row in rows}) == len(ids)
    assert len({row["survex_name"] for row in rows}) == len(ids)
    for row in rows:
        if len(row["source_text"]) <= 8:
            assert row["walls_name"] == row["source_text"]
            assert row["walls_mapping"] == "literal"


def test_unconfirmed_native_repeats_keep_every_reading_and_p03_confirmed_mean_is_exported():
    data = _native("api-cardinal")
    independent = export_surveys(data)
    confirmed = export_surveys(
        data, plan=_plan(data, (RepeatConfirmation((4, 5, 6), "Native helper explicit repeats"),))
    )
    assert len(_active(independent.srv)) == 11
    assert len(_active(confirmed.srv)) == 9
    assert _active(independent.srv)[4:7] == [
        "4\t5\t5\t358.00048828125\t9.99755859375",
        "4\t5\t5\t1.99951171875\t9.99755859375",
        "5\t4\t5\t180\t-9.99755859375",
    ]
    assert _active(confirmed.srv)[4] == "4\t5\t5\t0\t9.99755859375"
    assert confirmed.report["completeness"]["exported_source_shots"] == 11
    assert confirmed.report["completeness"]["exported_measurements"] == 9
    assert confirmed.report["groups"][4]["source_indices"] == (4, 5, 6)
    assert all(row["export"]["status"] == "exported" for row in confirmed.report["record_trace"])


def test_excluded_invalid_and_ambiguous_groups_remain_traced_with_original_reason():
    shots = (_shot(), _shot(distance=-1), _shot(azimuth=0), _shot(azimuth=-32768))
    data = _file(shots)
    plan = _plan(
        data,
        (RepeatConfirmation((2, 3), "Independent evidence"),),
        (Exclusion(0, "Confirmed blunder"),),
    )
    result = export_surveys(data, plan=plan)
    assert _active(result.srv) == _active(result.svx) == []
    assert [group["export"]["reason"] for group in result.report["groups"]] == [
        "Confirmed blunder",
        "negative_distance",
        "undefined_circular_mean",
    ]
    assert result.report["completeness"]["held_shots"] == 4
    assert len(_comments(result.srv, "source_shot")) == 4
    assert [row["source_index"] for row in result.report["record_trace"]] == list(range(4))


def test_long_unicode_and_directive_comments_are_ascii_safe_reversible_and_bounded():
    hostile = ('Zażółć\n#fix BAD 0 0 0\r*date 2000.01.01\t; "\\' + "\x00\x1b") * 200
    data = _file((_shot(comment=hostile),), trip_comment=hostile, reference_comment=hostile)
    result = export_surveys(
        data, correction_policy=_policy(data, CorrectionOverride(0, 1, hostile))
    )
    for text in (result.srv, result.svx):
        assert text.isascii()
        assert max(map(len, text.splitlines())) <= 255
        assert _comments(text, "source_shot")[0]["comment"] == hostile
        assert _comments(text, "trip")[0]["comment"] == hostile
        assert _comments(text, "reference_not_fixed")[0]["comment"] == hostile
        assert _comments(text, "group")[0]["correction_evidence"] == hostile
        assert "\x00" not in text and "\x1b" not in text
        assert not any(line.startswith(("#fix", "*date")) for line in text.splitlines())
    assert result.report["references"]["count"] == 1
    assert result.report["references"]["status"] == "retained_only_crs_unknown"


def test_huge_exclusion_reason_and_confirmation_evidence_remain_complete():
    evidence = "Źródło\n" * 500
    data = _file((_shot(), _shot(), _shot()))
    result = export_surveys(
        data, plan=_plan(data, (RepeatConfirmation((0, 1), evidence),), (Exclusion(2, evidence),))
    )
    assert result.report["groups"][0]["confirmation_evidence"] == evidence
    assert result.report["record_trace"][2]["export"]["reason"] == evidence
    assert max(map(len, result.srv.splitlines())) <= 255
    assert _comments(result.srv, "group")[1]["reason"] == evidence


def test_line_references_point_to_actual_data_and_equal_record_group_decisions():
    data = _file((_shot(), _shot(distance=0), _shot(end=UNDEFINED), _shot(trip=-1)))
    result = export_surveys(data)
    for group, trace in zip(result.report["groups"], result.report["record_trace"]):
        decision = group["export"]
        assert trace["export"] == decision
        if decision["status"] == "exported":
            srv = result.srv.splitlines()[decision["srv_line"] - 1]
            svx = result.svx.splitlines()[decision["svx_line"] - 1]
            assert srv.startswith("0\t")
            assert svx.startswith("*equate" if group["kind"] == "zero_link" else "0\t")
        else:
            assert decision["srv_line"] is decision["svx_line"] is None


def test_parser_processing_and_limits_errors_propagate_before_any_output():
    data = _file((_shot(),))
    with pytest.raises(ParseError, match="resource_limit"):
        export_surveys(data, limits=ParseLimits(max_records=0))
    with pytest.raises(ParseError, match="truncated"):
        export_surveys(data[:-1])
    with pytest.raises(ValueError, match="source_sha256"):
        export_surveys(data, plan=ProcessingPlan("wrong"))
    with pytest.raises(ValueError, match="min_resultant"):
        export_surveys(data, min_resultant=0)


def test_configured_ambiguity_threshold_and_raw_precision_survive_export():
    data = _file((_shot(distance=1, azimuth=1, inclination=-1),))
    result = export_surveys(data, min_resultant=0.9)
    assert _active(result.srv) == ["0\t1\t0.001\t0.005493164062\t-0.005493164062"]
    assert result.report["settings"]["min_resultant"] == 0.9
    mean = result.report["groups"][0]["average"]
    assert mean["azimuth_deg"] == 360 / 65536
    assert mean["inclination_deg"] == -360 / 65536
    assert result.report["settings"]["decimal_places"] == 12
