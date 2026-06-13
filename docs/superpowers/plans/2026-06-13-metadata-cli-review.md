# Metadata CLI Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move SRV and RAW metadata into a focused package and expose safe CLI commands used by repository skills.

**Architecture:** Domain parsing and formatting live under `jktz.metadata`; the existing `jktz-srv-metadata` entry point orchestrates file operations. SRV writes preserve non-header bytes through Latin-1 round trips and all writes use temporary files plus `os.replace`.

**Tech Stack:** Python 3.9, standard library, argparse, pytest, Ruff, uv.

---

### Task 1: Move metadata modules behind a consistent package API

**Files:**
- Create: `src/jktz/metadata/__init__.py`
- Move: `src/jktz/srv_metadata.py` to `src/jktz/metadata/srv.py`
- Move: `src/jktz/raw_metadata.py` to `src/jktz/metadata/raw.py`
- Move: `src/jktz/metadata_errors.py` to `src/jktz/metadata/errors.py`
- Modify: `src/jktz/validation/metadata.py`
- Modify: `tests/test_srv_metadata.py`
- Modify: `tests/test_raw_metadata.py`
- Modify: `tests/test_validation_metadata.py`

- [ ] **Step 1: Change tests to import the target package API**

Use `jktz.metadata.srv`, `jktz.metadata.raw`, and `jktz.metadata.errors`.
Rename `RawReadme` to `RawMetadata`, `parse_raw_readme` to
`parse_raw_metadata`, and `canonical_raw_readme` to `format_raw_metadata`.

- [ ] **Step 2: Run focused tests and verify RED**

Run:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest \
  tests/test_srv_metadata.py \
  tests/test_raw_metadata.py \
  tests/test_validation_metadata.py -q
```

Expected: collection fails because `jktz.metadata` does not exist.

- [ ] **Step 3: Move implementation and update imports**

Preserve serialized output and error messages. Keep the canonical blank lines in
`format_srv_metadata`.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run the command from Step 2. Expected: all focused tests pass.

### Task 2: Add tested atomic file helpers

**Files:**
- Create: `src/jktz/metadata/io.py`
- Create: `tests/test_metadata_io.py`

- [ ] **Step 1: Write failing tests**

Cover atomic replacement, preservation of an existing file mode, no write in
dry-run mode, Latin-1 SRV body-byte preservation, and UTF-8 RAW output.

- [ ] **Step 2: Run tests and verify RED**

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest tests/test_metadata_io.py -q
```

Expected: collection fails because `jktz.metadata.io` does not exist.

- [ ] **Step 3: Implement minimal helpers**

Provide:

```python
def read_srv(path: Path) -> str: ...
def encode_srv(text: str) -> bytes: ...
def atomic_write(path: Path, data: bytes) -> None: ...
```

`encode_srv` rejects non-ASCII metadata before it is combined with the preserved
Latin-1 body. `atomic_write` creates parent directories only when the caller has
already validated the generated document.

- [ ] **Step 4: Run tests and verify GREEN**

Run the command from Step 2. Expected: pass.

### Task 3: Add `srv-set` and `srv-update`

**Files:**
- Modify: `src/jktz/cli/srv_metadata.py`
- Create: `tests/test_srv_metadata_cli.py`

- [ ] **Step 1: Write failing `srv-set` tests**

Test creation, replacement while preserving body bytes, repeated options,
`--dry-run`, and rejection of invalid metadata without changing the file.

- [ ] **Step 2: Run the new tests and verify RED**

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest tests/test_srv_metadata_cli.py -q
```

Expected: argparse rejects the missing `srv-set` command.

- [ ] **Step 3: Implement `srv-set`**

Build `SrvMetadata` through `default_metadata`, serialize it, parse the result
again, then atomically write it unless `--dry-run` was selected.

- [ ] **Step 4: Run `srv-set` tests and verify GREEN**

Run the command from Step 2. Expected: `srv-set` cases pass.

- [ ] **Step 5: Write failing `srv-update` tests**

Test `--update-date`, repeated `--add-processing`, idempotency, required
existing metadata, and dry-run behavior.

- [ ] **Step 6: Implement `srv-update` and verify GREEN**

Parse the current document, copy dictionaries before mutation, validate the
updated serialization, and use the same atomic write path.

### Task 4: Add `raw-set` and retain `hash-raw`

**Files:**
- Modify: `src/jktz/cli/srv_metadata.py`
- Modify: `tests/test_srv_metadata_cli.py`

- [ ] **Step 1: Write failing tests**

Cover canonical UTF-8 README creation, replacement, repeated `--content`,
dry-run behavior, invalid status rejection, and unchanged `hash-raw` output.

- [ ] **Step 2: Run tests and verify RED**

Expected: argparse rejects the missing `raw-set` command.

- [ ] **Step 3: Implement `raw-set`**

Generate with `format_raw_metadata`, validate with `parse_raw_metadata`, and
atomically write UTF-8 bytes unless dry-run is active.

- [ ] **Step 4: Run CLI tests and verify GREEN**

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest tests/test_srv_metadata_cli.py -q
```

Expected: all CLI tests pass.

### Task 5: Connect repository skills and current documentation

**Files:**
- Modify: `.claude/skills/add-cave/SKILL.md`
- Modify: `.claude/skills/svx-to-srv/SKILL.md`
- Modify: `.claude/skills/average-shots/SKILL.md`
- Modify: `CLAUDE.md`
- Modify: `docs/superpowers/specs/2026-06-04-srv-metadata-design.md`
- Modify: `docs/superpowers/specs/2026-06-11-metadata-module-split-design.md`

- [ ] **Step 1: Replace manual helper guidance with exact commands**

Document `uv run jktz-srv-metadata raw-set`, `srv-set`, and `srv-update`.
Examples must use repeatable flags for repeated fields.

- [ ] **Step 2: Update current module references**

Point implementation references to `jktz.metadata.srv`,
`jktz.metadata.raw`, and `jktz.metadata.errors`. Do not rewrite historical
implementation plans.

- [ ] **Step 3: Check documentation consistency**

```bash
rg -n "jktz\\.(srv_metadata|raw_metadata|metadata_errors)|scripts/cli/srv_metadata" \
  src tests .claude CLAUDE.md docs/superpowers/specs
```

Expected: no stale current references.

### Task 6: Run the complete gate and publish the review fix

**Files:**
- All files from Tasks 1-5

- [ ] **Step 1: Run focused and full Python checks**

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest
UV_CACHE_DIR=/private/tmp/uv-cache uv run ruff format --check src scripts tests
UV_CACHE_DIR=/private/tmp/uv-cache uv run ruff check src scripts tests
git diff --check
```

Expected: all commands pass.

- [ ] **Step 2: Run repository validation**

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run jktz-validate
```

Expected: `12/12` validation passes.

- [ ] **Step 3: Commit and push**

Commit the implementation with a focused Polish commit message and push the
current PR branch.

- [ ] **Step 4: Verify GitHub Actions**

Confirm `python-tools`, Linux, Windows, and `pr-release-package` pass.

- [ ] **Step 5: Reply to both review comments**

Explain that the package API was unified and moved under `jktz.metadata`, while
the existing CLI layer was expanded rather than duplicated under
`scripts/cli/`. Include the commands now used by skills and the validation
results, then request review from `pawczak` again.
