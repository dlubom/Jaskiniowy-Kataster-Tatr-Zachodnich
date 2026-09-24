---
name: add-cave
description: Add a cave from source surveys, register its entrance through the GPS template, and create canonical SRV and RAW metadata.
---

Add a new cave to the kataster project.

Read the inputs from the user request; ask only for required values that cannot be established from the repository or supplied sources.
Expected format: `<cave-id> "<valley/subdir/path>" [/path/to/source.zip]`
Example: `$add-cave T.D-08.07 "D_Koscieliska/Organy" /tmp/MROZN.SRV.zip`

---

## Step 1 — Look up cave data in PIG database (single call)

The cave ID is ASCII — search for it directly with a fixed-string search:

```bash
rg -F '"<cave-id>"' doc/jaskinie_polski_pig_dump.jsonl
```

Parse the returned JSON for:
- `name` → CAVE_NAME (use ASCII equivalents for diacritics: ą→a, ć→c, ł→l, ó→o, ś→s, ź/ż→z, ę→e, ń→n)
- `latitude`, `longitude`, `absolute_height_masl` → archival location context; not the active GPS fix
- `other_names`, `authors_of_study`, `editorial` → inventory context. These fields do not establish authorship of the supplied survey; derive survey team/date from the actual sources.

If not found by ID, try searching by partial ASCII name.

## Step 2 — Identify the entrance and GPS object

Active entrance fixes come from the published `best-measurements.csv` in
`dlubom/gps-kataster-obiektow-tatr`, through `gps_fix(...)` in
`Poligony/OTWORY.SRV.j2`. Establish the GPS `object_id` and the corresponding
survey station from source evidence. Do not replace these with PIG coordinates
or a station inferred from a convenient geometric fit.

Read any supplied GNSS/source coordinates as provenance. If the object mapping
or entrance station cannot be established, report the missing information and
leave registration incomplete; do not invent a fix or an anchor shot.

## Step 3 — Determine directory path

Valley path from arguments (use ASCII, no diacritics in directory names):
`Poligony/<valley-path>/<Cave_Directory_ASCII>/`

Check if the valley subdirectory already exists. Match the style of neighbouring caves in that directory.

## Step 4 — Handle source files

If a source ZIP was provided:
1. Extract: `unzip -o <source.zip> -d /tmp/<cave_ascii>_raw/`
2. List contents: `find /tmp/<cave_ascii>_raw -not -path "*/__MACOSX*" -type f`
3. Read each survey file to understand its format (units, station naming, number of readings)

**If the source files are in Survex format (`.svx` files):** use the `$svx-to-srv` skill to perform the conversion before proceeding to Step 9. The skill handles measurement conversion, equate→zero-shot mapping, splay shots, declination, and the critical issue of junction stations positioned only by duplicate shots. Skip the manual survey-file skeleton in Step 9 — the skill produces all section `.SRV` files directly.

## Step 5 — Create directory structure

```bash
mkdir -p "Poligony/<valley-path>/<Cave_Directory_ASCII>/_RAW/01"
```

Copy source files to `_RAW/01/` preserving original names (never rename raw files):
```bash
cp /tmp/<cave_ascii>_raw/<file> "Poligony/<valley-path>/<Cave_Directory_ASCII>/_RAW/01/"
```

## Step 6 — Create `_RAW/01/README.md`

Use the metadata CLI instead of composing the README manually:

```bash
uv run jktz-srv-metadata raw-set \
  "Poligony/<valley-path>/<Cave_Directory_ASCII>/_RAW/01/README.md" \
  --title "<Cave Name ASCII> - paczka zrodlowa 01" \
  --status "dostępny" \
  --origin "<origin / who provided the data>" \
  --authors "<confirmed survey authors from source evidence or nieznane>" \
  --dates "<confirmed survey dates from source evidence or nieznane>" \
  --acquired "<date obtained or nieznane>" \
  --added-by "<person who added files or nieznane>" \
  --license-value "<source license or nieznane>" \
  --completeness "<completeness notes>" \
  --content '`<file>` - <one-line description>'
```

Repeat `--content` for every source file or directory. Leave genuinely unknown
fields as `nieznane`. If no raw material is available, use
`--status "niedostępny"` and
`--content "Brak materiałów źródłowych."`.

## Step 7 — Determine station prefix

See the **Prefix Convention** section in [`AGENTS.md`](../../../AGENTS.md) for the rules (CamelCase including short prepositions, single-section vs multi-section patterns, `#prefix2` for cave systems, scope rules).

For a typical single-section cave: cave name in CamelCase, no spaces, no diacritics (e.g. `Mrozna`, `MietusiaWyznia`).

## Step 8 — Update the entrance template and render the snapshot

Add this block in cave-prefix order to `Poligony/OTWORY.SRV.j2`:

```
{{ gps_fix('<PREFIX>:<STATION>', '<OBJECT-ID>') }}
#flag   <PREFIX>:<STATION>   /<Cave Label>
#flag   <PREFIX>:<STATION>   /ENTRANCE
#note   <PREFIX>:<STATION>   /<Cave Label>
```

