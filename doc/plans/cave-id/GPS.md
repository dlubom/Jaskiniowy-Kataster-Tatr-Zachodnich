# Pełne tabele katalogowe GPS — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Udostępnić JKTZ wszystkie ID jaskiń, obiektów i relacje systemów w istniejącym katalog.gpkg.
**Architecture:** ExportData obejmuje pełny katalog, niezależnie od pokrycia pomiarami. Dwie tabele attributes dołączają do istniejących warstw; weryfikacja zawartości poprzedza atomową publikację.
**Tech Stack:** Python, uv, SQLite/GeoPackage, GDAL; istniejący PostgreSQL/PostGIS snapshot.
**Spec:** [SPEC.md](SPEC.md), sekcja „Kontrakt GeoPackage”.

## Global Constraints

- Praca odbywa się w `dlubom/gps-kataster-obiektow-tatr`, w osobnej PR z aktualnego origin/main.
- YAML jest źródłem prawdy; ta zmiana eksportu nie modyfikuje katalogu ani historii pomiarów.
- Warstwy `best`, `measurements` zachowują dotychczasowy kontrakt.
- Null pozostaje SQL NULL. Nazwy w eksporcie zachowują diakrytykę.
- Nie dodajemy kolejnego formatu indeksu ani pliku do wydania.
- Hooki/bramki GPS i readback wszystkich produktów pozostają obowiązujące.
- G01–G03 nie upoważniają do merge, taga ani publikacji. G04 wymaga osobnego polecenia.

## Review Focus

- Jaskinia/system bez obiektów nadal trafia do caves (G01/G02).
- Obiekt bez Best nie znika z objects; źródłem jest dataset.objects (G01/G02).
- Puste tabele i same wartości null zachowują zadeklarowany schemat (G02).
- Brak jednego rekordu lub błędne FK nie przechodzą przez porównanie samych liczników (G02).
- Błąd odczytu nowych tabel nie publikuje części zestawu ani nie zmienia starych warstw (G03).

## Stan kart

| Karta | Wynik | Stan |
| --- | --- | --- |
| G01 | Pełne dane do eksportu i testy | do wykonania |
| G02 | Tabele attributes i niezależny readback | do wykonania |
| G03 | Pełna bramka, dokumentacja i dostarczona draft PR | do wykonania |
| G04 | Wydanie GPS dostępne dla JKTZ | wymaga osobnego polecenia |

Ścieżki poniżej są względne do repo GPS. Dokumenty planu pozostają w PR JKTZ;
PR GPS zapisuje link i SHA przeczytanej specyfikacji. Bieżący stan wykonania GPS
prowadź w jego PR oraz wymaganych context/backlog; po zakończeniu nie kopiuj
do GPS historycznych kart wbrew jego AGENTS.md.

## G01 — pełny katalog w ExportData

**Files:** `src/gps_kataster_obiektow_tatr/export_data.py`,
`tests/test_export_data.py`; dostosuj miejsca konstruowania ExportData wskazane
przez wyszukanie w repo. Przeczytaj AGENTS i wskazane w nim dokumenty kanoniczne.

**Interfaces:** zachowaj `prepare_export_data(dataset, *, generated_at=None) -> ExportData`.
Dodaj `ExportData.objects: tuple[ExportRecord, ...]`, zawierające
`object_id`, `name`, `cave_id`, `category` z dataset.objects. Istniejące
`ExportData.caves` zachowuje pola używane przez Excel; writer GPKG wybierze
`cave_id`, `cave_name AS name`, `system_cave_id`. Każdy zestaw uporządkowany po ID.

- [ ] Sprawdź Git, pobierz origin i utwórz izolowaną gałąź od aktualnego
  origin/main. Sprawdź istniejące PR, aby kontynuować właściwą, jeśli już powstała.
- [ ] Dodaj testy `test_cave_without_objects_is_exported`,
  `test_object_without_best_is_in_catalogue_export`,
  `test_catalogue_rows_preserve_nulls_unicode_and_order`.
  Asercje obejmują dokładne ID i wartości, także system bez otworów.
- [ ] Uruchom `uv run --frozen pytest -q tests/test_export_data.py` i potwierdź
  niepowodzenie z powodu brakującej kolekcji/pokrycia.
- [ ] Dodaj projekcję pełnych objects bez rekonstrukcji z `selected`/`history`.
  Użyj tego samego datasetu, nie ładuj ponownie YAML i nie uruchamiaj drugiej bazy.
- [ ] Uruchom testy, Ruff format/check dla zmienionego zakresu i wymaganą
  lokalną bramkę z AGENTS. Porównaj dotychczasowe projekcje przed/po.
- [ ] Commit/push i utwórz osobną draft PR GPS, jeżeli jeszcze nie istnieje.
  Zapisz link do tego planu, ukończone G01 i następne G02. Zatrzymaj się.

## G02 — tabele i walidacja GeoPackage

