# RAW Validation Boundary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Centralize `_RAW` path classification, keep archival material out of Walls-specific validation, and enforce the documented RAW structure, metadata, inventory, and `SOURCE_REF` contract.

**Architecture:** `jktz.validation._utils` owns the shared `_RAW` boundary used by active-file validators. `jktz.validation.metadata` remains the filesystem-aware validator for RAW packages and uses Git ignore state to exclude only ignored, untracked local artifacts. RAW README files carry the inventory; source material bytes and filenames are never modified.

**Tech Stack:** Python 3.11+, `pathlib`, Git `check-ignore`, pytest, Ruff, uv.

---

## File map

- Modify `src/jktz/validation/_utils.py`: shared RAW predicate and non-RAW iterators.
- Modify `src/jktz/validation/directives.py`: scan SRV files through the shared iterator.
- Modify `src/jktz/validation/filenames.py`: remove its local `_RAW` condition.
- Modify `src/jktz/validation/non_ascii.py`: remove both local `_RAW` conditions.
- Modify `src/jktz/validation/metadata.py`: validate README inventory against package material.
- Create `tests/test_validation_utils.py`: unit contract for shared path classification.
- Modify active-validator tests: prove every Walls-specific rule ignores `_RAW`.
- Modify `tests/test_validation_metadata.py`: RAW inventory and status regressions.
- Modify nine `_RAW/01|02/README.md` files found by the repository audit: make inventory metadata match existing materials without changing source files.

### Task 1: Centralize the `_RAW` boundary

**Files:**
- Create: `tests/test_validation_utils.py`
- Modify: `tests/test_validation_directives.py`
- Modify: `src/jktz/validation/_utils.py`
- Modify: `src/jktz/validation/directives.py`
- Modify: `src/jktz/validation/filenames.py`
- Modify: `src/jktz/validation/non_ascii.py`

- [ ] **Step 1: Write failing selector and directives regressions**

```python
def test_non_raw_paths_excludes_entire_raw_subtree(tmp_path: Path) -> None:
    active = tmp_path / "Cave" / "ACTIVE.SRV"
    source = tmp_path / "Cave" / "_RAW" / "01" / "SOURCE.SRV"
    active.parent.mkdir(parents=True)
    source.parent.mkdir(parents=True)
    active.write_text("")
    source.write_text("")
    assert list(non_raw_paths(tmp_path, "*.SRV")) == [active]


def test_ignores_raw_subtree(tmp_path: Path) -> None:
    source = tmp_path / "Cave" / "_RAW" / "01" / "SOURCE.SRV"
    source.parent.mkdir(parents=True)
    source.write_text("#<source syntax\n")
    directives.check(root=tmp_path)
```

- [ ] **Step 2: Run the focused tests and verify RED**

Run:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest tests/test_validation_utils.py tests/test_validation_directives.py -q
```

Expected: collection fails because `non_raw_paths` does not exist, and the directives regression fails against the current direct `rglob` loop.

- [ ] **Step 3: Implement the shared iterator and migrate consumers**

```python
def is_raw_path(path: Path) -> bool:
    return "_RAW" in path.parts


def non_raw_paths(root: Path, pattern: str = "*") -> Iterable[Path]:
    for path in root.rglob(pattern):
        if not is_raw_path(path):
            yield path


def srv_files(root: Path) -> Iterable[Path]:
    return non_raw_paths(root, "*.SRV")
```

Use `srv_files` in `directives`; use `non_raw_paths` in `filenames` and both loops in `non_ascii`.

- [ ] **Step 4: Run all active-validator tests and verify GREEN**

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest tests/test_validation_utils.py tests/test_validation_directives.py tests/test_validation_decimal_format.py tests/test_validation_prefixes.py tests/test_validation_non_ascii.py tests/test_validation_filenames.py -q
```

Expected: all tests pass.

### Task 2: Enforce RAW inventory and status consistency

**Files:**
- Modify: `tests/test_validation_metadata.py`
- Modify: `src/jktz/validation/metadata.py`

- [ ] **Step 1: Add failing tests for missing, unsafe, and uncovered entries**

Add focused tests that create a valid package and assert `CheckFailed` for:

```python
_raw_readme(contents=["`missing.svx` - source"])
# expected: declared RAW inventory path 'missing.svx' does not exist

_raw_readme(contents=["`../outside.svx` - source"])
# expected: unsafe RAW inventory path '../outside.svx'

_raw_readme(contents=["`listed.svx` - source"])
# with both listed.svx and unlisted.svx present
# expected: material missing from RAW inventory: unlisted.svx
```

