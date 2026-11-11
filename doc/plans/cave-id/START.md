# CAVE_ID — prompty do nowych okien

Wklej odpowiedni blok w oknie przypisanym do danego projektu. Pierwsze okna
mogą pracować niezależnie: JKTZ wykonuje inwentaryzację J01, GPS przygotowuje G01.
Po zakończeniu karty kolejne zlecenie wskazuje następną kartę z planu.

## Okno JKTZ — rozpocznij od J01

```text
Kontynuujemy uzgodnioną migrację CAVE_ID w repozytorium
dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich.

Znajdź istniejącą draft PR dla gałęzi codex/cave-id-gps. Sprawdź lokalny Git,
worktree, aktualny origin/master i żywy zdalny HEAD tej PR. Pracuj od HEAD PR
w osobnym worktree; zachowaj cudze zmiany i nie przywracaj starszego SHA.

Przeczytaj AGENTS.md oraz z tej PR:
- doc/plans/cave-id/SPEC.md
- doc/plans/cave-id/JKTZ.md

Wykonaj wyłącznie J01: pełne mapowanie aktywnych SRV do identyfikatorów GPS
oraz lista wydzieleń domiarów powierzchniowych. Aktualne, kompletne dane GPS
możesz odczytać z jego kanonicznego katalogu; zapisz SHA źródła. Nie zakładaj,
że best-measurements.csv zawiera wszystkie jaskinie/systemy.

Uzgodniony model jest w SPEC.md. GPS nadaje ID, system ma wspólne CAVE_ID,
pomiary powierzchniowe trafiają do osobnych plików, a OBJECT_REF wiąże
stację z obiektem bez dodawania fixu. Niejednoznaczne tożsamości wymagają
źródeł i decyzji, nie dopasowania po podobnej nazwie lub geometrii.

Dostarcz MAPPING.csv i MAPPING.md zgodnie z J01. Rozlicz każdy aktywny plik,
wszystkie podziały, źródła przypisań i nierozstrzygnięte przypadki.
Na tym etapie zmienia się tylko dokumentacja. Po wymaganych kontrolach
wykonaj commit/push do istniejącej PR i zaktualizuj stan J01.

Zakończ po J01. Podaj dokładny zdalny SHA, stan CI i liczbę brakujących
rozstrzygnięć. Nie zaczynaj J02, nie migruj danych i nie wykonuj merge,
tagowania ani wydania. Kontynuację zlecę osobno.
```

## Okno GPS — rozpocznij od G01

```text
Pracujemy w dlubom/gps-kataster-obiektow-tatr nad pełnymi tabelami caves
i objects w istniejącym katalog.gpkg, potrzebnymi do spójnego CAVE_ID w JKTZ.

Sprawdź Git, fetch origin, aktualny origin/main oraz otwarte PR. Jeśli PR
tego zadania już istnieje, kontynuuj jej żywy HEAD w osobnym worktree;
w przeciwnym razie zacznij izolowaną gałąź od aktualnego origin/main.
Nie używaj starego lokalnego checkoutu jako bazy tylko dlatego, że tam
znajdujesz pliki. Przeczytaj AGENTS.md i wskazane dokumenty kanoniczne GPS.

Specyfikacja i plan są w draft PR JKTZ na gałęzi codex/cave-id-gps:
https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/tree/codex/cave-id-gps/doc/plans/cave-id
Przeczytaj SPEC.md i GPS.md z jej aktualnego HEAD. Zapisz SHA przeczytanej
specyfikacji w swojej PR, aby wskazać dokładny wspólny kontrakt.

Wykonaj wyłącznie G01 z GPS.md: pełne rekordy obiektów w ExportData oraz
testy kompletności jaskiń/obiektów, nulli i niezależności od Best.
Nie rekonstruuj katalogu z pomiarów. Kanoniczny YAML, historia, wybór Best
i współrzędne pozostają bez zmian. Kolejne G02 dopiero zapisze nowe tabele.

Po wymaganych lokalnych kontrolach wykonaj commit/push, utwórz osobną draft
PR GPS, jeżeli jeszcze jej nie ma, i powiąż ją linkiem z PR JKTZ. Opisz
ukończone G01, pozostałe G02–G04, dokładny zdalny SHA i stan CI.

Zakończ po G01. Nie zaczynaj G02. Merge, tagowanie i wydanie GPS wymagają
osobnego polecenia; przygotowany eksport nie jest jeszcze opublikowanym
wejściem dla końcowej migracji JKTZ.
```

## Kolejność dalszych zleceń

```text
JKTZ J01 (audyt) ─────────────────────────────┐
GPS G01 → G02 (preview) → G03 → [zgoda] G04  │
           │                          │      │
           └→ JKTZ J02 → J03 ─────────┴──────┴→ J04 → J05
```

Start kolejnej karty wymaga jej zależności. Jeśli użytkownik wskazuje jedną
kartę, zakończ po niej także wtedy, gdy następna wydaje się łatwa.
