# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Jaskiniowy Kataster Tatr Zachodnich** (Tatra Cave Registry) is a speleological cave survey data project for the Western Tatra Mountains. It compiles cartographic data (survey measurements, cave entrance coordinates, terrain models) using the **Walls** cave survey software by Texas Speleological Survey.

- **Coordinate system**: WGS 84 geographic (lon/lat) for `#fix` entrance points; UTM projection for compiled 3D output
- **License**: Creative Commons Attribution-ShareAlike 4.0
- **Current version**: v1.0.0 — semantic versioning, tracked in `CHANGELOG.md`
- **Language**: Polish (cave names, documentation, comments in survey files)

## Tools & Processing

This is a data project, not a software application. The Python tooling is only
for release automation around the survey data.

- **Walls software** processes the data: reads `.SRV` survey files, compiles into binary `.NT*` files, and exports `.wrl` (VRML 3D models)
- The main project file `KATASTER.wpj` is opened in Walls to compile and visualize all survey data
- **Windows path limitation**: The project should be extracted to a short root path (e.g., `C:/`) because deep Windows paths can prevent some caves from displaying
- Python release tooling is managed with `uv`; validate it with
  `uv run ruff check scripts tests` and `uv run pytest`.

## Repository Structure

```
KATASTER.wpj              # Main Walls project file (hierarchical cave/survey tree)
CHANGELOG.md              # Version history (semver, from v0.00 to current)
INFO.txt                  # Project description, links, contributor credits
Poligony/                 # SOURCE DATA: ~150 .SRV survey files organized by valley
  OTWORY.SRV              # SHARED file: #fix/#flag/#note entrance entries for every cave
  D_Bystra/
  D_Chocholowska/
  D_Goryczkowa/
  D_Koscieliska/          # Largest region (Bandzioch, System Pawlikowskiego, etc.)
  D_ku_Dziurze/
  D_Malej_Laki/           # Contains System Wielkiej Snieznej
  D_Mietusia/
  D_Panszczyca/
  D_Tomanowa/
  J_Slowacji/
  _Domiary_Pow_/          # Surface measurement connections between caves
Powierzchnia/             # Terrain model (DEM from contour lines)
KATASTER/                 # COMPILED OUTPUT (git-ignored .NT* files)
.github/workflows/        # GitHub Actions (automated release ZIP on tag push)
```

## Key File Formats

### KATASTER.wpj (Project File)
Walls project definition using directives: `.BOOK` (folder), `.SURVEY` (file reference), `.NAME`, `.PATH`, `.STATUS`, `.REF` (coordinate reference), `.ENDBOOK`. This file defines the hierarchical tree structure of all caves and their survey data.

### .SRV Files (Survey Data) — the primary source files

- All entrance fixes (`#fix`, `#flag`, `#note`) for every cave live in a single shared file: `Poligony/OTWORY.SRV`.
- `Poligony/OTWORY.SRV.j2` is the release-time template for that shared file.
  `scripts/render_otwory_from_gps.py` renders it to `Poligony/OTWORY.SRV`
  from the latest `best-measurements.csv` asset in
  `dlubom/gps-kataster-obiektow-tatr`. Each `gps_fix(...)` call embeds the
  GPS `object_id` directly in the template. Missing object rows or empty
  `lon`/`lat`/`elevation_m` values are release-blocking errors.
- Each cave's directory contains one or more **survey files** with the measurements only. Naming: `CAVE.SRV` for a single-survey cave, or `CAVE_<SECTION_SHORTNAME>.SRV` for caves split across multiple surveys/sections (see Mietusia Wyznia for an example with sections `_OT`, `_SD`, `_MR`, `...`).

#### Local GPS render check

Use `uv` for the Python release tooling:

```
uv sync --locked
uv run ruff format --check scripts tests
uv run ruff check scripts tests
uv run pytest
```

To preview a rendered entrances file without touching the checked-in
`Poligony/OTWORY.SRV`, write it to a temporary path:

```
uv run python scripts/render_otwory_from_gps.py --output /tmp/OTWORY.SRV
```

To reproduce the release input locally, render in place and compile:

```
uv run python scripts/render_otwory_from_gps.py
cavern KATASTER.wpj
```

The renderer downloads the latest GitHub release asset from
`dlubom/gps-kataster-obiektow-tatr`. Any missing `object_id` mapping in the
template, missing release asset, or empty coordinate/elevation field is an
error.

