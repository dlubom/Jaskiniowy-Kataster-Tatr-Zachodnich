from __future__ import annotations

import hashlib
import sqlite3
from contextlib import closing
from pathlib import Path

import pytest

from jktz.gps_catalog import Catalogue, CatalogueObject, Cave, GpsSnapshot, read_catalogue
from jktz.metadata.identity import parse_identity
from jktz.validation.catalogue import check_reference_stations, validate_identities


@pytest.fixture
def catalogue():
    caves = (
        Cave("C-0078", "Bańdzioch Kominiarski", None),
        Cave("C-0295", "Wielka Śnieżna", None),
        Cave("C-0648", "Śnieżna", "C-0295"),
        Cave("C-0332", "Lodowa Małołącka, dolny otwór", "C-0588"),
        Cave("C-0588", "Lodowa Małołącka", None),
    )
    objects = (
        CatalogueObject("KSZ-0112", None, "C-0078", "jaskinia_otwor"),
        CatalogueObject("LEJ-0002", None, "C-0078", "jaskinia_otwor"),
        CatalogueObject("MLZ-0068", None, "C-0648", "jaskinia_otwor"),
        CatalogueObject("MLW-0011", None, "C-0332", "jaskinia_otwor"),
        CatalogueObject("MLW-0024", None, "C-0588", "jaskinia_otwor"),
        CatalogueObject("KSZ-9999", None, None, "punkt_terenowy"),
    )
    return Catalogue(
        {cave.cave_id: cave for cave in caves}, {obj.object_id: obj for obj in objects}
    )


def _underground(cave_id, *refs):
    return parse_identity(
        {"SURVEY_KIND": "underground", "CAVE_ID": cave_id, "CAVE_NAME": "System"},
        {"OBJECT_REF": list(refs)},
    )


def _surface(*refs):
    return parse_identity({"SURVEY_KIND": "surface"}, {"OBJECT_REF": list(refs)})


def test_bandzioch_uses_one_cave_id_for_both_openings(catalogue):
    identities = {
        Path("BK_DOL.SRV"): _underground("C-0078", "BandziochKom:000=KSZ-0112"),
        Path("BK_GORA.SRV"): _underground("C-0078", "BandziochKom:136=LEJ-0002"),
        Path("BK_CIAG.SRV"): _underground("C-0078"),
    }
    fixes = {"BandziochKom:000": "KSZ-0112", "BandziochKom:136": "LEJ-0002"}

    assert validate_identities(identities, catalogue, fixes) == []


def test_wielka_sniezna_system_uses_component_opening(catalogue):
    identities = {
        Path("SNI_CIAG.SRV"): _underground("C-0295", "WielkaSniezna:Ciag:s68=MLZ-0068"),
        Path("SNI_JAS.SRV"): _underground("C-0295"),
    }

    assert validate_identities(identities, catalogue, {}) == []
    assert catalogue.objects["MLZ-0068"].cave_id == "C-0648"
    assert all(obj.cave_id != "C-0295" for obj in catalogue.objects.values())


@pytest.mark.parametrize(
    "other_ref", ["LodowaMalolacka:31=MLW-0024", "WielkaSniezna:Ciag:s68=MLZ-0068"]
)
def test_surface_links_same_or_different_caves(catalogue, other_ref):
    identity = _surface("LodowaMalolacka:0=MLW-0011", other_ref)

    assert validate_identities({Path("POW.SRV"): identity}, catalogue, {}) == []


def test_wrong_existing_cave_is_rejected(catalogue):
    identity = _underground("C-0078", "WielkaSniezna:Ciag:s68=MLZ-0068")

    errors = validate_identities({Path("SNI_CIAG.SRV"): identity}, catalogue, {})

    assert len(errors) == 1
    assert all(
        value in errors[0]
        for value in (
            "SNI_CIAG.SRV",
            "OBJECT_REF",
            "MLZ-0068",
            "C-0648",
            "C-0295",
            "C-0078",
        )
    )


def test_underground_requires_terminal_system_even_without_refs(catalogue):
    identities = {Path("SNI_CIAG.SRV"): _underground("C-0648")}

    errors = validate_identities(identities, catalogue, {})

    assert len(errors) == 1
    assert all(value in errors[0] for value in ("SNI_CIAG.SRV", "CAVE_ID", "C-0648", "C-0295"))


def test_underground_accepts_object_at_end_of_transitive_system_chain(catalogue):
    catalogue.caves["C-1234"] = Cave("C-1234", "Część Śnieżnej", "C-0648")
    catalogue.objects["MLZ-1234"] = CatalogueObject("MLZ-1234", None, "C-1234", "jaskinia_otwor")
    identity = _underground("C-0295", "WielkaSniezna:Ciag:0=MLZ-1234")

    assert validate_identities({Path("SNI_CIAG.SRV"): identity}, catalogue, {}) == []


def test_conflicting_station_binding_is_rejected(catalogue):
    identities = {
        Path("B.SRV"): _surface(":BandziochKom:000=LEJ-0002"),
        Path("A.SRV"): _underground("C-0078", "BandziochKom:000=KSZ-0112"),
    }
    fixes = {"BandziochKom:000": "KSZ-0112"}

    errors = validate_identities(identities, catalogue, fixes)

    assert len(errors) == 1
    assert all(
        value in errors[0]
        for value in (
            "BandziochKom:000",
            "A.SRV",
            "B.SRV",
            "OBJECT_REF",
            "OTWORY.SRV.j2",
            "KSZ-0112",
            "LEJ-0002",
        )
    )
    assert validate_identities(identities, catalogue, {})  # conflicting headers alone
    assert validate_identities({Path("B.SRV"): identities[Path("B.SRV")]}, catalogue, fixes)


