# Metadata Module Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split SRV metadata, RAW README metadata, and measurement validation into focused package modules while replacing the test-only dynamic script import with normal imports.

**Architecture:** Move reusable behavior from `scripts/` and the combined `metadata_contract.py` into focused `jktz` modules. Keep `scripts/srv_metadata.py` as a compatibility wrapper and preserve all serialized formats and validator behavior.

**Tech Stack:** Python 3.9+, pytest, Ruff, Hatch/uv package layout.

---

### Task 1: Define the package import surface with failing tests

**Files:**
- Move: `tests/test_srv_metadata_script.py` to `tests/test_srv_metadata.py`
- Create: `tests/test_raw_metadata.py`
- Create: `tests/test_validation_measurements.py`
- Modify: `tests/test_metadata_contract.py`

- [ ] **Step 1: Replace the dynamic script loader with package imports**

Import SRV helpers from `jktz.srv_metadata`, RAW helpers from
`jktz.raw_metadata`, and shot validation from
`jktz.validation.measurements`.

- [ ] **Step 2: Run focused tests and verify RED**

Run:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest \
  tests/test_srv_metadata.py \
  tests/test_raw_metadata.py \
  tests/test_validation_measurements.py -q
```

Expected: collection fails because the new package modules do not exist yet.

### Task 2: Extract shared error and SRV metadata behavior

**Files:**
- Create: `src/jktz/metadata_errors.py`
- Create: `src/jktz/srv_metadata.py`
- Modify: `tests/test_srv_metadata.py`

- [ ] **Step 1: Move `MetadataError`, `SrvMetadata`, SRV parsing, formatting, path scope, `SOURCE_REF`, and helper functions into the package**

Preserve the current field order and the two canonical blank-line separators.

- [ ] **Step 2: Run SRV tests and verify GREEN**

Run:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest tests/test_srv_metadata.py -q
```

Expected: all SRV metadata tests pass.

### Task 3: Extract RAW README metadata behavior

**Files:**
- Create: `src/jktz/raw_metadata.py`
- Modify: `tests/test_raw_metadata.py`

- [ ] **Step 1: Move `RawReadme`, README parsing, canonical README formatting, and material hashing**

Use the shared `MetadataError` and keep README output unchanged.

- [ ] **Step 2: Run RAW tests and verify GREEN**

Run:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest tests/test_raw_metadata.py -q
```

Expected: all RAW metadata tests pass.

### Task 4: Extract measurement validation

**Files:**
- Create: `src/jktz/validation/measurements.py`
- Modify: `tests/test_validation_measurements.py`

- [ ] **Step 1: Move active-shot date/declination scanning and its private helpers**

Keep support for DAV, DVA, AVD, rectangular data, zero shots, comments, and
state changes in file order.

- [ ] **Step 2: Run measurement tests and verify GREEN**

Run:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest tests/test_validation_measurements.py -q
```

Expected: all measurement validation tests pass.

### Task 5: Rewire validation and CLI

**Files:**
- Create: `src/jktz/cli/srv_metadata.py`
- Modify: `src/jktz/validation/metadata.py`
- Modify: `scripts/srv_metadata.py`
- Delete: `src/jktz/metadata_contract.py`
- Modify: `pyproject.toml`

- [ ] **Step 1: Update validator imports to the focused modules**

Import SRV parsing from `jktz.srv_metadata`, RAW parsing from
`jktz.raw_metadata`, and shot scanning from `jktz.validation.measurements`.

- [ ] **Step 2: Make the script a thin CLI wrapper**

Expose `jktz-srv-metadata = "jktz.cli.srv_metadata:main"` and keep direct
execution of `python scripts/srv_metadata.py hash-raw` working.

- [ ] **Step 3: Run metadata integration and CLI tests**

Run:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest \
  tests/test_validation_metadata.py \
  tests/test_srv_metadata.py \
  tests/test_raw_metadata.py \
  tests/test_validation_measurements.py -q
```

Expected: all focused and integration tests pass.

### Task 6: Update current documentation references

**Files:**
- Modify: `docs/superpowers/specs/2026-06-04-srv-metadata-design.md`
- Modify: `CLAUDE.md`
- Modify: `.claude/skills/add-cave/SKILL.md`
- Modify: `.claude/skills/convert-survex/SKILL.md`
- Modify: `.claude/skills/average-shots/SKILL.md`

- [ ] **Step 1: Replace live references to the combined contract module**

Point SRV contract references to `jktz.srv_metadata` and RAW contract
references to `jktz.raw_metadata`. Keep the existing helper command and data
format instructions unchanged.

### Task 7: Full verification

**Files:**
- Verify all modified files.

- [ ] **Step 1: Run formatting and lint**

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run ruff format --check src scripts tests
UV_CACHE_DIR=/private/tmp/uv-cache uv run ruff check src scripts tests
git diff --check
```

- [ ] **Step 2: Run the complete test suite**

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest
```

- [ ] **Step 3: Run the complete repository validator**

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run jktz-validate
```

- [ ] **Step 4: Inspect the final diff**

Confirm that no active `.SRV` or `_RAW/NN/README.md` data file changed and
that canonical blank lines remain asserted in SRV formatter tests.
