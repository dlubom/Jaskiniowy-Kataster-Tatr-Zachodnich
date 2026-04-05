# Skill: docker-exports

Builds the `jktz-survex` Docker image and/or runs the release export pipeline locally, producing `.3d`, `.dxf`, `.shp`, and `.err` files in `exports/JKTZ-<VERSION>/`.

## When to use

- When you want to generate export files locally before or after a release (same pipeline as GitHub Actions).
- When the Docker image needs to be rebuilt (e.g. after changing `SURVEX_COMMIT` in `Dockerfile.releaseExports`).

## Usage

```
/docker-exports [VERSION]
/docker-exports --build-only
/docker-exports --run-only [VERSION]
```

- `VERSION` — version label for the output directory, e.g. `v1.2.6`. Defaults to `local`.
- `--build-only` — only build (or rebuild) the Docker image, do not run exports.
- `--run-only` — skip the build step and run exports immediately (image must already exist).

Examples:
```
/docker-exports v1.2.6
/docker-exports --build-only
/docker-exports --run-only v1.2.7
/docker-exports
```

## Steps

All commands must be run from the **repository root**.

### 1. Determine mode and version

- Parse the arguments:
  - If `--build-only`: set `DO_BUILD=true`, `DO_RUN=false`
  - If `--run-only`: set `DO_BUILD=false`, `DO_RUN=true`
  - Otherwise (default): set `DO_BUILD=true`, `DO_RUN=true`
- Set `VERSION` from the first non-flag argument, defaulting to `local`.

### 2. Build the Docker image (if `DO_BUILD=true`)

```bash
docker build -f docker/Dockerfile.releaseExports -t jktz-survex .
```

- The first build compiles Survex from source and takes several minutes.
- Subsequent builds are near-instant due to Docker layer caching (unless `SURVEX_COMMIT` changed).
- Show the full build output to the user.
- If the build fails, stop and report the error — do not proceed to the run step.

### 3. Run the export (if `DO_RUN=true`)

```bash
docker run --rm -v "$(pwd):/project" jktz-survex bash docker/exports.sh VERSION
```

Replace `VERSION` with the actual value. Show the full output.

On Windows the path binding requires the host path in Unix form or via `$(pwd)`. If running from Git Bash or WSL this works as-is. If `$(pwd)` fails in the user's shell, suggest the equivalent:

```bash
docker run --rm -v "${PWD}:/project" jktz-survex bash docker/exports.sh VERSION
```

### 4. Report results

After a successful run, tell the user:
- Output directory: `exports/JKTZ-<VERSION>/`
- ZIP archive: `exports/JKTZ-<VERSION>-exports.zip`
- Any `error:` or warning lines from the cavern log (found in `exports/JKTZ-<VERSION>/JKTZ-<VERSION>-cavern.log`)

If the export step fails, show the error and suggest checking the cavern log for details.
