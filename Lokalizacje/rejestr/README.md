# Rejestr YAML

Ten katalog zawiera plaski rejestr lokalizacji.

## Katalogi

- `obiekty/` - jeden plik YAML na jeden obiekt terenowy.

## Zasady edycji

- Obiekt terenowy ma wlasne `JKTZ-OBJ-*`.
- Informacja o jaskini i systemie jest kontekstem w pliku obiektu, nie osobnym bytem.
- Pomiary i ustalenia lokalizacji dopisujemy jako nowe pozycje `observations`.
- Aktualny stan wskazuje `current_observation_id`, zamiast usuwania starszych danych.
- Rekord PIG/Geoportal zostaje w `related_source_records`, jezeli dotyczy jaskini albo
  systemu z wieloma mozliwymi obiektami.

Pliki w tej wersji zostaly wygenerowane przez `../tools/import_locations.py` jako
bootstrap rejestru.
