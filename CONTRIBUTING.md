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

Progi, zakres, raporty i reguły pracy opisuje [polityka jakości Pythona](doc/PYTHON_QUALITY.md).
Główna bramka lokalna to `uv run jktz-quality` (95% linii, 90% gałęzi,
CRAP <= 25); mutacje: `uv run jktz-mutation` (81% na moduł rdzenia, POSIX,
Python >= 3.10; środowisko zgodne z CI: `uv sync --locked --python 3.12`).

```bash
uv run pytest -q
uv run ruff format --check src scripts tests .agents/skills
uv run ruff check src scripts tests .agents/skills
uv run jktz-render-otwory --check
uv run jktz-validate
```

Domyślnym agentem projektu jest Codex. Instrukcje w `AGENTS.md` opisują kontrakty
danych Walls/Survex, `_RAW`, metadanych i publikacji wydań. Skille znajdują się
w `.agents/skills/`; można wywołać je w poleceniu dla Codex, np.
`$docker-validate`. Skrypty pomocnicze skilli uruchamiaj przez `uv run python`.
Hooki Git działają niezależnie od agenta i wymagają instalacji powyższym
skryptem. Projekt korzysta z modelu i uprawnień wybranych w ustawieniach Codex.

Dokumentacja Codex: [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md),
[skille](https://learn.chatgpt.com/docs/build-skills).

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

See the [Python quality policy](doc/PYTHON_QUALITY.md) for scope and enforcement.
Run `uv run jktz-quality` (95% lines, 90% branches, CRAP <= 25) and
`uv run jktz-mutation` (81% per core module; POSIX and Python >= 3.10).
Use `uv sync --locked --python 3.12` to match CI.

```bash
uv run pytest -q
uv run ruff format --check src scripts tests .agents/skills
uv run ruff check src scripts tests .agents/skills
uv run jktz-render-otwory --check
uv run jktz-validate
```

Codex is the default project agent. Read `AGENTS.md`, which defines the Walls/Survex, `_RAW`,
metadata, and release contracts for this repository. Skills live in
`.agents/skills/`; invoke them in a Codex prompt, e.g. `$docker-validate`.
Run skill helpers through `uv run python`. Git hooks work independently of
the agent and must be installed using the bootstrap above. The project uses
the model and permissions selected in your Codex settings.

Codex documentation: [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md),
[skills](https://learn.chatgpt.com/docs/build-skills).
