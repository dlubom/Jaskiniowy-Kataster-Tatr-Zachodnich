# CAVE_ID — wspólny kontrakt JKTZ i GPS

Status: model uzgodniony 2026-11-11; implementacja jeszcze niewykonana.
Ta dokumentacja jest podstawą roboczej PR na gałęzi `codex/cave-id-gps`.

## Cel i decyzje

`CAVE_ID` w JKTZ identyfikuje jaskinię albo cały połączony system przez
identyfikator `cave_id` utrzymywany w `gps-kataster-obiektow-tatr`.
Wszystkie podziemne części systemu mają ID systemu. Numer inwentarzowy PIG,
identyfikator otworu i `SURVEY_ID` mają odrębne znaczenie.

- GPS jest jedynym miejscem nadawania ID jaskiń i obiektów. Nowa jaskinia
  otrzymuje tam rekord przed użyciem jej ID w JKTZ.
- Domiary powierzchniowe są osobnymi SRV. Nie mają sztucznego `CAVE_ID`;
  wskazują otwory, których dotyczą. Połączenie powierzchniowe nie tworzy systemu.
- Każdy SRV obejmuje jeden rodzaj pomiarów: `underground` albo `surface`.
  Typ `mixed` nie istnieje. Powierzchniowe części plików mieszanych wydzielamy.
- `katalog.gpkg` otrzymuje dwie pełne tabele bez geometrii: `caves`, `objects`.
  Warstwy `best`, `measurements` zachowują dotychczasowy kontrakt.
- JKTZ sprawdza tożsamość i współrzędne na jednym pobranym wydaniu GPS.
  Nieznane ID, sprzeczne relacje i niekompletny eksport powodują błąd.
- `_RAW` pozostaje archiwum. Rozdzielenie SRV zachowuje pomiary, stacje,
  jednostki, daty/deklinację, segmenty, powiązania i wynik kompilacji.

Nazwy pól SRV i sygnatury API poniżej są doprecyzowaniem wykonawczym modelu.
Nie oznaczają, że takie pola lub funkcje już istnieją.

## Źródła i stan odniesienia

| Projekt | Sprawdzony stan | Ustalenie |
| --- | --- | --- |
| JKTZ | `1e994ddc11071a0c7e8a48c16d304edb2a059596` | `metadata/srv.py` wymaga CAVE_ID/CAVE_NAME w każdym aktywnym SRV; nie weryfikuje ID w GPS |
| GPS | `3d3470f18894d7e6e9580da94764ea2643e78767` (drzewo v2.0.2) | GPKG ma dwie warstwy pomiarowe; `ExportData.caves` obejmuje pełny katalog; brak odrębnej kolekcji objects |

To punkty odniesienia, nie polecenie pracy na starym HEAD. Każde okno najpierw
sprawdza aktualną bazę i PR. Przykłady wymagające migracji: Bańdzioch ma zarówno
`WPJ:BK-…`, jak i `T.E-07.07`; `POW_ORM.SRV` ma dwa numery w jednym CAVE_ID;
`LODMAL.SRV` zawiera powierzchniowy ciąg `0–1p–2p–3p–31` i pomiary podziemne.

Potwierdzony przykład relacji GPS:

```text
MLZ-0068 (otwór) → C-0648 (Śnieżna) → C-0295 (Wielka Śnieżna)
KSZ-0112, LEJ-0002 (otwory) → C-0078 (Bańdzioch Kominiarski)
```

Istnienie ID nie dowodzi poprawnego przypisania konkretnego SRV. Mapowanie
plików bez bezpośredniej referencji otworu wymaga przeglądu źródeł w J01;
zgodność nazw, prefiksów, katalogów lub geometrii jest tylko przesłanką.

## Kontrakt GeoPackage

Obie tabele powstają z tego samego zweryfikowanego `LoadedDataset`, który
zasila pozostałe eksporty. Pełność oznacza wszystkie rekordy katalogowe,
także jaskinie bez otworów i obiekty bez wybranego pomiaru.

