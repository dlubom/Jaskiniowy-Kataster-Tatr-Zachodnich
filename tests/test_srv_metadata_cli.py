from __future__ import annotations

from pathlib import Path

import pytest

from jktz.cli.srv_metadata import main
from jktz.metadata.raw import parse_raw_metadata
from jktz.metadata.srv import parse_srv_metadata


def _srv_set_args(path: Path) -> list[str]:
    return [
        "srv-set",
        str(path),
        "--survey-kind",
        "underground",
        "--cave-id",
        "C-1001",
        "--cave-name",
        "Cave",
        "--survey-id",
        "CAVE",
        "--survey-name",
        "Main survey",
        "--source-ref",
        "_RAW/01",
        "--update-date",
        "2026-06-13",
        "--team",
        "A. Surveyor",
        "--team",
        "B. Surveyor",
        "--instrument",
        "DistoX",
        "--survey-date",
        "2024-01",
        "--processing",
        "konwersja SVX -> SRV",
    ]


def _raw_set_args(path: Path) -> list[str]:
    return [
        "raw-set",
        str(path),
        "--title",
        "Cave - paczka zrodlowa 01",
        "--status",
        "dostępny",
        "--origin",
        "A. Surveyor",
        "--authors",
        "A. Surveyor",
        "--dates",
        "2024-01",
        "--acquired",
        "2026-06-13",
        "--added-by",
        "Dariusz Lubomski",
        "--license-value",
        "nieznane",
        "--completeness",
        "pelny pomiar",
        "--content",
        "`source.svx` - pomiary",
        "--content",
        "`notes.txt` - notatki",
    ]


def test_srv_set_creates_metadata_and_preserves_existing_body_bytes(tmp_path: Path) -> None:
    path = tmp_path / "CAVE.SRV"
    body = b"#prefix Cave\n; legacy byte: \x9c\n0\t1\t1.0\t90\t0\n"
    path.write_bytes(body)

    result = main(_srv_set_args(path))

    assert result == 0
    written = path.read_bytes()
    assert written.endswith(body)
    parsed = parse_srv_metadata(path, written.decode("latin-1"))
    assert parsed.single["CAVE_ID"] == "C-1001"
    assert parsed.repeated["TEAM"] == ["A. Surveyor", "B. Surveyor"]
    assert parsed.repeated["SOURCE_REF"] == ["_RAW/01"]


def test_srv_set_dry_run_prints_result_without_modifying_file(
    tmp_path: Path, capsysbinary: pytest.CaptureFixture[bytes]
) -> None:
    path = tmp_path / "CAVE.SRV"
    original = b"#prefix Cave\n0\t1\t1.0\t90\t0\n"
    path.write_bytes(original)

    result = main([*_srv_set_args(path), "--dry-run"])

    captured = capsysbinary.readouterr()
    assert result == 0
    assert path.read_bytes() == original
    assert captured.out.startswith(b"#[\n")
    assert captured.out.endswith(original)


def test_srv_set_rejects_invalid_metadata_without_modifying_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "CAVE.SRV"
    original = b"#prefix Cave\n0\t1\t1.0\t90\t0\n"
    path.write_bytes(original)
    args = _srv_set_args(path)
    args[args.index("2026-06-13")] = "2026-02-30"

    result = main(args)

    assert result == 1
    assert path.read_bytes() == original
    assert "UPDATE_DATE" in capsys.readouterr().err


def test_srv_set_rejects_invalid_source_ref_without_modifying_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "CAVE.SRV"
    original = b"#prefix Cave\n0\t1\t1.0\t90\t0\n"
    path.write_bytes(original)
    args = _srv_set_args(path)
    args[args.index("_RAW/01")] = "sources/01"

    result = main(args)

    assert result == 1
    assert path.read_bytes() == original
    assert "must end with _RAW/NN" in capsys.readouterr().err


def test_srv_set_rejects_malformed_existing_block_without_modifying_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "CAVE.SRV"
    original = b"#[\nBROKEN\n#]\n\n#prefix Cave\n0\t1\t1.0\t90\t0\n"
    path.write_bytes(original)

    result = main(_srv_set_args(path))

    assert result == 1
    assert path.read_bytes() == original
    assert "invalid metadata line" in capsys.readouterr().err


def test_srv_update_changes_date_and_appends_processing_idempotently(tmp_path: Path) -> None:
    path = tmp_path / "CAVE.SRV"
    path.write_text("#prefix Cave\n0\t1\t1.0\t90\t0\n", encoding="ascii")
    assert main(_srv_set_args(path)) == 0

    args = [
        "srv-update",
        str(path),
        "--update-date",
        "2026-06-14",
        "--add-processing",
        "usredniono pomiary przod/tyl",
    ]
    assert main(args) == 0
    first_update = path.read_bytes()
    assert main(args) == 0

    parsed = parse_srv_metadata(path, path.read_text(encoding="latin-1"))
    assert parsed.single["UPDATE_DATE"] == "2026-06-14"
    assert parsed.repeated["PROCESSING"] == [
        "konwersja SVX -> SRV",
        "usredniono pomiary przod/tyl",
    ]
    assert path.read_bytes() == first_update


