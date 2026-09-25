"""Independent analytic overlay expectations and frozen native DXF coordinates."""

from __future__ import annotations

import copy
import hashlib
import json
import math
import struct
from dataclasses import replace
from pathlib import Path

import pytest

from jktz.pockettopo import (
    CorrectionOverride,
    CorrectionPolicy,
    ProcessingPlan,
    RepeatConfirmation,
    export_surveys,
    parse_bytes,
)
from jktz.pockettopo.model import Drawing, Point, StationId, XSection
from jktz.pockettopo.projection import project_geometry

EVIDENCE = Path(__file__).resolve().parents[1] / "doc/pockettopo/evidence"
UNDEFINED = -2147483648
ZERO = -2147483647


def _input(shots=(), correction=0):
    """Independent minimal v3 source fixture, literal raw angular units."""
    trip = struct.pack("<qBh", 632401344000000000, 0, correction)
    rows = b"".join(struct.pack("<iiihhBBh", *shot, 0, 0) for shot in shots)
    mapping = struct.pack("<iii", 0, 0, 500)
    return (
        b"Top\x03"
        + struct.pack("<i", 1)
        + trip
        + struct.pack("<i", len(shots))
        + rows
        + struct.pack("<i", 0)
        + mapping
        + mapping
        + b"\0"
        + mapping
        + b"\0"
    )


def _shot(start=0, end=1, distance=1000, azimuth=0, inclination=0, flip=False):
    return (
        ZERO + start,
        UNDEFINED if end is None else ZERO + end,
        distance,
        azimuth,
        inclination,
        int(flip),
    )


def _geometry(data, **kwargs):
    export = export_surveys(data, **kwargs)
    return project_geometry(parse_bytes(data), export.report)


def _positions(geometry, view="plan"):
    return {row["label"]: row["position"] for row in geometry["views"][view]["stations"]}


