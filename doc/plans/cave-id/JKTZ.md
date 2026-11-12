# CAVE_ID w JKTZ — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Zastąpić niejednoznaczne CAVE_ID referencjami do GPS i oddzielić domiary powierzchniowe.
**Architecture:** Pełny snapshot GPS zasila render i walidator referencji. Zatwierdzone mapowanie poprzedza atomowe przełączenie metadanych i danych; kompilatory potwierdzają zachowanie geometrii.
**Tech Stack:** Python, uv, sqlite3, pytest; Walls SRV/WPJ, Survex i natywny Walls.
**Spec:** [SPEC.md](SPEC.md) — jedyne źródło wspólnego kontraktu.

## Global Constraints

- Zakres bieżącej PR: `codex/cave-id-gps`, baza `master`; kontynuuj z żywego HEAD PR.
- `_RAW` pozostaje archiwum. Zachowaj bajty materiałów i źródłowe identyfikatory stacji.
- Każdy SRV obejmuje jeden rodzaj pomiarów: `underground` albo `surface`.
- GPS jest jedynym miejscem nadawania ID jaskiń i obiektów.
- Python uruchamiaj przez `uv`, testy/bramki na 3.12; zgodność runtime >=3.9 pozostaje.
- Progi: 95% line, 90% branch, CRAP <=25, 81% mutation w każdym skonfigurowanym module.
- Hooki są obowiązujące. Merge, tag i release wymagają osobnego polecenia.
- Wykonuj wyłącznie wskazaną kartę. Zmiany wymagające nowej decyzji zapisuj, nie zgaduj.

## Review Focus

- System bez własnego otworu: poprawny CAVE_ID przechodzi dzięki `caves` (J02/J03).
- Nowe wydanie GPS w trakcie walidacji: render i kontrola pozostają na jednym snapshotcie (J02/J05).
- Niefiksowany otwór: OBJECT_REF nie dodaje ani nie aktywuje #fix (J03/J04).
- Podział pliku z datami, units i prefixami: zachowane pomiary i geometria (J04).
- Istniejące, lecz błędnie przypisane ID: jawne referencje ujawniają sprzeczność;
  pozostałe pliki wymagają dowodu w mapowaniu, nie tylko wyszukania ID (J01/J03).

## Stan kart i zależności

| Karta | Wynik | Warunek startu | Stan |
| --- | --- | --- | --- |
| J01 | [Mapowanie i lista podziałów](MAPPING.md) | Aktualny HEAD tej PR | 210 potwierdzonych wierszy; GPS v2.1.2 sprawdzone J02; migracja i podmiana ID fixa bez przesunięcia wykonane w J04 |
| J02 | Wspólny snapshot GPS i czytnik katalogu | G02 preview z sumami albo G04 release | wykonana, sprawdzona na podglądzie G03 |
| J03 | Testowalny kontrakt tożsamości i referencji | J02 | wykonana |
| J04 | Migracja SRV, CLI i podziały | J01 bez nierozstrzygniętych wierszy; J03; G04 | wykonana; wyniki i końcowe CI w PR #163 |
| J05 | Włączenie pełnej bramki i dowody końcowe | J04 | bramka wdrożona; końcowe dowody CI i ZIP w opisie PR #163 |

G01–G04 opisuje [plan GPS](GPS.md). J02/J03 nie przełączają jeszcze produkcyjnej
bramki na nowy kontrakt, dzięki czemu każda karta może skończyć się zielonym
commitem. J04 przełącza parser wraz ze wszystkimi aktywnymi danymi; J05
obowiązkowo włącza walidację sieciową. PR #163 pozostaje draft po J05; scalenie wymaga osobnego polecenia.

## J01 — mapowanie wszystkich aktywnych plików

