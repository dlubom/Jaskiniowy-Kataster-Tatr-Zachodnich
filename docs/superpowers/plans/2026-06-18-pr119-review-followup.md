# PR #119 Review Follow-up Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the confirmed Windows test, CLI wrapper, and ignored `_RAW` artifact findings from PR #119 review.

**Architecture:** Keep metadata behavior in the installed `jktz` package, extend Windows CI to execute pytest, and make RAW layout validation consult Git only to identify ignored and untracked local artifacts. The validator remains strict for tracked files, ordinary untracked files, and directories outside a Git worktree.

**Tech Stack:** Python 3.12, pathlib, subprocess, pytest, Ruff, uv, GitHub Actions, Git.

---

## File map

- Modify `tests/test_validation_metadata.py`: use explicit encodings and add Git-aware RAW layout regression tests.
- Modify `src/jktz/validation/metadata.py`: batch-query Git ignore state and exclude only ignored, untracked loose `_RAW` entries.
- Create `tests/test_workflow_configuration.py`: lock in Windows pytest coverage.
- Modify `.github/workflows/validate.yml`: run pytest in the Windows validation job.
- Delete `scripts/srv_metadata.py`: remove the unused compatibility wrapper.

### Task 1: Make Windows test execution deterministic and required

**Files:**
- Modify: `tests/test_validation_metadata.py`
- Create: `tests/test_workflow_configuration.py`
- Modify: `.github/workflows/validate.yml`

- [ ] **Step 1: Add a failing workflow contract test**

Create `tests/test_workflow_configuration.py`:

```python
from pathlib import Path


WORKFLOW = Path(__file__).parents[1] / ".github" / "workflows" / "validate.yml"


def test_windows_validation_runs_pytest() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    windows_pytest_step = (
        "      - name: Run Pytest (Windows)\n"
        "        if: runner.os == 'Windows'\n"
        "        run: uv run pytest\n"
    )

    assert windows_pytest_step in text
```

- [ ] **Step 2: Run the workflow test and verify RED**

Run:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest tests/test_workflow_configuration.py -q
```

Expected: one failure because `validate.yml` does not contain a Windows pytest step.

- [ ] **Step 3: Make metadata test fixture encodings explicit**

In `tests/test_validation_metadata.py`, add `encoding="utf-8"` to every
`Path.write_text` call. The affected forms become:

```python
(raw / "README.md").write_text(_raw_readme(), encoding="utf-8")
(raw / "source.xlsx").write_text("raw", encoding="utf-8")
(cave / "CAVE.SRV").write_text(_srv(), encoding="utf-8")
(raw / "README.md").write_text(
    _raw_readme().replace("- **Licencja źródłowa:** nieznane\n", ""),
    encoding="utf-8",
)
(raw / "loose.txt").write_text("raw", encoding="utf-8")
(cave / "BAD.SRV").write_text("#prefix Cave\n0\t1\t1.0\t90\t0\n", encoding="utf-8")
(cave / "CAVE.SRV").write_text(
    _srv(body="0\t1\t1.0\t90\t0\n"), encoding="utf-8"
)
(raw / "source.svx").write_text("raw", encoding="utf-8")
(section / "SECTION.SRV").write_text(
    _srv(source_ref="../_RAW/02"), encoding="utf-8"
)
(raw / "ORIG.SRV").write_text("0\t1\t1.0\t90\t0\n", encoding="utf-8")
(poligony / "OTWORY.SRV").write_text(
    "#fix Cave:0 E19.9 N49.2 1000m\n", encoding="utf-8"
)
surface.write_text("0\t1\t1.0\t90\t0\n", encoding="utf-8")
```

The file contains 15 `write_text` calls. Update all 15, including all three
repeated RAW README writes and both direct `_RAW/ORIG.SRV` writes. Confirm no
call was missed with:

```bash
rg -n 'write_text\(' tests/test_validation_metadata.py
```

Expected: each reported call either contains `encoding="utf-8"` on the same
line or continues into a following line containing that argument.

- [ ] **Step 4: Add pytest to the Windows validation job**

In `.github/workflows/validate.yml`, immediately after `Sync Python tooling`, add:

```yaml
      - name: Run Pytest (Windows)
        if: runner.os == 'Windows'
        run: uv run pytest
