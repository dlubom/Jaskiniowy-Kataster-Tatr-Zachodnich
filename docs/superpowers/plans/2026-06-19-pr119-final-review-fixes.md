# PR #119 Final Review Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the three remaining metadata-contract gaps found in the final review of PR #119.

**Architecture:** Keep reusable validation in `jktz.metadata.srv`, make the CLI validate generated metadata before writing, and extend the measurement scanner with the Walls block-comment state it currently lacks. Preserve the existing separation between single-file CLI validation and repository-wide cross-file existence checks.

**Tech Stack:** Python 3.9+, pathlib, datetime, argparse, pytest, Ruff, uv, Cavern/Survex.

---

## File map

- Modify `tests/test_srv_metadata_cli.py`: lock in pre-write `SOURCE_REF` rejection.
- Modify `tests/test_srv_metadata.py`: lock in invalid partial-date rejection.
- Modify `tests/test_validation_measurements.py`: lock in Walls block-comment semantics.
- Modify `src/jktz/metadata/srv.py`: share `SOURCE_REF` syntax validation and validate year-month values.
- Modify `src/jktz/cli/srv_metadata.py`: validate each generated source reference before writing.
- Modify `src/jktz/validation/measurements.py`: ignore directives and shots inside `#[...#]`.

### Task 1: Reject malformed SOURCE_REF before writing

- [ ] Add `test_srv_set_rejects_invalid_source_ref_without_modifying_file` to `tests/test_srv_metadata_cli.py` by replacing `_RAW/01` in `_srv_set_args`, then asserting exit code 1, unchanged bytes, and `must end with _RAW/NN` on stderr.
- [ ] Run `UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest tests/test_srv_metadata_cli.py::test_srv_set_rejects_invalid_source_ref_without_modifying_file -q`; expect failure because the current result is 0.
- [ ] Add this reusable validator to `src/jktz/metadata/srv.py` and call it at the start of `resolve_source_ref`:

```python
def validate_source_ref(value: str) -> str:
    normalized = posixpath.normpath(value)
    parts = normalized.split("/")
    if len(parts) < 2 or parts[-2] != "_RAW" or not re.fullmatch(r"\d{2}", parts[-1]):
        raise MetadataError(f"SOURCE_REF {value!r} must end with _RAW/NN")
    if normalized.startswith("/"):
        raise MetadataError(f"SOURCE_REF {value!r} must be relative")
    return normalized
```

- [ ] In `src/jktz/cli/srv_metadata.py`, find the nearest `Poligony` ancestor of the target or fall back to the target parent, then call `resolve_source_ref` for each generated source reference before rendering. Do not check filesystem existence.
- [ ] Run `UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest tests/test_srv_metadata_cli.py tests/test_srv_metadata.py -q`; expect all focused tests to pass.

### Task 2: Respect Walls block comments

- [ ] Add `test_active_shot_scanner_ignores_date_inside_block_comment` with `#[ disabled\n#date 2004-06-19\n#]\n0 1 1.0 90 0`; expect `False`.
- [ ] Add `test_active_shot_scanner_ignores_shots_inside_block_comment` with `#[ deferred\n0 1 1.0 90 0\n#]`; expect `True`.
- [ ] Run `UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest tests/test_validation_measurements.py -q`; expect both new tests to fail for opposite reasons.
- [ ] In `has_dated_or_declared_active_shots`, track `in_block_comment`; detect a stripped line beginning with `#[`, ignore all content until a stripped line beginning with `#]`, and process neither directives nor shot tokens while the flag is set.
- [ ] Run `UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest tests/test_validation_measurements.py -q`; expect all measurement tests to pass.

### Task 3: Validate partial calendar dates

- [ ] Add a parametrized `test_rejects_impossible_partial_dates` to `tests/test_srv_metadata.py` for `2004-00`, `2004-13`, and `2004-06/2004-99`, replacing the valid `SURVEY_DATE` in `VALID_BLOCK` and expecting `MetadataError`.
- [ ] Run `UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest tests/test_srv_metadata.py::test_rejects_impossible_partial_dates -q`; expect three failures because the values are currently accepted.
- [ ] In `_is_valid_contract_date`, when `value.count("-") == 1`, call `date.fromisoformat(f"{value}-01")` and return `False` on `ValueError`; preserve the existing full-date path.
- [ ] Run `UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest tests/test_srv_metadata.py -q`; expect all SRV metadata tests to pass.

### Task 4: Final verification

- [ ] Run `UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest -q` and require zero failures.
- [ ] Run Ruff format and lint checks over `src scripts tests`.
- [ ] Run `git diff --check`.
- [ ] Run `UV_CACHE_DIR=/private/tmp/uv-cache uv run jktz-validate` and require 12/12 steps.
- [ ] Review `git diff` and confirm no unrelated files changed.
