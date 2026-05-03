# Skill: docker-exports

Builds the `jktz-survex` Docker image and/or runs the release export pipeline locally, producing `.3d`, `.dxf`, `.shp`, and `.err` files in `exports/JKTZ-<VERSION>/`.

## When to use

- When you want to generate export files locally before or after a release (same pipeline as GitHub Actions).
- When the Docker image needs to be rebuilt (e.g. after changing `SURVEX_VERSION` in `Dockerfile.survexImage-release` or `SURVEX_COMMIT` in `Dockerfile.survexImage-commit`).

## Dockerfile variants

Two `Dockerfile.survexImage-*` variants are available — both produce an image tagged `jktz-survex`:

- **`Dockerfile.survexImage-release`** — builds Survex from the official release tarball (`survex.com`). **Stable**, default for release exports.
- **`Dockerfile.survexImage-commit`** — builds Survex from a pinned commit of `ojwb/survex`. Use only when testing unreleased upstream fixes.

Default to the `release` variant unless the user asks for the commit-based image.

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

Default — stable release variant:

```bash
docker build -f docker/Dockerfile.survexImage-release -t jktz-survex .
```

Use the commit-based variant only if the user requested it:

```bash
docker build -f docker/Dockerfile.survexImage-commit -t jktz-survex .
```

- The first build compiles Survex from source and takes several minutes.
- Subsequent builds are near-instant due to Docker layer caching (unless `SURVEX_VERSION` / `SURVEX_COMMIT` changed).
- Show the full build output to the user.
- If the build fails, stop and report the error — do not proceed to the run step.

### 3. Run the export (if `DO_RUN=true`)

```bash
docker run --rm -v "$(pwd):/project" jktz-survex bash docker/exports.sh VERSION
```

Replace `VERSION` with the actual value. Show the full output.

**Windows note:** `$(pwd)` in Git Bash produces a Unix-style path (e.g. `/c/Users/...`) that Docker Desktop on Windows cannot resolve. If the bind mount fails, use the explicit Windows path instead.

```bash
docker run --rm -v "C:/path/to/repo:/project" jktz-survex bash docker/exports.sh VERSION
```

### 4. Report results

After a successful run, tell the user:
- Output directory: `exports/JKTZ-<VERSION>/`
- Any `error:` or warning lines from the cavern log (found in `exports/JKTZ-<VERSION>/JKTZ-<VERSION>-cavern.log`)

If the export step fails, show the error and suggest checking the cavern log for details.
