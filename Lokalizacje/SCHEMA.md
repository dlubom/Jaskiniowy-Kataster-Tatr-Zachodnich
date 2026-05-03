# Schemat danych lokalizacji

## Zasada podstawowa

Rejestr jest plaski: podstawowym bytem jest obiekt terenowy `JKTZ-OBJ-*`.
Jaskinia, numer inwentarzowy i system sa kontekstem obiektu, a nie osobnymi rekordami
z wlasnym ID w rejestrze lokalizacji.

## YAML w `rejestr/obiekty/`

Jeden plik YAML oznacza jeden obiekt terenowy.

Przyklad skrocony:

```yaml
id: "JKTZ-OBJ-000225"
type: "otwor_jaskini"
name: "Jaskinia Mylna, S"
label: "S"
cave:
  inventory_id: "T.E-08.04"
  name: "Jaskinia Mylna"
  assignment_status: "explicit"
systems:
  - inventory_id: "T-Jaskinie Pawlikowskiego"
    name: "Jaskinie Pawlikowskiego"
current_observation_id: "JKTZ-OBS-000225"
observations:
  - id: "JKTZ-OBS-000225"
    source: "TPN"
related_source_records:
  - source: "Geoportal_PIG"
    relation_type: "cave_level_source_record"
```

Najwazniejsze pola:

- `id` - trwaly identyfikator obiektu.
- `type` - typ obiektu ze `slowniki/typy_obiektow.csv`, np. `otwor_jaskini`,
  `sztolnia`, `wywierzysko`, `ponor`.
- `subtype` - wartosc pomocnicza ze zrodla, np. `jaskinia`, `sztolnia`.
- `name` - nazwa robocza obiektu.
- `label` - oznaczenie otworu/wejscia, jesli istnieje.
- `cave.inventory_id` - numer inwentarzowy jaskini, jesli znany.
- `cave.assignment_status` - `explicit`, `inferred_by_unique_name` albo `missing`.
- `systems` - systemy/agregaty, do ktorych nalezy jaskinia obiektu.
- `source_ids` - identyfikatory zrodlowe konkretnego obiektu.
- `current_observation_id` - obserwacja uznana za obowiazujaca lokalizacje.
- `observations` - historia pomiarow/ustalen przypisanych do tego obiektu.
- `related_source_records` - rekordy zrodlowe zwiazane z jaskinia/systemem, ale nie z
  jednym konkretnym obiektem.

### Slowniki

Walidator korzysta ze slownikow w `slowniki/`:

- `typy_obiektow.csv` - dopuszczalne wartosci `type`.
- `zrodla.csv` - dopuszczalne wartosci `source`.
- `klasy_dokladnosci.csv` - dopuszczalne wartosci `accuracy_class`.

Rejestr lokalizacji obejmuje obiekty terenowe, nie tylko jaskinie. Dopuszczalne sa
otwory jaskin, sztolnie, wywierzyska i ponory. Informacja o jaskini pozostaje
kontekstem w `cave.*`; dla obiektow bez takiego kontekstu pola moga byc puste, a
`cave.assignment_status` powinno miec wartosc `missing`.

## `dane/obiekty.csv`

Plaska tabela obiektow, generowana z importu/YAML.

- `jktz_object_id` - trwaly identyfikator obiektu.
- `object_type` - typ obiektu, np. `otwor_jaskini`, `sztolnia`.
- `object_subtype` - doprecyzowanie ze zrodla.
- `name` - nazwa robocza obiektu.
- `source_name` - nazwa w TPN.
- `object_label` - oznaczenie otworu/wejscia.
- `cave_inventory_id` - numer inwentarzowy jaskini jako kontekst.
- `cave_name` - nazwa jaskini jako kontekst.
- `cave_assignment_status` - sposob przypisania obiektu do jaskini.
- `current_observation_id` - aktualnie obowiazujaca obserwacja.
- `current_source` - zrodlo aktualnej obserwacji.
- `current_x1992`, `current_y1992`, `current_z` - aktualne wspolrzedne i wysokosc.
- `current_lat_wgs84`, `current_lon_wgs84` - aktualne WGS84, jesli znane.
- `accuracy_class` - klasa ze `slowniki/klasy_dokladnosci.csv`.
- `verification_status` - stan weryfikacji aktualnej lokalizacji.
- `review_status` - status porzadkowania rekordu.
- `notes` - uwagi robocze.
- `source_tpn_globalid` - identyfikator TPN obiektu.
- `import_key` - techniczny klucz do zachowania ID przy ponownym imporcie.

