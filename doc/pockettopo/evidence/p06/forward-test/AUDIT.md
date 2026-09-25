# Independent forward test of pockettopo-convert

Evidence was copied here from the original temporary workspace. The package, hashes and command logs below are retained in this directory.

Workspace: `/private/tmp/p06-forward-5pvz9E`. All written artifacts are here. No repository/source changes were made by the tester. Skill routing succeeded without implementation source, PRD/P06 evidence or prior discussion.

Source SHA-256: `52e16f9561f2fbf3b66e595c29fce113c9ed1cc44fc5865897cb5f06b1aaba94` (unchanged).
Renderer: resvg 0.48.1, binary SHA-256 matches documented macOS digest. Compilers: cavern/dump3d 1.4.22.

## Commands and outcomes

Executed from `/Users/dariuszlubomski/proj/Jaskiniowy-Kataster-Tatr-Zachodnich`, with `PYTHONDONTWRITEBYTECODE=1` and `UV_CACHE_DIR=/private/tmp/p06-forward-5pvz9E/uv-cache`:

- `/private/tmp/p01-resvg/macos/resvg --version` — exit 0 (resvg-version)
- `cavern --version` — exit 0 (cavern-version)
- `dump3d --version` — exit 0 (dump3d-version)
- `uv run --no-sync jktz-pockettopo inspect /Users/dariuszlubomski/proj/Jaskiniowy-Kataster-Tatr-Zachodnich/doc/pockettopo/evidence/repeat-candidates/okna/okna.top` — exit 0 (inspect)
- `uv run --no-sync jktz-pockettopo convert /Users/dariuszlubomski/proj/Jaskiniowy-Kataster-Tatr-Zachodnich/doc/pockettopo/evidence/repeat-candidates/okna/okna.top --output /private/tmp/p06-forward-5pvz9E/package --resvg /private/tmp/p01-resvg/macos/resvg` — exit 2 (convert)
- `uv run --no-sync jktz-pockettopo convert /Users/dariuszlubomski/proj/Jaskiniowy-Kataster-Tatr-Zachodnich/doc/pockettopo/evidence/repeat-candidates/okna/okna.top --output /private/tmp/p06-forward-5pvz9E/package --resvg /private/tmp/p01-resvg/macos/resvg` — exit 1 (reuse-existing-output)
- `uv run --no-sync jktz-pockettopo inspect /Users/dariuszlubomski/proj/Jaskiniowy-Kataster-Tatr-Zachodnich/doc/pockettopo/evidence/repeat-candidates/okna/okna.top` — exit 0 (inspect-after-parent-wording-fix)

## Conversion result

`package/` contains exactly 12 files. All 11 manifest hashes match actual files; the audit separately hashes the report too. The returned code 2 is a published audit package, not CLI failure. There are 14 source shots and 14 trace entries: 13 active exports, one held record (index 0, `zero_unnamed_shot`, missing trip). No repeat confirmation, correction override, exclusion, date or CRS was invented. Stored explicit zero correction was reproduced. All readings remain singleton groups.

Both SRV and SVX compile without warnings through Survex, with the expected five named stations, four compiler-combined named edges and one splay; format geometry agrees with max station delta 0.0 m. This is not a Walls runtime test. `conversion_complete=false` and `drawing_overlay_complete=false`; drawing notices are `held_source_shots_not_projected` and `unadjusted_closure`.

## Four PNG visual checks

All four PNG were opened with view_image. Nonempty black source sketches are preserved on white; measurement variants show magenta survey/stations, cyan splay, readable labels and red CHECK OVERLAY. No visible clipping. The plan 2.1 branch extends beyond the drawn passage and is preserved. Side is an extended section, not a geographic elevation. No printed scale bar/axis/north arrow is provided: the report supplies x-right/y-down and effective scales 39.9146, 39.9458, 40.0 and 39.9768 px/m. Independent first-leg trigonometry agrees with reported plan/side endpoints within 1e-8 mm. Actual PNG dimensions match all report viewports.

## Collision and integrity

Reusing the same output target returns code 1 with `Output already exists (collision policy: error)`. Every one of the 12 previous file sizes and hashes remains identical; source hash is unchanged. No deletion or overwrite was attempted.

## Usability finding and recheck

Initial inspect output included stale wording saying sketches/CLI/package remain P05/P06. The parent corrected this wording, and a subsequent inspect-only run verifies the new inspection-only limitation. The decoded source, groups, record trace and trips remain identical. The original inspect output is retained as `inspect.stdout`; recheck is `inspect-after-fix.stdout`. No conversion rerun was necessary and the existing package still has identical hashes.

Detailed commands, per-file hashes, all checks, viewports and visual notes are in `audit.json`; stdout/stderr are retained separately. The temporary audit helpers are not shipped as project tooling; the retained JSON and package support independent readback.
