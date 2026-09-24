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


def test_average_keeps_first_direction_and_final_line_without_newline(tmp_path, average):
    path = tmp_path / "CAVE.SRV"
    path.write_bytes(b"  b a 2 45 10\n  a b 4 225 -14\n  b a 6 45 12")

    average.average_shots(path)

    assert path.read_bytes() == b"  b\ta\t4.000\t45.00\t12.00"


def test_average_does_not_write_earlier_groups_if_a_later_group_is_invalid(tmp_path, average):
    path = tmp_path / "CAVE.SRV"
    original = b"a b 2 45 10\na b 4 45 12\nb c 2 0 0\nb c 2 180 0\n"
    path.write_bytes(original)

    with pytest.raises(ValueError, match="unambiguous"):
        average.average_shots(path)

    assert path.read_bytes() == original


def test_average_never_reformats_single_or_unsupported_rows(tmp_path, average):
    path = tmp_path / "CAVE.SRV"
    original = (
        b"\n; comment\n#prefix Cave\na b 2 45 10\nb c 4 20 5\n"
        b"c d invalid 4 5\nc d 2 4\na a 4 5 6\n-- b 4 5 6\na * 4 5 6\n"
    )
    path.write_bytes(original)

    average.average_shots(path)

    assert path.read_bytes() == original


@pytest.mark.parametrize("rotation", [0, 35, 120, 220, 310])
def test_circular_mean_respects_rotation_across_all_quadrants(average, rotation):
    angles = [(rotation - 20) % 360, rotation % 360, (rotation + 20) % 360]

    actual = average.circular_mean_degrees(angles)

    assert (actual - rotation + 180) % 360 - 180 == pytest.approx(0, abs=1e-10)


@pytest.mark.parametrize(
    ("coordinates", "warning"),
    [
        ((152168.79, 564375.07), None),
        ((140000, 550000), None),
        ((170000, 580000), None),
        ((564375.07, 152168.79), "SWAPPED"),
        ((0, 0), "coordinates out of Tatra"),
        ((139999, 564375.07), "northing range"),
        ((152168.79, 580001), "easting range"),
    ],
)
def test_gnss_range_diagnostics(coordinates, warning):
    gnss = load_helper("gnss-to-wgs84", "gnss_to_wgs84.py")

    warnings = gnss.validate_input(*coordinates)

    assert len(warnings) == (1 if warning else 0)
    if warning:
        assert warning in warnings[0]


@pytest.mark.parametrize("elevation", [[], ["1486.69"]])
def test_gnss_cli_converts_reference_and_preserves_optional_height(monkeypatch, capsys, elevation):
    gnss = load_helper("gnss-to-wgs84", "gnss_to_wgs84.py")
    monkeypatch.setattr("sys.argv", ["gnss_to_wgs84.py", "152168.79", "564375.07", *elevation])

    gnss.main()

    captured = capsys.readouterr()
    assert captured.err == ""
    assert "lat=49.23364130  lon=19.88454604" in captured.out
    fix = captured.out.splitlines()[1].split()
    assert fix[:4] == ["#fix", "STATION", "E19.88454604", "N49.23364130"]
    assert fix[4:] == elevation


@pytest.mark.parametrize(
    ("skill", "filename", "args"),
    [
        ("gnss-to-wgs84", "gnss_to_wgs84.py", []),
        ("utm34n-wgs84", "utm34n_wgs84.py", []),
        ("utm34n-wgs84", "utm34n_wgs84.py", ["other", "19.9", "49.2"]),
    ],
)
def test_coordinate_clis_fail_on_invalid_invocation(skill, filename, args, monkeypatch, capsys):
    helper = load_helper(skill, filename)
    monkeypatch.setattr("sys.argv", [filename, *args])

    with pytest.raises(SystemExit) as exc:
        helper.main()

    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "Usage:" in captured.out + captured.err


@pytest.mark.parametrize("elevation", [[], ["1391.87"]])
def test_utm_cli_to_wgs84_reference(monkeypatch, capsys, elevation):
    utm = load_helper("utm34n-wgs84", "utm34n_wgs84.py")
    monkeypatch.setattr(
        "sys.argv", ["utm34n_wgs84.py", "to-wgs84", "419557.06", "5455328.95", *elevation]
    )

    utm.main()

    captured = capsys.readouterr()
    assert captured.err == ""
    assert "lon=19.8947380569  lat=49.2454436384" in captured.out
    fix = captured.out.splitlines()[1].split()
    assert fix[:4] == ["#fix", "STATION", "E19.8947380569", "N49.2454436384"]
    assert fix[4:] == (["1391.87m"] if elevation else [])


def test_utm_cli_to_utm_reference(monkeypatch, capsys):
    utm = load_helper("utm34n-wgs84", "utm34n_wgs84.py")
    monkeypatch.setattr(
        "sys.argv", ["utm34n_wgs84.py", "to-utm", "19.8947380569", "49.2454436384", "1391.87"]
    )

    utm.main()

    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out == "easting=419557.06  northing=5455328.95  elev=1391.87\n"


def test_coordinate_cli_reports_both_input_and_result_outside_tatras(monkeypatch, capsys):
    gnss = load_helper("gnss-to-wgs84", "gnss_to_wgs84.py")
    monkeypatch.setattr("sys.argv", ["gnss_to_wgs84.py", "0", "0"])
    gnss.main()
    assert "coordinates out of Tatra" in capsys.readouterr().err
    assert gnss.validate_output(0, 0)

    utm = load_helper("utm34n-wgs84", "utm34n_wgs84.py")
    monkeypatch.setattr("sys.argv", ["utm34n_wgs84.py", "to-wgs84", "100000", "1000000"])
    utm.main()
    warnings = capsys.readouterr().err
    assert "easting=" in warnings and "northing=" in warnings
    assert "lon=" in warnings and "lat=" in warnings

    monkeypatch.setattr("sys.argv", ["utm34n_wgs84.py", "to-utm", "10", "40"])
    utm.main()
    warnings = capsys.readouterr().err
    assert "lon=" in warnings and "lat=" in warnings
    assert "easting=" in warnings and "northing=" in warnings