```

This runs before the Windows-only Survex and GDAL installation steps, so an
encoding failure stops the job early.

- [ ] **Step 5: Verify GREEN locally, including a non-UTF-8 locale**

Run:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest tests/test_workflow_configuration.py tests/test_validation_metadata.py -q
PYTHONUTF8=0 PYTHONCOERCECLOCALE=0 LC_ALL=C UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest tests/test_validation_metadata.py -q
```

Expected: both commands pass. The second command previously reproduced the
`UnicodeEncodeError` on `ł`.

- [ ] **Step 6: Commit the Windows portability fix**

```bash
git add .github/workflows/validate.yml tests/test_validation_metadata.py tests/test_workflow_configuration.py
git commit -m "[codex] Uruchamiaj testy na Windows"
```

### Task 2: Ignore only Git-ignored, untracked loose RAW artifacts

**Files:**
- Modify: `tests/test_validation_metadata.py`
- Modify: `src/jktz/validation/metadata.py`

- [ ] **Step 1: Add Git test setup and two regression tests**

Add the import and helper to `tests/test_validation_metadata.py`:

```python
import subprocess


def _git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    )
```

Add these tests:

```python
def test_metadata_check_ignores_git_ignored_untracked_material_under_raw(
    tmp_path: Path,
) -> None:
    _git(tmp_path, "init", "--quiet")
    (tmp_path / ".gitignore").write_text("*.err\n", encoding="utf-8")
    raw = tmp_path / "Poligony" / "Cave" / "_RAW"
    raw.mkdir(parents=True)
    (raw / "generated.err").write_bytes(b"")

    metadata.check(root=tmp_path / "Poligony")


def test_metadata_check_rejects_tracked_ignored_material_under_raw(tmp_path: Path) -> None:
    _git(tmp_path, "init", "--quiet")
    (tmp_path / ".gitignore").write_text("*.err\n", encoding="utf-8")
    raw = tmp_path / "Poligony" / "Cave" / "_RAW"
    raw.mkdir(parents=True)
    generated = raw / "generated.err"
    generated.write_bytes(b"")
    _git(tmp_path, "add", "--force", str(generated.relative_to(tmp_path)))

    with pytest.raises(CheckFailed, match="material left directly under _RAW"):
        metadata.check(root=tmp_path / "Poligony")
```

- [ ] **Step 2: Run the new tests and verify RED**

Run:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest \
  tests/test_validation_metadata.py::test_metadata_check_ignores_git_ignored_untracked_material_under_raw \
  tests/test_validation_metadata.py::test_metadata_check_rejects_tracked_ignored_material_under_raw -q
```

Expected: the ignored/untracked test fails with `material left directly under
_RAW`; the force-added tracked test passes.

- [ ] **Step 3: Add one batched Git ignore query**

In `src/jktz/validation/metadata.py`, add imports:

```python
import os
import subprocess
```

Add these helpers after `_is_numbered_package_dir`:

```python
def _raw_root_material(raw_dir: Path) -> list[Path]:
    return [
        child
        for child in sorted(raw_dir.iterdir())
        if child.name != "README.md" and not _is_numbered_package_dir(child)
    ]