Entrance coordinates are maintained in
[`dlubom/gps-kataster-obiektow-tatr`](https://github.com/dlubom/gps-kataster-obiektow-tatr/releases/tag/v1.0.0)
and are injected automatically here during release rendering. Look there for
measurement provenance and best-measurement selection details.

---

### File Templates

#### Template: Entrance entry in `Poligony/OTWORY.SRV`

Append a block like this (alphabetised by cave prefix) to `Poligony/OTWORY.SRV`:

```
#fix	PREFIX:STATION	E<lon>	N<lat>	<elevation>m
#flag	PREFIX:STATION	/Cave Label
#flag	PREFIX:STATION	/ENTRANCE
#note	PREFIX:STATION	/Cave Label
```

`PREFIX:STATION` is fully qualified (e.g. `Marmurowa:0`, `MietusiaWyznia:ot_gps`, `WielkaSniezna:Ciag:0`). LON/LAT in WGS84 geographic — use decimal degrees (e.g. `E19.894900 N49.245399`);

The entrance station referenced here must exist in the cave's survey file (Walls/cavern resolves it across the whole project tree).

#### Template: Survey File (`CAVE.SRV` or `CAVE_<SECTION_SHORTNAME>.SRV`)
```
#[
CAVE_ID			"T.X-00.00"
CAVE_NAME		"Jaskinia Nazwa"
SURVEY_ID		SURVEY_SHORT_ID
SURVEY_NAME		"Survey description"
UPDATE_DATE		YYYY-MM-DD
PROJECT_NAME		"Kataster jaskin tatrzanskich"
COORDINATOR		"Dariusz Lubomski"
COORDINATOR_EMAIL	"darek.lubomski@gmail.com"
DATA_SOURCE		"source name"
LICENSE			"http://creativecommons.org/licenses/by-sa/4.0/"

TEAM "team member names"
INSTRUMENT "instrument name"
#]

#prefix STATION_PREFIX
#units meters order=DAV
#units A=D V=D
#units DECL=X.X
; NOTE: #units DECL= must come BEFORE #date directive (standard convention in this project).
; Do NOT place DECL= after #date — if "Derive from #Date" is enabled in the
; project's Geographical Reference settings, #date directive overrides any preceding DECL=
; with the IGRF model value, causing Walls and Survex to disagree.
#date YYYY-MM-DD

;Section description

0	1	4.61	293	2
1	2	2.06	303	7

;Splay shots

0	-	5.52	51	8
0	-	5.47	265	76
```

## Data Conventions

- **Cave IDs** follow the pattern `T.{region}-{number}.{sub}` (e.g., `T.C-16.01` for Jaskinia Kalacka, `T.B-14.01` for Dziura)
- **Station naming**: `{cave_id}_{survey_id}` prefix (e.g., `tb1401_A1` for Dziura survey A1)
- **`#prefix` / `#prefix2` convention**: see the **Prefix Convention** subsection below
- **Directory hierarchy**: Valley → Mountain/Region → Cave → Survey files
- **SRV file naming**: UPPERCASE basename + `.SRV` extension (e.g., `DZIUR_S.SRV`, `MARMUR_OT.SRV`, `TC1601A1.SRV`). The basename must match the `.NAME` directive in `KATASTER.wpj`. This is required for Linux compatibility — `cavern` (Survex) on case-sensitive filesystems only tries: all-lowercase, Initial-cap, and ALL-UPPERCASE variants when resolving `.NAME` references.
- **Directory naming conventions** (to keep paths short for Windows compatibility):
  - **No spaces** — use underscores: `Studnia_na_Szlaku`, not `Studnia na Szlaku`
  - **Valley prefix**: `D_` instead of `Dolina ` (e.g., `D_Koscieliska`, `D_Mietusia`)
  - **Drop "Jaskinia "** from cave directories (e.g., `Kalacka` not `Jaskinia Kalacka`, `Zwolinskiego` not `Jaskinia Zwolinskiego`)
  - **Shorten long names** where sensible (e.g., `Kom_Wierch`, `Rapt_Turnia`, `Syst_Pawlikowskiego`)
  - Directory names must match `.PATH` directives in `KATASTER.wpj` exactly (case-sensitive)
  - These are filesystem names only — display names in `KATASTER.wpj` (`.BOOK` directives) keep their full, human-readable form
- Polish and Slovak diacritical marks are **not allowed** in `.wpj` paths, `.SRV` filenames, or survey text content used by Walls
- Use ASCII equivalents instead (e.g., `ą->a`, `ć->c`, `ł->l`, `ó->o`, `ś->s`, `ż->z`, `č->c`, `š->s`, `ť->t`, `ž->z`)
- Keep `_RAW/` files untouched as archival originals, even if they contain non-ASCII text
- Files use **no BOM** encoding; some legacy files have encoding artifacts in Polish characters

### Prefix Convention

Cave names in `#prefix` use **CamelCase**, no spaces, no diacritics. Every word — including short prepositions (`w`, `na`, `pod`) — starts with a capital letter (e.g. "Lodowa w Ciemniaku" → `LodowaWCiemniaku`).

Two options, picked by cave shape:

**Option 1 — single `#prefix` (simple cave).** One `#prefix` for the whole cave; stations qualify as `Prefix:Station`.
- Example: Marmurowa — `#prefix Marmurowa`, entrance `Marmurowa:0`.

**Option 2 — `#prefix2` + `#prefix` (multi-section cave or cave system).** Outer `#prefix2 SystemName` shared by every file; inner `#prefix SectionName` per file. Stations qualify as `System:Section:Station`.
- Example: System Wielkiej Śnieżnej — `#prefix2 WielkaSniezna`, `#prefix Ciag`/`Jasna`/...; entrance `WielkaSniezna:Ciag:0`.

### Detecting Data Quality Issues in SRV Files

**Important:** SRV files may contain non-UTF-8 bytes (CP1250/Latin-1 legacy encoding). Always use `LC_ALL=C` with grep/sed to handle these correctly. The Edit tool (which operates in UTF-8) will corrupt these bytes — use `LC_ALL=C sed -i ''` instead for byte-safe replacements.

**Walls duplicate-vector warnings** — with `Options | Compilation | Look for Duplicates` enabled, Walls logs duplicate FROM/TO station pairs independently of segment tags. Adding `#S L` or `#S /Duplicate` is useful for statistics/segment handling, but it does **not** suppress the "Duplication of shot" warning. Fix depending on the data:
- Repeated instrument readings for the same leg: average them into one measurement.
- Truly duplicate survey/resurvey leg: choose one source or keep both only if you accept the Walls warning when duplicate checking is enabled.
- Conflicting measurements with the same station names: do not blindly average; resolve from source material, or rename the alternate traverse stations and tie the endpoints explicitly.

**Decimal comma (,) instead of dot (.)** — Walls treats comma as whitespace, shifting all subsequent fields:
```bash
# Detect: comma between digits in measurement fields (excluding comments, LRUD, metadata, _RAW/)
LC_ALL=C grep -rn '[0-9],[0-9]' Poligony/ --include='*.SRV' | grep -v '/_RAW/' | grep -v ':#\|:;' | grep -v '<.*,.*>'
```

**Non-ASCII characters** — Polish diacritics that should have been replaced with ASCII:
```bash
# Detect: any non-ASCII bytes in SRV files (excluding _RAW/)
LC_ALL=C grep -rn '[^[:print:][:space:]]' Poligony/ --include='*.SRV' | grep -v '/_RAW/'

# Fix: replace CP1250 Polish characters with ASCII equivalents
LC_ALL=C sed -i '' \
  -e "$(printf 's/\xf3/o/g')" -e "$(printf 's/\xd3/O/g')" \
  -e "$(printf 's/\xb9/a/g')" -e "$(printf 's/\xb3/l/g')" \
  -e "$(printf 's/\xea/e/g')" -e "$(printf 's/\xe6/c/g')" \
  -e "$(printf 's/\xbf/z/g')" -e "$(printf 's/\x9c/s/g')" \
  -e "$(printf 's/\xf1/n/g')" FILE.SRV
```

### Raw Source Files (`_RAW/`)

Cave directories contain (or will contain) a `_RAW/` subdirectory with original, unmodified source files provided by survey authors. Purpose:
1. **Archival** — preserving original data in its native format (Therion, Survex, DistoX exports, scanned notes, etc.)
2. **Verification** — allowing later validation of the converted `.SRV` measurements against the original source data
3. **Audit trail** — documenting provenance of all data in the project

The `_RAW/` contents are not processed by Walls but are tracked in git for reference.

**Required structure:**
```
<cave>/_RAW/
  README.md              # Metadata (required)
  source.zip             # ZIP archive (required if source has multiple files)
  source/                # Unpacked contents (required if ZIP exists)
    ...raw files...
```

If the source material is a single file, the ZIP + unpacked folder are not needed — just place the file directly in `_RAW/` alongside `README.md`.

**README.md must contain:**
- Source / origin of the data
- Author(s) of the original survey
- Date the data was obtained
- Person who added the files to `_RAW/`
- Notes on completeness (full dataset, partial, missing elements)

**Rules:**
- Preserve original filenames and directory structure — no renaming or reorganizing
- Never modify raw source files (even to fix encoding, formatting, or errors)
- Non-ASCII characters are allowed in `_RAW/` files (unlike `.SRV` files used by Walls)

## .gitignore

Compiled Walls outputs are git-ignored: `*.nta`, `*.ntn`, `*.ntv`, `*.nts`, `*.ntp`, `*.wrl`, `*.log`, `*.lst`. The `logs/` directory is also ignored. Only `.SRV` source data and `.wpj` project file are tracked.

## Versioning and Releases

The project uses [semantic versioning](https://semver.org/) starting from v1.0.0. All version history is in `CHANGELOG.md`.

### Release process
1. Update `CHANGELOG.md` with a new `## [vX.Y.Z] - YYYY-MM-DD` entry
2. Commit, merge to master
3. Create an annotated tag: `git tag -a vX.Y.Z -m "vX.Y.Z - description"`
4. Push the tag: `git push origin vX.Y.Z`
5. GitHub Actions renders `Poligony/OTWORY.SRV` from the latest GPS best
   measurements, then automatically creates a release with a ZIP archive
   (`JKTZ-vX.Y.Z.zip`)

The version in `INFO.txt` is set automatically — the `__VERSION__` placeholder is replaced with the tag name during the release build.

The release ZIP excludes: `.git/`, `.github/`, `.claude/`, `.gitignore`, `CLAUDE.md`, `doc/`, `scripts/`, `Poligony/OTWORY.SRV.j2`, `logs/`, `*/_RAW/*`, `.DS_Store`, and compiled Walls outputs. Users who need `_RAW/` or `doc/` should clone the repository.

## Documentation Resources (`doc/`)

When working with this project, Claude Code can use the following reference materials:

### Walls Software Documentation
- **`doc/Walls_manual.md`** — Markdown version of the Walls cave survey software manual. Use this for details on `.SRV` file syntax, directives (`#fix`, `#units`, `#date`, etc.), project file structure, and compilation options.
- **`doc/Walls_manual.pdf`** — Original PDF manual (same content as the markdown version).
- **Walls source code** — For advanced or edge-case questions about Walls behavior, the source code is available at https://github.com/wallscavesurvey/walls

### Polish Cave Registry Data (PIG)
- **`doc/jaskinie_polski_pig_dump.jsonl`** — Full JSONL dump from the Polish Geological Institute cave registry (https://jaskiniepolski.pgi.gov.pl/). Each line is a JSON object with comprehensive cave data.

**Use this file when:**
- Adding new caves — search for existing official data (coordinates, dimensions, description)
- Verifying or correcting entrance coordinates (`latitude`, `longitude`, `absolute_height_masl`)
- Finding cave metadata (inventory number, region, length, depth, denivelation)
- Researching documentation history (who surveyed, when, survey dates)
- Finding alternative cave names (`other_names` field)
- Checking geographic location and access descriptions

**Always search by cave ID, not name** — the ID is ASCII and unambiguous. Cave names contain Polish diacritics (ź, ą, etc.) that cause grep to fail silently:

```bash
# Correct — search by ID (always works)
grep '"T.B-14.01"' doc/jaskinie_polski_pig_dump.jsonl

# Avoid — searching by name may fail on diacritics
grep -i "dziura" doc/jaskinie_polski_pig_dump.jsonl
```

Returns data including:
- Official name: "Dziura" with aliases "Jaskinia Strążyska, Zbójnicka Jama"
- Coordinates: 49.27°N, 19.92°E, 1020 m n.p.m.
- Dimensions: length 175m, depth 15.6m, denivelation 40.4m
- Location: Dolina ku Dziurze, TPN
- Documentation history: survey dates and authors

## Git Commits

When creating commits in this project:
- **Do NOT add `Co-Authored-By` lines** — commit messages should not include Claude Code attribution
- Use Polish language for commit messages when appropriate
- Keep messages concise and descriptive
- When releasing a new version, create an **annotated tag** (`git tag -a vX.Y.Z -m "..."`) on master after merging — see "Versioning and Releases" above

## Available Skills

### `/add-cave` — `.claude/skills/add-cave/SKILL.md`

Guides through adding a new cave end-to-end. Usage:

```
/add-cave <cave-id> "<valley/subdir/path>" [/path/to/source.zip]
```

Example:
```
/add-cave T.D-08.07 "Dolina Koscieliska/Organy" /tmp/MROZN.SRV.zip
```

Covers: PIG lookup → coordinate conversion → directory creation → `_RAW/` + README → entrance entry appended to `Poligony/OTWORY.SRV` → survey file skeleton(s) → `KATASTER.wpj` entry.

### `/average-shots` — `.claude/skills/average-shots/SKILL.md`

Averages multiple repeat shots for the same leg (forward A→B + backward B→A) into a single measurement in a survey `.SRV` file. Use after importing raw DistoX data. Usage:

```
/average-shots <path/to/FILE.SRV>
```

### `/survex-stats` — `.claude/skills/survex-stats/SKILL.md`

Compiles a Survex `.svx` file with `cavern` and prints the output and statistics. Useful for cross-checking raw source data before or after conversion. Usage:

```
/survex-stats <path/to/file.svx>
```

### `/svx-to-srv` — `.claude/skills/svx-to-srv/SKILL.md`

Converts Survex (`.svx`) survey files to Walls (`.SRV`) format. Covers measurement conversion, equate→zero-shot mapping, flag handling, and the critical issue of junction stations positioned only by duplicate shots. Usage:

```
/svx-to-srv <cave-id> <path/to/source.svx>
```

### `/docker-exports` — `.claude/skills/docker-exports/SKILL.md`

Builds the `jktz-survex` Docker image and/or runs the release export pipeline locally, generating `.3d`, `.dxf`, `.shp`, and `.err` files in `exports/JKTZ-<VERSION>/`. Mirrors the GitHub Actions release pipeline. Usage:

```
/docker-exports [VERSION]
/docker-exports --build-only
/docker-exports --run-only [VERSION]
```

### `/docker-validate` — `.claude/skills/docker-validate/SKILL.md`

Runs the validation pipeline locally using Docker (same `jktz-survex` image as `/docker-exports`). Checks SRV naming, invalid directives, compiles with cavern, and reports unattached-station errors. Mirrors the Linux job in GitHub Actions `validate.yml`. Usage:

```
/docker-validate
```

### `/verify-cave-refactor` — `.claude/skills/verify-cave-refactor/SKILL.md`

Verifies that a refactor of a single cave's SRV files (split, prefix rename, formatting) did not change the survey itself. Compiles the project before and after the change, exports station coordinates for the named cave, and diffs them. Usage:

```
/verify-cave-refactor <cave-prefix>
```

Example:
```
/verify-cave-refactor Marmurowa
```

### `/gnss-to-wgs84` — `.claude/skills/gnss-to-wgs84/SKILL.md`

Converts coordinates from Polish EPSG:2180 (PUWG 1992 / "uklad 1992") to WGS84 geographic (EPSG:4326). Useful when processing GNSS survey reports. Requires `pyproj` (`pip3 install pyproj`). Usage:

```
/gnss-to-wgs84 <X_northing> <Y_easting> [<elevation>]
```

Example:
```
/gnss-to-wgs84 152168.79 564375.07 1486.69
```

## Workflow for Adding a New Cave

Use the `/add-cave` skill (see above) or follow these steps manually:

1. **Research the cave** in `doc/jaskinie_polski_pig_dump.jsonl` — search by cave ID (see PIG section above) to find official coordinates, dimensions, and documentation history
2. Create a directory under the appropriate valley in `Poligony/` (use underscores, no spaces, short names)
3. Create the cave's survey `.SRV` file(s) with metadata block and survey data (one file for a simple cave, one per section for a multi-section cave)
4. Append entrance fix/flag/note for the cave to `Poligony/OTWORY.SRV` (fully-qualified station name, e.g. `Marmurowa:0`)
5. If using Claude for adding cave: **Close Walls** before editing `KATASTER.wpj` — Walls overwrites the file on save, discarding any manually added entries
6. Add `.BOOK`/`.SURVEY` entries to `KATASTER.wpj` referencing the new files
7. Update `CHANGELOG.md` with a new version entry
8. All new data should be coordinated through the project coordinator (darek.lubomski@gmail.com)
