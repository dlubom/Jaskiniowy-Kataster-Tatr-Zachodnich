from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

SKILLS = Path(__file__).parents[1] / ".agents" / "skills"


def load_helper(skill: str, filename: str):
    spec = importlib.util.spec_from_file_location(filename, SKILLS / skill / filename)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def average():
    return load_helper("average-shots", "average_shots.py")


def test_average_preserves_splays_ties_metadata_encoding_and_line_endings(tmp_path, average):
    path = tmp_path / "CAVE.SRV"
    untouched = (
        b"#[\r\nTEAM a 1 2 3\r\nTEAM a 3 4 5\r\n#]\r\n"
        b"; legacy \xf3\r\n#units meters order=DAV\r\n#units A=D V=D\r\n"
        b"0 - 1 10 20\r\n0 - 2 30 40\r\n"
        b"0 1 0 0 0\r\n0 1 0 0 0\r\n"
    )
    path.write_bytes(untouched + b"1 2 4 359 10\r\n2 1 6 181 -12\r\n")

    average.average_shots(path)

    assert path.read_bytes() == untouched + b"1\t2\t5.000\t0.00\t11.00\r\n"


def test_average_keeps_groups_separated_by_directives_and_annotations(tmp_path, average):
    path = tmp_path / "CAVE.SRV"
    data = b"1 2 3 4 5\n#date 2026-09-24\n1 2 5 6 7\n1 2 6 7 8 ; note\n"
    path.write_bytes(data)

    average.average_shots(path)

    assert path.read_bytes() == data


@pytest.mark.parametrize("newline", [b"\r", b"\n", b"\r\n"])
def test_average_preserves_legacy_line_boundaries(tmp_path, average, newline):
    path = tmp_path / "CAVE.SRV"
    header = b"; CP1250 ellipsis: \x85 1 2 3 4 5" + newline
    path.write_bytes(header + newline.join([b"1 2 3 4 5", b"1 2 5 6 7", b"2 3 8 9 10", b""]))

    average.average_shots(path)

    assert (
        path.read_bytes() == header + b"1\t2\t4.000\t5.00\t6.00" + newline + b"2 3 8 9 10" + newline
    )


@pytest.mark.parametrize("azimuth", ["180", "nan", "inf"])
def test_average_rejects_undefined_mean_without_changing_file(tmp_path, average, azimuth):
    path = tmp_path / "CAVE.SRV"
    data = f"1 2 3 0 1\n1 2 3 {azimuth} 1\n".encode()
    path.write_bytes(data)

    with pytest.raises(ValueError):
        average.average_shots(path)

    assert path.read_bytes() == data


def test_average_refuses_raw_source(tmp_path, average):
    path = tmp_path / "_RAW" / "01" / "CAVE.SRV"
    path.parent.mkdir(parents=True)
    data = b"1 2 3 4 5\n1 2 5 6 7\n"
    path.write_bytes(data)

    with pytest.raises(ValueError, match="_RAW"):
        average.average_shots(path)

    assert path.read_bytes() == data


def test_coordinate_helpers_known_reference_and_round_trip():
    gnss = load_helper("gnss-to-wgs84", "gnss_to_wgs84.py")
    utm = load_helper("utm34n-wgs84", "utm34n_wgs84.py")

    lat, lon = gnss.convert(152168.79, 564375.07)
    assert lat == pytest.approx(49.23364130, abs=1e-8)
    assert lon == pytest.approx(19.88454604, abs=1e-8)
    lon, lat, height = utm.utm34n_to_wgs84(419557.06, 5455328.95, 1391.87)
    assert lon == pytest.approx(19.8947380569, abs=1e-9)
    assert lat == pytest.approx(49.2454436384, abs=1e-9)
    easting, northing, height = utm.wgs84_to_utm34n(lon, lat, height)
    assert easting == pytest.approx(419557.06, abs=1e-5)
    assert northing == pytest.approx(5455328.95, abs=1e-5)
    assert height == 1391.87
    assert "SWAPPED" in gnss.validate_input(564375.07, 152168.79)[0]


@pytest.mark.parametrize(
    ("skill", "filename", "args"),
    [
        ("gnss-to-wgs84", "gnss_to_wgs84.py", ["nan", "564375.07"]),
        ("utm34n-wgs84", "utm34n_wgs84.py", ["to-utm", "19.9", "49.2", "inf"]),
    ],
)
def test_coordinate_cli_rejects_non_finite_input(skill, filename, args, monkeypatch, capsys):
    helper = load_helper(skill, filename)
    monkeypatch.setattr("sys.argv", [filename, *args])

    with pytest.raises(ValueError, match="finite"):
        helper.main()

    assert "#fix" not in capsys.readouterr().out
