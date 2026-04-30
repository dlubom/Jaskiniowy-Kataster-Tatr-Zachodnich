# Surowe eksporty lokalizacji

Katalog zawiera niezmienione eksporty CSV uzyte do pierwszego importu rejestru
lokalizacji.

## Pliki

- `tpn_otwory_jaskin_2026-04-29.csv` - eksport danych obiektow/otworow z TPN.
- `pig_geoportal_otwory_jaskin_2026-04-29.csv` - eksport danych jaskin z PIG/Geoportalu.

Data w nazwie oznacza date wlaczenia pliku do projektu, nie musi byc data wykonania
eksportu przez system zrodlowy.

## Zasady

- Plikow w `_RAW/` nie poprawiamy recznie.
- Normalizacja liczb, dopasowanie rekordow i wybor aktualnych lokalizacji sa wykonywane
  przez `../tools/import_locations.py`.
- Jesli pojawi sie nowszy eksport, dodajemy go jako nowy plik, a nie nadpisujemy
  poprzedniego.
