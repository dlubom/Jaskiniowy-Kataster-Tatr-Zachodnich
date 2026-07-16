# Rozwój projektu / Development

## Polski

### Pierwsze uruchomienie

Wymagane są Python 3.9 lub nowszy oraz
[`uv`](https://docs.astral.sh/uv/getting-started/installation/). Po świeżym
sklonowaniu repozytorium uruchom:

```bash
python scripts/initial-setup.py
```

To jedyny skrypt przeznaczony do uruchomienia przed instalacją środowiska.
Sprawdza obecność `uv`, wykonuje `uv sync --locked`, instaluje hooki pre-commit
i pre-push oraz informuje o brakujących narzędziach systemowych. Jest
idempotentny, więc można uruchomić go ponownie po zmianach w `uv.lock` albo
konfiguracji hooków.

Właściwe narzędzia projektu są instalowane z `src/jktz/` i udostępniane jako
polecenia `uv run jktz-*`. Nie należy dodawać kolejnych narzędzi wykonywanych po
instalacji do katalogu `scripts/`.

### Narzędzia systemowe

- Survex (`cavern`) — kompilacja sieci pomiarowej;
- GDAL (`ogr2ogr`) — budowanie i sprawdzanie shapefile;
- Docker — opcjonalny zamiennik lokalnej instalacji Survex/GDAL.

Bez Survex i GDAL szybkie testy Pythona działają, ale pełna walidacja pre-push
nie przejdzie.

### Sprawdzenie zmian

```bash
uv run pytest -q
uv run ruff format --check src scripts tests
uv run ruff check src scripts tests
uv run jktz-render-otwory --check
uv run jktz-validate
```

Agenci powinni dodatkowo przeczytać `CLAUDE.md`, ponieważ opisuje on kontrakty
danych Walls/Survex, `_RAW`, metadanych i publikacji wydań.

## English

### First-time setup

Python 3.9 or newer and
[`uv`](https://docs.astral.sh/uv/getting-started/installation/) are required.
After a fresh clone, run:

```bash
python scripts/initial-setup.py
```

This is the only script intended to run before the project environment is
installed. It verifies `uv`, runs `uv sync --locked`, installs the pre-commit
and pre-push hooks, and reports missing system tools. It is idempotent and can
be run again after changes to `uv.lock` or the hook configuration.

The actual repository tooling is installed from `src/jktz/` and exposed as
`uv run jktz-*` commands. Tools that run after environment setup should not be
added to `scripts/`.

### System tools

- Survex (`cavern`) — compiles the survey network;
- GDAL (`ogr2ogr`) — builds and validates shapefiles;
- Docker — optional alternative to installing Survex/GDAL locally.

Python tests can run without Survex and GDAL, but the full pre-push validation
will not pass without them.

### Validating changes

```bash
uv run pytest -q
uv run ruff format --check src scripts tests
uv run ruff check src scripts tests
uv run jktz-render-otwory --check
uv run jktz-validate
```

Agents should also read `CLAUDE.md`, which defines the Walls/Survex, `_RAW`,
metadata, and release contracts for this repository.
