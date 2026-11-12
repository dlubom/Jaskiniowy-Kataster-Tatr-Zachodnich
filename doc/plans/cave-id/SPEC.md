# CAVE_ID — wspólny kontrakt JKTZ i GPS

Kontrakt metadanych SRV, katalogu GPS i wspólnego snapshotu walidacji.
Historyczne przypisania plików oraz uzasadnienia decyzji opisuje
[mapowanie migracji](MAPPING.md).

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
- `katalog.gpkg` zawiera dwie pełne tabele bez geometrii: `caves`, `objects`.
  Warstwy `best`, `measurements` zachowują dotychczasowy kontrakt.
- JKTZ sprawdza tożsamość i współrzędne na jednym pobranym wydaniu GPS.
  Nieznane ID, sprzeczne relacje i niekompletny eksport powodują błąd.
- `_RAW` pozostaje archiwum. Rozdzielenie SRV zachowuje pomiary, stacje,
  jednostki, daty/deklinację, segmenty, powiązania i wynik kompilacji.

## Identyfikatory

Potwierdzony przykład relacji GPS:

```text
MLZ-0068 (otwór) → C-0648 (Śnieżna) → C-0295 (Wielka Śnieżna)
KSZ-0112, LEJ-0002 (otwory) → C-0078 (Bańdzioch Kominiarski)
```

Istnienie ID nie dowodzi poprawnego przypisania konkretnego SRV. Mapowanie
plików bez bezpośredniej referencji otworu wymaga przeglądu źródeł;
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

`OBJECT_REF` wiąże stację z obiektem GPS bez dodawania fixu:

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
żadnego otworu, przypisanie wymaga rozstrzygnięcia źródłowego lub decyzji
koordynatora; nie wolno tworzyć fikcyjnej referencji.

Aktywne `gps_fix` w `OTWORY.SRV.j2` oraz `OBJECT_REF` tworzą wspólnie mapę
stacja–obiekt. Powtórzenie zgodnego powiązania w różnych miejscach jest
dozwolone; sprzeczność jest błędem. Komentarz z `gps_fix` nie aktywuje kotwicy.
Przykładowo górny otwór Lodowej Małołąckiej ma referencję, ale nie ma
aktywnego fixu.

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
`--csv` służy do podglądu renderu w osobnym pliku lub sprawdzenia
zgodności tekstu; nie zastępuje pełnej walidacji katalogowej. CI i wydania
używają pełnego snapshotu.
Każdy job CI korzysta z tego samego przygotowanego snapshotu danego runu,
również jeżeli w międzyczasie pojawi się nowy GPS latest.

Model terenu `Powierzchnia/`, materiały `_RAW` i generowane `OTWORY.SRV`
pozostają poza kontraktem nagłówków aktywnych jaskiniowych SRV.

## Obsługa

Snapshot zawiera `best-measurements.csv`, `katalog.gpkg` i lokalny
`snapshot.json` z pochodzeniem oraz sumami obu plików. Manifest nie jest
artefaktem wydania GPS. `--gps-snapshot` odtwarza kontrolę offline i nie
łączy się z `--csv`; bez niego pełna walidacja pobiera bieżące wydanie.
Zapis wersjonowanego OTWORY sprawdza kandydata w tymczasowym projekcie
przed atomową podmianą.

Polecenia, środowisko i hooki: [CONTRIBUTING.md](../../../CONTRIBUTING.md).
Kontrakt nagłówków i CLI metadanych: [AGENTS.md](../../../AGENTS.md#raw-source-files-_raw).
