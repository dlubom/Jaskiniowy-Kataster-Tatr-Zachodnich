# Skill: svx-to-srv

Converts a Survex (`.svx`) cave survey into Walls (`.SRV`) format for inclusion in the Jaskiniowy Kataster Tatr Zachodnich project.

## When to use

When new cave survey data arrives in Survex format (`.svx` files) and needs to be added to the project.

## Usage

```
/svx-to-srv <cave-id> <path/to/source.svx> [or ZIP with multiple .svx files]
```

Example:
```
/svx-to-srv T.D-10.01 "Poligony/D_Mietusia/M_Swistowka/Mietusia_Wyznia/_RAW/source/mietusia_wyznia.svx"
```

This produced 16 section SRV files in `Poligony/D_Mietusia/M_Swistowka/Mietusia_Wyznia/`. The cave's entrance fix is appended to the shared `Poligony/OTWORY.SRV` (see `/add-cave` Step 8).

## Conversion rules

### Measurement format

Survex `*data normal from to tape compass clino` → Walls `#units meters order=DAV`

The field order maps directly: `FROM TO DISTANCE AZIMUTH INCLINATION`

### Directives mapping

| Survex | Walls | Notes |
|--------|-------|-------|
| `*data normal from to tape compass clino` | `#units meters order=DAV` | Standard shot format |
| `*declination X` | drop it when `#date` is present | Declination derives from `#date` (IGRF). Only if the file has no reliable date, use `#units DECL=X` instead of `#date`. Note: `#dec` does NOT exist in Walls |
| `*calibrate declination X` | drop it when `#date` is present | Legacy pre-1.2.22 way of specifying declination (NOT an instrument correction). **Opposite sign** to `*declination`: actual declination = `-X`. Sanity-check `-X` against IGRF for the survey date/location — a large mismatch means the author baked in something else (grid convergence, empirical fix) and needs investigation. If the file has no reliable date, use `#units DECL=-X` instead of `#date` |
| `*calibrate compass/clino/tape X [scale]` | `#units INCA=-X` / `INCV=-X` / `INCD=-X` | Genuine instrument zero-error corrections — do NOT drop. Survex subtracts the zero error, Walls INC* values are added, so the sign flips |
| `*date YYYY.MM.DD` | `#date YYYY-MM-DD` | Dash separator in Walls |
| `*team ...` | `TEAM "..."` in metadata block | |
| `*instrument ...` | `INSTRUMENT "..."` in metadata block | |
| `*entrance` | `#flag`, `#note`, `#fix` appended to `Poligony/OTWORY.SRV` | Fully-qualified station name (e.g. `Marmurowa:0`). See add-cave skill Step 8 for coordinate conversion |

### What to skip (do NOT convert)

