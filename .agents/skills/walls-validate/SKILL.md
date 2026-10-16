---
name: walls-validate
description: Use when a review needs actual Walls compilation of KATASTER.wpj on Windows or macOS/Wine, native diagnostics, or confirmation that Windows CI tested Walls rather than only Survex.
---

# Native Walls validation

Use the repository's `uv run jktz-walls-validate`. It runs the real
**Walls v2.3.0-beta.1, build 2025-09-13**, through the bundled Win32 driver.
A `cavern` result, launching Walls, or finding old NT files is insufficient.
This checks compilation, not survey provenance, geometry equivalence or visual map quality.
Use `validate-cave` or `verify-cave-refactor` for those additional questions.

## Prepare

1. Establish the reviewed SHA and working-tree status. Run from that checkout;
   the command snapshots **current disk inputs**, including uncommitted SRV edits.
   Save `git rev-parse HEAD` and `git status --porcelain` beside the run's
   evidence (in its parent directory), before and after compilation.
   For base/head comparison use separate checkouts and evidence directories.
2. Keep the checked-in entrance snapshot. Do not silently fetch/render new GPS
   coordinates during a reproducibility check.
3. Use the pinned official installer and hashes in
   [install-walls/action.yml](../../../.github/actions/install-walls/action.yml).
   On Windows that action shows the exact download/install commands; installation
   requires Windows Installer permissions. Locate `Walls32.exe` before running.
4. Use a fresh Windows CI session, or a **dedicated Wine prefix**, never the
   user's everyday prefix. The driver refuses to run if Walls is already open
   in its session. Do not close the user's app or kill all Wine processes.

The snapshot contains non-archival SRV/WPJ files and `INFO.txt`. WPJ references
must resolve inside it; absolute paths and parent traversal are rejected.
Root compilation preserves attached/detached branches as defined in the WPJ.
Detached surveys are copied but not compiled; this is not an audit of every
archival or detached survey. Use short ASCII scratch paths to avoid Walls'
Windows path limit. Originals and existing NT presentation settings stay in place.

## Windows

From the reviewed checkout, with the pinned Walls installed:

```powershell
uv sync --locked
cmake -S .agents/skills/walls-validate -B "$env:TEMP/walls-build" -A x64
cmake --build "$env:TEMP/walls-build" --config Release
$env:WALLS_EXE = 'C:\Program Files (x86)\Walls Cave Survey\Walls v2.3.0-beta.1\Walls32.exe'
$env:WALLS_DRIVER = "$env:TEMP/walls-build/Release/walls-driver.exe"
$env:WALLS_SCRATCH_ROOT = 'C:\'
uv run pytest -q tests/test_walls_native.py
uv run jktz-walls-validate --walls "$env:WALLS_EXE" --driver "$env:WALLS_DRIVER" --scratch-root C:\ --output .verification/YYYY-MM-DD-walls/head
```

Requires CMake and Visual Studio C tools. Stop on any failed setup/build/test
command. Use a **new** evidence directory on each run.

## macOS / Wine

Requires Wine and MinGW (`x86_64-w64-mingw32-gcc`). Locate the installed Windows
executable, for example under `~/.wine/drive_c/Program Files (x86)/Walls Cave Survey/`.
Its DLLs must remain beside it. Use its absolute POSIX path in `WALLS_EXE`:

```sh
uv sync --locked
export WINEPREFIX="$HOME/.wine-walls-validation"
mkdir -p "$WINEPREFIX"
export WINEDEBUG=-all MVK_CONFIG_LOG_LEVEL=0
wineboot -u
x86_64-w64-mingw32-gcc -O2 -Wall -Wextra -Werror \
  .agents/skills/walls-validate/driver.c -o /tmp/walls-driver.exe -luser32
export WALLS_EXE='/absolute/path/to/Walls32.exe'
export WALLS_DRIVER=/tmp/walls-driver.exe WALLS_WINE=wine WALLS_SCRATCH_ROOT=/tmp
uv run pytest -q tests/test_walls_native.py
uv run jktz-walls-validate --walls "$WALLS_EXE" --driver "$WALLS_DRIVER" \
  --wine wine --scratch-root /tmp --output .verification/YYYY-MM-DD-walls/head
```

The driver uses Wine's default `Z:` mapping to the POSIX filesystem. A custom
mapping or inaccessible graphical session is an infrastructure failure; do not
report it as a survey error or substitute a Survex pass.

## Read the evidence

Read `result.json` and `driver.log`, including on failure. A preparation
failure (e.g. a missing source/compiler or an already existing output directory)
may occur before these files exist: preserve the command's console error and
report the check as failed. Report the reviewed
SHA, actual executable hash/build, result, diagnostics and evidence path.
`project/` preserves the input copy and generated outputs. Keep evidence under
this checkout's ignored `.verification/` (or the user's explicit destination).

A pass requires all of these:

- Own child process, supported build, root selected and `Recompile item` invoked.
- Completed Review state, no unexpected modal dialog, normal process shutdown.
- Five new, nonempty `NTA/NTN/NTP/NTS/NTV` files in a newly created scratch tree.
- No nonempty Walls `.LOG` and no changed input hashes.

Timeouts, errors, warnings and unrecognized states fail. Only the startup
“Tip of the Day” is automatically dismissed. Default timeout is 180 seconds
(`--timeout`, at most 1800). Never reuse old results as proof of a fresh run.

**Duplicate-vector audit is separate**, as agreed for CI. Normal compilation
uses Walls' startup default, `Look for Duplicates` off. Add `--duplicates` and
use a new evidence directory for the stricter audit; a duplicate dialog fails
that run and records both source locations. Do not average or discard independent
surveys merely to make this check pass.

## CI and maintenance

`walls-windows` installs the pinned MSI, builds this driver, runs real consumer fixtures (success, syntax error, duplicate fix warning, duplicate leg,
timeout and recovery),
then recompiles Kataster. Failures block the PR package. Evidence is uploaded
on success and failure, including checkout and PR-head SHAs. This job explicitly checks out PR head;
verify both recorded SHAs equal the final pushed SHA on PR runs; the existing Windows Survex job is a separate check.

Driver message IDs and UI signals are version-specific. Sources:
[resource.h](https://github.com/wallscavesurvey/walls/blob/v2.3.0-beta.1/Walls32/resource.h),
[prjview.cpp](https://github.com/wallscavesurvey/walls/blob/v2.3.0-beta.1/Walls32/prjview.cpp),
[compile.cpp](https://github.com/wallscavesurvey/walls/blob/v2.3.0-beta.1/Walls32/compile.cpp).
When upgrading Walls, recheck these contracts and rerun the positive and negative
fixtures on native Windows. Merely changing the accepted title is insufficient.
