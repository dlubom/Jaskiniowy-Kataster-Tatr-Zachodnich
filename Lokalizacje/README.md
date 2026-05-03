# Lokalizacje obiektow terenowych

Ten katalog jest rejestrem lokalizacji konkretnych obiektow terenowych. Obiektem jest
np. otwor jaskini, sztolnia, a w przyszlosci takze ponor, wywierzysko albo inny typ
uzgodniony w slowniku.

## Model

- `JKTZ-OBJ-*` identyfikuje obiekt terenowy i jest glownym ID rejestru.
- `JKTZ-OBS-*` identyfikuje pojedynczy pomiar, obserwacje albo ustalenie lokalizacji.
- Jaskinia nie jest osobnym bytem rejestru lokalizacji. Jest kontekstem obiektu:
  `cave.inventory_id`, `cave.name`, `systems`.
- TPN traktujemy jako dane per obiekt terenowy.
- PIG/Geoportal traktujemy jako dane per jaskinia albo per system.
- PIG/Geoportal trafia do `observations` tylko wtedy, gdy dana jaskinia ma jeden
  obiekt TPN. Przy jaskiniach wielootworowych trafia do `related_source_records`.
- Aktualna lokalizacja obiektu jest wskazana przez `current_observation_id`.
- Niczego nie kasujemy: starsze pomiary i ustalenia zostaja w `observations`.

## Struktura

- `rejestr/obiekty/` - jeden plik YAML na jeden obiekt terenowy; to format do
  kuratorowania recznego.
- `dane/` - wygenerowane tabele CSV do przegladu, filtrowania i przyszlych eksportow.
- `slowniki/` - slowniki typow obiektow, zrodel i klas dokladnosci.
- `_RAW/` - surowe eksporty zrodlowe bez recznych poprawek.
- `tools/import_locations.py` - importer budujacy pierwszy plaski rejestr z TPN i PIG.
- `raport_importu.md` - krotki raport z ostatniego importu.

Opis kolumn i struktury YAML znajduje sie w `SCHEMA.md`.

## Wspolrzedne

Kolumny `x1992` i `y1992` przechowuja wartosci zrodlowe w ukladzie PUWG 1992
(EPSG:2180). W nazewnictwie zrodel `X1992` oznacza northing, a `Y1992` easting.
Przy eksporcie GIS geometrie punktow w EPSG:2180 powinny wiec uzywac:

- easting = `y1992`
- northing = `x1992`

Kolumny `lat_wgs84` i `lon_wgs84` sa wypelniane, gdy zrodlo podaje WGS84 albo gdy
dodamy jawna konwersje.

## Walidacja i eksport

Repo ma lokalne srodowisko Python zarzadzane przez `uv`. Narzedzia uruchamiamy przez
`uv run`, bez instalowania pakietow do systemowego Pythona:

```bash
uv sync --dev
uv run jktz-locations validate
uv run jktz-locations export
```

Walidator sprawdza m.in. skladnie YAML, unikalnosc `JKTZ-OBJ-*` i `JKTZ-OBS-*`,
zgodnosc `current_observation_id`, slowniki `source`, `accuracy_class` i `object_type`,
kompletnosc wspolrzednych, robocze zakresy Tatr Zachodnich, zgodnosc EPSG:2180 z WGS84,
naglowki CSV, powiazania ID miedzy CSV i YAML oraz poprawny JSON w `raw_json`.

Eksporter buduje aktualne lokalizacje z `current_observation_id` i zapisuje:

- `exports/lokalizacje/aktualne_lokalizacje.csv`
- `exports/lokalizacje/aktualne_lokalizacje.xlsx`
- `exports/lokalizacje/aktualne_lokalizacje.gpx`
- `exports/lokalizacje/aktualne_lokalizacje_2180.{shp,shx,dbf,prj,cpg}`

Shapefile jest w EPSG:2180. GPX jest w WGS84; brakujace WGS84 jest wyliczane z
EPSG:2180. Jezeli walidator zglasza bledy danych, eksport mozna awaryjnie odpalic
przez `uv run jktz-locations export --skip-validate`, ale docelowo najpierw poprawiamy
rejestr.

## Import i odtwarzalnosc

Surowe eksporty sa zachowane w `_RAW/`. Importer:

```bash
python3 Lokalizacje/tools/import_locations.py
```

Importer zachowuje juz nadane ID obiektow i obserwacji, jesli w `dane/*.csv` istnieje
ten sam `import_key`. To pozwala odtworzyc pierwszy rejestr bez przypadkowej zmiany
identyfikatorow.

Uwaga praktyczna: po rozpoczeciu recznego kuratorowania `rejestr/obiekty/` importer z
surowych CSV powinien byc uzywany ostroznie, bo pliki YAML sa zapisywane ponownie.
Docelowy nastepny krok to osobny eksport z YAML do CSV/GeoJSON/Shapefile.

## Dodawanie wlasnych pomiarow GNSS

Nowy pomiar dopisujemy jako kolejna obserwacje w pliku obiektu:

- `source`: `JKTZ_GNSS`
- `observation_date`: data pomiaru
- `method`: np. `GNSS RTK`, `GNSS statyczny`, `GNSS rekreacyjny`
- `device`: model odbiornika / zestawu
- `accuracy_class`: jedna z wartosci ze `slowniki/klasy_dokladnosci.csv`
- `estimated_accuracy_m`: liczba, jesli jest znana
- `verification_status`: np. `robocze`, `zweryfikowane`, `odrzucone`
- `tags`: dodatkowe flagi, np. `teren;rtk;kontrola`

Gdy pomiar staje sie najlepszym aktualnym stanem, w obiekcie ustawiamy
`current_observation_id` na jego `JKTZ-OBS-*`.

Obiektem rejestru moze byc nie tylko otwor jaskini. Slownik `slowniki/typy_obiektow.csv`
obejmuje teraz takze `sztolnia`, `wywierzysko`, `ponor` oraz typy robocze. Dla
wywierzysk i ponorow pola `cave.*` moga zostac puste, dopoki obiekt nie ma
jednoznacznego kontekstu jaskiniowego albo systemowego.

Minimalny reczny pomiar GNSS w `observations` powinien miec:

```yaml
- id: "JKTZ-OBS-001858"
  source: "JKTZ_GNSS"
  observation_date: "2026-05-01"
  method: "GNSS RTK"
  device: "model odbiornika"
  coords:
    epsg2180:
      northing: "152971.36"
      easting: "562235.67"
      z: "1297.37"
    wgs84:
      lat: ""
      lon: ""
  accuracy_class: "0_10_1_m"
  estimated_accuracy_m: "0.5"
  verification_status: "robocze"
  verification_notes: ""
  tags: "teren;rtk"
  match_status: "source_object"
```

## Sprawy do rozstrzygniecia

Rekordy wymagajace decyzji sa w `dane/problemy_importu.csv`. Najczestszy przypadek to
obiekty TPN bez `NR_INWENT`. Jezeli nazwa jednoznacznie pasuje do istniejacej jaskini,
importer oznacza to jako `needs_inventory_id_confirmation`, a nie jako pewnik.

Rekordy PIG/Geoportal, ktorych nie wolno przypisac do pojedynczego obiektu, sa w
`dane/powiazane_rekordy_zrodel.csv` i w polu `related_source_records` odpowiednich
plikow YAML.
