---
name: add-cave
description: Add a new cave to the Jaskiniowy Kataster Tatr Zachodnich project. Creates the full directory structure, SRV files, _RAW/ folder, and KATASTER.wpj entry.
argument-hint: <cave-id> <valley-path> [source-zip]
---

Add a new cave to the kataster project.

Arguments: $ARGUMENTS
Expected format: `<cave-id> "<valley/subdir/path>" [/path/to/source.zip]`
Example: `/add-cave T.D-08.07 "Dolina Koscieliska/Organy" /tmp/MROZN.SRV.zip`

---

## Step 1 — Look up cave data in PIG database (single call)

The cave ID is ASCII — search for it directly with a single grep:

```bash
grep '"<cave-id>"' doc/jaskinie_polski_pig_dump.jsonl
```

Parse the returned JSON for:
- `name` → CAVE_NAME (use ASCII equivalents for diacritics: ą→a, ć→c, ł→l, ó→o, ś→s, ź/ż→z, ę→e, ń→n)
- `latitude`, `longitude`, `absolute_height_masl` → entrance coordinates
- `other_names`, `authors_of_study`, `editorial` → for README and metadata

If not found by ID, try searching by partial ASCII name.

## Step 2 — Determine coordinates (coordinate source priority)

**Always use decimal degrees** for `#fix` (preferred format, per project convention).

### Which coordinates to use?

Coordinate sources in order of preference:
1. **GPS from `_RAW/` source files** — most accurate if the survey team recorded GPS readings in their original data. Check source files for GPS stations, `*fix`, or coordinate blocks. If found, use these.
2. **PIG dump** (`latitude`, `longitude`, `absolute_height_masl`) — official registry data; good fallback. Already in decimal degrees — round to 6 decimal places.
3. **Ask the user** — if neither source has reliable coords, ask the user to provide them.

**Ask the user explicitly:** after reading the `_RAW/` files, ask: "Do the source files contain GPS coordinates? If yes, which station and what values?" This matters because survey-measured GPS is more accurate than the PIG registry, and the `#fix` station must match the actual survey network.

Format: `E<lon>  N<lat>` (decimal degrees, 6 decimal places)
Example: `E19.898750  N49.246611  1270.0m`

## Step 3 — Determine directory path

Valley path from arguments (use ASCII, no diacritics in directory names):
`Jaskinie-poligony/<valley-path>/<Cave Name ASCII>/`

Check if the valley subdirectory already exists. Match the style of neighbouring caves in that directory.

## Step 4 — Handle source files

If a source ZIP was provided:
1. Extract: `unzip -o <source.zip> -d /tmp/<cave_ascii>_raw/`
2. List contents: `find /tmp/<cave_ascii>_raw -not -path "*/__MACOSX*" -type f`
3. Read each survey file to understand its format (units, station naming, number of readings)

**If the source files are in Survex format (`.svx` files):** use the `/svx-to-srv` skill to perform the conversion before proceeding to Step 9. The skill handles measurement conversion, equate→zero-shot mapping, splay shots, declination, and the critical issue of junction stations positioned only by duplicate shots. Skip the manual survey-file skeleton in Step 9 — the skill produces all section `.SRV` files directly.

## Step 5 — Create directory structure

```bash
mkdir -p "Jaskinie-poligony/<valley-path>/<Cave Name>/_RAW/01"
```

Copy source files to `_RAW/01/` preserving original names (never rename raw files):
```bash
cp /tmp/<cave_ascii>_raw/<file> "Jaskinie-poligony/<valley-path>/<Cave Name>/_RAW/01/"
```

## Step 6 — Create `_RAW/01/README.md`

Use the metadata CLI instead of composing the README manually:

```bash
uv run jktz-srv-metadata raw-set \
  "Poligony/<valley-path>/<Cave Name ASCII>/_RAW/01/README.md" \
  --title "<Cave Name ASCII> - paczka zrodlowa 01" \
  --status "dostępny" \
  --origin "<origin / who provided the data>" \
  --authors "<authors from source/PIG or nieznane>" \
  --dates "<dates from source/PIG or nieznane>" \
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

See the **Prefix Convention** section in [`CLAUDE.md`](../../../CLAUDE.md) for the rules (CamelCase including short prepositions, single-section vs multi-section patterns, `#prefix2` for cave systems, scope rules).

For a typical single-section cave: cave name in CamelCase, no spaces, no diacritics (e.g. `Mrozna`, `MietusiaWyznia`).

## Step 8 — Append entrance entry to `Poligony/OTWORY.SRV`

All entrance fixes/flags/notes for every cave live in a single shared file: `Poligony/OTWORY.SRV`.

Append a block like this (alphabetised by cave prefix) to `Poligony/OTWORY.SRV`:

```
#fix    <PREFIX>:<STATION>   E<lon-dd>  N<lat-dd>  <elevation>m
#flag   <PREFIX>:<STATION>   /<Cave Label>
#flag   <PREFIX>:<STATION>   /ENTRANCE
#note   <PREFIX>:<STATION>   /<Cave Label>
```

`<PREFIX>:<STATION>` is the fully-qualified entrance station name (e.g. `Marmurowa:0`, `MietusiaWyznia:ot_gps`, `WielkaSniezna:Ciag:0`). The station must exist in the cave's survey file — Walls/cavern resolves it across the whole project tree.

If the entrance station is unknown, comment out the block and add a TODO note:
```
; #fix   <PREFIX>:???   E<lon-dd>  N<lat-dd>  <elevation>m  ; TODO: uzupelnic numer stacji wejscia
; #flag  <PREFIX>:???   /<Cave Label>
; #flag  <PREFIX>:???   /ENTRANCE
; #note  <PREFIX>:???   /<Cave Label>
```

## Step 9 — Create the survey file (`CAVE.SRV` or `CAVE_<SECTION_SHORTNAME>.SRV`)

First create the Walls body without a hand-written metadata block:

```
#prefix <PREFIX>
#units meters order=DAV
#units A=D V=D
; do NOT add #units DECL= when #date is present — declination derives from #date (see CLAUDE.md);
; use #units DECL=X.X instead of #date only when the file has no reliable date
#date <YYYY-MM-DD>

;<Section description>

FROM    TO      DISTANCE    AZIMUTH     INCLINATION
0       1       4.61        293         2
1       2       2.06        303         7

;Splay shots (cross-sections)

0       -       5.52        51          8
0       -       5.47        265         76
```

Then atomically prepend the validated metadata block:

```bash
uv run jktz-srv-metadata srv-set \
  "Poligony/<valley-path>/<Cave Name ASCII>/<CAVE_FILE>.SRV" \
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

If the raw source file contains multiple readings per shot, note this and leave measurements as TODO:
```
; TODO: przetworzyc pomiary z _RAW/<filename>
; Plik zrodlowy zawiera pomiary potrojne — wymagaja usrednienia lub konwersji.
; Stacje numerowane od <first-station> — numer stacji otworu nieznany.
```

## Step 10 — Update KATASTER.wpj

**IMPORTANT: Ask the user to close Walls before this step.** Walls overwrites the .wpj file when it saves, discarding any manually added entries.

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

Use `Edit` tool with sufficient surrounding context to make the match unique.
Verify with: `grep -n "<CAVE_SHORT_ID>" KATASTER.wpj`

## Step 11 — Summary

Report to the user:
- Files created (list all paths)
- Data filled in vs left as TODO/unknown
- Any fields needing manual follow-up (entrance station, instrument, who added raw files)
- Reminder: if Walls was open, it may overwrite the .wpj entry — check after reopening
