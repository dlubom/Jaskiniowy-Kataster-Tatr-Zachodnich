# Skill: survex-stats

Compiles a Survex `.svx` file using `cavern` and prints compilation output and statistics. Useful for cross-checking a raw Survex source against the Walls project data.

## When to use

When you want to compile and inspect a Survex `.svx` file — for example after `/svx-to-srv` conversion, to verify shot counts, warnings, or total length before comparing with the Walls result.

## Usage

```
/survex-stats <path/to/file.svx>
```

Example:
```
/survex-stats Poligony/D_Mietusia/M_Swistowka/Mietusia_Wyznia/_RAW/mietusia_wyznia.svx
```

## Steps

1. Run the `survex-stats.sh` script located in the repository root, passing the `.svx` path as the argument:

   ```bash
   bash .claude/skills/survex-stats/survex-stats.sh "<path/to/file.svx>"
   ```

2. Show the full output to the user — it includes cavern warnings, errors, and the summary statistics (total length, number of stations, etc.).

3. If `cavern` is not on PATH, tell the user to install Survex and ensure `cavern` is available in their shell.

4. After showing the output, briefly summarise:
   - Whether compilation succeeded or failed
   - Any warnings or errors cavern reported
   - Key stats: total survey length, number of stations (if present in output)
