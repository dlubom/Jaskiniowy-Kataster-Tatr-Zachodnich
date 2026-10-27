"""Exercise the installer action with controlled release downloads."""

from __future__ import annotations

import io
import stat
import subprocess
import urllib.request
import zipfile
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

ACTION = Path(__file__).parents[1] / ".github/actions/install-survex-duplicates/action.yml"
VERSION = "survex-duplicates v1.0.0 (c1e59ebd15ff41aef46f453d57100e58772c8c71)"
BINARY = b"published executable bytes"
PLATFORMS = [
    (
        "Linux",
        "X64",
        "linux_amd64",
        "82a300abd021e81613c9319dc2378e1fba756fc50682c87e262a788e6e84f503",
    ),
    (
        "Linux",
        "ARM64",
        "linux_arm64",
        "3f55957c808885bca1a1283832983f6420d6993f2cf04c4ff96c9190f181286b",
    ),
    (
        "Windows",
        "X64",
        "windows_amd64",
        "d073786c82513f7c0598189dfd16eb62e88a5b1c74d5c73d726f6d80290ff22b",
    ),
    (
        "Windows",
        "ARM64",
        "windows_arm64",
        "df4ec4ed592e1122776b2ea9584cd83808248638c193594d3fc6c5d5b038d041",
    ),
    (
        "macOS",
        "X64",
        "darwin_amd64",
        "721d1ab6359dbcac726d52e4f8afe1d44a6911be8ef344d0190f0050a057f8ff",
    ),
    (
        "macOS",
        "ARM64",
        "darwin_arm64",
        "ade65593c02bb090c1e7f404d5e63fb1a4034b1aedb7707b2c6a2b16eb8cb848",
    ),
]


def release_zip(executable: str | None) -> bytes:
    content = io.BytesIO()
    with zipfile.ZipFile(content, "w") as package:
        if executable:
            package.writestr(executable, BINARY)
        package.writestr("README.md", "release documentation")
        package.writestr("examples/kataster/model.3d", b"bundled example")
        package.writestr("../unexpected.txt", "must never be extracted")
    return content.getvalue()


@pytest.fixture
def installer(monkeypatch, tmp_path):
    environment = tmp_path / "github.env"
    environment.write_text("EXISTING=value\n", encoding="utf-8")
    temporary = tmp_path / "runner temp"
    temporary.mkdir()
    monkeypatch.setenv("RUNNER_TEMP", str(temporary))
    monkeypatch.setenv("GITHUB_ENV", str(environment))

    def run(
        platform=PLATFORMS[0],
        *,
        trusted=True,
        version=VERSION + "\n",
        missing_binary=False,
        smoke_error=False,
    ):
        import hashlib

        runner, architecture, target, expected_sha = platform
        executable = "survex-duplicates.exe" if runner == "Windows" else "survex-duplicates"
        payload = release_zip(None if missing_binary else executable)
        monkeypatch.setenv("RUNNER_OS", runner)
        monkeypatch.setenv("RUNNER_ARCH", architecture)

        def download(url, *, timeout):
            assert url == (
                "https://github.com/dlubom/survex-duplicates/releases/download/v1.0.0/"
                f"survex-duplicates_v1.0.0_{target}.zip"
            )
            assert timeout == 60
            return io.BytesIO(payload)

        def trusted_hash(data):
            assert data == payload
            return SimpleNamespace(hexdigest=lambda: expected_sha)

        def smoke(command, *, check, capture_output, text, timeout):
            assert command[1:] == ["--version"]
            binary = Path(command[0])
            assert binary.is_absolute()
            assert binary.name == executable
            assert binary.read_bytes() == BINARY
            assert environment.read_text(encoding="utf-8") == "EXISTING=value\n"
            assert check and capture_output and text and timeout == 30
            if smoke_error:
                raise subprocess.CalledProcessError(1, command)
            return SimpleNamespace(stdout=version)

        monkeypatch.setattr(urllib.request, "urlopen", download)
        if trusted:
            monkeypatch.setattr(hashlib, "sha256", trusted_hash)
        monkeypatch.setattr(subprocess, "run", smoke)
        action = yaml.safe_load(ACTION.read_text(encoding="utf-8"))
        for step in action["runs"]["steps"]:
            assert step["shell"] == "python"
            exec(compile(step["run"], str(ACTION), "exec"), {"__name__": "__main__"})
        return temporary

    return run, environment, temporary


@pytest.mark.parametrize("platform", PLATFORMS, ids=lambda value: str(value))
def test_installs_the_pinned_platform_executable_only_and_exports_absolute_path(
    installer, platform
):
    run, environment, _ = installer
    temporary = run(platform)
    exported = environment.read_text(encoding="utf-8").splitlines()
    assert exported[0] == "EXISTING=value"
    assert len(exported) == 2
    key, value = exported[1].split("=", 1)
    assert key == "SURVEX_DUPLICATES"
    executable = Path(value)
    assert executable.is_absolute() and executable.is_relative_to(temporary)
    assert executable.read_bytes() == BINARY
    assert sorted(path.name for path in executable.parent.iterdir()) == sorted(
        [executable.name, f"survex-duplicates_v1.0.0_{platform[2]}.zip"]
    )
    assert not (temporary / "unexpected.txt").exists()
    if platform[0] != "Windows":
        assert stat.S_IMODE(executable.stat().st_mode) == 0o755


def test_rejects_a_download_with_a_wrong_digest_before_extracting_or_exporting(installer):
    run, environment, temporary = installer
    with pytest.raises(RuntimeError, match="SHA-256 mismatch"):
        run(trusted=False)
    assert environment.read_text(encoding="utf-8") == "EXISTING=value\n"
    assert not any(path.name == "survex-duplicates" for path in temporary.rglob("*"))


@pytest.mark.parametrize(
    "version",
    [
        "survex-duplicates v1.0.1 (c1e59ebd15ff41aef46f453d57100e58772c8c71)\n",
        "survex-duplicates v1.0.0 (unknown)\n",
        VERSION + " unexpected suffix\n",
        "",
    ],
)
def test_refuses_to_publish_an_executable_with_an_unpinned_version(installer, version):
    run, environment, _ = installer
    with pytest.raises(RuntimeError, match="Unexpected survex-duplicates version"):
        run(version=version)
    assert environment.read_text(encoding="utf-8") == "EXISTING=value\n"


def test_does_not_publish_an_executable_that_cannot_run(installer):
    run, environment, _ = installer
    with pytest.raises(subprocess.CalledProcessError):
        run(smoke_error=True)
    assert environment.read_text(encoding="utf-8") == "EXISTING=value\n"


def test_requires_the_executable_in_the_verified_archive(installer):
    run, environment, _ = installer
    with pytest.raises(KeyError):
        run(missing_binary=True)
    assert environment.read_text(encoding="utf-8") == "EXISTING=value\n"
