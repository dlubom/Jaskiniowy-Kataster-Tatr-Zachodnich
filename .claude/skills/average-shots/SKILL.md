# Skill: average-shots

Averages multiple survey shots for the same cave passage leg into a single shot in a Walls `.SRV` file.

## When to use

DistoX and other electronic distance meters record several repeat measurements per leg during a cave survey, including both a **forward shot** (A→B) and a **backward shot** (B→A) for quality control. Before incorporating data into the project, these repeated shots must be condensed into a single representative measurement per leg.

Use this skill when a `.SRV` file contains multiple shots for the same station pair (typically 3 forward + 3 backward = 6 shots per leg).

## Usage

```
/average-shots <path/to/FILE_S.SRV>
```

## Algorithm

### 1. Identify groups

Parse every survey measurement line (format: `FROM  TO  DIST  AZ  INC`).

Group **consecutive** lines that measure the **same station pair**, regardless of direction:
- `1.3  1.4  ...` and `1.4  1.3  ...` belong to the **same group** (pair `{1.3, 1.4}`)

The forward direction is defined by whichever shot appears **first** in the file.

### 2. Convert backward shots to forward direction

Before averaging, normalize all backward shots to the forward direction:

| Field       | Backward → Forward conversion              |
|-------------|---------------------------------------------|
| Distance    | unchanged                                   |
| Azimuth     | `az_fwd = (az_back + 180) % 360`            |
| Inclination | `inc_fwd = -inc_back`                       |

Example — leg 1.3→1.4:
```
Forward shots (1.3→1.4):  dist=3.850  az=215.00  inc=5.42
                           dist=3.850  az=215.00  inc=5.40
                           dist=3.850  az=215.00  inc=5.33

Backward shots (1.4→1.3): dist=3.850  az=35.10   inc=-5.44  → converted: az=215.10  inc=5.44
                           dist=3.850  az=35.03   inc=-5.22  → converted: az=215.03  inc=5.22
                           dist=3.850  az=34.97   inc=-5.45  → converted: az=214.97  inc=5.45

Average:  1.3  1.4  3.850  215.02  5.38
```

### 3. Compute averages

- **Distance**: arithmetic mean of all measurements
- **Azimuth**: **circular mean** (handles the 0°/360° boundary)
- **Inclination**: arithmetic mean of all measurements (after converting backward shots)

**Circular mean formula** (use this for azimuth, not arithmetic mean):
```
az_mean = atan2(Σsin(az_i), Σcos(az_i))  converted to degrees in [0, 360)
```

This matters when azimuths straddle the 0/360° boundary (e.g., averaging 358° and 2° → 0°, not 180°).

### 4. Output format

Replace the entire group with a single averaged shot:
```
FROM  TO  DIST  AZ  INC
```
- Distance: 3 decimal places
- Azimuth: 2 decimal places
- Inclination: 2 decimal places
- Tab-separated fields, same indentation as the original

Non-shot lines (metadata `#[...]`, directives `#date`, `#units`, `#prefix`, comments `;`, zero-distance branch connections) are preserved unchanged.

## Edge cases

| Situation | Handling |
|-----------|----------|
| Only forward shots (no backsight) | Average the forward shots only |
| Only backward shots (no foresight) | Average as-is (no direction flip needed since the first shot defines forward) |
| Single shot for a leg | Keep unchanged |
| Zero-distance connection shots (`A  B  0  0  0`) | Keep unchanged (single-shot group) |
| Groups spanning across section breaks | Groups are only formed from **consecutive** same-pair shots |

## Implementation

The script lives at `.claude/skills/average-shots/average_shots.py`. Run it directly:

```
python .claude/skills/average-shots/average_shots.py <path/to/FILE_S.SRV>
```

## What to update after averaging

After running, update the metadata block in the `.SRV` file:
- `UPDATE_DATE` → today's date (`YYYY-MM-DD`)

## Example results (MROZNA_S.SRV, 2026-02-26)

- Input: 854 lines, 831 measurement shots across 196 legs
- Output: 222 lines, 199 measurement shots
- Removed: 632 redundant shots
- Main traverse legs: 6 shots each (3 fwd + 3 bwd) → 1 averaged shot
- Branch/dead-end legs: 3 shots each (fwd only) → 1 averaged shot
