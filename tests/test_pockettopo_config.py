"""P06 decision documents retain explicit evidence and fail closed on mistakes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from jktz.pockettopo import (
    CorrectionOverride,
    CorrectionPolicy,
    Exclusion,
    ProcessingPlan,
    RepeatConfirmation,
    export_surveys,
)
from jktz.pockettopo.config import load_decisions

CASE = Path(__file__).resolve().parents[1] / "doc/pockettopo/evidence/p01/cases/api-cardinal"
DIGEST = "a" * 64


def _load(tmp_path, document):
    path = tmp_path / "decisions.json"
    path.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
    return load_decisions(path)


def test_defaults_preserve_independent_readings_and_unverified_dates(tmp_path):
    data = next(CASE.glob("*.top")).read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    plan, policy = _load(tmp_path, {"source_sha256": digest})
    assert plan == ProcessingPlan(digest)
    assert policy == CorrectionPolicy(digest)
    exported = export_surveys(data, plan=plan, correction_policy=policy)
    assert exported.report["completeness"]["exported_measurements"] == 11
    assert all(trip["used_date"] is None for trip in exported.report["trips"])
    assert "#date" not in exported.srv
    assert "*date" not in exported.svx


def test_valid_decisions_apply_to_real_export_and_retain_full_reasons(tmp_path):
    data = next(CASE.glob("*.top")).read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    evidence = " Źródło niezależne\n "
    plan, policy = _load(
        tmp_path,
        {
            "source_sha256": digest,
            "confirmations": [{"indices": [4, 5, 6], "reason": evidence}],
            "exclusions": [{"index": 0, "reason": "Jawny błąd"}],
            "corrections": [{"trip_index": 0, "degrees": 1.25, "reason": evidence}],
        },
    )
    assert plan == ProcessingPlan(
        digest, (RepeatConfirmation((4, 5, 6), evidence),), (Exclusion(0, "Jawny błąd"),)
    )
    assert policy == CorrectionPolicy(digest, (CorrectionOverride(0, 1.25, evidence),))
    exported = export_surveys(data, plan=plan, correction_policy=policy)
    assert exported.report["completeness"]["exported_measurements"] == 8
    assert exported.report["groups"][4]["source_indices"] == (4, 5, 6)
    assert exported.report["groups"][4]["confirmation_evidence"] == evidence
    assert exported.report["record_trace"][0]["export"]["reason"] == "Jawny błąd"
    assert "#units DECL=1.25" in exported.srv
    assert "*declination 1.25 degrees" in exported.svx
    assert all(trip["used_date"] is None for trip in exported.report["trips"])


@pytest.mark.parametrize("degrees", [-180, 0, 180, -179.9999, 179.9999])
@pytest.mark.parametrize("trip_index", [-1, 0])
def test_numeric_boundaries(tmp_path, degrees, trip_index):
    plan, policy = _load(
        tmp_path,
        {
            "source_sha256": DIGEST,
            "confirmations": [],
            "exclusions": [],
            "corrections": [{"trip_index": trip_index, "degrees": degrees, "reason": "evidence"}],
        },
    )
    assert plan == ProcessingPlan(DIGEST)
    assert policy.overrides == (CorrectionOverride(trip_index, degrees, "evidence"),)


@pytest.mark.parametrize("document", [None, [], "text", 1, True])
def test_root_must_be_an_object(tmp_path, document):
    with pytest.raises(ValueError, match="must be a JSON object"):
        _load(tmp_path, document)


@pytest.mark.parametrize("digest", [None, True, 1, [], "", "a" * 63, "a" * 65, "g" * 64, "A" * 64])
def test_digest_requires_canonical_sha256(tmp_path, digest):
    with pytest.raises(ValueError, match="source_sha256"):
        _load(tmp_path, {"source_sha256": digest})


@pytest.mark.parametrize("key", ["date", "auto_confirm", "correction", "source_sha25"])
def test_unknown_root_keys_fail_instead_of_silently_inferring_decisions(tmp_path, key):
    with pytest.raises(ValueError, match="unknown keys"):
        _load(tmp_path, {"source_sha256": DIGEST, key: None})


def test_missing_digest_is_an_error(tmp_path):
    with pytest.raises(ValueError, match="missing required keys: source_sha256"):
        _load(tmp_path, {})


@pytest.mark.parametrize("name", ["confirmations", "exclusions", "corrections"])
@pytest.mark.parametrize("value", [None, {}, "", 0, True])
def test_collections_are_arrays(tmp_path, name, value):
    with pytest.raises(ValueError, match="must be a JSON array"):
        _load(tmp_path, {"source_sha256": DIGEST, name: value})


@pytest.mark.parametrize("name", ["confirmations", "exclusions", "corrections"])
@pytest.mark.parametrize("row", [None, [], 0, True, "text"])
def test_rows_are_objects(tmp_path, name, row):
    with pytest.raises(ValueError, match="must be a JSON object"):
        _load(tmp_path, {"source_sha256": DIGEST, name: [row]})


ROWS = [
    ("confirmations", {"indices": [0, 1], "reason": "evidence"}),
    ("exclusions", {"index": 0, "reason": "evidence"}),
    ("corrections", {"trip_index": 0, "degrees": 0, "reason": "evidence"}),
]


@pytest.mark.parametrize("name,row", ROWS)
def test_each_row_field_is_required_and_unknown_fields_are_rejected(tmp_path, name, row):
    for key in row:
        incomplete = {field: value for field, value in row.items() if field != key}
        with pytest.raises(ValueError, match=f"missing required keys: {key}"):
            _load(tmp_path, {"source_sha256": DIGEST, name: [incomplete]})
    with pytest.raises(ValueError, match="unknown keys: inferred"):
        _load(tmp_path, {"source_sha256": DIGEST, name: [dict(row, inferred=True)]})


@pytest.mark.parametrize("name,row", ROWS)
@pytest.mark.parametrize("reason", [None, 0, True, [], {}, "", " \n\t"])
def test_reasons_must_be_explicit_nonblank_text(tmp_path, name, row, reason):
    with pytest.raises(ValueError, match="reason must be nonblank text"):
        _load(tmp_path, {"source_sha256": DIGEST, name: [dict(row, reason=reason)]})


@pytest.mark.parametrize("indices", [None, "0,1", {}, [], [0], 0, True])
def test_confirmation_requires_at_least_two_indices(tmp_path, indices):
    with pytest.raises(ValueError, match="array of at least two"):
        _load(
            tmp_path,
            {"source_sha256": DIGEST, "confirmations": [{"indices": indices, "reason": "x"}]},
        )


@pytest.mark.parametrize("index", [True, False, 0.0, "0", None, [], {}, -1])
@pytest.mark.parametrize("name", ["confirmations", "exclusions"])
def test_record_indices_are_nonnegative_integers(tmp_path, index, name):
    row = (
        {"indices": [0, index], "reason": "x"}
        if name == "confirmations"
        else {
            "index": index,
            "reason": "x",
        }
    )
    with pytest.raises(ValueError, match="must be an integer >= 0"):
        _load(tmp_path, {"source_sha256": DIGEST, name: [row]})


@pytest.mark.parametrize("index", [True, False, 0.0, "0", None, [], {}, -2])
def test_trip_indices_are_integers_at_least_minus_one(tmp_path, index):
    with pytest.raises(ValueError, match="must be an integer >= -1"):
        _load(
            tmp_path,
            {
                "source_sha256": DIGEST,
                "corrections": [{"trip_index": index, "degrees": 0, "reason": "x"}],
            },
        )


@pytest.mark.parametrize("degrees", [True, False, "0", None, [], {}, -180.1, 180.1, 10**100])
def test_correction_requires_bounded_number(tmp_path, degrees):
    with pytest.raises(ValueError, match="degrees must be a finite number"):
        _load(
            tmp_path,
            {
                "source_sha256": DIGEST,
                "corrections": [{"trip_index": 0, "degrees": degrees, "reason": "x"}],
            },
        )


@pytest.mark.parametrize("number", ["NaN", "Infinity", "-Infinity", "1e309", "-1e309"])
def test_nonfinite_json_numbers_are_rejected(tmp_path, number):
    path = tmp_path / "decisions.json"
    path.write_text('{"source_sha256": "' + DIGEST + '", "corrections": ' + number + "}")
    with pytest.raises(ValueError, match="Nonfinite JSON number"):
        load_decisions(path)


@pytest.mark.parametrize(
    "text",
    [
        '{"source_sha256":"' + DIGEST + '", "source_sha256":"' + DIGEST + '"}',
        '{"source_sha256":"' + DIGEST + '", "exclusions":[{"index":0,"index":1,"reason":"x"}]}',
        '{"source_sha256":"'
        + DIGEST
        + '", "exclusions":[{"index":0,"reason":"x","reas\\u006fn":"y"}]}',
    ],
)
def test_duplicate_json_keys_cannot_silently_replace_decisions(tmp_path, text):
    path = tmp_path / "decisions.json"
    path.write_text(text)
    with pytest.raises(ValueError, match="Duplicate JSON key"):
        load_decisions(path)


@pytest.mark.parametrize("data", [b"", b"{", b"{} trailing", b"\xff", b"[" * 2000])
def test_invalid_json_and_encoding_report_value_error(tmp_path, data):
    path = tmp_path / "decisions.json"
    path.write_bytes(data)
    with pytest.raises(ValueError, match="Invalid decision JSON"):
        load_decisions(path)


def test_read_failures_remain_oserror(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_decisions(tmp_path / "missing.json")


def test_source_mismatch_is_checked_by_export_before_applying_decisions(tmp_path):
    plan, policy = _load(tmp_path, {"source_sha256": DIGEST})
    data = next(CASE.glob("*.top")).read_bytes()
    with pytest.raises(ValueError, match="source_sha256 does not match"):
        export_surveys(data, plan=plan, correction_policy=policy)
    with pytest.raises(ValueError, match="source_sha256 does not match"):
        export_surveys(data, correction_policy=policy)


@pytest.mark.parametrize(
    "decisions,error",
    [
        ({"confirmations": [{"indices": [4, 6], "reason": "x"}]}, "sorted_and_consecutive"),
        ({"exclusions": [{"index": 999, "reason": "x"}]}, "in_range_integer"),
        ({"corrections": [{"trip_index": 999, "degrees": 0, "reason": "x"}]}, "in_range_integer"),
        (
            {"exclusions": [{"index": 0, "reason": "x"}, {"index": 0, "reason": "y"}]},
            "duplicate_exclusion",
        ),
        (
            {
                "corrections": [
                    {"trip_index": 0, "degrees": 0, "reason": "x"},
                    {"trip_index": 0, "degrees": 1, "reason": "y"},
                ]
            },
            "duplicate_correction_override",
        ),
    ],
)
def test_record_dependent_validation_remains_owned_by_existing_apis(tmp_path, decisions, error):
    data = next(CASE.glob("*.top")).read_bytes()
    plan, policy = _load(tmp_path, {"source_sha256": hashlib.sha256(data).hexdigest(), **decisions})
    with pytest.raises(ValueError, match=error):
        export_surveys(data, plan=plan, correction_policy=policy)
