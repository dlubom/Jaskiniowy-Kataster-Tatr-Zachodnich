# Skill: docker-exports

Builds the `jktz-survex` Docker image and/or runs the release export pipeline locally, producing `.3d`, `.dxf`, `.shp`, and `.err` files in `<OUTDIR>/` (default `exports/`), with version embedded in filenames.

## When to use

- When you want to generate export files locally before or after a release (same pipeline as GitHub Actions).
- When the Docker image needs to be rebuilt (e.g. after changing `SURVEX_VERSION` in `Dockerfile.survexImage-release` or `SURVEX_COMMIT` in `Dockerfile.survexImage-commit`, or after a `pyproject.toml` / `uv.lock` change since the image pre-fetches Python deps at build time).

## Dockerfile variants

Two `Dockerfile.survexImage-*` variants are available — both produce an image tagged `jktz-survex`:

- **`Dockerfile.survexImage-release`** — builds Survex from the official release tarball (`survex.com`). **Stable**, default for release exports.
- **`Dockerfile.survexImage-commit`** — builds Survex from a pinned commit of `ojwb/survex`. Use only when testing unreleased upstream fixes.

Default to the `release` variant unless the user asks for the commit-based image.

## Usage

```
/docker-exports [VERSION] [OUTDIR]
/docker-exports --build-only
/docker-exports --run-only [VERSION] [OUTDIR]
```

- `VERSION` — version label embedded in output filenames, e.g. `v1.2.6`. Defaults to `local`.
- `OUTDIR` — output directory (host-relative, must be inside the bind-mounted repo). Defaults to `exports`.
- `--build-only` — only build (or rebuild) the Docker image, do not run exports.
- `--run-only` — skip the build step and run exports immediately (image must already exist).

Examples:
```
/docker-exports v1.2.6
/docker-exports v1.2.6 exports/pr-check
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
- Set `OUTDIR` from the second non-flag argument, defaulting to `exports`. If supplied, omit it from the container command when it equals `exports` to match CI behaviour exactly.

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
docker run --rm -v "$(pwd):/project" jktz-survex uv run jktz-exports VERSION [OUTDIR]
```

Replace `VERSION` (and `OUTDIR` if non-default) with the actual values. Show the full output.

`OUTDIR` is resolved **inside the container**, so it must point to a path within the bind-mounted `/project` (i.e. a host-relative path inside the repo) — otherwise the files won't appear on the host.

**Windows note:** `$(pwd)` in Git Bash produces a Unix-style path (e.g. `/c/Users/...`) that Docker Desktop on Windows cannot resolve. If the bind mount fails, use the explicit Windows path instead.

```bash
docker run --rm -v "C:/path/to/repo:/project" jktz-survex uv run jktz-exports VERSION [OUTDIR]
```

### 4. Report results

After a successful run, tell the user where the artefacts landed. The pipeline writes files **directly into `<OUTDIR>/`** — the version is embedded in each filename:

```
<OUTDIR>/
├── JKTZ-<VERSION>-cavern-log.txt
├── JKTZ-<VERSION>.3d
├── JKTZ-<VERSION>.err
├── JKTZ-<VERSION>.dxf
├── JKTZ-<VERSION>-all.shp   (+ .shx, .dbf, .prj sidecars)
└── caves/
    ├── <CaveName>.shp       (+ sidecars)
    └── ...
```

Surface to the user:
- The output directory path (e.g. `exports/`).
- Any `error:` or warning lines from `<OUTDIR>/JKTZ-<VERSION>-cavern-log.txt`.

If the export step fails, show the error and suggest checking the cavern log for details.