def test_srv_update_requires_existing_metadata_and_preserves_file_on_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "CAVE.SRV"
    original = b"#prefix Cave\n0\t1\t1.0\t90\t0\n"
    path.write_bytes(original)

    result = main(
        [
            "srv-update",
            str(path),
            "--add-processing",
            "usredniono pomiary przod/tyl",
        ]
    )

    assert result == 1
    assert path.read_bytes() == original
    assert "must start with #[" in capsys.readouterr().err


def test_raw_set_creates_canonical_utf8_metadata(tmp_path: Path) -> None:
    path = tmp_path / "Cave" / "_RAW" / "01" / "README.md"

    result = main(_raw_set_args(path))

    assert result == 0
    parsed = parse_raw_metadata(path, path.read_text(encoding="utf-8"))
    assert parsed.fields["Status materiału"] == "dostępny"
    assert parsed.content_items == [
        "`source.svx` - pomiary",
        "`notes.txt` - notatki",
    ]


def test_raw_set_dry_run_does_not_create_file(
    tmp_path: Path, capsysbinary: pytest.CaptureFixture[bytes]
) -> None:
    path = tmp_path / "Cave" / "_RAW" / "01" / "README.md"

    result = main([*_raw_set_args(path), "--dry-run"])

    captured = capsysbinary.readouterr()
    assert result == 0
    assert not path.exists()
    assert "Status materiału".encode() in captured.out


def test_raw_set_rejects_invalid_status_without_modifying_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "README.md"
    path.write_text("existing\n", encoding="utf-8")
    args = _raw_set_args(path)
    args[args.index("dostępny")] = "archiwalny"

    result = main(args)

    assert result == 1
    assert path.read_text(encoding="utf-8") == "existing\n"
    assert "invalid value for RAW field 'Status materiału'" in capsys.readouterr().err


def test_hash_raw_keeps_existing_output_format(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    raw = tmp_path / "_RAW" / "01"
    raw.mkdir(parents=True)
    source = raw / "source.srv"
    source.write_bytes(b"raw")

    result = main(["hash-raw", str(tmp_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert output.endswith(f"  {source.as_posix()}\n")


@pytest.mark.parametrize("kind", ["underground", "surface"])
@pytest.mark.parametrize("dry_run", [False, True])
def test_identity_cli_preserves_body_and_supports_update(tmp_path, capsysbinary, kind, dry_run):
    path = tmp_path / "CAVE.SRV"
    body = b"#prefix Cave\r\n; legacy \x9c\r\n#date 2004-01-01\r\n0 1 1 90 0\r\n"
    path.write_bytes(body)
    args = _srv_set_args(path)
    args[args.index("underground")] = kind
    if kind == "surface":
        for flag in ("--cave-id", "--cave-name"):
            index = args.index(flag)
            del args[index : index + 2]
    args += ["--object-ref", "Cave:0=MLW-0011", "--object-ref", "Cave:31=MLW-0024"]
    assert main(args + (["--dry-run"] if dry_run else [])) == 0
    data = capsysbinary.readouterr().out if dry_run else path.read_bytes()
    assert data.endswith(body)
    parsed = parse_srv_metadata(path, data.decode("latin-1"))
    assert parsed.single["SURVEY_KIND"] == kind
    assert parsed.repeated["OBJECT_REF"] == ["Cave:0=MLW-0011", "Cave:31=MLW-0024"]
    if dry_run:
        assert path.read_bytes() == body
    else:
        assert main(["srv-update", str(path), "--add-processing", "test update"]) == 0
        assert path.read_bytes().endswith(body)
        assert (
            parse_srv_metadata(path, path.read_bytes().decode("latin-1")).repeated["OBJECT_REF"]
            == parsed.repeated["OBJECT_REF"]
        )


@pytest.mark.parametrize(
    "case",
    [
        "missing-kind",
        "missing-id",
        "missing-name",
        "legacy",
        "surface-cave",
        "surface-no-ref",
        "duplicate-ref",
    ],
)
def test_identity_cli_rejects_invalid_input_atomically(tmp_path, case):
    path = tmp_path / "CAVE.SRV"
    original = b"#prefix Cave\r\n; \x9c\r\n"
    path.write_bytes(original)
    args = _srv_set_args(path)
    if case in {"missing-kind", "missing-id", "missing-name"}:
        flag = {
            "missing-kind": "--survey-kind",
            "missing-id": "--cave-id",
            "missing-name": "--cave-name",
        }[case]
        index = args.index(flag)
        del args[index : index + 2]
    elif case == "legacy":
        args[args.index("C-1001")] = "WPJ:CAVE"
    elif case.startswith("surface"):
        args[args.index("underground")] = "surface"
        if case == "surface-no-ref":
            for flag in ("--cave-id", "--cave-name"):
                index = args.index(flag)
                del args[index : index + 2]
    else:
        args += ["--object-ref", "Cave:0=MLW-0011"] * 2
    if case == "missing-kind":
        with pytest.raises(SystemExit) as error:
            main(args)
        assert error.value.code == 2
    else:
        assert main(args) == 1
    assert path.read_bytes() == original


def test_metadata_cli_preserves_leading_body_blank_lines(tmp_path):
    path = tmp_path / "CAVE.SRV"
    body = b"\r\n\r\n#prefix Cave\r\n; legacy \x9c\r\n"
    path.write_bytes(body)
    assert main(_srv_set_args(path)) == 0
    first = path.read_bytes()
    assert first.endswith(body)
    assert main(["srv-update", str(path), "--add-processing", "update"]) == 0
    assert path.read_bytes().endswith(body)
