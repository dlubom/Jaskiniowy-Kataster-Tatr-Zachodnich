---
---
name: verify-cave-refactor
description: Verify that a refactor of cave SRV files (file split, prefix rename, formatting changes) did not alter the survey topology or coordinates. Compiles the project before and after the change, exports station coordinates for the named cave, and diffs them.
argument-hint: <cave-prefix>
---

Verify that a refactor preserved survey data for a single cave.

Arguments: $ARGUMENTS
Expected format: `<cave-prefix>` — the `#prefix` value used by the cave (e.g. `Marmurowa`, `MietusiaWyznia`, `WielkaSniezna`).

Use after refactors that **should not change the survey itself** — splitting a single SRV into multiple files, renaming `#prefix` values, renaming stations, reorganising `#units` directives, removing duplicate metadata, etc. The output of `cavern` should be bit-identical for the named cave's stations (modulo station names if they were intentionally renamed).

---

## Flow

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

## Output location

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

## Caveats

- Splay shots (`to = -`) do not appear in the `.3d` file. If the refactor touched splay-shot lines, the CSV diff will not catch the change — sanity-check splay counts separately (e.g. `grep -c $'\t-\t' Poligony/.../*.SRV` before and after).
- The diff must be empty for a *pure* refactor. Any coordinate difference means a real shot was added, removed, or altered — investigate before committing.
- Sort the output before diffing; cavern does not guarantee a stable station order between runs.

## Reporting

Show the user:
- Which diff variant was run (coords / full / legs) and whether the diff was empty (refactor confirmed safe) or non-empty (lines that differ)
- Station count before vs after (`wc -l` on each filtered CSV) — should match for pure refactors
- Leg count before vs after (if the legs check was run) — should match for pure refactors
- Any cavern errors or new warnings introduced by the refactor
