---
---
name: verify-cave-refactor
description: Verify that a refactor did not lose cave data. Two modes — (a) single cave HEAD vs WIP for a local refactor, (b) whole project current-branch vs master for a branch-level refactor (e.g. OTWORY GPS render).
argument-hint: <cave-prefix> | --whole-project
---

Verify that a refactor preserved survey data.

Arguments: $ARGUMENTS

Two modes:

- **Single-cave mode** — argument is a `#prefix` value (`Marmurowa`, `MietusiaWyznia`, `WielkaSniezna`, …). Compares HEAD-without-WIP against HEAD-with-WIP, filtered to one cave. Use after refactors that *should not change the survey itself* — splitting a single SRV into multiple files, renaming `#prefix` values, renaming stations, reorganising `#units` directives, removing duplicate metadata, etc. The output of `cavern` should be bit-identical for the named cave's stations (modulo station names if they were intentionally renamed).
- **Whole-project mode** — argument is `--whole-project`. Compares the current branch's HEAD against `master`'s HEAD across **every** cave, using the release-pipeline outputs (`.3d`, station CSV, per-cave shapefiles). Use after branch-level changes that touch many caves at once — e.g. the OTWORY-from-GPS render refactor. Reports loss-focused stats: caves dropped, stations dropped, legs dropped, shapefile feature deltas.