def _git_ignored_untracked(paths: list[Path], scan_root: Path) -> set[Path]:
    if not paths:
        return set()

    payload = b"\0".join(os.fsencode(path.resolve()) for path in paths) + b"\0"
    try:
        result = subprocess.run(
            ["git", "-C", str(scan_root), "check-ignore", "--stdin", "-z"],
            input=payload,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        return set()

    if result.returncode in {0, 1}:
        return {
            Path(os.fsdecode(item)).resolve()
            for item in result.stdout.split(b"\0")
            if item
        }

    stderr = os.fsdecode(result.stderr).strip()
    if "not a git repository" in stderr:
        return set()
    raise CheckFailed(f"ERROR: failed to query Git ignore state: {stderr}")
```

`git check-ignore` does not report indexed paths unless `--no-index` is used,
which is exactly the required tracked-versus-untracked distinction.

- [ ] **Step 4: Apply the ignored set to RAW root validation**

Change `_check_raw_root` to accept the ignored set and retain strict behavior
for every other candidate:

```python
def _check_raw_root(raw_dir: Path, errors: list[str], ignored: set[Path]) -> None:
    children = sorted(raw_dir.iterdir())
    numbered_packages = [child for child in children if _is_numbered_package_dir(child)]

    for child in _raw_root_material(raw_dir):
        if child.resolve() in ignored:
            continue
        errors.append(f"  {child.as_posix()}: material left directly under _RAW")

    for package in numbered_packages:
        _check_raw_package(package, errors)
```

In `check`, replace the RAW loop with one batch query:

```python
    raw_dirs = [path for path in sorted(scan_root.rglob("_RAW")) if path.is_dir()]
    raw_root_material = [
        child for raw_dir in raw_dirs for child in _raw_root_material(raw_dir)
    ]
    ignored = _git_ignored_untracked(raw_root_material, scan_root)

    for raw_dir in raw_dirs:
        _check_raw_root(raw_dir, errors, ignored)
```

- [ ] **Step 5: Verify GREEN and strict fallback behavior**

Run:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest tests/test_validation_metadata.py -q
```

Expected: all metadata validation tests pass, including the existing non-Git
test that rejects direct `_RAW/ORIG.SRV` material.

- [ ] **Step 6: Commit Git-aware RAW validation**

```bash
git add src/jktz/validation/metadata.py tests/test_validation_metadata.py
git commit -m "[codex] Pomijaj ignorowane artefakty RAW"
```

### Task 3: Remove the unused metadata script wrapper

**Files:**
- Delete: `scripts/srv_metadata.py`

- [ ] **Step 1: Confirm the installed entry point and active references**

Run:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run jktz-srv-metadata --help
git grep -n 'scripts/srv_metadata.py' -- ':!docs/superpowers/**'
git grep -n 'jktz-srv-metadata' -- ':!docs/superpowers/**'
```

Expected: the installed command lists `srv-set`, `srv-update`, `raw-set`, and
`hash-raw`; there are no active wrapper references; CLAUDE.md and the three
metadata-related skills use `jktz-srv-metadata`.

- [ ] **Step 2: Delete the wrapper**

Delete `scripts/srv_metadata.py` without changing historical design or plan
documents.

- [ ] **Step 3: Verify the installed entry point remains functional**

Run:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run jktz-srv-metadata --help
UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest tests/test_srv_metadata_cli.py -q
```

Expected: the command lists all four subcommands and all CLI tests pass.

- [ ] **Step 4: Commit wrapper removal**

```bash
git add scripts/srv_metadata.py
git commit -m "[codex] Usun nieuzywany wrapper metadanych"
```

### Task 4: Run final repository verification

**Files:**
- Verify all files changed in Tasks 1-3.

- [ ] **Step 1: Run formatting and static checks**

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run ruff format --check src scripts tests
UV_CACHE_DIR=/private/tmp/uv-cache uv run ruff check src scripts tests
git diff --check master...HEAD
```

Expected: every command exits zero with no diagnostics.

- [ ] **Step 2: Run the complete Python test suite**

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest -q
```

Expected: all tests pass with zero failures.

- [ ] **Step 3: Run the authoritative repository validation gate**

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run jktz-validate
```

Expected: all 12 validation stages pass, including Cavern warnings and export
checks.

- [ ] **Step 4: Review scope and commit state**

```bash
git status --short
git log --oneline -4
git diff --stat master...HEAD
```

Expected: the worktree is clean and the latest commits correspond to the
approved spec, Windows fix, RAW validation fix, and wrapper removal.
