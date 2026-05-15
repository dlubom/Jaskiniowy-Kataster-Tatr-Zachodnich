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

## Walidacja projektu

```bash
docker run --rm -v "$(pwd):/project" jktz-survex bash scripts/validation/validate.sh
```

## Eksport

```bash
docker run --rm -v "$(pwd):/project" jktz-survex bash scripts/exports/exports.sh v1.2.6
```

Podmień `v1.2.6` na dowolna etykietę wersji.