**Files:** `src/gps_kataster_obiektow_tatr/geopackage.py`,
`tests/test_postgres_exports.py`, ewentualnie osobny
`tests/test_geopackage_catalogue.py` dla nowych przypadków.
Fixture `tests/fixtures/geopackage_fields.json` nadal opisuje warstwy punktowe;
nie udawaj, że nowe tabele mają ten sam schemat.

**Interfaces:** `write_geopackage(export_data: ExportData, output_path: Path)`
zapisuje wszystkie cztery tabele z jednego ExportData. Rozszerz istniejące
`verify_geopackage(path, layers, *, binary=None)` o wymagany argument nazwany
`catalogue_tables`, mapujący caves/objects na oczekiwane rekordy eksportu.
Zaktualizuj wszystkie wywołania; brak danych oczekiwanych nie pomija kontroli.

- [ ] Dodaj testy `test_gpkg_has_two_spatial_and_two_attribute_tables`,
  `test_gpkg_catalogue_preserves_all_ids_and_nulls`,
  `test_empty_gpkg_declares_catalogue_schema`,
  `test_gpkg_rejects_missing_extra_duplicate_or_changed_catalogue_row`,
  `test_gpkg_rejects_bad_catalogue_fk_or_registration`.
  Kontroluj INTEGER PK, UNIQUE domenowych ID, typy TEXT, nullability,
  gpkg_contents=attributes, brak geometrii i zgodność wszystkich wartości.
- [ ] Uruchom nowe testy i sprawdź, że wykrywają brak tabel.
- [ ] Dodaj tabele zgodnie ze specyfikacją. Utrzymuj poprawny nagłówek/wersję
  GeoPackage, FKs i rejestrację. `fid` nie zastępuje stabilnych ID domenowych.
- [ ] Rozszerz niezależny odczyt SQLite i GDAL. Sprawdzaj każdy rekord oraz
  integralność/relacje, a dotychczasowe dwie warstwy weryfikuj jak przed zmianą.
- [ ] Uruchom testy G01/G02 i pełny build. Odczytaj rzeczywisty artefakt:
  C-0295 musi istnieć nawet bez obiektu; MLZ-0068 → C-0648 → C-0295.
  Dowód obejmuje sumy plików i wszystkie rekordy, nie tylko te przykłady.
- [ ] Commit/push do PR GPS, zapisz dokładne SHA i wskazanie preview dostępnego
  dla JKTZ J02. Zatrzymaj się po G02.

## G03 — publikacja atomowa, dokumentacja i weryfikacja PR

**Files:** `tests/test_postgres_exports.py`, `tests/test_release_artifacts.py`,
`tests/test_catalog_publication_regressions.py`,
`src/gps_kataster_obiektow_tatr/release_artifacts.py` tylko jeśli integracja
wymaga zmiany; `specyfikacja_gps_kataster_obiektow_tatr_v_2.md`,
`docs/operations.md`, `CHANGELOG.md`, context/backlog zgodnie z AGENTS.

**Interfaces:** nazwa `katalog.gpkg`, zestaw 13 artefaktów i
`ReleaseArtifactsResult` pozostają. Zmienia się udokumentowana zawartość GPKG.

- [ ] Dodaj `test_catalogue_readback_failure_preserves_previous_artifact_set`:
  wymuszony błąd nowych tabel pozostawia wszystkie stare artefakty bajtowo
  identyczne. Dodaj kontrolę liczby/nazw artefaktów i niezmienionych warstw.
- [ ] Uruchom test regresyjny; jeżeli istniejąca atomowość już go spełnia,
  zachowaj test i nie zmieniaj produkcji bez potrzeby.
- [ ] Uzupełnij dokumentację schematu oraz przykład zapytania jaskinia–system.
  Nie zmieniaj źródłowego schema/catalog.sql tylko z powodu projekcji eksportowej.
- [ ] Uruchom `uv sync --frozen`, następnie
  `uv run --frozen python scripts/check_project.py --base-ref origin/main`.
  Jeśli aktualny AGENTS zmienił bramkę, użyj nowej i odnotuj różnicę.
- [ ] Push i sprawdź terminalne CI dokładnego SHA. Pobierz preview, sprawdź
  manifest/proweniencję i wszystkie 13 produktów; odczytaj GPKG, odtwórz dump.
  Porównuj warstwy semantycznie, bo cały plik GPKG celowo zmieni bajty.
- [ ] Uzupełnij PR GPS linkiem do PR JKTZ, kontraktem tabel i dowodami.
  Dostarcz tag/commit preview, SHA-256 GPKG i CSV. Zatrzymaj się przed publikacją.

## G04 — wydanie po odrębnej autoryzacji

Ta karta nie jest upoważnieniem do wydania. Po osobnym poleceniu użytkownika:

- [ ] Zastosuj aktualną procedurę release GPS i sprawdź CI dokładnego SHA.
- [ ] Pobierz opublikowane CSV i GPKG z tego samego wydania, odczytaj obie
  nowe tabele i potwierdź ich kompletność oraz sumy.
- [ ] Przekaż do PR JKTZ: URL wydania, tag, source commit, ID/nazwy artefaktów,
  SHA-256, liczby rekordów i wynik readback. To odblokowuje JKTZ J04.
