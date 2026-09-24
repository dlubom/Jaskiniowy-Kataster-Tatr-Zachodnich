# AGENTS.md

Codex is the default coding agent for this repository. Read this file for project contracts and use the relevant skills in `.agents/skills/`. Model selection and personal permissions remain in the user's Codex settings; this repository does not override them.

## Project Overview

**Jaskiniowy Kataster Tatr Zachodnich** (Tatra Cave Registry) is a speleological cave survey data project for the Western Tatra Mountains. It compiles cartographic data (survey measurements, cave entrance coordinates, terrain models) using the **Walls** cave survey software by Texas Speleological Survey.

- **Coordinate system**: WGS 84 geographic (lon/lat) for `#fix` entrance points; UTM projection for compiled 3D output
- **License**: Creative Commons Attribution-ShareAlike 4.0
- **Version history**: see `CHANGELOG.md`; ordinary changes go under `Unreleased`
- **Language**: Polish (cave names, documentation, comments in survey files)

## Tools & Processing

This is a data project, not a software application. Python tooling validates survey data, manages metadata and entrance snapshots,
and builds release exports.

- **Walls software** processes the data: reads `.SRV` survey files, compiles into binary `.NT*` files, and exports `.wrl` (VRML 3D models)
- The main project file `KATASTER.wpj` is opened in Walls to compile and visualize all survey data
- **Windows path limitation**: The project should be extracted to a short root path (e.g., `C:/`) because deep Windows paths can prevent some caves from displaying
- Python release tooling is managed with `uv`; validate it with
  `uv run ruff check src scripts tests .agents/skills` and `uv run pytest`.
- The required Python gate is `uv run jktz-quality`: Ruff, fresh tests, at least
  95% line and 90% branch coverage, and CRAP <= 25 per function. Run
  `uv run jktz-mutation` on POSIX/Python >= 3.10 for at least 81% killed mutations
  in each configured core module; incomplete/error runs fail. Use Python 3.12 to
  match CI. See `doc/PYTHON_QUALITY.md` for scope, reports, and enforcement.
  Do not lower thresholds, narrow scope, or add exclusions to make a check pass.
  Add behavior-based regression tests for confirmed bugs; metrics alone do not
  authorize unrelated production refactoring.
  The gate also rejects live Python files outside the declared scope and
  functions with no executed statements. Keep the inventory check active when
  moving or adding tooling; archival `_RAW` packages are not executable tooling.

## Local development setup

After cloning, install Python tooling and git hooks with one command:

    python scripts/initial-setup.py

