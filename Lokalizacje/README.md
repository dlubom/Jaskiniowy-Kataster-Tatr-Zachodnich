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
- `slowniki/` - slowniki zrodel i klas dokladnosci.
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

## Sprawy do rozstrzygniecia

Rekordy wymagajace decyzji sa w `dane/problemy_importu.csv`. Najczestszy przypadek to
obiekty TPN bez `NR_INWENT`. Jezeli nazwa jednoznacznie pasuje do istniejacej jaskini,
importer oznacza to jako `needs_inventory_id_confirmation`, a nie jako pewnik.

Rekordy PIG/Geoportal, ktorych nie wolno przypisac do pojedynczego obiektu, sa w
`dane/powiazane_rekordy_zrodel.csv` i w polu `related_source_records` odpowiednich
plikow YAML.
