---
name: survex-stats
description: Compile a Survex or Walls source and inspect its compilation statistics without writing output beside the source.
---

Compiles a Survex `.svx` file (or the main `KATASTER.wpj` project) using `cavern` and prints compilation output and statistics. Useful for cross-checking a raw Survex source against the Walls project data, or for validating the whole project.

## When to use

- When you want to compile and inspect a Survex `.svx` file — for example after `$svx-to-srv` conversion, to verify shot counts, warnings, or total length before comparing with the Walls result.
- When you want to validate the entire project by compiling `KATASTER.wpj` with cavern (a compile/statistics check; full CI also validates metadata, warnings, GPS snapshots, and exports).

## Usage

```
$survex-stats <path/to/file.svx>
$survex-stats KATASTER.wpj
```

Examples:
```
$survex-stats Poligony/D_Mietusia/M_Swistowka/Mietusia_Wyznia/_RAW/01/<source>.svx
$survex-stats KATASTER.wpj
```

## Resolving options and diagnostics

Use [cavern.rst](../../../doc/Survex_manual/cavern.rst) for command options,
[datafile.rst](../../../doc/Survex_manual/datafile.rst) for Survex syntax, and
[walls.rst](../../../doc/Survex_manual/walls.rst) for warnings and limitations
when compiling `.SRV`/`.WPJ`. For native Walls semantics consult
[Walls_manual.md](../../../doc/Walls_manual.md), with the PDF as the reference
for ambiguous conversion. Check `cavern --version` against the
[documented release](../../../doc/Survex_manual/README.md) before explaining
version-dependent behavior.

## Steps

1. Run the Python CLI on the provided `.svx` or `.wpj` file:

   ```bash
   uv run jktz-survex-stats "<path/to/file.svx>"
   ```

   For the full project use:

   ```bash
   uv run jktz-survex-stats KATASTER.wpj
   ```

2. Show the full output to the user — it includes cavern warnings, errors, and the summary statistics (total length, number of stations, etc.).

3. If `cavern` is not on PATH, tell the user to install Survex and ensure `cavern` is available in their shell.

4. After showing the output, briefly summarise:
   - Whether compilation succeeded or failed
   - Any warnings or errors cavern reported
   - Key stats: total survey length, number of stations (if present in output)
   - For `KATASTER.wpj`: flag any `error:` lines or "not attached to a fixed/control point" warnings, and explain that `jktz-survex-stats` alone does not enforce the full warning-free validation contract
