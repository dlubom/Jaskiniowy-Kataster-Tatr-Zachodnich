# PR #119 final review fixes design

## Goal

Close the three remaining contract gaps found in the final review of PR #119:

- reject malformed `SOURCE_REF` values before `srv-set` modifies a file;
- ignore Walls block comments while deciding whether active shots have an
  effective `#date` or `#Units DECL=...`;
- reject impossible partial dates such as `YYYY-99`.

## SOURCE_REF validation in the writer

`srv-set` creates a canonical metadata block, so it must reject a value that
the repository validator would reject for lexical or containment reasons. The
shared SRV metadata module will expose a focused validator for `SOURCE_REF`.
Both the CLI and repository path resolver will use it, avoiding two separate
definitions of the `_RAW/NN` suffix rule.

The CLI will validate relative syntax and safe containment under `Poligony`
before writing. It will not require the package directory or README to exist:
skills may generate the SRV and RAW package in separate commands, while the
repository-wide `jktz-validate` gate remains responsible for cross-file
existence checks.

## Walls block comments

The active-shot scanner will track `#[...#]` comment state. Lines inside a
block comment must neither establish orientation state nor count as active
shots. Openers may contain text, as in the existing `#[TODO...` block in
`Harda/DNO.SRV`; a line whose first non-whitespace characters are `#]` closes
the block. The leading metadata block is already removed by the metadata
parser before the scanner runs, so this state concerns only the survey body.

## Partial dates

`SURVEY_DATE` continues to accept `YYYY`, `YYYY-MM`, `YYYY-MM-DD`, and ranges
formed from those values. Full dates use `date.fromisoformat` as before.
Year-month values will be validated by appending day `01`, so month `00` and
months above `12` are rejected without inventing additional date precision.

## Tests and verification

Regression tests will cover invalid CLI `SOURCE_REF` without file mutation,
commented-out `#date`, commented-out nonzero shots, and invalid standalone and
range year-month values. Each test will be observed failing before production
code changes. Final verification includes focused tests, the complete pytest
suite, Ruff, `git diff --check`, and `jktz-validate`.
