# Granica walidacji aktywnych plikow i materialow RAW

Data projektu: 2026-06-19

## Cel

Walidacja ma jednoznacznie odrozniać aktywne pliki projektu od archiwalnych
materialow w `_RAW`. Reguly potrzebne Walls maja obejmowac tylko pliki poza
`_RAW`. W `_RAW` walidowane sa wylacznie struktura paczek, metadane README,
inwentarz materialow oraz powiazania `SOURCE_REF`.

Walidator nigdy nie ocenia tresci, kodowania, nazw ani skladni oryginalnych
materialow. Pliki zrodlowe pozostaja bitowo nietkniete.

## Wspolna klasyfikacja sciezek

`src/jktz/validation/_utils.py` jest jednym miejscem definiujacym granice
archiwum:

- `is_raw_path(path)` rozpoznaje segment `_RAW` w sciezce;
- `non_raw_paths(root, pattern)` zwraca sciezki pasujace do wzorca poza `_RAW`;
- `srv_files(root)` korzysta z `non_raw_paths(root, "*.SRV")`.

Nazwa `active` nie jest uzywana w tym API. `is_active_srv_path()` w kontrakcie
metadanych ma wezsza semantyke: poza `_RAW` wyklucza rowniez generowany
`Poligony/OTWORY.SRV` oraz pliki spoza `Poligony/`.

Walidatory `directives`, `decimal_format` i `prefixes` uzywaja `srv_files`.
Walidatory `filenames` i `non_ascii`, ktore skanuja takze katalogi lub pliki z
innymi rozszerzeniami, uzywaja `non_raw_paths`.

## Kontrakt walidacji RAW

Walidator metadanych sprawdza:

1. `_RAW` zawiera opcjonalny indeks `README.md`, numerowane paczki oraz co
   najwyzej ignorowane i niesledzone artefakty lokalnych narzedzi.
2. Kazda paczka `_RAW/NN` ma poprawny plik `README.md` w UTF-8 z wymaganymi
   polami, dozwolonym statusem i sekcja `## Zawartość`.
3. Kazda pozycja inwentarza zaczyna sie od pojedynczej sciezki wzglednej w
   backtickach. Sciezka nie moze byc bezwzgledna ani zawierac `..`.
4. Zadeklarowany plik lub katalog istnieje w paczce. Deklaracja katalogu
   obejmuje cala jego zawartosc.
5. Kazdy rzeczywisty plik materialu jest pokryty deklaracja pliku albo jednego
   z katalogow nadrzednych.
6. Z inwentarza i pokrycia wylaczone sa korzeniowy `README.md`, repozytoryjny
   `.gitignore` oraz artefakty rozpoznane przez Git jako ignorowane i
   niesledzone.
7. Paczka ze statusem `niedostępny` nie zawiera materialow i deklaruje
   `Brak materiałów źródłowych.`. Pozostale statusy wymagaja co najmniej jednego
   materialu.
8. Kazdy `SOURCE_REF` aktywnego SRV wskazuje istniejaca paczke z README.

Dowolne notatki o konwersji lub wykorzystaniu materialu naleza do sekcji po
`## Zawartość`, na przyklad `## Uwagi`, a nie do inwentarza.

## Poza zakresem

W `_RAW` nie sa sprawdzane:

- dyrektywy Walls lub Survex;
- przecinki dziesietne, prefiksy i inne reguly aktywnego SRV;
- ASCII, kodowanie lub wielkosc liter w nazwach;
- poprawnosc merytoryczna pomiarow;
- niezmiennosc wzgledem historii Git.

Niezmiennosc materialow jest kontrolowana podczas migracji przez porownanie
hashy i przeglad diffu, poniewaz walidator pojedynczego drzewa roboczego nie
odroznia poprawnego dodania zrodla od niedozwolonej zmiany istniejacego pliku.

## Migracja istniejacych README

Audyt wykazal 74 katalogi `_RAW`, 77 paczek i 9 rozbieznosci inwentarza.
Migracja zmienia tylko odpowiednie `_RAW/NN/README.md`:

- dopisuje brakujace materialy;
- zastępuje wpisy odnoszace sie do nieistniejacych dawnych nazw;
- rozdziela grupy plikow na pojedyncze pozycje;
- przenosi notatki niebedace inwentarzem do `## Uwagi`.

Materialy inne niz README nie sa modyfikowane.

## Testy i weryfikacja

Testy regresyjne potwierdzaja:

- wspolna klasyfikacje sciezek `_RAW`;
- pomijanie `_RAW` przez kazdy walidator aktywnych plikow, w tym
  `directives`;
- odrzucenie brakujacej, niebezpiecznej i niepokrywajacej pozycji inwentarza;
- akceptacje deklaracji katalogu, spacji i znakow narodowych w nazwie zrodla;
- pomijanie ignorowanych, niesledzonych artefaktow bez pomijania plikow
  sledzonych;
- zgodnosc statusu paczki z obecnoscia materialow.

Pelna bramka obejmuje `pytest`, Ruff, `git diff --check` i
`uv run jktz-validate`.
