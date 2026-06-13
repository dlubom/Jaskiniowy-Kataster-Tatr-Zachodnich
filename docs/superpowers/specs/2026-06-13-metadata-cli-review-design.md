# Pakiet metadanych i CLI dla skills

## Cel

Obsluzyc dwa komentarze review PR #119:

1. udostepnic przez CLI istniejace operacje tworzenia i aktualizacji metadanych,
   tak aby repozytoryjne skills nie skladaly blokow recznie;
2. uporzadkowac moduly SRV i RAW w jednym pakiecie oraz ujednolicic ich publiczne
   nazewnictwo.

Zmiana nie modyfikuje kontraktu danych, aktywnych plikow `.SRV`, paczek
`_RAW/NN` ani zaakceptowanych pustych linii w kanonicznym formacie SRV.

## Architektura pakietu

Kod domenowy znajduje sie pod `src/jktz/metadata/`:

- `srv.py` zawiera `SrvMetadata`, parser, formatter, walidacje pol, obsluge
  `SOURCE_REF` oraz funkcje tworzenia i aktualizacji metadanych;
- `raw.py` zawiera `RawMetadata`, parser, formatter i sumy materialow
  zrodlowych;
- `errors.py` zawiera wspolny `MetadataError`;
- `__init__.py` nie re-eksportuje calego API. Konsumenci importuja jawnie z
  `jktz.metadata.srv`, `jktz.metadata.raw` albo `jktz.metadata.errors`.

Publiczne nazwy sa symetryczne:

- `parse_srv_metadata` / `format_srv_metadata`;
- `parse_raw_metadata` / `format_raw_metadata`.

Funkcje specyficzne dla jednego formatu zachowuja nazwy domenowe, na przyklad
`resolve_source_ref` i `material_hashes`.

## CLI

Wlasciwa implementacja pozostaje w `src/jktz/cli/srv_metadata.py`, zgodnie z
ukladem pozostalych komend pakietu. `scripts/srv_metadata.py` pozostaje cienka
nakladka kompatybilnosciowa. Nie powstaje drugi katalog `scripts/cli/`.

Entry point `jktz-srv-metadata` udostepnia:

### `srv-set`

Tworzy albo zastepuje kanoniczny blok metadanych wskazanego pliku `.SRV`.
Przyjmuje wymagane pola strukturalne i powtarzalne opcje `--source-ref`,
`--team`, `--instrument`, `--survey-date` i `--processing`. Brakujace pola
opisowe otrzymuja jawne wartosci domyslne kontraktu.

Jesli plik juz istnieje, cala tresc za blokiem `#[ ... #]` pozostaje bez zmian.
Jesli plik nie istnieje, powstaje plik zawierajacy sam blok metadanych.

### `srv-update`

Aktualizuje istniejacy poprawny blok bez ponownego podawania wszystkich pol.
Pierwszy zakres obejmuje:

- `--update-date`;
- powtarzalne `--add-processing`, dopisywane idempotentnie.

Komenda odrzuca plik bez poprawnego istniejacego bloku.

### `raw-set`

Tworzy albo zastepuje kanoniczny `_RAW/NN/README.md` na podstawie wszystkich
wymaganych pol i powtarzalnego `--content`.

### `hash-raw`

Zachowuje obecne zachowanie i format wyjscia.

Kazda komenda zapisujaca obsluguje `--dry-run`. W tym trybie wynik trafia na
standardowe wyjscie, a plik nie jest tworzony ani modyfikowany.

## Bezpieczenstwo zapisu

Aktywne `.SRV` sa odczytywane i zapisywane jako bajty mapowane przez Latin-1.
Dzieki temu kazdy bajt tresci poza naglowkiem ma jednoznaczne odwzorowanie i
wraca do pliku bez zmiany. Nowy blok metadanych jest osobno sprawdzany jako
ASCII przed polaczeniem z zachowana trescia.

README paczek RAW uzywa UTF-8.

Zapis jest atomowy:

1. wygenerowanie i ponowne sparsowanie wyniku w pamieci;
2. zapis pliku tymczasowego w katalogu docelowym;
3. zachowanie dotychczasowych uprawnien, jesli plik istnial;
4. `os.replace` na sciezke docelowa;
5. usuniecie pliku tymczasowego przy bledzie.

Blad walidacji wystepuje przed modyfikacja pliku.

## Integracja ze skills

- `add-cave` tworzy szkielet pomiarowy, a nastepnie wywoluje `raw-set` i
  `srv-set`;
- `svx-to-srv` wywoluje `srv-set` dla kazdego wyniku konwersji;
- `average-shots` po zmianie pomiarow wywoluje `srv-update` z aktualna data i
  `--add-processing "usredniono pomiary przod/tyl"`.

Skills zawieraja konkretne przyklady komend i nie sugeruja recznego korzystania
z funkcji Pythona.

## Testy

Testy obejmuja:

- nowe sciezki importow i symetryczne API parser/formatter;
- zachowanie dotychczasowych formatow SRV i RAW;
- `srv-set` dla nowego oraz istniejacego pliku;
- `srv-update`, w tym idempotentne `PROCESSING`;
- wielokrotne pola;
- `raw-set`;
- `--dry-run`;
- brak zapisu przy blednych danych;
- zachowanie bajtow tresci SRV poza blokiem;
- zachowanie `hash-raw`.

Pelna bramka pozostaje: `pytest`, Ruff, `git diff --check` i
`jktz-validate`.
