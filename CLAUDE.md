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
- Polish diacritical marks are **removed** from file/directory names but may appear in metadata
- Files use **no BOM** encoding; some legacy files have encoding artifacts in Polish characters

## .gitignore

Compiled Walls outputs are git-ignored: `*.nta`, `*.ntn`, `*.ntv`, `*.nts`, `*.ntp`, `*.wrl`, `*.log`, `*.lst`. Only `.SRV` source data and `.wpj` project file are tracked.

## Workflow for Adding a New Cave

1. Create a directory under the appropriate valley in `Jaskinie-poligony/`
2. Create `.SRV` file(s) with metadata block and survey data (newer format: separate `_M.SRV` for coordinates and `_S.SRV` for measurements)
3. Add `.BOOK`/`.SURVEY` entries to `KATASTER.wpj` referencing the new files
4. Update `INFO.txt` with a new version entry
5. All new data should be coordinated through the project coordinator (darek.lubomski@gmail.com)