| Tabela | Kolumny i ograniczenia |
| --- | --- |
| `caves` | `fid INTEGER PRIMARY KEY`, `cave_id TEXT NOT NULL UNIQUE`, `name TEXT NOT NULL`, `system_cave_id TEXT NULL REFERENCES caves(cave_id)` |
| `objects` | `fid INTEGER PRIMARY KEY`, `object_id TEXT NOT NULL UNIQUE`, `name TEXT NULL`, `cave_id TEXT NULL REFERENCES caves(cave_id)`, `category TEXT NOT NULL` |

`name` jaskini pochodzi z `data.caves[].name`; `name` obiektu z `name_local`.
Null pozostaje SQL NULL. Nazwy w eksporcie zachowują diakrytykę.
`fid` służy GeoPackage; integracje używają wyłącznie `cave_id` i `object_id`.
Rekordy zapisujemy w kolejności ID, bez uzależnienia od kolejności pomiarów.

Tabele są zarejestrowane w `gpkg_contents` jako `attributes`, z pustymi
wartościami zasięgu i `srs_id`. Nie mają wpisów w `gpkg_geometry_columns`.
Wersja i deklaracje pliku muszą odpowiadać standardowi GeoPackage co najmniej
1.2. Zasady tabel i klucza całkowitego:
[OGC GeoPackage 1.4, §2.4](https://www.geopackage.org/spec140/index.html#_attributes).

Weryfikacja producenta porównuje pełne zestawy ID i wszystkie wartości ze
źródłowym snapshotem, a nie tylko liczbę rekordów. Sprawdza deklaracje tabel,
unikalność, FK, cykle systemów, integralność SQLite oraz odczyt GDAL.
Dotychczasowe kontrole geometrii i atrybutów obu warstw punktowych pozostają.
Błąd odczytu blokuje atomową publikację całego zestawu artefaktów.

Nie dodajemy kolejnego formatu indeksu ani pliku do wydania. Wybrano GPKG
zamiast osobnego JSON (łatwy tekstowy odczyt, lecz dodatkowy artefakt) i
odczytu dumpa/Excela przez JKTZ (dodatkowe wymagania dla konsumenta).

## Metadane SRV

| Pole | `underground` | `surface` |
| --- | --- | --- |
| `SURVEY_KIND` | Wymagane: `underground` | Wymagane: `surface` |
| `CAVE_ID` | Jeden istniejący ID jaskini/systemu | Nie występuje |
| `CAVE_NAME` | Opisowa nazwa jaskini/systemu, ASCII; nie jest kluczem | Nie występuje; opis zapewnia `SURVEY_NAME` |
| `OBJECT_REF` | Referencje rozpoznanych otworów w pliku; brak w częściach bez otworów | Co najmniej jedna jawna referencja; dla domiaru między otworami wszystkie rozpoznane końce |
| Pozostałe pola | Dotychczasowy kontrakt, w tym `SURVEY_ID` i `SOURCE_REF` | Ten sam kontrakt |

`OBJECT_REF` zastępuje przykładowe `OBJECT_IDS` z rozmowy. Zapisuje dodatkowo
stację, co pozwala zweryfikować powiązanie bez dodawania fixu:

```text
SURVEY_KIND     "surface"
OBJECT_REF      "LodowaMalolacka:0=MLW-0011"
OBJECT_REF      "LodowaMalolacka:31=MLW-0024"
```

Wartość ma dokładnie jeden separator `=` i dwa niepuste człony. Lewy człon
jest pełną nazwą stacji zgodną z regułami Walls; prawy to istniejący object_id.
Wskazany obiekt musi mieć powiązanie z jaskinią; obiekty katalogowe bez takiej
relacji nadal występują w eksporcie, lecz nie są referencjami otworów w SRV.
Duplikat referencji w jednym nagłówku i przypisanie jednej stacji do różnych
obiektów są błędami.
Referencja nie wprowadza pomiaru, equate ani #fix. Dodatkowe punkty terenowe
ciągu nie muszą dostawać identyfikatorów GPS. Jeżeli nie da się potwierdzić
żadnego otworu, plik wymaga rozstrzygnięcia w J01, a nie fikcyjnej referencji.

Aktywne `gps_fix` w `OTWORY.SRV.j2` oraz `OBJECT_REF` tworzą wspólnie mapę
stacja–obiekt. Powtórzenie zgodnego powiązania w różnych miejscach jest
dozwolone; sprzeczność jest błędem. Komentarz z `gps_fix` nie aktywuje kotwicy.
Przy podziale LODMAL górny otwór nadal pozostaje bez aktywnego fixu.

W JKTZ efektywny ID to wskazana jaskinia, a jeśli ma `system_cave_id` —
końcowy system po przejściu jawnych relacji. Cykl albo brak rekordu rodzica
jest błędem. Podziemny SRV ma wskazywać ten końcowy ID. Otwór zachowuje
przypisanie do jaskini składowej w GPS. Dla domiaru wyznaczamy zbiór
efektywnych ID z referencji, bez zapisywania go drugi raz w metadanych.

## Snapshot i walidacja

1. Pobierz metadane wydania GPS raz; zapisz repo, tag, release ID i tożsamość
   artefaktów. Pobierz z niego CSV oraz GPKG, oblicz SHA-256 obu plików.
2. Utrzymuj ten snapshot przez całą walidację i render. Odczyt GPKG jest
   tylko do odczytu przez standardowe `sqlite3`. Brak tabel to błąd kontraktu.
3. Zweryfikuj ID/relacje oraz zgodność pól `cave_id` i `system_cave_id` CSV
   z katalogiem. Nie odtwarzaj brakujących jaskiń z wierszy Best.
4. Sprawdź metadane i jawne referencje; po kompilacji sprawdź istnienie
   wskazanych stacji w wyniku kompilatora. Literówka nie może tworzyć
   referencji do nieistniejącego punktu.
5. Zapisz źródło snapshotu i błędy z nazwą pliku, polem, zastanym ID oraz
   oczekiwanym powiązaniem. Błąd nie może nadpisywać wersjonowanego OTWORY.

Tryb offline dostaje oba artefakty wraz z manifestem tagu i ich SHA-256.
Testy jednostkowe używają lokalnych fixture i nie łączą się z siecią.
Istniejący `--csv` może nadal służyć samemu renderowaniu; nie jest dowodem
przejścia pełnej walidacji katalogowej. CI i wydania używają pełnego snapshotu.
Każdy job CI korzysta z tego samego przygotowanego snapshotu danego runu,
również jeżeli w międzyczasie pojawi się nowy GPS latest.

Model terenu `Powierzchnia/`, materiały `_RAW` i generowane `OTWORY.SRV`
pozostają poza kontraktem nagłówków aktywnych jaskiniowych SRV.

## Kolejność, akceptacja i granice

- [Plan GPS](GPS.md): G01–G03 przygotowują eksport i osobną draft PR.
  G04 oznacza publikację dopiero po osobnym poleceniu użytkownika.
- [Plan JKTZ](JKTZ.md): J01 można rozpocząć od razu. J02–J03 mogą korzystać
  z dokładnie oznaczonego preview GPS; J04 wymaga wydanego kontraktu i
  rozstrzygniętego mapowania. J05 domyka całość.
- [Prompty startowe](START.md): każde okno wykonuje wskazaną kartę, aktualizuje
  jej stan i zatrzymuje się. Lista kart nie upoważnia do wykonania wszystkich.
- Na koniec: brak starych CAVE_ID w aktywnych danych, brak plików mieszanych,
  pełne rozliczenie wejść/wyjść migracji, przejście bramek i dowody kompilacji.
- Ten etap tworzy dokumentację i draft PR. Nie wdraża kontraktu, nie zmienia
  danych GPS/JKTZ ani nie upoważnia do merge, tagowania i wydania.