def _dxf_entities(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    pairs = list(zip(map(int, lines[::2]), lines[1::2]))
    enabled = False
    entity = None
    result = []
    for code, value in pairs:
        if (code, value) == (2, "ENTITIES"):
            enabled = True
        elif enabled and code == 0:
            if entity:
                result.append(entity)
            if value == "ENDSEC":
                break
            entity = {"type": value}
        elif entity is not None:
            entity[code] = value
    return result


def _dxf_lines(path, layer):
    return [
        (
            [float(row[10]) * 500, -float(row[20]) * 500],
            [float(row[11]) * 500, -float(row[21]) * 500],
        )
        for row in _dxf_entities(path)
        if row["type"] == "LINE" and row[8] == layer
    ]


def _assert_line_multiset(actual, expected, tolerance=1.0):
    pending = list(expected)
    assert len(actual) == len(pending)
    for line in actual:
        match = next(
            (
                index
                for index, (start, end) in enumerate(pending)
                if line["start"] == pytest.approx(start, abs=tolerance)
                and line["end"] == pytest.approx(end, abs=tolerance)
            ),
            None,
        )
        assert match is not None, (line, pending)
        pending.pop(match)
    assert not pending


def test_empty_geometry_has_no_invented_stations_or_datum():
    geometry = _geometry(_input())
    assert geometry["components"] == 0
    assert geometry["diagnostics"] == []
    assert geometry["axes"] == "x_right_y_down"
    assert geometry["units"] == "millimetres"
    assert geometry["loop_adjustment"] is False
    assert geometry["references_applied"] is geometry["mapping_applied"] is False
    for view in geometry["views"].values():
        assert view == {"survey": [], "splays": [], "stations": [], "xsections": []}


def test_cardinal_vertical_zero_and_flip_have_independent_analytic_coordinates():
    geometry = _geometry(
        _input(
            (
                _shot(0, 1, 1000),
                _shot(1, 2, 2000, 16384, flip=True),
                _shot(2, 3, 3000, -32768),
                _shot(3, 4, 4000, -16384),
                _shot(4, 5, 500, inclination=16384),
                _shot(5, 6, 750, inclination=-16384),
                _shot(6, 7, 0, 8192, 1234),
            )
        )
    )
    plan = _positions(geometry)
    side = _positions(geometry, "side")
    for name, position in {
        "0": [0, 0],
        "1": [0, -1000],
        "2": [2000, -1000],
        "3": [2000, 2000],
        "4": [-2000, 2000],
        "5": [-2000, 2000],
        "6": [-2000, 2000],
        "7": [-2000, 2000],
    }.items():
        assert plan[name] == pytest.approx(position, abs=1e-9)
    assert side["2"] == pytest.approx([-1000, 0])
    assert side["5"] == pytest.approx([6000, -500])
    assert side["7"] == pytest.approx([6000, 250])
    assert geometry["diagnostics"] == []
    for view in geometry["views"].values():
        assert [row["source_indices"] for row in view["survey"]] == [[i] for i in range(7)]


def test_reverse_encountered_edge_and_branches_keep_source_identities():
    geometry = _geometry(
        _input(
            (
                _shot(0, 1),
                _shot(2, 1, 2000, 16384),
                _shot(1, 3, 3000, -32768, flip=True),
                _shot(2, 4, 4000, -16384),
            )
        )
    )
    plan = _positions(geometry)
    assert plan["2"] == pytest.approx([-2000, -1000])
    assert plan["3"] == pytest.approx([0, 2000], abs=1e-9)
    assert plan["4"] == pytest.approx([-6000, -1000])
    assert _positions(geometry, "side")["2"] == pytest.approx([3000, 0])
    assert geometry["diagnostics"] == []


def test_unadjusted_loop_and_conflicting_reading_keep_measured_endpoint_and_residual():
    geometry = _geometry(
        _input(
            (_shot(0, 1), _shot(1, 2, 2000, 16384), _shot(2, 0, 3000, -32768), _shot(0, 1, 1500))
        )
    )
    lines = geometry["views"]["plan"]["survey"]
    assert len(lines) == 4
    assert lines[3]["end"] == pytest.approx([0, -1500])
    assert lines[3]["target_station_position"] == pytest.approx([0, -1000])
    assert lines[3]["closure_residual_mm"] == pytest.approx(500)
    # Source-order placement follows 0 to 1 to 2 and preserves the closure error.
    assert _positions(geometry)["2"] == pytest.approx([2000, -1000], abs=1e-9)
    assert lines[1]["end"] == pytest.approx([2000, -1000])
    assert any(row["code"] == "unadjusted_closure" for row in geometry["diagnostics"])


def test_disconnected_and_splay_only_components_have_explicit_local_origins():
    geometry = _geometry(_input((_shot(0, 1), _shot(5, 6, 2000), _shot(9, None))))
    assert geometry["components"] == 3
    assert geometry["diagnostics"] == [
        {"code": "disconnected_components_local_origins", "components": 3}
    ]
    for view in geometry["views"].values():
        assert [row["component"] for row in view["stations"]] == [0, 0, 1, 1, 2]
        assert len(view["splays"]) == 1
        assert view["splays"][0]["source_indices"] == [2]
    assert _positions(geometry)["5"] == _positions(geometry)["9"] == [0, 0]


def test_auto_is_held_and_pinned_override_applies_once_without_mutation():
    data = _input((_shot(),), correction=-32768)
    assert _geometry(data)["components"] == 0
    policy = CorrectionPolicy(
        hashlib.sha256(data).hexdigest(),
        (CorrectionOverride(0, 90, "Analytic eastward correction"),),
    )
    export = export_surveys(data, correction_policy=policy)
    before = copy.deepcopy(export.report)
    source = parse_bytes(data)
    result = project_geometry(source, export.report)
    assert export.report == before
    assert source == parse_bytes(data)
    assert _positions(result)["1"] == pytest.approx([1000, 0], abs=1e-9)
    assert _positions(result, "side")["1"] == pytest.approx([1000, 0], abs=1e-9)


def test_native_p01_flip_stations_lines_and_section_connectors_match_every_coordinate():
    case = EVIDENCE / "p01/cases/api-drawings"
    data = next(case.glob("*.top")).read_bytes()
    geometry = _geometry(data)
    for view, name in (("plan", "native-plan.dxf"), ("side", "native-side.dxf")):
        projected = geometry["views"][view]
        _assert_line_multiset(projected["survey"], _dxf_lines(case / name, "Shots"), tolerance=1e-8)
        _assert_line_multiset(
            [section["connector"] for section in projected["xsections"]],
            _dxf_lines(case / name, "Sketch"),
            tolerance=1e-8,
        )
        assert all(section["splays"] == [] for section in projected["xsections"])
        assert all(section["status"] == "projected" for section in projected["xsections"])
    assert _positions(geometry, "side")["2"] == pytest.approx([0, 0], abs=1e-8)


def test_unconfirmed_repeats_remain_separate_and_confirmed_average_retains_p03_contract():
    case = EVIDENCE / "p01/cases/api-cardinal"
    data = next(case.glob("*.top")).read_bytes()
    independent = _geometry(data)
    plan = ProcessingPlan(
        hashlib.sha256(data).hexdigest(),
        (RepeatConfirmation((4, 5, 6), "Native explicit fixture repeat"),),
    )
    confirmed = _geometry(data, plan=plan)
    assert len(independent["views"]["plan"]["survey"]) == 10
    assert len(confirmed["views"]["plan"]["survey"]) == 8
    row = confirmed["views"]["plan"]["survey"][4]
    assert row["source_indices"] == [4, 5, 6]
    assert row["end"][0] == pytest.approx(-2000, abs=1e-8)
    expected_north = 5000 * math.cos(math.radians(1820 * 360 / 65536))
    assert row["start"][1] - row["end"][1] == pytest.approx(expected_north)
    # Native averages 3D horizontal components and rounds to 4922 mm; the
    # contracted circular azimuth mean and arithmetic D/V are deliberately distinct.
    assert abs(expected_north - 4922) > 1
    json.dumps(confirmed, allow_nan=False)


def test_missing_xsection_station_is_retained_with_no_invented_connector():
    data = _input((_shot(),))
    source = parse_bytes(data)
    section = XSection(Point(123, -456), StationId(ZERO + 100), 0)
    source = replace(source, outline=Drawing(source.outline.mapping, (section,)))
    geometry = project_geometry(source, export_surveys(data).report)
    row = geometry["views"]["plan"]["xsections"][0]
    assert row == {
        "element_index": 0,
        "position": [123, -456],
        "station_raw": ZERO + 100,
        "direction": 0,
        "status": "station_not_in_active_overlay",
        "connector": None,
        "splays": [],
    }


@pytest.mark.parametrize(
    ("direction", "expected"),
    [(-1, [2000, 0]), (0, [2000, 0]), (16384, [0, 0]), (32768, [-2000, 0]), (49152, [0, 0])],
)
def test_xsection_cardinal_projection_and_source_element_index(direction, expected):
    data = _input((_shot(), _shot(1, None, 2000, 16384)))
    source = parse_bytes(data)
    section = XSection(Point(100, -200), StationId(ZERO + 1), direction)
    source = replace(source, outline=Drawing(source.outline.mapping, (section,)))
    row = project_geometry(source, export_surveys(data).report)["views"]["plan"]["xsections"][0]
    assert row["splays"][0]["start"] == [100, -200]
    assert row["splays"][0]["end"] == pytest.approx(
        [100 + expected[0], -200 + expected[1]], abs=1e-9
    )
    assert row["splays"][0]["source_indices"] == [1]


@pytest.mark.parametrize("name", ["loop", "branch", "xsection"])
@pytest.mark.parametrize("view", ["plan", "side"])
def test_native_p05_every_survey_splay_and_xsection_line_coordinate(name, view):
    case = EVIDENCE / "p05/native" / name
    data = next(case.glob("*.top")).read_bytes()
    geometry = _geometry(data)["views"][view]
    path = case / f"native-{view}.dxf"
    _assert_line_multiset(geometry["survey"], _dxf_lines(path, "Shots"), tolerance=3)
    _assert_line_multiset(
        geometry["splays"]
        + [line for section in geometry["xsections"] for line in section["splays"]],
        _dxf_lines(path, "XSect"),
        tolerance=3,
    )
    sections = geometry["xsections"]
    if sections:
        _assert_line_multiset(
            [section["connector"] for section in sections], _dxf_lines(path, "Sketch"), tolerance=3
        )


def test_shadow_every_native_survey_and_splay_coordinate_without_repeat_inference():
    case = EVIDENCE / "shadow"
    data = (case / "shadow.top").read_bytes()
    geometry = _geometry(data)
    for view, suffix in (("plan", "P"), ("side", "S")):
        projected = geometry["views"][view]
        native = case / f"shadow-native{suffix}.dxf"
        assert len(projected["survey"]) == 30
        assert len(projected["splays"]) == 1
        _assert_line_multiset(projected["survey"], _dxf_lines(native, "Shots"), tolerance=3)
        _assert_line_multiset(projected["splays"], _dxf_lines(native, "XSect"), tolerance=3)
    # The only held source record is an invalid same-station zero link; P04
    # already records the reason. No source splay or independent leg disappears.
    export = export_surveys(data)
    assert export.report["completeness"]["held_shots"] == 1
    assert all(len(group["source_indices"]) == 1 for group in export.report["groups"])


def test_splays_use_incoming_leg_azimuth_not_outgoing_or_declination_and_flip():
    data = _input(
        (_shot(0, 1, 1000, flip=True), _shot(1, 2, 1000, 16384), _shot(1, None, 2000, 0)),
        correction=16384,
    )
    geometry = _geometry(data)
    line = geometry["views"]["side"]["splays"][0]
    assert line["start"] == pytest.approx([-1000, 0])
    assert line["end"] == pytest.approx([-3000, 0])
    assert geometry["views"]["plan"]["splays"][0]["end"] == pytest.approx([3000, 0], abs=1e-9)


def test_root_splay_has_no_inferred_side_axis():
    geometry = _geometry(_input((_shot(0, None, 2000, 16384, 8192),)))
    line = geometry["views"]["side"]["splays"][0]
    assert line["start"] == [0, 0]
    assert line["end"] == pytest.approx([0, -math.sqrt(2) * 1000])


def test_zero_link_defines_no_side_projection_axis_for_splays():
    geometry = _geometry(_input((_shot(0, 1, 0, 16384), _shot(1, None, 2000, 16384, 8192))))
    assert geometry["views"]["side"]["splays"][0]["end"] == pytest.approx([0, -math.sqrt(2) * 1000])


@pytest.mark.parametrize("first_flipped", [False, True])
def test_mixed_flip_confirmation_has_explicit_unconfirmed_representative_and_diagnostic(
    first_flipped,
):
    data = _input((_shot(flip=first_flipped), _shot(flip=not first_flipped)))
    plan = ProcessingPlan(
        hashlib.sha256(data).hexdigest(),
        (RepeatConfirmation((0, 1), "Confirmed D/A/V repetitions; direction not resolved"),),
    )
    export = export_surveys(data, plan=plan)
    geometry = project_geometry(parse_bytes(data), export.report)
    assert geometry["mixed_flip_policy"] == "first_source_reading_unconfirmed_side_direction"
    assert geometry["diagnostics"] == [
        {
            "code": "mixed_flip_first_source_reading",
            "group_id": 0,
            "source_indices": [0, 1],
            "source_flags": [int(first_flipped), int(not first_flipped)],
            "selected_source_index": 0,
            "side_direction_status": "unconfirmed",
        }
    ]
    assert geometry["views"]["side"]["survey"][0]["end"] == pytest.approx(
        [-1000 if first_flipped else 1000, 0]
    )
    assert geometry["views"]["plan"]["survey"][0]["end"] == pytest.approx([0, -1000])
    assert [row["flags"] for row in export.report["record_trace"]] == [
        int(first_flipped),
        int(not first_flipped),
    ]


def test_many_sections_without_splays_do_not_rescan_every_measurement():
    class CountingGroup(dict):
        visits = 0

        def __getitem__(self, key):
            if key == "kind":
                type(self).visits += 1
            return super().__getitem__(key)

    data = _input(tuple(_shot(index, index + 1) for index in range(1000)))
    source = parse_bytes(data)
    sections = tuple(
        XSection(Point(index, index), StationId(ZERO + index % 1000), -1) for index in range(2000)
    )
    source = replace(source, outline=Drawing(source.outline.mapping, sections))
    report = export_surveys(data).report
    report["groups"] = [CountingGroup(group) for group in report["groups"]]
    geometry = project_geometry(source, report)
    assert len(geometry["views"]["plan"]["xsections"]) == 2000
    assert all(not section["splays"] for section in geometry["views"]["plan"]["xsections"])
    assert CountingGroup.visits < 20 * len(report["groups"])


@pytest.mark.parametrize(("count", "rejected"), [(4, False), (5, True)])
def test_xsection_expansion_budget_counts_both_views_before_projecting(
    monkeypatch, count, rejected
):
    import jktz.pockettopo.projection as projection

    monkeypatch.setattr(projection, "MAX_SECTION_SPLAY_LINES", 4)
    data = _input((_shot(), _shot(1, None)))
    source = parse_bytes(data)
    section = XSection(Point(0, 0), StationId(ZERO + 1), 0)
    source = replace(
        source,
        outline=Drawing(source.outline.mapping, (section,) * 2),
        sideview=Drawing(source.sideview.mapping, (section,) * (count - 2)),
    )
    report = export_surveys(data).report
    if rejected:

        def must_not_project(*args):
            pytest.fail("expansion limit must reject before constructing any vectors")

        monkeypatch.setattr(projection, "_vector", must_not_project)
        with pytest.raises(ValueError, match="xsection_projection_limit_exceeded: 5"):
            project_geometry(source, report)
    else:
        geometry = project_geometry(source, report)
        assert (
            sum(
                len(section["splays"])
                for view in geometry["views"].values()
                for section in view["xsections"]
            )
            == 4
        )