Dispatch on the argument: if it starts with `--whole-project`, run [Whole-project mode](#whole-project-mode-branch-vs-master); otherwise treat it as a cave prefix and run [Single-cave mode](#single-cave-mode-head-vs-wip).

---

## Single-cave mode (HEAD vs WIP)
<a id="single-cave-mode-head-vs-wip"></a>

### Flow

The verification compares the compiled output **before** and **after** the refactor. Use a **`git worktree`** for the baseline:

1. **Create a baseline worktree.** `git worktree add <host-tmp>/verify-cave-refactor/<cave-prefix>/baseline HEAD --detach`. This is a read-only second checkout of the repo at the last committed state, in a separate directory. The user's main checkout (with WIP applied) is untouched.
2. **Compile and export "before"** inside the worktree. Mount the worktree path as `/project` in the `jktz-survex` container, run `cavern KATASTER.wpj`, then `survexport --csv KATASTER.3d` to dump every station's coordinates. Filter to the cave by prefix, sort, and write to `before.csv` in the persistent output directory (see below).
3. **Compile and export "after"** in the main checkout (the user's working tree, WIP applied). Same compile + export + filter + sort, written to `after.csv` in the same directory.
4. **Diff the two exports.** Pick the variant that matches the kind of change:
   - **Pure rename refactor** (station names changed): compare only coordinate columns — `diff <(cut -d, -f1-3 before.csv | sort) <(cut -d, -f1-3 after.csv | sort)`. Empty diff = same set of 3D points = geometry preserved.
   - **No-rename refactor** (file split, formatting): compare the full sorted lines — `diff <(sort before.csv) <(sort after.csv)`. Empty diff = identical output including names.
   - **Legs-only / strict graph check** (truest topology test, ignores station names *and* coordinate fix-point shifts): export the network's edges with `dump3d KATASTER.3d`, filter to `LEG` lines, drop station names, sort, then diff. Each leg appears as its two endpoint coordinates — two surveys with the same edge set are topologically identical regardless of how stations are labelled or how loop-closure adjustments distributed around a loop. Useful when the simpler coord-only diff shows tiny shifts and you want to confirm whether the underlying graph actually changed.

   Run all three if unsure — they answer slightly different questions.

5. **Remove the baseline worktree** when finished: `git worktree remove <host-tmp>/verify-cave-refactor/<cave-prefix>/baseline`. The exported CSV / leg files stay in the output directory for further investigation.

Run both compiles in the same Docker image (`jktz-survex`) and same shell session so the only variable is the source files.

### Output location

Write all exports to a stable, host-side directory so the files survive after the verification finishes and can be re-inspected later:

```
<host-tmp>/verify-cave-refactor/<cave-prefix>/before.csv
<host-tmp>/verify-cave-refactor/<cave-prefix>/after.csv
<host-tmp>/verify-cave-refactor/<cave-prefix>/before-legs.txt   ; only if the legs check is run
<host-tmp>/verify-cave-refactor/<cave-prefix>/after-legs.txt
```

`<host-tmp>` is `/tmp` on Linux/macOS and `$env:TEMP` on Windows. Inside Docker, mount this path as an extra volume so the container can write to it and the user can open the files afterwards:

```
-v "<host-tmp>/verify-cave-refactor:/output"
```

Then have the container script write the export files under `/output/<cave-prefix>/`. Do not use the container's own `/tmp` — it is discarded when the container exits.

After the diff, tell the user the absolute paths to all four files so they can grep / open them for further investigation.

### Caveats

- Splay shots (`to = -`) do not appear in the `.3d` file. If the refactor touched splay-shot lines, the CSV diff will not catch the change — sanity-check splay counts separately (e.g. `grep -c $'\t-\t' Poligony/.../*.SRV` before and after).
- The diff must be empty for a *pure* refactor. Any coordinate difference means a real shot was added, removed, or altered — investigate before committing.
- Sort the output before diffing; cavern does not guarantee a stable station order between runs.

### Reporting

Show the user:
- Which diff variant was run (coords / full / legs) and whether the diff was empty (refactor confirmed safe) or non-empty (lines that differ)
- Station count before vs after (`wc -l` on each filtered CSV) — should match for pure refactors
- Leg count before vs after (if the legs check was run) — should match for pure refactors
- Any cavern errors or new warnings introduced by the refactor

---

## Whole-project mode (branch vs master)
<a id="whole-project-mode-branch-vs-master"></a>

Compare the current branch against `master` across the whole project, with the loss question front-and-centre: **did the refactor drop any caves, stations, or legs?**

The branch-level refactor covered by this mode keeps `Poligony/OTWORY.SRV` as
a versioned snapshot rendered from GPS data. To get a
meaningful comparison, the skill verifies that the current-branch snapshot
matches the latest GPS release before compiling. The check needs internet
because it downloads the latest release asset from
`dlubom/gps-kataster-obiektow-tatr`.

### Flow

Both checkouts run in separate `git worktree`s so the user's working tree is never modified.

1. **Build the image if needed.**
   ```bash
   docker images -q jktz-survex | grep -q . || docker build -f docker/Dockerfile.survexImage-release -t jktz-survex .
   ```

2. **Create both worktrees.**
   ```bash
   OUTROOT="<host-tmp>/verify-cave-refactor/whole-project"
   mkdir -p "$OUTROOT"
   git worktree add "$OUTROOT/master"  master  --detach
   git worktree add "$OUTROOT/branch" HEAD    --detach
   ```

3. **Check OTWORY in the branch worktree.** Run from inside the branch worktree, with its own `.venv` so the host environment is untouched:
   ```bash
   ( cd "$OUTROOT/branch" && uv sync --locked && uv run jktz-render-otwory --check )
   ```
   If this fails (no network, missing asset, missing `object_id` mapping, or a stale snapshot), stop and report — the comparison would be meaningless without it. Do **not** render in the master worktree; master uses the `OTWORY.SRV` it ships with.

4. **Run the release export pipeline in both worktrees.** Same image, same console script, same version label per side:
   ```bash
   docker run --rm -v "$OUTROOT/master:/project"  jktz-survex uv run jktz-exports master  exports
   docker run --rm -v "$OUTROOT/branch:/project" jktz-survex uv run jktz-exports branch exports
   ```
   Each side produces `exports/JKTZ-{master,branch}.3d`, `.dxf`, `-all.shp`, plus `exports/caves/<cave>.shp` for every cave.

5. **Generate station + entrance CSVs** from the compiled `.3d` (the shapefile contains legs only — for "stations lost" we need the station list directly):
   ```bash
   docker run --rm -v "$OUTROOT/master:/project" jktz-survex bash -c \
     "survexport --csv         exports/JKTZ-master.3d  exports/JKTZ-master-stations.csv && \
      survexport --entrances   --csv exports/JKTZ-master.3d  exports/JKTZ-master-entrances.csv"
   # …same for branch…
   ```
   Copy the resulting CSVs and the `caves/` shapefile directories out of each worktree into `$OUTROOT/` so they survive worktree removal:
   ```
   $OUTROOT/master-stations.csv   $OUTROOT/branch-stations.csv
   $OUTROOT/master-entrances.csv  $OUTROOT/branch-entrances.csv
   $OUTROOT/master-caves/         $OUTROOT/branch-caves/   (per-cave .shp/.dbf/.shx)
   $OUTROOT/master-all.shp + sidecars   $OUTROOT/branch-all.shp + sidecars
   ```

6. **Compute the loss summary.** Use station-name set diffs as the primary signal; shapefile feature counts as a secondary cross-check.

   - **Caves dropped.** Extract the cave prefix (substring before the first `:` of column 4 in the entrances CSV) on each side, sort-unique, then `comm -23 master-caves.txt branch-caves.txt`. Any cave on the left is missing from the branch — a hard regression.
   - **Stations dropped.** From each `*-stations.csv`, take column 4 (full station name), sort-unique. `comm -23` again — stations on master but not on branch. Group by cave prefix when reporting.
   - **Legs dropped.** Run `dump3d` on each `.3d`, filter `^LEG`, normalise (drop station labels — keep only the two endpoint coords sorted within the line and across the file), then `comm -23`. Catches legs lost even when both endpoints survive.
   - **Per-cave shapefile feature deltas.** For each cave `C` present on master, run `ogrinfo -so -al $OUTROOT/master-caves/C.shp` and `… branch-caves/C.shp`, parse the `Feature Count:` line, and flag any cave where the count dropped. (Shapefile features here are leg polylines from the per-cave DXF, so this is a leg-level sanity check at the cave granularity.)

7. **Remove the worktrees** when finished (export artefacts are already copied out into `$OUTROOT`):
   ```bash
   git worktree remove "$OUTROOT/master"
   git worktree remove "$OUTROOT/branch"
   ```

### Output location

Same `<host-tmp>` convention as single-cave mode (`/tmp` on Linux/macOS, `$env:TEMP` on Windows). Final artefacts in `<host-tmp>/verify-cave-refactor/whole-project/`:

```
master-stations.csv      branch-stations.csv
master-entrances.csv     branch-entrances.csv
master-caves/<cave>.shp  branch-caves/<cave>.shp     (+ .dbf .shx .prj sidecars)
master-all.shp           branch-all.shp              (+ sidecars)
caves-lost.txt           stations-lost.txt           legs-lost.txt
per-cave-feature-deltas.txt
```

Tell the user the absolute paths so they can inspect anything flagged.

### Caveats

- The snapshot check needs internet and a GPS-coordinate row for every cave in `OTWORY.SRV.j2`. If the check fails, the comparison is not done — surface the renderer's error directly rather than continuing with stale OTWORY.
- Coordinate **shifts** in the branch output are *expected* (the whole point of the refactor is to update entrance coordinates from GPS). The report should NOT flag those as losses — only flag missing names / missing rows.
- Splay shots are still invisible to `.3d` and shapefiles. Splay loss isn't covered by this mode; check `_RAW/` or grep splay counts separately if you suspect it.
- The release pipeline is slow (cavern + DXF + one shapefile per cave). The first build of `jktz-survex` from scratch adds several minutes on top.

### Reporting

Loss-focused, single-screen summary:

- **Caves**: master = N, branch = M, dropped = list (truncate to ~5 with "+X more")
- **Stations**: master = N, branch = M, dropped = list-by-cave (truncate)
- **Legs**: master = N, branch = M, dropped = N (per-cave breakdown if any)
- **Per-cave shapefile feature deltas**: list only caves with non-zero delta
- **cavern log diff**: any new `error:` or `warning:` lines on the branch side that aren't on master
- **Verdict**: "no losses" or "losses detected" — followed by the paths under `$OUTROOT`
