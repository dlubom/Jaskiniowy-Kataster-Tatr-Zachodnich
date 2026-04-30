# Raport importu lokalizacji

Data importu: 2026-04-29

## Licznosci

- Rekordy TPN: 1005
- Rekordy PIG/Geoportal: 860
- Obiekty terenowe JKTZ: 1005
- Obserwacje przypisane do obiektow: 1857
- Rekordy zrodlowe powiazane kontekstowo: 8

## Typy obiektow

- obiekt_terenowy: 7
- otwor_jaskini: 970
- otwor_jaskini_lub_sztolnia: 1
- sztolnia: 27

## Aktualne lokalizacje

- TPN: 1005

## Zrodla obserwacji przypisanych do obiektow

- Geoportal_PIG: 852
- TPN: 1005

## Jaskinie z wieloma obiektami TPN

- T.D-08.07 Jaskinia Mroźna: 2 obiekty
- T.D-08.08 Jaskinia Zimna: 2 obiekty
- T.D-12.10 Jaskinia nad Korytem: 2 obiekty
- T.E-08.04 Jaskinia Mylna: 2 obiekty
- T.E-08.07 Smocza Jama: 2 obiekty
- T.E-09.12 Jaskinia Czarna: 2 obiekty

## Niejednoznacznosci i braki

- pig_system_without_candidate_objects: 1
- tpn_missing_inventory_id: 141
- tpn_missing_inventory_id_inferred: 2

PIG/Geoportal trafia do obserwacji obiektu tylko wtedy, gdy numer inwentarzowy ma jeden obiekt TPN. Przy jaskiniach wielootworowych i systemach zostaje w `powiazane_rekordy_zrodel.csv` oraz `related_source_records` w YAML.