**Files:** utwórz `doc/plans/cave-id/MAPPING.csv` i `MAPPING.md` obok tego planu.
Źródła: `Poligony/`, `KATASTER.wpj`, `OTWORY.SRV.j2` oraz pełny katalog GPS.
Nie zmieniaj jeszcze SRV, WPJ ani kodu. Narzędzia jednorazowe trzymaj poza repo.

**Interfaces:** CSV UTF-8, jeden wiersz na docelowy plik: `source_path`,
`source_sha256`, `target_path`, `survey_kind`, `cave_id`, `object_refs`,
`evidence`, `status`. Podział ma kilka wierszy z tym samym source_path;
`object_refs` zapisuje tablicę JSON stringów `station=object_id`.
Statusy: `confirmed`, `needs_decision`, `missing_gps`. MAPPING.md dokumentuje
podstawę, SHA obu repo, tag/snapshot GPS, sesje i bloki przenoszonych pomiarów.

- [x] Zapisz bazę: status Git/PR, pełny wykaz aktywnych SRV według
  `is_active_srv_path`, sumy materiałów RAW oraz wersje kompilatorów.
- [x] Rozlicz każdy aktywny SRV i wszystkie wystąpienia pomiarów powierzchniowych;
  skontroluj także pliki, których nazwa nie sugeruje domiaru. Wypełnij mapowanie
  na podstawie źródeł, oznaczeń otworów i jawnych relacji GPS.
- [x] Rozpisz podziały, zaczynając od LODMAL i POW_ORM. Dla każdego określ
  plik docelowy, sesje, prefixy, units, date/declination, segmenty i SOURCE_REF.
- [x] Zweryfikuj, że zbiór source_path dokładnie odpowiada inwentarzowi,
  target_path są unikalne, hashe aktualne, a każdy `confirmed` ma dowód.
  Wszystkie luki pokaż użytkownikowi; karta może zakończyć audyt z lukami,
  lecz takie zakończenie nie odblokowuje J04.
- [x] Commit/push dokumentacji do tej PR, podaj liczbę źródeł, wyników i luk.
  Zatrzymaj się po J01.

## J02 — snapshot wydania GPS

**Files:** utwórz `src/jktz/gps_catalog.py`, `tests/test_gps_catalog.py`;
zmień `src/jktz/entrances/render.py`, `tests/test_render_otwory.py` tylko
w zakresie ponownego użycia pobranego CSV. Użyj obecnego mechanizmu requestów,
zachowując ochronę tokena i brak wykonywania treści szablonu.

**Interfaces:** `GpsSnapshot` zawiera tag, release ID, ścieżki CSV/GPKG i SHA-256;
`Catalogue` zawiera słowniki `caves` i `objects`. Publiczne funkcje:
`download_snapshot(repo: str, destination: Path) -> GpsSnapshot`,
`load_snapshot(directory: Path) -> GpsSnapshot`,
`read_catalogue(snapshot: GpsSnapshot) -> Catalogue`,
`effective_cave_id(cave_id: str, catalogue: Catalogue) -> str`.
Lokalny `snapshot.json` zapisuje pochodzenie i sumy; jest artefaktem cache/CI,
nie nowym plikiem wydania GPS. `render_entrances(..., csv_path=...)` pozostaje
wejściem do renderu z tego snapshotu.

- [x] Dodaj testy: `test_catalogue_contains_system_without_object`,
  `test_snapshot_resolves_release_once`, `test_snapshot_rejects_hash_mismatch`,
  `test_catalogue_rejects_missing_tables`, `test_catalogue_rejects_dangling_or_cyclic_system`.
  Użyj fixture SQLite z całym wymaganym schematem; system C-0295 nie ma obiektu.
  Dwa kolejne wywołania API latest zwracają różne wydania; oczekiwane jest
  dokładnie jedno wywołanie i oba pliki z pierwszej odpowiedzi.
- [x] Uruchom `uv run --python 3.12 pytest -q tests/test_gps_catalog.py` i
  potwierdź niepowodzenie z powodu brakującego zachowania.
