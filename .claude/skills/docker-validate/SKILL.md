# Skill: docker-validate

Runs the validation pipeline locally using Docker (same `jktz-survex` image as `/docker-exports`, built from `docker/Dockerfile.survexImage-release` by default, or `docker/Dockerfile.survexImage-commit` for the commit-pinned variant). Checks SRV file naming, invalid directives, compiles with cavern, and reports any unattached-station errors. Mirrors the Linux job in GitHub Actions `validate.yml`.

## When to use

- Before committing or pushing, to catch validation errors locally.
- When you want to reproduce exactly what GitHub Actions runs on Linux.
- When `cavern` is not installed locally but Docker is available.

## Usage

```
/docker-validate
```

No arguments — always validates the current working tree.

## Steps

All commands must be run from the **repository root**.

### 1. Ensure the Docker image exists

```bash
docker image inspect jktz-survex > /dev/null 2>&1 && echo "exists" || echo "missing"
```

If missing, build it (first time takes several minutes; subsequent builds are near-instant due to layer caching). If the image was built before the bash→Python migration, **rebuild it** so the image picks up `uv` and the `jktz` package. Default — stable release variant:

```bash
docker build -f docker/Dockerfile.survexImage-release -t jktz-survex .
```

Use the commit-based variant only if the user explicitly requested it:

```bash
docker build -f docker/Dockerfile.survexImage-commit -t jktz-survex .
```

Show the build output. If the build fails, stop and report the error.

### 2. Run the validation

```bash
docker run --rm -v "$(pwd):/project" jktz-survex uv run jktz-validate
```

**Windows note:** `$(pwd)` in Git Bash produces a Unix-style path (e.g. `/c/Users/...`) that Docker Desktop on Windows cannot resolve. If the bind mount fails, use the explicit Windows path instead.

```bash
docker run --rm -v "C:/path/to/repo:/project" jktz-survex uv run jktz-validate
```

Show the **full output** to the user.

### 3. Report results

- If the script exits 0: tell the user validation passed and highlight any warnings from the cavern output.
- If the script exits non-zero: show which check failed and suggest a fix (e.g. rename `.srv` → `.SRV`, remove `#<` directives).