Prerequisite: `uv` on PATH (https://docs.astral.sh/uv/getting-started/installation/). The script uses only the Python standard library and delegates all project work to `uv` subprocesses, so it does not need to be invoked via `uv run`. Idempotent — safe to re-run after changes to dev tooling.

`scripts/` is reserved for this pre-install bootstrap. Once setup completes,
repository tooling lives under `src/jktz/` and is invoked through the
`uv run jktz-*` commands declared in `pyproject.toml`. Human contributor setup
is also documented in `CONTRIBUTING.md`.

It does four things:
1. Verifies `uv` is on PATH.
2. Runs `uv sync --locked` (installs ruff, pytest, pre-commit, and the `jktz-*` CLIs into `.venv`).
3. Installs `pre-commit` and `pre-push` git hooks defined in `.pre-commit-config.yaml`.
4. Reports (warning only, never fails) whether these optional system tools are available:
   - **Survex** (`cavern`) — needed by `uv run jktz-validate`. Install: https://survex.com/download.html
   - **GDAL** (`ogr2ogr`) — needed by the exports step of `jktz-validate`. Windows: conda-forge or OSGeo4W. macOS: `brew install gdal`. Linux: `apt install gdal-bin`.
   - **Docker** — optional; enables `$docker-validate` and `$docker-exports` as a fallback if Survex/GDAL aren't installed locally.

### Git hooks

Defined in `.pre-commit-config.yaml`. Run via the [pre-commit framework](https://pre-commit.com/).

- **pre-commit** (every `git commit`, fast): `ruff format`, `ruff check --fix`, `jktz-quality` (fresh tests, coverage and CRAP). The first two hooks receive staged Python files under `src/`, `scripts/`, `tests/`, `.agents/skills/`, and `web/`; the quality gate checks the whole source scope. If `ruff format` modifies a file, the commit **fails** (does not auto-stage) — review and re-stage only the intended files, then commit again. This is the standard pre-commit framework behavior; it guarantees no commit ships unformatted code.
- **pre-push** (every `git push`, slow): `uv run jktz-validate` — full cavern compile + exports pipeline. The validation fails if `cavern` emits any compile warnings. Takes a few minutes. Requires Survex and GDAL on PATH.

If a hook fails, resolve the cause and rerun it. Use the Docker validation skill when local Survex/GDAL are unavailable. Report infrastructure blockers separately from data failures; do not silently bypass hooks. Full validation also downloads the latest GPS release, so it needs network access.

These are Git hooks, installed by the bootstrap for both manual and Codex commits/pushes. There are no separate agent lifecycle hooks to install.

## Repository Structure

```
KATASTER.wpj              # Main Walls project file (hierarchical cave/survey tree)
CHANGELOG.md              # Version history (semver, from v0.00 to current)
INFO.txt                  # Project description, links, contributor credits
Poligony/                 # SOURCE DATA: .SRV survey files organized by valley
  OTWORY.SRV.j2           # SHARED template: #fix/#flag/#note entrance entries for every cave
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
.github/workflows/        # GitHub Actions: PR validation/packages, releases, Pages
```

## Key File Formats

### KATASTER.wpj (Project File)
Walls project definition using directives: `.BOOK` (folder), `.SURVEY` (file reference), `.NAME`, `.PATH`, `.STATUS`, `.REF` (coordinate reference), `.ENDBOOK`. This file defines the hierarchical tree structure of all caves and their survey data.

### .SRV Files (Survey Data) — the primary source files

- All entrance fixes (`#fix`, `#flag`, `#note`) for every cave live in
  `Poligony/OTWORY.SRV`, a versioned generated snapshot for reviewable diffs.
- `Poligony/OTWORY.SRV.j2` is the source template for that snapshot.
  `uv run jktz-render-otwory` renders it from the latest
  `best-measurements.csv` asset in `dlubom/gps-kataster-obiektow-tatr`.
  Each `gps_fix(...)` call embeds the GPS `object_id` directly in the template.
  Missing object rows or empty `lon`/`lat`/`elevation_m` values are
  release-blocking errors.
- Each cave's directory contains one or more **survey files** with the measurements only. Naming: `CAVE.SRV` for a single-survey cave, or `CAVE_<SECTION_SHORTNAME>.SRV` for caves split across multiple surveys/sections (see Mietusia Wyznia for an example with sections `_OT`, `_SD`, `_MR`, `...`).

#### Local GPS render check

Use `uv` for the Python release tooling:

```
uv sync --locked
uv run ruff format --check src scripts tests .agents/skills
uv run ruff check src scripts tests .agents/skills
uv run pytest
```

To preview a rendered entrances file without changing the versioned
`Poligony/OTWORY.SRV`, write it to a temporary path:

```
uv run jktz-render-otwory --output /tmp/OTWORY.SRV
```

To reproduce the release input locally, render in place and compile:

```
uv run jktz-render-otwory
cavern KATASTER.wpj
```

Before committing, check that the versioned `Poligony/OTWORY.SRV` snapshot
matches the template rendered from the latest GPS release:

```
uv run jktz-render-otwory --check
```

The renderer downloads the latest GitHub release asset from
`dlubom/gps-kataster-obiektow-tatr`. Any missing `object_id` mapping in the
template, missing release asset, or empty coordinate/elevation field is an
error.

Entrance coordinates are maintained in
[`dlubom/gps-kataster-obiektow-tatr`](https://github.com/dlubom/gps-kataster-obiektow-tatr/releases)
and are injected automatically into the versioned snapshot. Look there for
measurement provenance and best-measurement selection details.

---

### File Templates

#### Template: Entrance entry in `Poligony/OTWORY.SRV.j2`

Append a block like this (alphabetised by cave prefix) to
`Poligony/OTWORY.SRV.j2`, then render and commit the updated
`Poligony/OTWORY.SRV` snapshot:

```
{{ gps_fix('PREFIX:STATION', 'OBJECT-ID') }}
#flag	PREFIX:STATION	/Cave Label
#flag	PREFIX:STATION	/ENTRANCE
#note	PREFIX:STATION	/Cave Label
```

`PREFIX:STATION` is fully qualified (e.g. `Marmurowa:0`,
`MietusiaWyznia:ot_gps`, `WielkaSniezna:Ciag:0`). `OBJECT-ID` is the
corresponding opening/object id from `dlubom/gps-kataster-obiektow-tatr`.
The rendered `Poligony/OTWORY.SRV` contains WGS84 geographic lon/lat decimal
degrees (e.g. `E19.894900 N49.245399`).

The entrance station referenced here must exist in the cave's survey file (Walls/cavern resolves it across the whole project tree).

#### Template: Survey File (`CAVE.SRV` or `CAVE_<SECTION_SHORTNAME>.SRV`)

Create the Walls body, then use `uv run jktz-srv-metadata srv-set ...` to
atomically prepend the canonical block shown below. Use
`uv run jktz-srv-metadata srv-update ...` for later `UPDATE_DATE` or
`PROCESSING` changes, and `raw-set` for `_RAW/NN/README.md`. All write commands
support `--dry-run`.

```
#[
CAVE_ID         "T.X-00.00"
CAVE_NAME       "Cave Name ASCII"
SURVEY_ID       "SURVEY_ID"
SURVEY_NAME     "Survey name"
UPDATE_DATE     "2026-06-05"
PROJECT_NAME    "Kataster jaskin tatrzanskich"
COORDINATOR     "nieznane"
COORDINATOR_EMAIL "nieznane"
SOURCE_REF      "_RAW/01"
LICENSE         "http://creativecommons.org/licenses/by-sa/4.0/"

TEAM            "nieznane"
INSTRUMENT      "nieznane"
SURVEY_DATE     "nieznane"
SURVEY_GRADE    "nieznane"
PROCESSING      "utworzono aktywny plik SRV z materialow zrodlowych"
#]

#prefix STATION_PREFIX
#units meters order=DAV
#units A=D V=D
; NOTE: do NOT add a #units DECL= directive when a #date directive is present.
; Declination is derived from #date via the IGRF model ("Derive from #Date" in the
; project's Geographical Reference settings). An explicit DECL= would either be
; overridden by #date or conflict with it, causing Walls and Survex to disagree.
; Only when the file has NO reliable date, use an explicit #units DECL=X.X instead of #date.
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
- **Station naming**: preserve source station identifiers; qualify them with the cave/section prefixes below. Do not infer station identity from matching measurements or geometry.
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

**Important:** SRV files may contain non-UTF-8 bytes (CP1250/Latin-1 legacy encoding). Always use `LC_ALL=C` with grep/sed to handle these correctly. Inspect the bytes before editing. Preserve encoding and line endings; use byte-aware replacements or the metadata CLI rather than decoding legacy data as UTF-8.

**Walls duplicate-vector warnings** — with `Options | Compilation | Look for Duplicates` enabled, Walls logs duplicate FROM/TO station pairs independently of segment tags. Adding `#S L` or `#S /Duplicate` is useful for statistics/segment handling, but it does **not** suppress the "Duplication of shot" warning. Fix depending on the data:
- Repeated instrument readings for the same leg: average them into one measurement.
- Independent surveys/resurveys must remain distinguishable. Do not discard one merely to silence duplicate warnings; record the source and explain any exclusion from statistics.
- Conflicting measurements with the same station names: do not blindly average; resolve from source material, or namespace the alternate traverse separately. Tie stations only with independent evidence of identity.

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

Cave directories contain (or will contain) a `_RAW/` subdirectory with original, unmodified source files provided by survey authors. The contract below is enforced by `src/jktz/validation/metadata.py` and managed through `uv run jktz-srv-metadata`. Purpose:
1. **Archival** — preserving original data in its native format (Therion, Survex, DistoX exports, scanned notes, etc.)
2. **Verification** — allowing later validation of the converted `.SRV` measurements against the original source data
3. **Audit trail** — documenting provenance of all data in the project

The `_RAW/` contents are not processed by Walls but are tracked in git for reference.

**Required structure:**
```
<cave>/_RAW/
  README.md              # Optional index only
  01/
    README.md            # Required package metadata
    ...raw files...
  02/
    README.md            # Required if another source package exists
    ...raw files...
```

`_RAW/NN/README.md` must contain:
- `Status materiału` (`dostępny`, `częściowy`, or `niedostępny`)
- `Pochodzenie danych`
- `Autorzy pomiarów`
- `Daty pomiarów`
- `Data pozyskania`
- `Dodał do _RAW`
- `Licencja źródłowa`
- `Kompletność`
- `## Zawartość` with one item per source file/directory, or `Brak materiałów źródłowych.` for `niedostępny`

**Rules:**
- Active `.SRV` metadata is mandatory and must start at the beginning of the file.
- `SOURCE_REF` links each active `.SRV` to an existing `_RAW/NN` package.
- `DATA_SOURCE` is deprecated in active `.SRV`; source provenance belongs in `_RAW/NN/README.md`.
- `_RAW` material files are never modified, even to fix encoding, formatting, or errors.
- `_RAW/NN/README.md` is metadata and may be created or updated.
- Preserve original filenames and directory structure inside the selected `_RAW/NN` package.
- Non-ASCII characters are allowed in `_RAW/` files (unlike `.SRV` files used by Walls)
- Create and update these metadata documents with `uv run jktz-srv-metadata`;
  reusable Python APIs live under `src/jktz/metadata/`.

## .gitignore

Compiled Walls outputs are git-ignored: `*.nta`, `*.ntn`, `*.ntv`, `*.nts`, `*.ntp`, `*.wrl`, `*.log`, `*.lst`. The `logs/` directory is also ignored. Source archives, documentation, templates, and tooling are also tracked.
`Poligony/OTWORY.SRV` is versioned intentionally: it is generated from
`Poligony/OTWORY.SRV.j2`, but kept in Git so coordinate changes have normal
review diffs. CI verifies that the snapshot matches the latest GPS release.

## Versioning and Releases

The project uses [semantic versioning](https://semver.org/) starting from v1.0.0. All version history is in `CHANGELOG.md`.

### Release process

Only release when explicitly requested. A draft PR request does not authorize merging, tagging, or publishing.

1. Update `CHANGELOG.md` with a new `## [vX.Y.Z] - YYYY-MM-DD` entry
2. Commit, merge to master
3. Create an annotated tag: `git tag -a vX.Y.Z -m "vX.Y.Z - description"`
4. Push the tag: `git push origin vX.Y.Z`
5. GitHub Actions verifies that `Poligony/OTWORY.SRV` matches the latest GPS
   best measurements, then automatically creates a release with a ZIP archive
   (`JKTZ-vX.Y.Z.zip`)

The version in `INFO.txt` is set automatically — the `__VERSION__` placeholder is replaced with the tag name during the release build.

The release ZIP excludes: `.git/`, `.github/`, legacy `.claude/`, `.agents/`, `.codex/`, `.venv/`, Python/tool caches, Python tooling files (`pyproject.toml`, `uv.lock`, `tests/`), `.gitignore`, `AGENTS.md`, `CONTRIBUTING.md`, `doc/`, `scripts/`, `Poligony/OTWORY.SRV.j2`, `logs/`, `*/_RAW/*`, `.DS_Store`, local Survex build directories, validation scratch outputs, previous `JKTZ-*.zip` files, and compiled Walls outputs. Users who need `_RAW/` or `doc/` should clone the repository.

Pull requests build a temporary test release package after validation succeeds.
The package is uploaded as a GitHub Actions artifact with short retention and
linked from the `pr-release-package` check summary. For branches in this
repository, the workflow also tries to update a PR comment with the same link;
that comment is best-effort so token permission issues do not fail the build.
These PR packages are not GitHub Releases and do not affect `/releases/latest`.

## Documentation Resources (`doc/`)

When working with this project, Codex can use the following reference materials:

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

Prefer the inventory ID for an unambiguous lookup, using `rg -F`:

```bash
rg -F '"T.B-14.01"' doc/jaskinie_polski_pig_dump.jsonl
```

Name searches also work with matching Unicode spelling; aliases and diacritics
can make them incomplete. The dump is an archival reference, not a current
measurement source. Do not infer survey authors from inventory editors, or
choose ambiguous scan digits by agreement with compiled length/closure.

Returns data including:
- Official name: "Dziura" with aliases "Jaskinia Strążyska, Zbójnicka Jama"
- Coordinates: 49.27°N, 19.92°E, 1020 m n.p.m.
- Dimensions: length 175m, depth 15.6m, denivelation 40.4m
- Location: Dolina ku Dziurze, TPN
- Documentation history: survey dates and authors

## Git Commits

When creating commits in this project:
- **Do NOT add `Co-Authored-By` lines** — commit messages should not include agent attribution
- Use Polish language for commit messages when appropriate
- Keep messages concise and descriptive
- When releasing a new version, create an **annotated tag** (`git tag -a vX.Y.Z -m "..."`) on master after merging — see "Versioning and Releases" above

## Available Skills

Repository skills live under `.agents/skills/<name>/SKILL.md`. Codex discovers
their `name` and `description`; invoke one with `$skill-name` in a prompt or let
Codex select it when relevant. These examples are prompts, not shell commands.
Run shell commands from the repository root; use `uv run` for Python tooling.

| Skill | Purpose |
| --- | --- |
| `$add-cave` | Add source material, survey metadata, GPS mapping, and project entries |
| `$svx-to-srv` | Convert Survex source measurements to Walls |
| `$average-shots` | Average confirmed repeat instrument readings in a working SRV |
| `$survex-stats` | Compile a source and inspect statistics |
| `$verify-cave-refactor` | Compare source data and compiled output before/after a refactor |
| `$gnss-to-wgs84` | Convert PUWG 1992 (X northing, Y easting) to WGS84 |
| `$utm34n-wgs84` | Convert WGS84 UTM 34N and geographic coordinates |
| `$docker-validate` | Run full data validation using Docker |
| `$docker-exports` | Build local release exports using Docker |

Skill helper scripts stay beside their `SKILL.md`; they are checked by the
same Ruff/pytest gates as the installed Python tooling.

## Workflow for Adding a New Cave

Use the `$add-cave` skill (see above) or follow these steps manually:

1. **Research the cave** in `doc/jaskinie_polski_pig_dump.jsonl` — search by cave ID (see PIG section above) to find archival inventory context, dimensions, and documentation history; active entrance fixes come from the GPS project
2. Create a directory under the appropriate valley in `Poligony/` (use underscores, no spaces, short names)
3. Create the cave's survey `.SRV` body and run `uv run jktz-srv-metadata srv-set` for each file
4. Append entrance fix/flag/note for the cave to `Poligony/OTWORY.SRV.j2` (fully-qualified station name, e.g. `Marmurowa:0`)
5. **Close Walls if it has this project open** before editing `KATASTER.wpj` — Walls overwrites the file on save, discarding any manually added entries
6. Add `.BOOK`/`.SURVEY` entries to `KATASTER.wpj` referencing the new files
7. Update `LISTA_JASKIN.md` and add a concise entry under `Unreleased` in `CHANGELOG.md`
8. All new data should be coordinated through the project coordinator (darek.lubomski@gmail.com)