def test_same_station_binding_across_headers_and_fix_is_allowed(catalogue):
    identities = {
        Path("POW.SRV"): _surface("BandziochKom:000=KSZ-0112"),
        Path("BK_DOL.SRV"): _underground("C-0078", "BandziochKom:000=KSZ-0112"),
    }

    assert validate_identities(identities, catalogue, {"BandziochKom:000": "KSZ-0112"}) == []


def test_reports_unknown_ids_and_missing_cave_in_stable_order(catalogue):
    identities = {
        Path("Z.SRV"): _underground("C-9999", "X:0=MLW-9999"),
        Path("A.SRV"): _surface("X:2=KSZ-9999", "X:1=MLZ-9999"),
    }

    errors = validate_identities(identities, catalogue, {})

    assert len(errors) == 4
    assert errors == sorted(errors)
    assert errors == validate_identities(dict(reversed(list(identities.items()))), catalogue, {})
    assert any("Z.SRV" in err and "CAVE_ID" in err and "C-9999" in err for err in errors)
    assert any("Z.SRV" in err and "OBJECT_REF" in err and "MLW-9999" in err for err in errors)
    assert any("A.SRV" in err and "OBJECT_REF" in err and "MLZ-9999" in err for err in errors)


def test_referenced_object_requires_cave(catalogue):
    identity = _surface("Punkt:0=KSZ-9999")

    errors = validate_identities({Path("POW.SRV"): identity}, catalogue, {})

    assert len(errors) == 1
    assert all(value in errors[0] for value in ("POW.SRV", "OBJECT_REF", "KSZ-9999", "cave_id"))


def test_surface_reports_broken_system_link(catalogue):
    catalogue.caves["C-0332"] = Cave("C-0332", "Lodowa Małołącka", "C-9999")
    identity = _surface("LodowaMalolacka:0=MLW-0011")

    errors = validate_identities({Path("POW.SRV"): identity}, catalogue, {})

    assert len(errors) == 1
    assert all(value in errors[0] for value in ("POW.SRV", "OBJECT_REF", "MLW-0011", "C-9999"))


def test_missing_station_is_rejected():
    identities = {
        Path("Z.SRV"): _surface("WielkaSniezna:Ciag:s68=MLZ-0068"),
        Path("A.SRV"): _surface("LodowaMalolacka:31=MLW-0024", "LodowaMalolacka:0=MLW-0011"),
    }
    names = {
        "LodowaMalolacka:0",
        "LodowaMalolacka:13",
        "WielkaSniezna:Ciag:S68",
        "Other:Ciag:s68",
        "WielkaSniezna:Other:s68",
    }

    errors = check_reference_stations(identities, names)

    assert len(errors) == 2
    assert errors == sorted(errors)
    assert all(
        value in errors[0] for value in ("A.SRV", "OBJECT_REF", "LodowaMalolacka:31", "MLW-0024")
    )
    assert all(
        value in errors[1]
        for value in ("Z.SRV", "OBJECT_REF", "WielkaSniezna:Ciag:s68", "MLZ-0068")
    )
    assert (
        check_reference_stations(
            identities, names | {"LodowaMalolacka:31", "WielkaSniezna:Ciag:s68"}
        )
        == []
    )


def test_reference_stations_match_survex_empty_prefix_normalization():
    identity = _surface(":LodowaMalolacka::31=MLW-0024")

    assert check_reference_stations({Path("POW.SRV"): identity}, {"LodowaMalolacka: :31"}) == []


def test_unfixed_reference_does_not_require_best_or_fix(tmp_path):
    csv = tmp_path / "best-measurements.csv"
    csv.write_text("object_id,cave_id,system_cave_id\n", encoding="utf-8")
    gpkg = tmp_path / "katalog.gpkg"
    with closing(sqlite3.connect(gpkg)) as connection:
        connection.executescript(
            """
            CREATE TABLE caves (fid INTEGER PRIMARY KEY, cave_id TEXT, name TEXT,
                                system_cave_id TEXT);
            CREATE TABLE objects (fid INTEGER PRIMARY KEY, object_id TEXT, name TEXT,
                                  cave_id TEXT, category TEXT);
            INSERT INTO caves VALUES (1, 'C-0588', 'Lodowa Małołącka', NULL);
            INSERT INTO objects VALUES (1, 'MLW-0024', NULL, 'C-0588', 'jaskinia_otwor');
            """
        )
    snapshot = GpsSnapshot(
        "dlubom/gps-kataster-obiektow-tatr",
        "fixture",
        None,
        csv,
        gpkg,
        hashlib.sha256(csv.read_bytes()).hexdigest(),
        hashlib.sha256(gpkg.read_bytes()).hexdigest(),
    )
    catalogue = read_catalogue(snapshot)
    identities = {Path("LODMAL_POW.SRV"): _surface("LodowaMalolacka:31=MLW-0024")}
    fixes: dict[str, str] = {}

    assert validate_identities(identities, catalogue, fixes) == []
    assert check_reference_stations(identities, {"LodowaMalolacka:31"}) == []
    assert fixes == {}