Use the fully qualified station name, e.g. `Marmurowa:0` or
`WielkaSniezna:Ciag:0`. Confirm it exists in the survey network.
Run `uv run jktz-render-otwory`, inspect the complete diff, and include both
the template and generated `Poligony/OTWORY.SRV` snapshot in the change.
Do not edit the generated snapshot directly. Missing GPS rows are errors.

## Step 9 — Create the survey file (`CAVE.SRV` or `CAVE_<SECTION_SHORTNAME>.SRV`)

First create the Walls body without a hand-written metadata block:

```
#prefix <PREFIX>
#units meters order=DAV
#units A=D V=D
; do NOT add #units DECL= when #date is present — declination derives from #date (see AGENTS.md);
; use #units DECL=X.X instead of #date only when the file has no reliable date
#date <YYYY-MM-DD>

;<Section description>

;FROM   TO      DISTANCE    AZIMUTH     INCLINATION
0       1       4.61        293         2
1       2       2.06        303         7

;Splay shots (cross-sections)

0       -       5.52        51          8
0       -       5.47        265         76
```

Then atomically prepend the validated metadata block:

```bash
uv run jktz-srv-metadata srv-set \
  "Poligony/<valley-path>/<Cave_Directory_ASCII>/<CAVE_FILE>.SRV" \
  --cave-id "T.X-NN.MM" \
  --cave-name "<Cave Name ASCII>" \
  --survey-id "<SURVEY_ID>" \
  --survey-name "<Survey name>" \
  --source-ref "_RAW/01" \
  --update-date "<YYYY-MM-DD>" \
  --processing "utworzono aktywny plik SRV z materialow zrodlowych"
```

Repeat `--source-ref`, `--team`, `--instrument`, `--survey-date`, and
`--processing` when multiple values exist. Optional descriptive values default
to `nieznane`. `SURVEY_ID` and `SURVEY_NAME` cannot be `nieznane`.
`SOURCE_REF` must point to an existing `_RAW/NN` package README. Do not use
`DATA_SOURCE` in active `.SRV`; preserve source provenance in the RAW README.
Use `--dry-run` to inspect the complete file without writing it.

For confirmed repeated instrument readings, use `$average-shots` on a working copy. Keep independent surveys separate. If the grouping is unknown, document it without inventing measurements:
```
; TODO: przetworzyc pomiary z _RAW/01/<filename>
; Plik zrodlowy zawiera pomiary potrojne — wymagaja usrednienia lub konwersji.
; Stacje numerowane od <first-station> — numer stacji otworu nieznany.
```

## Step 10 — Update KATASTER.wpj

**Close Walls if it has this project open before editing it.** Walls overwrites the .wpj file when it saves, discarding any manually added entries.

Find the correct `.BOOK` parent in KATASTER.wpj. The path hierarchy corresponds to the directory structure:
- Each `.BOOK` with `.PATH <dir>` builds the cumulative path from the project root
- Surveys without their own `.PATH` inherit the parent book's path

Insert a new `.BOOK` block for the cave in the correct location.

Convention (drop the `Jaskinia` prefix from cave names everywhere):

- `<CaveName>` — cave name without the `Jaskinia` prefix (e.g. `Marmurowa`). Used for `.BOOK`, `.PATH`, and as the prefix in `.SURVEY` display names.
- `<CAVE_SHORT_ID>` — 3–8 char UPPERCASE dataset ID, unique within the project (e.g. `MARMUR`).
- `<SECTION_SHORTNAME>` — short section code (e.g. `OT`, `KK`, `ME`, `DU`). Omit for a single-survey cave.

Template — one `.SURVEY` block per `.SRV` file in the cave directory:

```
.BOOK	<CaveName>
.NAME	<CAVE_SHORT_ID>
.PATH	<CaveName>
.STATUS	8
.SURVEY	<CaveName> <section description>
.NAME	<CAVE_SHORT_ID>_<SECTION_SHORTNAME>
.STATUS	8
.ENDBOOK
```

For a single-survey cave drop ` <section description>` from `.SURVEY` and `_<SECTION_SHORTNAME>` from `.NAME`.

Concrete example — Marmurowa (multi-section):

```
.BOOK	Marmurowa
.NAME	MARMUR
.PATH	Marmurowa
.STATUS	8
.SURVEY	Marmurowa otwor - Piaskownice II
.NAME	MARMUR_OT
.STATUS	8
.SURVEY	Marmurowa Komin KKTJ
.NAME	MARMUR_KK
.STATUS	8
.ENDBOOK
```

Apply a focused, encoding-preserving edit with enough surrounding context to identify the parent book uniquely.
Verify with: `grep -n "<CAVE_SHORT_ID>" KATASTER.wpj`

## Step 11 — Validate and document

Update `LISTA_JASKIN.md` and add a short entry under `Unreleased` in
`CHANGELOG.md`. Run `uv run jktz-validate` (or `$docker-validate`) and review
metadata, source preservation, entrance mappings, and compile warnings.
Commit/push only when included in the user request.

## Summary

Report to the user:
- Files created (list all paths)
- Data filled in vs left as TODO/unknown
- Any fields needing manual follow-up (entrance station, instrument, who added raw files)
- Reminder: if Walls was open, it may overwrite the .wpj entry — check after reopening