- [x] Zaimplementuj interfejsy, odczyt SQLite read-only, walidację wymaganych
  kolumn/ID/relacji oraz offline manifest. Błędy nie usuwają wcześniejszych
  wejść użytkownika. Token pozostaje ograniczony do api.github.com.
- [x] Uruchom testy obu modułów i `uv run --python 3.12 jktz-quality`.
  Odnotuj odczyt prawdziwego GPKG z dokładnego SHA preview/release GPS.
- [x] Commit/push, uaktualnij stan karty i zatrzymaj się po J02.

W próbie offline użyto [podglądu G03 z PR GPS #49](https://github.com/dlubom/gps-kataster-obiektow-tatr/actions/runs/43102249228/artifacts/13892347441)
dla HEAD `881c96425514c1918253cb73516a3062f9b6a0ef`. Z jednego ZIP-a
zweryfikowano `preview.json` oraz zgodność `SHA256SUMS` z oboma plikami
i przypiętymi sumami.

| Plik | SHA-256 |
| --- | --- |
| `katalog.gpkg` | `e2f2a01a94642f529203f2af3d377b0484f238b2d073d443a8fb0a45078f822c` |
| `best-measurements.csv` | `c69c858f024a368852eb149bc4031db9f9e29d7cbfef121dcd35812c69d41568` |

Lokalny `snapshot.json` zawiera `repo`, `tag`, `release_id` i mapę `assets`
z polem `sha256` dla każdej nazwy pliku. Pobranie wydania zapisuje także
`id` obu artefaktów. W próbie podgląd oznaczono tagiem
`pr-preview-49-881c96425514c1918253cb73516a3062f9b6a0ef` i `release_id: null`.

Odczyt dał 1026 jaskiń i 1029 obiektów. `C-0295` nie ma własnego obiektu.
`MLZ-0068` należy do `C-0648`, której końcowym systemem jest `C-0295`.
Render z tego CSV odtworzył 87 fixów zgodnie z wersjonowanym `OTWORY.SRV`.

## J03 — tożsamość pomiaru i referencje

**Files:** utwórz `src/jktz/metadata/identity.py`,
`src/jktz/validation/catalogue.py`, `tests/test_survey_identity.py`,
`tests/test_validation_catalogue.py`. Produkcyjny parser nagłówków i aktywne
SRV pozostają na starym kontrakcie do wspólnego przełączenia w J04.

**Interfaces:** `SurveyIdentity(kind, cave_id, object_refs)` i
`ObjectRef(station_id, object_id)` są niezmiennymi rekordami.
`parse_identity(single: dict[str, str], repeated: dict[str, list[str]]) -> SurveyIdentity`
stosuje tabelę ze specyfikacji. `validate_identities(identities: Mapping[Path, SurveyIdentity],
catalogue: Catalogue, entrance_bindings: Mapping[str, str]) -> list[str]`
zwraca komplet stabilnie uporządkowanych diagnostyk. `check_reference_stations(
identities: Mapping[Path, SurveyIdentity], station_names: set[str]) -> list[str]`
sprawdza nazwy uzyskane z kompilatora, z jego udokumentowaną normalizacją.
Sprawdzenie wejść nie wymaga parsowania pełnej składni pomiarowej Walls.

- [x] Dodaj testy pozytywne Bańdziocha i systemu Śnieżnej oraz testy:
  `test_surface_links_same_or_different_caves`, `test_wrong_existing_cave_is_rejected`,
  `test_surface_requires_reference_and_forbids_cave_fields`,
  `test_conflicting_station_binding_is_rejected`, `test_missing_station_is_rejected`,
  `test_referenced_object_requires_cave`,
  `test_unfixed_reference_does_not_require_best_or_fix`,
  `test_unknown_kind_and_legacy_cave_ids_are_rejected`.
  Sprawdź brak SURVEY_KIND, puste ID, błędny separator i duplikaty OBJECT_REF.
- [x] Uruchom nowe testy i potwierdź brak implementowanego zachowania.
- [x] Zaimplementuj podane funkcje. Odróżnij walidację powiązań od geometrii;
  wynik nie dopisuje fixów i nie zmienia źródłowego przypisania obiektu w GPS.
  Nie wyprowadzaj referencji z samych nazw katalogów/prefiksów.
- [x] Uruchom nowe testy oraz `uv run --python 3.12 jktz-quality`.
- [x] Commit/push, uaktualnij stan i zatrzymaj się po J03.

Sprawdzono pięć referencji Bańdziocha, Wielkiej Śnieżnej i Lodowej
Małołąckiej na tym samym podglądzie GPS co w J02 i na nazwach stacji z
Survex 1.4.24. `LodowaMalolacka:31` występuje w wyniku kompilacji bez
aktywnego fixu. Osobny test odczytuje `MLW-0024` z katalogu z pustym CSV
Best. Porównanie nazw zachowuje wielkość liter i uwzględnia zapis pustych
poziomów prefiksu opisany w instrukcji Survex.

## J04 — przełączenie metadanych i wydzielenie powierzchni

**Files:** zmień `src/jktz/metadata/srv.py`, `src/jktz/cli/srv_metadata.py`,
`src/jktz/validation/metadata.py`, ich istniejące testy, aktywne SRV zgodnie
z MAPPING.csv, `KATASTER.wpj`, `AGENTS.md`, odpowiednie `.agents/skills/`
oraz `CHANGELOG.md` pod Unreleased. OTWORY zmieniaj tylko w zakresie jawnie
uzasadnionego mapowania; ta migracja nie aktualizuje automatycznie współrzędnych.
W skillach zmień co najmniej `add-cave/SKILL.md` i `svx-to-srv/SKILL.md`:
oddziel numer inwentarzowy używany do wyszukiwania PIG od nowego `--cave-id`.

**Interfaces:** parser/formatter używa `parse_identity`. CLI otrzymuje
`--survey-kind underground|surface` i powtarzalne `--object-ref station=object_id`;
`--cave-id`/`--cave-name` są wymagane tylko dla underground i zabronione dla surface.
`--dry-run` oraz atomowy zapis zachowują kontrakt. Brak SURVEY_KIND w aktywnym
pliku jest błędem; nie zostawiaj ścieżki zgodności dla WPJ/T./ROBOCZE.

- [x] Odśwież hashe źródeł z J01. Zmiana któregokolwiek wejścia wymaga
  ponownego przeglądu jego mapowania. Potwierdź G04 i wszystkie decyzje mapowania.
- [x] Dodaj regresje parsera/formatter/CLI dla obu rodzajów, zachowania bajtów
  treści, niezmienionego pliku po błędzie i `--dry-run`. Uruchom je przed zmianą kodu.
- [x] Zaimplementuj nowy kontrakt i przygotuj całą migrację przed commitem.
  Nie twórz commita z parserem odrzucającym niemigrowane aktywne dane.
- [x] Przenieś sesje powierzchniowe do osobnych plików, m.in. `LODMAL_POW.SRV`.
  Zachowaj skuteczny kontekst dyrektyw i zakresy SOURCE_REF, unikalny SURVEY_ID,
  kodowanie/EOL. Zamknij Walls przed zmianą WPJ. Górny otwór LODMAL pozostaje
  niefiksowany; samo OBJECT_REF nie upoważnia do zmiany OTWORY.
- [x] Użyj `$verify-cave-refactor` i `$walls-validate`: porównaj wszystkie
  rekordy z krotnością, komplet nazwanych stacji/odcinków, geometrię i semantykę
  powierzchni przed/po na tym samym snapshotcie i wersjach narzędzi.
  Zachowaj dowody w `.verification/` i ich podsumowanie dostępne w PR.
- [x] Uruchom testy parsera/CLI/metadata, `uv run --python 3.12 jktz-quality`,
  `uv run --python 3.12 jktz-mutation`, `uv run --python 3.12 jktz-validate`.
  Brak danych do mapowania albo różnica geometrii blokuje zakończenie J04.
- [x] Commit/push całego spójnego przełączenia, rozlicz MAPPING.csv i zatrzymaj się.

## J05 — pełna bramka i zamknięcie wdrożenia

**Files:** `src/jktz/validation/suite.py`, `src/jktz/cli/validate.py`,
`src/jktz/cli/render_otwory.py`, `tests/test_validation_suite.py`,
`tests/test_workflow_configuration.py`, `.github/workflows/validate.yml`,
`.github/workflows/release.yml`, `AGENTS.md` i instrukcje dodawania jaskiń.
Dodaj `read_station_names(three_d: Path) -> set[str]` w
`src/jktz/validation/catalogue.py`; użyj `exports.tools.survexport` do
tymczasowego CSV i odczytaj kolumnę nazwy według lokalnego `survexport.rst`.
Wywołanie kompilatora/eksportera pozostaje w istniejącej warstwie narzędzi.

**Interfaces:** `run_validation(context)` przygotowuje jeden `GpsSnapshot`,
przekazuje jego CSV rendererowi i Catalogue walidatorowi. CLI pełnej walidacji
oraz renderu przyjmuje `--gps-snapshot DIR` dla odtworzenia; jednoczesne
`--csv` i `--gps-snapshot` jest błędem. CI przygotowuje snapshot raz i przekazuje
go jako artefakt między jobami. W wydaniu to samo wejście zasila kontrolę i eksport.

- [x] Dodaj regresje integracyjne: jedna odpowiedź release/latest na run,
  snapshot współdzielony przez render i metadata, brak tabel blokuje publikację,
  błąd ID nie nadpisuje OTWORY, brak stacji blokuje eksport po kompilacji.
  Uruchom i potwierdź oczekiwane niepowodzenia przed podłączeniem bramki.
- [x] Podłącz walidację wszystkich aktywnych SRV i referencji. Odczytaj nazwy
  stacji z wyniku `dump3d`/`survexport`, zgodnie z lokalną dokumentacją wersji;
  nie twórz konkurencyjnego parsera całego Walls. Obsłuż Windows i POSIX.
- [x] Uruchom quality, mutation, pełne jktz-validate i natywny Walls; ponownie
  sprawdź kompletność mapowania, RAW oraz brak plików mieszanych.
- Końcowy dowód: [opis PR #163](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/pull/163)
  wiąże terminalny CI i sprawdzony ZIP z dokładnym HEAD oraz osobnym SHA
  testowego merge. W opisie są także wyniki lokalne i ograniczenia.
  PR pozostaje draft.

J05 korzysta z jednego snapshotu CSV/GPKG na przebieg. Tryb offline weryfikuje
sumy z manifestu. Walidacja sprawdza wszystkie aktywne SRV i powiązania
szablonu, a po kompilacji wczytuje pełne nazwy stacji z CSV Survex.
Pakowanie PR i wydania używa eksportów zachowanych po pełnej walidacji.
Dane SRV, WPJ, OTWORY, DZX, RAW i mapowanie zachowują stan J04.


Lokalne dowody w głównym checkoutcie: `.verification/2026-11-12-cave-id-j05/`.
Walidacja i pakiet lokalny użyły GPS v2.1.2 (release ID 442948071);
mapowanie 207 → 210 (205 underground, 5 surface), 83 aktywne fixy,
12 112 stacji, 18 554 odcinków, w tym 41 powierzchniowych.
Workflow tagu nie został uruchomiony; ścieżkę pakowania sprawdzono lokalnie
i przez paczkę PR. Przyjęcie snapshotu nie rozstrzyga tożsamości pliku bez
jawnego otworu; przypisania tych plików wynikają z zatwierdzonego mapowania.