Also add passing tests for a declared directory containing Unicode and spaces, and for an ignored untracked generated artifact omitted from the README.

- [ ] **Step 2: Run inventory tests and verify RED**

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest tests/test_validation_metadata.py -q
```

Expected: the new missing/unsafe/uncovered tests do not raise with the current validator.

- [ ] **Step 3: Parse and validate inventory paths**

Implement private helpers in `validation/metadata.py` that:

```python
def _inventory_path(item: str) -> PurePosixPath | None:
    if item == "Brak materiałów źródłowych.":
        return None
    match = re.match(r"^`([^`]+)`(?:\s.*)?$", item)
    if match is None:
        raise ValueError("inventory item must start with a path in backticks")
    path = PurePosixPath(match.group(1))
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError(f"unsafe RAW inventory path {match.group(1)!r}")
    return path
```

For each declared path, check lexical containment and existence. Treat a declared directory as covering all descendant files. Build the actual material set recursively, excluding package-root `README.md`, package-root `.gitignore`, and paths returned by `_git_ignored_untracked`.

- [ ] **Step 4: Add and satisfy status consistency tests**

Add regressions requiring:

- `niedostępny` + `Brak materiałów źródłowych.` + no material: pass;
- `niedostępny` with material: fail;
- `dostępny` or `częściowy` without material: fail.

Run:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest tests/test_validation_metadata.py -q
```

Expected: all metadata validation tests pass.

### Task 3: Reconcile the nine repository inventories

**Files:**
- Modify: `Poligony/D_Kasprowa/Kasprowa_Niznia/_RAW/01/README.md`
- Modify: `Poligony/D_Koscieliska/Kamienne_Zad/Lod_w_Ciemniaku/_RAW/01/README.md`
- Modify: `Poligony/D_Koscieliska/Kom_Wierch/Bandzioch_Kom/_RAW/02/README.md`
- Modify: `Poligony/D_Koscieliska/Organy/Czarna/_RAW/01/README.md`
- Modify: `Poligony/D_Koscieliska/Zar/Psia/_RAW/01/README.md`
- Modify: `Poligony/D_Mietusia/Kazaln_Miet/Marmurowa/_RAW/01/README.md`
- Modify: `Poligony/D_Mietusia/M_Swistowka/Mietusia_Wyznia/_RAW/01/README.md`
- Modify: `Poligony/D_Mietusia/W_Swistowka/Harda/_RAW/01/README.md`
- Modify: `Poligony/D_Mietusia/Wantule/Mietusia/_RAW/01/README.md`

- [ ] **Step 1: Run the repository metadata validator and record all inventory failures**

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest tests/test_validation_metadata.py -q
UV_CACHE_DIR=/private/tmp/uv-cache uv run python -c 'from jktz.validation import metadata; metadata.check()'
```

Expected: unit tests pass; repository check lists exactly the stale or incomplete README inventories.

- [ ] **Step 2: Update README metadata only**

For each reported package:

- add each missing file or directory as a separate backticked inventory item;
- replace declarations of paths that no longer exist with the current archived path;
- move explanatory bullets that do not declare a path to `## Uwagi`;
- keep descriptions and provenance information intact where still accurate.

Do not modify, rename, normalize, or delete any non-README file under `_RAW`.

- [ ] **Step 3: Verify repository inventory GREEN and prove the source boundary**

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run python -c 'from jktz.validation import metadata; metadata.check()'
git diff --name-only
```

Expected: metadata check exits zero; every changed path under `_RAW` ends with `/README.md`.

### Task 4: Full verification

**Files:**
- Verify all modified files.

- [ ] **Step 1: Run the full Python suite**

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest -q
```

Expected: zero failures.

- [ ] **Step 2: Run formatting and lint checks**

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run ruff format --check .
UV_CACHE_DIR=/private/tmp/uv-cache uv run ruff check .
git diff --check
```

Expected: all commands exit zero.

- [ ] **Step 3: Run the authoritative repository validation**

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run jktz-validate
```

Expected: all 12 validation stages pass.

- [ ] **Step 4: Inspect final scope**

```bash
git status --short
git diff --stat HEAD~1
git diff --name-only HEAD~1
```

Expected: changes are limited to the shared validators, their tests and plans, plus RAW package README metadata; no original RAW material is changed.
