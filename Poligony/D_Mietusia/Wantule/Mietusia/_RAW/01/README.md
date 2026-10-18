# Mietusia - paczka zrodlowa 01

- **Status materiału:** dostępny
- **Pochodzenie danych:** https://github.com/RadostW/jaskinie
- **Autorzy pomiarów:** Radost Waszkiewicz, Stanislaw Mielczarek
- **Daty pomiarów:** 2024-02-10
- **Data pozyskania:** nieznane
- **Dodał do _RAW:** nieznane
- **Licencja źródłowa:** nieznane
- **Kompletność:** nieznane

## Zawartość

- `mietusia.svx` — główny plik projektu Survex; zawiera *include dla wszystkich sekcji i *equate łączące stacje
- `gps_mietusia.svx` — dwa odczyty GPS: gps_mietusia_2024 (Garmin etrex, W. Gutfeter, 2024-02-10, E19.898750 N49.246611 1270m) połączony z jaskinią przez *equate w mietusia.svx; gps_mietusia_2022 (Garmin etrex, J. Jurczyk, 2022-10-23, E19.898626 N49.246429 1256.5m) — orphan, nie połączony z jaskinią
- `gps.svx` — plik nadrzędny GPS z projektu RadostW; zawiera kontekst dla obu plików GPS oraz współrzędne szacunkowe innych jaskiń w okolicy
- `rura.svx` — pomiar głównego ciągu (stacje 0–40), 2022-10-21, instrument DistoX
- `matka_boska.svx` — pomiar Sali Matki Boskiej (stacje 0–19 dołączone do rura.40), 2024-02-10
- `powierzchnia.svx` — pomiar powierzchniowy (domiar GPS do otworu), 2024-02-10, *flags surface
- `rura_res_a.svx` — pomiar powtórzony rura stacje 0–10, 2022-10-22, *flags duplicate
- `rura_res_b.svx` — pomiar powtórzony rura stacje 0–38, 2022-10-23, *flags duplicate
- `rura_res_c.svx` — pomiar powtórzony rura stacje 0–38, 2022-10-23, *flags duplicate

## Uwagi

- rura_res_*.svx pominięte w SRV (flaga duplicate)
- powierzchnia.svx pominięta w SRV (flaga surface)
- Dane zdigitalizowane (Digitized/) pominięte — nie są pierwotnymi pomiarami
- Shot 10→11 w rura.svx powtórzony 4-krotnie identycznie — zachowano jedną kopię
- gps_mietusia.svx: użyto odczytu 2024 (E19.898750 N49.246611 1270m) jako #fix pw_3 w MIET_M.SRV; odczyt 2022 nie był połączony z jaskinią w źródle Survex

## Uzupełnienie LRUD (2026-10-18)

- Przywrócono 22 rekordy LRUD z `rura.svx` i 23 z `matka_boska.svx`,
  bez zmiany wartości L/R/U/D, pomiarów osi ani splajów.
- Zachowano osobne zestawy przekrojów na rozgałęzieniach. W SRV każdy
  rekord wskazuje plik i wiersz źródłowy. Jawne azymuty siatkowe przekrojów
  wyliczono z geometrii poligonu JKTZ i kolejności bloków `*data passage`:
  kierunek skrajnego odcinka na końcach, dwusieczna pozioma wewnątrz bloku.
- Serie `rura_res_a/b/c` pozostają w archiwum. Nie uśredniono ich z `rura`,
  ponieważ brak potwierdzonej mapy tożsamości pośrednich stacji; serie mają
  różną liczbę punktów. Źródłowe `*equate` wiążą tylko wybrane kotwy.
