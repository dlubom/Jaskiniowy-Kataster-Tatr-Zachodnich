# _RAW — Jaskinia Miętusia (T.D-11.01)

**Źródło:** https://github.com/RadostW/jaskinie
**Autorzy pomiarów:** Stanisław Mielczarek, Joanna Jurczyk, Weronika Gutfeter, Paweł Jarosz, Jan Grzeszek, Paweł Nowikowski, Marcin Lewandowski, Radost Waszkiewicz
**Data pomiaru:** 2022-10-21 (rura), 2022-10-22–23 (pomiary powtórzone), 2024-02-10 (Sala Matki Boskiej, pomiar powierzchniowy)
**Data pozyskania:** 2026-03-18
**Dodał:** Paweł Gogolak
**Kompletność:** Dane post-2020 z pomiarów DistoX (TopoDroid). Plik mietusia.svx zawiera również odnośniki do danych zdigitalizowanych ze starych map (katalog Digitized/) — te pliki NIE są dołączone do _RAW/ i NIE zostały skonwertowane do SRV (dane archiwalne, nie pomiary pierwotne).
**Narzędzie:** DistoX (rura, rura_res_*), DistoX2 4027 / DistoXBLE 0109 (matka_boska, powierzchnia); Pixel 6a
**Licencja:** CC BY SA 4.0

## Pliki

- `mietusia.svx` — główny plik projektu Survex; zawiera *include dla wszystkich sekcji i *equate łączące stacje
- `rura.svx` — pomiar głównego ciągu (stacje 0–40), 2022-10-21, instrument DistoX
- `matka_boska.svx` — pomiar Sali Matki Boskiej (stacje 0–19 dołączone do rura.40), 2024-02-10
- `powierzchnia.svx` — pomiar powierzchniowy (domiar GPS do otworu), 2024-02-10, *flags surface
- `rura_res_a.svx` — pomiar powtórzony rura stacje 0–10, 2022-10-22, *flags duplicate
- `rura_res_b.svx` — pomiar powtórzony rura stacje 0–38, 2022-10-23, *flags duplicate
- `rura_res_c.svx` — pomiar powtórzony rura stacje 0–38, 2022-10-23, *flags duplicate

**Uwagi do konwersji:**
- rura_res_*.svx pominięte w SRV (flaga duplicate)
- powierzchnia.svx pominięta w SRV (flaga surface)
- Dane zdigitalizowane (Digitized/) pominięte — nie są pierwotnymi pomiarami
- Shot 10→11 w rura.svx powtórzony 4-krotnie identycznie — zachowano jedną kopię
