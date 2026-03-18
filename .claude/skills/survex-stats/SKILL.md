# Skill: survex-stats

Compiles a Survex `.svx` file (or the main `KATASTER.wpj` project) using `cavern` and prints compilation output and statistics. Useful for cross-checking a raw Survex source against the Walls project data, or for validating the whole project.

## When to use

- When you want to compile and inspect a Survex `.svx` file — for example after `/svx-to-srv` conversion, to verify shot counts, warnings, or total length before comparing with the Walls result.
- When you want to validate the entire project by compiling `KATASTER.wpj` with cavern (same check as the GitHub CI).

## Usage

```
/survex-stats <path/to/file.svx>
/survex-stats KATASTER.wpj
```

Examples:
```
/survex-stats Poligony/D_Mietusia/M_Swistowka/Mietusia_Wyznia/_RAW/mietusia_wyznia.svx
/survex-stats KATASTER.wpj
```

## Steps

1. Run cavern on the provided file:

   - For a `.svx` file, run the `survex-stats.sh` script:
     ```bash
     bash .claude/skills/survex-stats/survex-stats.sh "<path/to/file.svx>"
     ```
   - For `KATASTER.wpj` (full project validation), run cavern directly:
     ```bash
     cavern KATASTER.wpj 2>&1
     ```

2. Show the full output to the user — it includes cavern warnings, errors, and the summary statistics (total length, number of stations, etc.).

3. If `cavern` is not on PATH, tell the user to install Survex and ensure `cavern` is available in their shell.

4. After showing the output, briefly summarise:
   - Whether compilation succeeded or failed
   - Any warnings or errors cavern reported
   - Key stats: total survey length, number of stations (if present in output)
   - For `KATASTER.wpj`: flag any `error:` lines or "not attached to a fixed/control point" warnings, as these are what the GitHub CI checks for
