# Podzial modulow metadanych SRV i RAW

## Cel

Obsluzyc uwagi z review PR #119 przez rozdzielenie odpowiedzialnosci
`src/jktz/metadata_contract.py` oraz usuniecie testowego importu
`scripts/srv_metadata.py` przez `importlib`.

Refaktor nie zmienia kontraktu danych, zawartosci aktywnych plikow `.SRV`,
formatu README paczek `_RAW/NN` ani wyniku walidacji.

## Docelowe moduly

### `src/jktz/metadata/srv.py`

Modul zawiera kontrakt aktywnego SRV:

- `SrvMetadata`;
- parsowanie i formatowanie bloku `#[ ... #]`;
- walidacje pol SRV;
- rozpoznawanie aktywnych plikow SRV;
- rozwiazywanie `SOURCE_REF`;
- helpery tworzenia i aktualizacji metadanych SRV.

Canonical formatter nadal zapisuje pusta linie:

- pomiedzy polami strukturalnymi i polami opisujacymi pomiar;
- pomiedzy `#]` i trescia Walls.

### `src/jktz/metadata/raw.py`

Modul zawiera kontrakt README paczki `_RAW/NN`:

- `RawMetadata`;
- parsowanie i walidacje README;
- generowanie canonical README;
- obliczanie sum SHA-256 materialow zrodlowych z pominieciem README.

### `src/jktz/validation/measurements.py`

Modul zawiera walidacje tresci pomiarowej niezalezna od metadanych:

- sledzenie `#date` i `#Units DECL=...`;
- rozpoznawanie kolejnosci kolumn Walls;
- sprawdzanie, czy niezerowe aktywne strzaly maja stan orientacji.

### `src/jktz/metadata/errors.py`

Modul zawiera wspolny `MetadataError`, aby kontrakt SRV i kontrakt RAW nie
zalezaly od siebie.

### `src/jktz/cli/srv_metadata.py`

Modul zawiera parser argumentow i implementacje komend `srv-set`,
`srv-update`, `raw-set` oraz `hash-raw`.
`scripts/srv_metadata.py` pozostaje cienka, zgodna wstecznie nakladka
uruchamiajaca `jktz.cli.srv_metadata.main`.

## Testy

Testy beda importowaly publiczne funkcje zwyklymi importami z pakietu `jktz`.
Zostana rozdzielone zgodnie z odpowiedzialnosciami:

- `tests/test_srv_metadata.py`;
- `tests/test_raw_metadata.py`;
- `tests/test_validation_measurements.py`.

Integracyjny test `tests/test_validation_metadata.py` nadal sprawdza wspolne
dzialanie kontraktow i walidacji repozytorium.

## Kompatybilnosc

- `scripts/srv_metadata.py hash-raw` zachowuje dotychczasowe zachowanie.
- `jktz-srv-metadata` udostepnia zapisujace komendy z opcja `--dry-run`.
- Komunikaty bledow kontraktow pozostaja bez zmian.
- `jktz-validate` wykonuje te same kontrole.
- Historyczne plany implementacyjne nie sa przepisywane.
- Aktualna specyfikacja kontraktu i instrukcje wskazujace modul implementacji
  zostana zaktualizowane do nowych sciezek.
