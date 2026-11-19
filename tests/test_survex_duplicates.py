from __future__ import annotations

import csv
import json
import os
import subprocess
from pathlib import Path

import pytest

from jktz.cli.survex_duplicates import main, report_count


@pytest.fixture
def detector(monkeypatch, tmp_path):
    calls = []

    def configure(*, count=0, content="auto", summary="auto", returncode=0):
        def run(command, **kwargs):
            calls.append((command, kwargs))
            output = Path(command[command.index("--out") + 1])
            if content == "auto":
                with output.open("w", newline="", encoding="utf-8") as stream:
                    writer = csv.writer(stream)
                    writer.writerow(["leg_a", "leg_b"])
                    writer.writerows((str(i), str(i + 1)) for i in range(count))
            elif content is not None:
                output.write_text(content, encoding="utf-8")
            stderr = json.dumps({"K": count}) if summary == "auto" else summary
            return subprocess.CompletedProcess(command, returncode, "", stderr)

        monkeypatch.setattr("jktz.cli.survex_duplicates.subprocess.run", run)
        source = tmp_path / "model.3d"
        source.write_bytes(b"model preserved")
        output = tmp_path / "reports/pairs.csv"
        return source, output

    return configure, calls


@pytest.mark.parametrize(("count", "expected"), [(0, 0), (1, 1), (42, 1)])
def test_gate_rejects_every_pair_and_keeps_report(detector, count, expected, capsys):
    configure, calls = detector
    source, output = configure(count=count)
    result = main([str(source), "--detector", "detector", "--output", str(output)])
    assert result == expected
    assert source.read_bytes() == b"model preserved"
    assert output.is_file() and output.with_suffix(".log").is_file()
    command = calls[0][0]
    assert command[0] == "detector"
    assert "--exclude-splays" in command
    assert "--include-duplicates" not in command
    assert command[command.index("--relative-percent") + 1] == "5"
    assert str(count) in capsys.readouterr().out


@pytest.mark.parametrize(
    ("content", "summary", "returncode"),
    [
        (None, '{"K":0}', 0),
        ("", '{"K":0}', 0),
        ("wrong,header\n", '{"K":0}', 0),
        ("leg_a,leg_b\n1\n", '{"K":1}', 0),
        ('leg_a,leg_b\n"unclosed', '{"K":1}', 0),
        ("leg_a,leg_b\n", "not JSON", 0),
        ("leg_a,leg_b\n", "{}", 0),
        ("leg_a,leg_b\n", "[]", 0),
        ("leg_a,leg_b\n", '{"K":false}', 0),
        ("leg_a,leg_b\n", '{"K":42}', 0),
        (None, "detector failed", 2),
    ],
)
def test_invalid_or_failed_detector_never_passes(detector, content, summary, returncode):
    configure, _ = detector
    source, output = configure(content=content, summary=summary, returncode=returncode)
    assert main([str(source), "--output", str(output)]) == 1


@pytest.mark.parametrize(
    "error", [OSError("missing detector"), subprocess.TimeoutExpired("detector", 180)]
)
def test_launch_and_timeout_fail(monkeypatch, tmp_path, error):
    def run(*args, **kwargs):
        raise error

    monkeypatch.setattr("jktz.cli.survex_duplicates.subprocess.run", run)
    assert main(["missing.3d", "--output", str(tmp_path / "pairs.csv")]) == 1


def test_unwritable_report_directory_fails(tmp_path):
    obstruction = tmp_path / "file"
    obstruction.write_text("preserved")
    assert main(["model.3d", "--output", str(obstruction / "pairs.csv")]) == 1
    assert obstruction.read_text() == "preserved"


@pytest.mark.parametrize("environment", [None, "published-detector"])
def test_default_input_and_installed_executable(monkeypatch, detector, environment):
    configure, calls = detector
    _, output = configure()
    if environment is None:
        monkeypatch.delenv("SURVEX_DUPLICATES", raising=False)
    else:
        monkeypatch.setenv("SURVEX_DUPLICATES", environment)
    assert main(["--output", str(output)]) == 0
    assert calls[0][0][:2] == [environment or "survex-duplicates", "KATASTER.3d"]


@pytest.mark.parametrize(
    ("second", "expected"), [(None, 0), ("", 1), ("DUPLICATE", 0), ("SPLAY", 0)]
)
def test_published_binary_applies_gate_policy(tmp_path, second, expected):
    executable = os.environ.get("SURVEX_DUPLICATES")
    if not executable:
        if os.environ.get("JKTZ_REQUIRE_SURVEX_DUPLICATES") == "1":
            pytest.fail("Published survex-duplicates executable is required")
        pytest.skip("Published survex-duplicates executable is not configured")
    source = tmp_path / "model.dump"
    lines = [
        'TITLE "CI"',
        'DATE "@0"',
        "DATE_NUMERIC 0",
        "VERSION 8",
        "SEPARATOR ':'",
        "--",
        "LEG 0 0 0 10 0 0 [ci] STYLE=NORMAL",
    ]
    if second is not None:
        lines.append(f"LEG 0 0 0 10 0 0 [ci] STYLE=NORMAL {second}".rstrip())
    lines.append("STOP")
    source.write_text("\n".join(lines) + "\n", encoding="utf-8")
    output = tmp_path / "pairs.csv"
    assert main([str(source), "--output", str(output)]) == expected
    assert report_count(output) == expected
    assert json.loads(output.with_suffix(".log").read_text())["K"] == expected