## `dane/pomiary_lokalizacji.csv`

Jeden rekord oznacza pojedynczy pomiar, obserwacje albo ustalenie przypisane do obiektu.

- `jktz_observation_id` - trwaly identyfikator obserwacji.
- `jktz_object_id` - obiekt, do ktorego obserwacja jest przypisana.
- `source` - kod zrodla ze `slowniki/zrodla.csv`.
- `source_record_id` - identyfikator rekordu w zrodle.
- `source_external_id` - link albo dodatkowy identyfikator zewnetrzny.
- `source_inventory_id` - numer inwentarzowy podany przez zrodlo.
- `inferred_inventory_id` - numer wywnioskowany przez import, wymagajacy potwierdzenia.
- `source_name` - nazwa w zrodle.
- `source_object_label` - oznaczenie obiektu w zrodle.
- `observation_date` - data pomiaru, jesli wynika ze zrodla.
- `source_data_date` - data albo rok stanu danych w zrodle.
- `method` - metoda pomiaru lub weryfikacji.
- `device` - urzadzenie pomiarowe.
- `x1992`, `y1992`, `z` - wspolrzedne z obserwacji.
- `lat_wgs84`, `lon_wgs84` - WGS84 z obserwacji, jesli znane.
- `accuracy_class` - klasa dokladnosci.
- `estimated_accuracy_m` - szacowana dokladnosc w metrach, jesli znana.
- `verification_status` - stan weryfikacji obserwacji.
- `verification_notes` - uwagi o weryfikacji.
- `tags` - tagi rozdzielane srednikami.
- `match_status` - sposob przypisania, np. `source_object`, `cave_single_object_assumed`.
- `raw_json` - oryginalny rekord zrodlowy jako JSON.
- `import_key` - techniczny klucz do zachowania ID obserwacji.

## `dane/powiazane_rekordy_zrodel.csv`

Rekordy, ktore sa zwiazane z obiektem przez jaskinie/system, ale nie powinny byc
traktowane jako pomiar konkretnego obiektu terenowego.

- `source` - zrodlo rekordu.
- `source_record_id` - identyfikator rekordu w zrodle.
- `source_external_id` - link zrodlowy.
- `source_inventory_id` - numer inwentarzowy albo identyfikator systemu.
- `source_name` - nazwa w zrodle.
- `relation_type` - np. `cave_level_source_record`, `system_level_source_record`.
- `candidate_object_ids` - obiekty, ktorych rekord moze dotyczyc kontekstowo.
- `note` - wyjasnienie, dlaczego rekord nie jest obserwacja obiektu.
- `x1992`, `y1992`, `z`, `lat_wgs84`, `lon_wgs84` - wspolrzedne rekordu zrodlowego.
- `raw_json` - oryginalny rekord zrodlowy jako JSON.

## `dane/identyfikatory_zrodel.csv`

Tabela laczaca identyfikatory zewnetrzne z obiektami.

- `jktz_object_id` - identyfikator obiektu JKTZ.
- `source` - zrodlo identyfikatora.
- `identifier_type` - typ, np. `GLOBALID`, `PIG_ID`, `NR_INWENT`.
- `identifier_value` - wartosc identyfikatora.
- `scope` - `object` albo `cave_context`.
- `match_status` - sposob dopasowania.

## `dane/problemy_importu.csv`

Lista spraw do recznej decyzji: braki numerow inwentarzowych, numery wywnioskowane po
nazwie i rekordy systemowe bez znalezionych obiektow kandydackich.
