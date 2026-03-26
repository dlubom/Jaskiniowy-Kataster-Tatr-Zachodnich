# Jaskinia Mietusia Wyznia — surowe materialy zrodlowe

- **Źródło**: https://github.com/RadostW/jaskinie (Speleoklub Warszawski)
- **Autorzy pomiarów**: Radost Waszkiewicz, Stanislaw Mielczarek, Michal Smaga, Weronika Gutfeter, Pawel Jarosz, Jan Grzeszek
- **Przyrząd**: DistoX2, format TopoDroid
- **Data pomiaru**: luty 2024
- **Licencja źródłowa**: CC BY SA 4.0
- **Data pozyskania**: 2026-03-08
- **Dodał**: Paweł Gogolak
- **Kompletność**: pełny projekt Survex — 18 pliów pomiarowych (.svx) dla poszczególnych ciągów + plik GPS + plik główny

## Pliki

- `mietusia_wyznia.svx` — plik główny / zbiorczy (equate + include)
- `mietusia_wyznia_simplified.svx` — uproszczona wersja całości
- `gps_mietusia_wyznia.svx` — 5 odczytów GPS otworu z różnych urządzeń (etrex, 2x telefon, zegarek, garmin66i), 2024-02-13; stacje NIE są połączone z jaskinią w Survex (orphan)
- `gps.svx` — plik nadrzędny GPS z projektu RadostW; zawiera *fix gps_mietusia_wyznia z OSM (E19.894801 N49.245350 1383m, "large uncertainty") — to jest stacja faktycznie łącząca jaskinię z układem współrzędnych w Survex przez *equate w mietusia_wyznia.svx; w SRV użyto zamiast tego średniej z 5 odczytów urządzeń (E19.894900 N49.245399 1377m)
- `otwor.svx`, `suche_dno.svx`, `mylna_rura.svx`, `wyznia_matka.svx` — ciagi główne
- `problem_speleoklubu.svx`, `traba.svx`, `trzy_syfony.svx`, `detektor_lawinowy.svx` — odnogi
- `pawlacz.svx`, `komin.svx`, `obejscie.svx`, `odejscie_l2.svx` — odnogi
- `mr_studnia.svx`, `urlop_tacierzynski.svx`, `perystaltyka.svx`, `mylna_rura_studnia.svx` — odnogi
