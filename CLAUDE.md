# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Jaskiniowy Kataster Tatr Zachodnich** (Tatra Cave Registry) is a speleological cave survey data project for the Western Tatra Mountains. It compiles cartographic data (survey measurements, cave entrance coordinates, terrain models) using the **Walls** cave survey software by Texas Speleological Survey.

- **Coordinate system**: WGS 84, UTM projection
- **License**: Creative Commons Attribution-ShareAlike 2.0
- **Current version**: v0.28 (tracked in INFO.txt)
- **Language**: Polish (cave names, documentation, comments in survey files)

## Tools & Processing

This is a data project, not a software project. There is no build system, test suite, or linter.

- **Walls software** processes the data: reads `.SRV` survey files, compiles into binary `.NT*` files, and exports `.wrl` (VRML 3D models)
- The main project file `KATASTER.wpj` is opened in Walls to compile and visualize all survey data
- **Windows path limitation**: The project should be extracted to a short root path (e.g., `C:/`) because deep Windows paths can prevent some caves from displaying

## Repository Structure

```
KATASTER.wpj              # Main Walls project file (hierarchical cave/survey tree)
INFO.txt                  # Version history and contributor credits
Jaskinie-poligony/        # SOURCE DATA: ~150 .SRV survey files organized by valley
  Dolina Bystra/
  Dolina Chocholowska/
  Dolina Goryczkowa/
  Dolina Koscieliska/     # Largest region (Bandzioch, System Pawlikowskiego, etc.)
  Dolina ku Dziurze/
  Dolina Malej Laki/      # Contains System Wielkiej Snieznej
  Dolina Mietusia/
  Dolina Tomanowa/
  Jaskinie Slowacji/
  _Domiary Powierzchniowe_/  # Surface measurement connections between caves
Powierzchnia/             # Terrain model (DEM from contour lines)
KATASTER/                 # COMPILED OUTPUT (git-ignored .NT* files)
```

## Key File Formats

### KATASTER.wpj (Project File)
Walls project definition using directives: `.BOOK` (folder), `.SURVEY` (file reference), `.NAME`, `.PATH`, `.STATUS`, `.REF` (coordinate reference), `.ENDBOOK`. This file defines the hierarchical tree structure of all caves and their survey data.

### .SRV Files (Survey Data) — the primary source files
Two conventions exist:

**Newer format** (e.g., Dziura, Mylna, Oblazkowa) splits data into two files per cave:
- `*_M.SRV` — metadata + fixed entrance coordinates (`#fix`), map label (`#flag`, `#note`)
- `*_S.SRV` — metadata + survey measurements (shots, splay shots, dates)

**Older format** (e.g., CAVE.SRV) — single file with metadata, coordinates, and measurements combined.

---

### File Templates

#### Template: Meta File (`CAVE_M.SRV`)
```
#[
CAVE_ID			"T.X-00.00"
CAVE_NAME		"Jaskinia Nazwa"
UPDATE_DATE		YYYY-MM-DD
PROJECT_NAME		"Kataster jaskin tatrzanskich"
COORDINATOR		"Dariusz Lubomski"
COORDINATOR_EMAIL	"darek.lubomski@gmail.com"
REFERENCE_SYSTEM	"WGS84"
COORDINATE_SYSTEM	"UTM"
DATA_SOURCE		"source name"
LICENSE			"http://creativecommons.org/licenses/by-sa/2.0/"
#]

#prefix PREFIX
#flag	STATION	/Cave Label
#note	STATION	/Cave Label
#fix	STATION	EASTING	NORTHING	ELEVATION
```

#### Template: Survey File (`CAVE_S.SRV`)
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
LICENSE			"http://creativecommons.org/licenses/by-sa/2.0/"

TEAM "team member names"
INSTRUMENT "instrument name"
#]

#prefix STATION_PREFIX
#date YYYY-MM-DD
#units meters order=DAV
#units A=D V=D

;Section description

FROM	TO	DISTANCE	AZIMUTH	INCLINATION
0	1	4.61	293	2
1	2	2.06	303	7

;Splay shots (cross-sections)

0	-	5.52	51	8
0	-	5.47	265	76
```

## Data Conventions

- **Cave IDs** follow the pattern `T.{region}-{number}.{sub}` (e.g., `T.C-16.01` for Jaskinia Kalacka, `T.B-14.01` for Dziura)
- **Station naming**: `{cave_id}_{survey_id}` prefix (e.g., `tb1401_A1` for Dziura survey A1)
- **Directory hierarchy**: Valley → Mountain/Region → Cave → Survey files
- Polish and Slovak diacritical marks are **not allowed** in `.wpj` paths, `.SRV` filenames, or survey text content used by Walls
- Use ASCII equivalents instead (e.g., `ą->a`, `ć->c`, `ł->l`, `ó->o`, `ś->s`, `ż->z`, `č->c`, `š->s`, `ť->t`, `ž->z`)
- Keep `_RAW/` files untouched as archival originals, even if they contain non-ASCII text
- Files use **no BOM** encoding; some legacy files have encoding artifacts in Polish characters

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

Compiled Walls outputs are git-ignored: `*.nta`, `*.ntn`, `*.ntv`, `*.nts`, `*.ntp`, `*.wrl`, `*.log`, `*.lst`. Only `.SRV` source data and `.wpj` project file are tracked.

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

**Example: Searching for cave "Dziura" (T.B-14.01)**
```bash
grep -i "T\.B-14" doc/jaskinie_polski_pig_dump.jsonl
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

## Workflow for Adding a New Cave

1. **Research the cave** in `doc/jaskinie_polski_pig_dump.jsonl` to find official coordinates, dimensions, and documentation history
2. Create a directory under the appropriate valley in `Jaskinie-poligony/`
3. Create `.SRV` file(s) with metadata block and survey data (newer format: separate `_M.SRV` for coordinates and `_S.SRV` for measurements)
4. Add `.BOOK`/`.SURVEY` entries to `KATASTER.wpj` referencing the new files
5. Update `INFO.txt` with a new version entry
6. All new data should be coordinated through the project coordinator (darek.lubomski@gmail.com)
