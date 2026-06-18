# PR #119 review follow-up design

## Goal

Address the three review findings without weakening the SRV and RAW metadata
contract:

- make metadata validation tests independent of the host text encoding;
- ensure Windows CI executes the Python test suite;
- remove the unused compatibility wrapper `scripts/srv_metadata.py`;
- allow ignored, untracked build artifacts under `_RAW` while continuing to
  reject repository material left outside numbered packages.

## Windows test coverage

Every text fixture in `tests/test_validation_metadata.py` will use an explicit
encoding. UTF-8 is appropriate for RAW README fixtures because they contain
Polish metadata labels. Active SRV fixtures will also name their encoding so
their behavior does not depend on the operating-system locale.

The existing Windows validation job will run the complete pytest suite after
`uv sync --locked` and before installing Survex and GDAL. The Ubuntu
`python-tools` job remains responsible for Ruff, pytest, and the rendered
entrance snapshot. This adds Windows portability coverage without duplicating
the Ubuntu tooling job.

## CLI entry point

Delete `scripts/srv_metadata.py`. All current repository instructions and
skills invoke the installed `jktz-srv-metadata` entry point declared in
`pyproject.toml`; the wrapper has no active consumer. Historical design and
plan documents remain unchanged because they describe earlier implementation
decisions.

## Git-aware RAW validation

The RAW layout validator will distinguish repository content from local build
artifacts:

- candidates directly under `_RAW` remain invalid by default;
- a candidate is skipped only when Git reports it as ignored and untracked;
- tracked files remain subject to validation even when their names match a
  `.gitignore` pattern;
- outside a Git worktree, validation retains its current strict behavior.

The implementation will ask Git for ignored candidates in one batch rather
than starting one process per path. Git failures other than "not ignored" or
"not in a worktree" will not silently weaken validation.

This rule is deliberately based on Git state rather than hard-coded Survex
extensions. It therefore follows the repository's `.gitignore` contract and
also handles ignored directories or future generated-file patterns.

## Tests

Regression coverage will prove that:

1. metadata validation fixtures are written with explicit encodings;
2. an ignored, untracked generated file directly under `_RAW` does not fail
   validation;
3. the same path, when force-added to Git, is still rejected as misplaced
   repository material;
4. existing rejection of ordinary loose material remains unchanged;
5. the Windows workflow runs pytest.

Verification will include the focused metadata tests, the full pytest suite,
Ruff, `git diff --check`, and the repository-wide `jktz-validate` gate.
