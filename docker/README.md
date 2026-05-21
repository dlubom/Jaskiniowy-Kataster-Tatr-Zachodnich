# Docker — Budowa obrazu Survex dla kompilacji projektu

Dwa warianty — oba tworzą obraz pod tagiem `jktz-survex`:

**`Dockerfile.survexImage-release`** — buduje Survex z oficjalnego archiwum wydania (tarball z `survex.com`). Wariant **stabilny**, zalecany do generowania oficjalnych eksportów.

```bash
docker build -f docker/Dockerfile.survexImage-release -t jktz-survex .
```

**`Dockerfile.survexImage-commit`** — buduje Survex z konkretnego commita w repozytorium `ojwb/survex` (zmienna `SURVEX_COMMIT`). Do testowania niewydanych poprawek.

```bash
docker build -f docker/Dockerfile.survexImage-commit -t jktz-survex .
```

Obraz zawiera również `uv` oraz wstępnie zsynchronizowane zależności Pythona (`pyproject.toml` + `uv.lock` z repozytorium są pobierane w czasie budowy obrazu). Entrypoint wykonuje `uv sync --locked` z `/project` (bind-mount), po czym uruchamia komendę przekazaną do `docker run`.

## Walidacja projektu

```bash
docker run --rm -v "$(pwd):/project" jktz-survex uv run jktz-validate
```

## Eksport

```bash
docker run --rm -v "$(pwd):/project" jktz-survex uv run jktz-exports v1.2.6
```

Podmień `v1.2.6` na dowolna etykietę wersji.

## Spakowanie wydania (ZIP)

```bash
docker run --rm -v "$(pwd):/project" jktz-survex uv run jktz-build-zip v1.2.6
```
