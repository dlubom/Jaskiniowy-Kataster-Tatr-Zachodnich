"""Real Walls consumer tests, mandatory in the dedicated Windows job."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from jktz.walls import validate

pytestmark = pytest.mark.skipif(
    not os.environ.get("WALLS_EXE"), reason="native Walls not configured"
)


@pytest.mark.parametrize(
    ("body", "duplicates", "expected", "message"),
    [
        ("a b 1 0 0\n", False, "PASS", "COMPILE_COMPLETE"),
        ("a b invalid 0 0\n", False, "FAIL", "Compile aborted:  DATA"),
        ("#fix a 0 0 0\n#fix a 0 0 0\na b 1 0 0\n", False, "FAIL", "non-fatal errors"),
        ("a b 1 0 0\na b 1 0 0\n", True, "FAIL", "Duplicate Name Pair"),
    ],
)
def test_native_walls_accepts_valid_and_rejects_errors_and_warnings(
    tmp_path, body, duplicates, expected, message
):
    source = tmp_path / "source"
    source.mkdir()
    project = source / "TEST.wpj"
    project.write_text(
        ".BOOK Fixture\n.NAME TEST\n.STATUS 3\n.SURVEY Data\n.NAME DATA\n.STATUS 8\n.ENDBOOK\n"
    )
    (source / "DATA.SRV").write_text("#units meters order=DAV\n" + body)
    report = validate(
        project,
        Path(os.environ["WALLS_EXE"]),
        Path(os.environ["WALLS_DRIVER"]),
        tmp_path / "evidence",
        wine=os.environ.get("WALLS_WINE"),
        timeout=45,
        scratch_root=Path(os.environ["WALLS_SCRATCH_ROOT"]),
        duplicates=duplicates,
    )
    assert report["status"] == expected, report
    assert report["inputs_unchanged"]
    # Negative fixtures must fail because Walls rejected them, not because the runner broke.
    log = (tmp_path / "evidence" / "driver.log").read_text()
    assert ("COMPILE_COMPLETE" if expected == "PASS" else "WALLS_DIALOG") in log, log
    assert "INFRA:" not in log, log
    assert message in log, log


def test_native_timeout_fails_and_releases_its_session(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    project = source / "TEST.wpj"
    project.write_text(
        ".BOOK Fixture\n.NAME TEST\n.STATUS 3\n.SURVEY Data\n.NAME DATA\n.STATUS 8\n.ENDBOOK\n"
    )
    (source / "DATA.SRV").write_text("#units meters order=DAV\na b 1 0 0\n")
    for timeout, status in [(1, "FAIL"), (45, "PASS")]:
        output = tmp_path / f"run-{timeout}"
        report = validate(
            project,
            Path(os.environ["WALLS_EXE"]),
            Path(os.environ["WALLS_DRIVER"]),
            output,
            wine=os.environ.get("WALLS_WINE"),
            timeout=timeout,
            scratch_root=Path(os.environ["WALLS_SCRATCH_ROOT"]),
        )
        assert report["status"] == status, report
        log = (output / "driver.log").read_text()
        assert ("deadline" if timeout == 1 else "COMPILE_COMPLETE") in log, log
