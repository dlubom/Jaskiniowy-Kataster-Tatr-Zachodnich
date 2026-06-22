# RAW Metadata Review Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve RAW metadata diagnostics and make the parser boundary tests describe one behavior each.

**Architecture:** Keep parsing and validation behavior unchanged. Treat Polish schema labels as quoted identifiers inside English diagnostics, and separate the heading-boundary assertion from the empty-section validation assertion.

**Tech Stack:** Python 3.11+, pytest, Ruff, uv

---

### Task 1: Specify readable RAW metadata diagnostics

**Files:**
- Modify: `tests/test_raw_metadata.py`
- Modify: `tests/test_srv_metadata_cli.py`
- Modify: `src/jktz/metadata/raw.py`

- [ ] **Step 1: Update tests with exact diagnostic expectations**

Assert these messages through real parser and CLI calls:

```python
"duplicate RAW field 'Status materiału'"
"missing RAW field(s): 'Licencja źródłowa'"
"invalid value for RAW field 'Status materiału': 'uszkodzony'"
"section '## Zawartość' must contain at least one item"
```

- [ ] **Step 2: Run focused tests and verify RED**

Run:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest tests/test_raw_metadata.py tests/test_srv_metadata_cli.py -q
```

Expected: failures show the existing unquoted or grammatically mixed messages.

- [ ] **Step 3: Implement the minimal diagnostic changes**

Use `repr()` formatting for dynamic field names and values, and the literal
quoted section name for the empty-section error:

```python
raise MetadataError(f"{path.as_posix()} duplicate RAW field {name!r}")
quoted_missing = ", ".join(repr(name) for name in missing)
raise MetadataError(f"{path.as_posix()} missing RAW field(s): {quoted_missing}")
raise MetadataError(
    f"{path.as_posix()} invalid value for RAW field 'Status materiału': "
    f"{fields['Status materiału']!r}"
)
raise MetadataError(
    f"{path.as_posix()} section '## Zawartość' must contain at least one item"
)
```

- [ ] **Step 4: Run focused tests and verify GREEN**

Run the focused command from Step 2. Expected: all selected tests pass.

### Task 2: Separate section-boundary and empty-section behavior

**Files:**
- Modify: `tests/test_raw_metadata.py`

- [ ] **Step 1: Rewrite the boundary test**

Construct a README containing one inventory item before `## Uwagi` and another
list item after it. Parse successfully and assert:

```python
assert parsed.content_items == ["`source.xlsx` - arkusz z pomiarami"]
```

- [ ] **Step 2: Add the dedicated empty-section test**

Remove the sole inventory item and assert the exact section error:

```python
with pytest.raises(
    MetadataError,
    match="section '## Zawartość' must contain at least one item",
):
    parse_raw_metadata(Path("_RAW/01/README.md"), text)
```

- [ ] **Step 3: Prove the boundary test detects a regression**

Temporarily disable the `line.startswith("## ")` stop condition, run only the
boundary test, and confirm it fails because the post-heading item is included.
Restore the parser immediately afterward.

- [ ] **Step 4: Run complete verification**

Run:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest -q
UV_CACHE_DIR=/private/tmp/uv-cache uv run ruff check src/jktz/metadata/raw.py tests/test_raw_metadata.py tests/test_srv_metadata_cli.py
UV_CACHE_DIR=/private/tmp/uv-cache uv run ruff format --check src/jktz/metadata/raw.py tests/test_raw_metadata.py tests/test_srv_metadata_cli.py
git diff --check
UV_CACHE_DIR=/private/tmp/uv-cache uv run jktz-validate
```

Expected: pytest passes, Ruff is clean, the diff has no whitespace errors, and
all repository validation checks pass.
