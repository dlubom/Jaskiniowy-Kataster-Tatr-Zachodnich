from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from jktz.metadata.errors import MetadataError
from jktz.metadata.identity import ObjectRef, SurveyIdentity, parse_identity


def test_underground_identity_preserves_reference_order_and_is_immutable():
    refs = ["BandziochKom:136=LEJ-0002", "BandziochKom:000=KSZ-0112"]
    identity = parse_identity(
        {"SURVEY_KIND": "underground", "CAVE_ID": "C-0078", "CAVE_NAME": "Bandzioch Kominiarski"},
        {"OBJECT_REF": refs},
    )
    refs.clear()

    assert identity == SurveyIdentity(
        "underground",
        "C-0078",
        (ObjectRef("BandziochKom:136", "LEJ-0002"), ObjectRef("BandziochKom:000", "KSZ-0112")),
    )
    with pytest.raises(FrozenInstanceError):
        identity.cave_id = "C-0295"
    with pytest.raises(FrozenInstanceError):
        identity.object_refs[0].object_id = "KSZ-0112"


def test_underground_section_can_omit_object_refs():
    identity = parse_identity(
        {"SURVEY_KIND": "underground", "CAVE_ID": "C-0295", "CAVE_NAME": "Wielka Sniezna"},
        {},
    )

    assert identity == SurveyIdentity("underground", "C-0295", ())


def test_surface_identity_accepts_full_walls_labels():
    identity = parse_identity(
        {"SURVEY_KIND": "surface", "SURVEY_NAME": "Domiary"},
        {"OBJECT_REF": ["P3:P2:P1:1.0=MLW-0011", ":P2::31=MLW-0024", "DATUM=KSZ-0112"]},
    )

    assert identity == SurveyIdentity(
        "surface",
        None,
        (
            ObjectRef("P3:P2:P1:1.0", "MLW-0011"),
            ObjectRef(":P2::31", "MLW-0024"),
            ObjectRef("DATUM", "KSZ-0112"),
        ),
    )


@pytest.mark.parametrize(
    ("cave_fields", "refs", "field"),
    [
        ({}, [], "OBJECT_REF"),
        ({"CAVE_ID": ""}, ["LodowaMalolacka:31=MLW-0024"], "CAVE_ID"),
        ({"CAVE_NAME": "Lodowa Malolacka"}, ["LodowaMalolacka:31=MLW-0024"], "CAVE_NAME"),
    ],
)
def test_surface_requires_reference_and_forbids_cave_fields(cave_fields, refs, field):
    with pytest.raises(MetadataError, match=field):
        parse_identity({"SURVEY_KIND": "surface", **cave_fields}, {"OBJECT_REF": refs})


@pytest.mark.parametrize(
    ("fields", "field"),
    [
        ({"SURVEY_KIND": None}, "SURVEY_KIND"),
        ({"SURVEY_KIND": ""}, "SURVEY_KIND"),
        ({"SURVEY_KIND": "mixed"}, "SURVEY_KIND"),
        ({"SURVEY_KIND": "Surface"}, "SURVEY_KIND"),
        ({"CAVE_ID": None}, "CAVE_ID"),
        ({"CAVE_ID": ""}, "CAVE_ID"),
        ({"CAVE_ID": "WPJ:BK-01"}, "CAVE_ID"),
        ({"CAVE_ID": "T.E-07.07"}, "CAVE_ID"),
        ({"CAVE_ID": "ROBOCZE"}, "CAVE_ID"),
        ({"CAVE_ID": "C-0078,C-0295"}, "CAVE_ID"),
    ],
)
def test_unknown_kind_and_legacy_cave_ids_are_rejected(fields, field):
    single = {
        "SURVEY_KIND": "underground",
        "CAVE_ID": "C-0078",
        "CAVE_NAME": "Bandzioch Kominiarski",
        **fields,
    }
    with pytest.raises(MetadataError, match=field):
        parse_identity({key: value for key, value in single.items() if value is not None}, {})


@pytest.mark.parametrize("name", [None, "", "   ", "Bańdzioch", "Bandzioch\nKominiarski"])
def test_underground_requires_descriptive_ascii_cave_name(name):
    single = {"SURVEY_KIND": "underground", "CAVE_ID": "C-0078"}
    if name is not None:
        single["CAVE_NAME"] = name
    with pytest.raises(MetadataError, match="CAVE_NAME"):
        parse_identity(single, {})


@pytest.mark.parametrize(
    "ref",
    [
        "BandziochKom:000/KSZ-0112",
        "BandziochKom:000=KSZ-0112=LEJ-0002",
        "=KSZ-0112",
        "BandziochKom:000=",
        "BandziochKom:000=KSZ-abc",
        "Bandzioch Kom:000=KSZ-0112",
        "BandziochKom:a;b=KSZ-0112",
        "BandziochKom:=KSZ-0112",
        "BandziochKom:-=KSZ-0112",
        "A:B:C:D:0=KSZ-0112",
        "BandziochKom:123456789=KSZ-0112",
        f"{'P' * 128}:0=KSZ-0112",
    ],
)
def test_malformed_object_ref_is_rejected(ref):
    with pytest.raises(MetadataError, match="OBJECT_REF"):
        parse_identity({"SURVEY_KIND": "surface"}, {"OBJECT_REF": [ref]})


@pytest.mark.parametrize("second", ["BandziochKom:000=KSZ-0112", ":BandziochKom:000=KSZ-0112"])
def test_duplicate_object_ref_in_one_header_is_rejected(second):
    with pytest.raises(MetadataError, match=r"OBJECT_REF.*duplicate.*KSZ-0112"):
        parse_identity(
            {"SURVEY_KIND": "surface"},
            {"OBJECT_REF": ["BandziochKom:000=KSZ-0112", second]},
        )


def test_conflicting_object_refs_in_one_header_are_rejected():
    with pytest.raises(MetadataError, match=r"OBJECT_REF.*BandziochKom:000.*KSZ-0112.*LEJ-0002"):
        parse_identity(
            {"SURVEY_KIND": "surface"},
            {"OBJECT_REF": ["BandziochKom:000=KSZ-0112", "BandziochKom:000=LEJ-0002"]},
        )


@pytest.mark.parametrize(
    ("extra_single", "repeated", "field"),
    [
        ({"OBJECT_REF": "LodowaMalolacka:31=MLW-0024"}, {}, "OBJECT_REF"),
        ({}, {"CAVE_ID": ["C-0588"]}, "CAVE_ID"),
    ],
)
def test_identity_fields_cannot_bypass_cardinality_via_wrong_mapping(extra_single, repeated, field):
    with pytest.raises(MetadataError, match=field):
        parse_identity({"SURVEY_KIND": "surface", **extra_single}, repeated)