| Survex construct | Action |
|-----------------|--------|
| `*flags duplicate` shots | **Convert with `#S /Duplicate` tag** — append `#S /Duplicate` to each shot line. This preserves station topology (no disconnected components) while allowing the shots to be detached/hidden in Walls UI to exclude from statistics. |
| `*flags surface` shots | **Skip** — exception: the GPS→entrance shot that anchors the cave (keep as zero-shot or use coordinates from PIG) |
| `*data passage` (LRUD) | **Convert** — Walls supports LRUD as `<L,R,U,D>` appended to the shot line. Survex LRUD blocks are separate lines; in Walls they are inline. Optionally set style with `#units LRUD=F/T/FB/TB`. |
| `*flags not X` | Mark end of flag X — check this **before** checking `*flags X` (it's a substring of it, causing a bug if order is wrong) |


### Splay shots

Survex splay shots (anonymous stations, often `*` or `-`) → Walls `FROM - DIST AZ INC` (use `-` as TO station). Keep unchanged.

### Multi-file surveys and equates

Survex `*equate cave.A other.B` connections → **zero-shots** at the top of the relevant `.SRV` file:
```
other_B    cave_A    0    0    0
```

One zero-shot per equate. Place them in a `; === Polaczenia z innymi cigami ===` section before measurements.

### Prefixes and station naming

- Survex uses hierarchical prefixes (`*begin section`, `*end section`) — flatten according to the project's prefix convention
- For prefix structure (single `#prefix` Pattern A vs two-level `#prefix2`+`#prefix` Pattern B), CamelCase rules including short prepositions, scope rules, and which pattern applies to which cave system, see the **Prefix Convention** section in [`CLAUDE.md`](../../../CLAUDE.md)
- Pattern A example: section names become station infixes: `traba.1` → `tb_1` (with `#prefix td1001`); station full name: `td1001_tb_1`

---

## Junction stations positioned by duplicate shots

When `*flags duplicate` shots are **skipped** (instead of converted with `#S /Duplicate`), junction stations positioned only by those shots become disconnected from the network.

### The problem

In Survex, a station can be positioned by **duplicate shots** between two already-connected stations:

```survex
*equate traba.0 suche_dno.12   ; tb_0 = sd_12 (connected)
*equate traba.2 suche_dno.14   ; tb_2 = sd_14 (connected)

*flags duplicate
  0  1  4.77  256.9  9.7   ; sd_12 → tb_1
  1  2  9.30  278.2  1.3   ; tb_1  → sd_14
*flags not duplicate
  1  3  2.82  57.8  72.4   ; actual survey branches from tb_1
```

Here `traba.1` (= `tb_1`) is positioned by the duplicate shots. It is NOT equated to anything — its position is computed from the duplicate traversal. Dropping the duplicate shots leaves `tb_1` with no path to the network.

### Correct fix: use `#S /Duplicate`

Convert duplicate shots normally but append `#S /Duplicate`:

```srv
; === Polaczenia z innymi cigami ===
sd_12    tb_0    0    0    0
sd_14    tb_2    0    0    0

; === Pomiary (duplicate) ===
tb_0    tb_1    4.77    256.9    9.7    #S /Duplicate
tb_1    tb_2    9.30    278.2    1.3    #S /Duplicate

; === Pomiary ===
tb_1    tb_3    2.82    57.8    72.4
```

This preserves topology (tb_1 is connected) while allowing the duplicate shots to be detached/hidden in Walls UI.

### Legacy workaround: zero-shot

If duplicate shots were already skipped, add a zero-shot for each affected junction station:

```srv
sd_12    tb_0    0    0    0
tb_0     tb_1    0    0    0   ; fixes disconnected tb_1
sd_14    tb_2    0    0    0
```

### Real example: Mietusia Wyżnia (T.D-10.01), section TB (Trąba)

- `traba.svx` had `tb_0` and `tb_2` equated to `suche_dno`
- `tb_1` was intermediate in duplicate shots → positioned between `sd_12` and `sd_14`
- Duplicate shots were skipped during initial conversion → `tb_1` became a floating island
- Applied legacy fix: added `tb_0 tb_1 0 0 0` in `MWYZN_TB.SRV` (line 25)

---

## File structure for multi-section caves

One `.SRV` file per Survex `*begin`/`*end` block (or logical section). Naming: `{CAVE_ABBR}_{SECTION}.SRV`, e.g.:

```
MWYZN_OT.SRV   ; otwor (entrance passage)
MWYZN_SD.SRV   ; suche_dno
MWYZN_TB.SRV   ; traba
...
```

The prefix structure (single `#prefix` vs `#prefix2`+`#prefix`) follows the project convention — see the **Prefix Convention** section in [`CLAUDE.md`](../../../CLAUDE.md).

The cave's entrance fix/flag/note goes into the shared `Poligony/OTWORY.SRV`.

## Conversion checklist

- [ ] Read all `.svx` files to understand the structure (main file, `*include` chain)
- [ ] Map Survex section names to SRV file abbreviations
- [ ] Convert measurements, skipping `*flags duplicate` and `*flags surface`
- [ ] Map `*equate` directives to zero-shots
- [ ] **Check for junction stations in duplicate shots** — add zero-shots as needed (see critical section above)
- [ ] Drop `*declination` / `*calibrate declination` when `#date` is present (declination derives from `#date`); use `#units DECL=` instead of `#date` only when there is no reliable date. Mind the sign: `*calibrate declination X` → `DECL=-X`
- [ ] Convert `*calibrate compass/clino/tape` (instrument corrections) → `#units INCA=/INCV=/INCD=` with the sign flipped — never drop these
- [ ] Place all shots in correct chronological order per `*date`

## Adding the converted cave to the project

Once all `.SRV` files are ready, use the `/add-cave` skill to register the cave in the project:

```
/add-cave <cave-id> "<valley/subdir/path>"
```

The `/add-cave` skill handles:
- Placing `_RAW/` source files with a `README.md`
- Appending the entrance fix/flag/note to `Poligony/OTWORY.SRV` (from PIG dump or GPS)
- Adding `.BOOK`/`.SURVEY` entries to `KATASTER.wpj`
- Updating `CHANGELOG.md` and committing

When running `/add-cave` after SVX conversion, the section `.SRV` files are already created — skip the survey-file skeleton step and point the skill at the existing files.

## Common pitfalls

| Pitfall | Detail |
|---------|--------|
| `*flags not duplicate` substring bug | Always check `*flags not duplicate` before `*flags duplicate` when parsing flag lines |
| `#dec` does not exist | In the rare no-date case use `#units DECL=X`, not `#dec X` |
| Floating junction stations | See critical section above — most likely cause of disconnected components |
| Non-ASCII in station names | Survex allows Polish diacritics; replace with ASCII equivalents in Walls SRV files |
| LRUD format change | Survex LRUD is on separate `*data passage` lines; Walls LRUD is inline `<L,R,U,D>` appended to the shot line — merge them during conversion |
