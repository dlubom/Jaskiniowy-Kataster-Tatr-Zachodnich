---
name: verify-cave-refactor
description: Compare survey source and compiled geometry before and after a cave or whole-project refactor.
---

Compare source measurements and compiled outputs using the same Survex version,
settings, and explicit input revisions. Read the data contracts in
[AGENTS.md](../../../AGENTS.md).

## References when results differ

Consult [walls.rst](../../../doc/Survex_manual/walls.rst) for known differences
between Walls and Survex, [datafile.rst](../../../doc/Survex_manual/datafile.rst)
for source directives, and [survexport.rst](../../../doc/Survex_manual/survexport.rst)
or [dump3d.rst](../../../doc/Survex_manual/dump3d.rst) for the selected output.
Use [Walls_manual.md](../../../doc/Walls_manual.md) and its original PDF to
resolve native Walls syntax. When comparing the two programs, record the Walls
build as well as the Survex version: different IGRF models can change
date-derived declination even with identical measurements. Reproduce unexplained
behavior on a minimal temporary input before proposing source-data changes.

## Inputs

- `$verify-cave-refactor <cave-prefix>`: compare HEAD with the current working
  tree for one cave, including unstaged changes.
- `$verify-cave-refactor --whole-project`: compare the current branch HEAD with
  the agreed base (normally `origin/master`). This excludes uncommitted changes;
  state that limitation or use a working-tree copy when those changes matter.

Record the exact baseline/candidate SHAs, dirty state, cave prefix, and any
intended station renames or GPS changes before comparing.

## Prepare isolated outputs

Use a fresh temporary directory per run and detached baseline worktrees, e.g.
`git worktree add --detach <temporary-baseline> <base-ref>`. For whole-project
mode, create a second detached candidate worktree. Never stash or reset the
user's checkout to manufacture a baseline.

For a working-tree comparison, compile the current checkout with output directed
to the temporary directory. Keep all generated files outside `_RAW/` and retain
reports outside worktrees scheduled for removal.

Use local Survex or the same `jktz-survex` Docker image for both sides. The
Docker image/build commands are in [docker-exports](../docker-exports/SKILL.md).
Do not regenerate entrance snapshots while comparing: compare the snapshots in
the selected revisions. Separately run `uv run jktz-render-otwory --check` on the
candidate when checking current release readiness. Failure of that online check
is distinct from a comparison of the recorded survey states.

## Compile and export

From each checkout, with a different absolute output stem per side:

```bash
cavern --no-auxiliary-files -o <output-stem> KATASTER.wpj
survexport --csv <output-stem>.3d <output-stem>-stations.csv
```

Capture exit status and logs; do not declare success after a failed compile.
For whole-project exports use `uv run jktz-exports <label> <output-directory>`
in both checkouts. Docker output paths must be bind-mounted to the host.

Parse CSV with a CSV reader. Filter stations by the exact cave prefix plus `:`
(including section prefixes) and sort the records before comparison. Check
headers and actual output precision rather than assuming a column index.

## Compare source and compiled data

1. **Source measurements:** compare the complete measurement multiset after
   any documented station-name mapping, retaining distances, directions,
   inclinations, splays, LRUD, flags, calibration, dates, and units. Compare
   source equates/ties as well as measured legs. Preserve multiplicity: a set
   comparison alone can hide duplicate or lost records.
2. **Station geometry:** without renaming, compare names and coordinates. With
   renaming, apply the explicit name map before comparing. Report maximum
   coordinate differences and export precision. Identical point coordinates
   alone do not establish identical connectivity.
3. **Connectivity:** compare source edges after applying the station map.
   Compiled edge coordinates change with GPS anchoring or loop adjustment, so
   they are not a shift-invariant topology check. If using `dump3d`, inspect its
   actual record format; reconstruct edges from `MOVE`/`LINE` records rather
   than searching for nonexistent `LEG` records. Anonymous/coincident stations
   may prevent an unambiguous graph reconstruction; state the limit.
4. **Whole project:** list caves and named stations added/removed, along with
   per-cave source-leg and export-feature counts. Use shapefile feature counts
   as secondary evidence: one polyline need not equal one survey leg. An
   entrance list alone does not establish the full cave inventory.

Check splays directly in source even if exports omit anonymous station labels.
Counts alone do not detect changed readings. A geometry difference may come
from dates, units, calibration, anchors, or solver behavior, not only changed
measurements. Investigate it before calling the refactor equivalent. Separate
intended GPS shifts/renames from unexplained differences.

## Report and cleanup

Report revisions, scope, source/geometry/connectivity results, compile warnings,
counts, maximum coordinate differences, and any uncovered cases. Link retained
logs/CSV/diffs by absolute path. Claim equivalence only for the checks actually
performed; do not label ambiguous results as “no losses”.

Remove only worktrees created for this comparison after copying reports out.
Do not force removal of a dirty worktree without inspecting its new files.
