# P04 — sprawdzenie w rzeczywistym Walls

Wykonano 2026-09-25 w zainstalowanym **Walls 2.3.0-beta.1 2025-09-13**, przez
Wine na macOS. SHA-256 `Walls32.exe`:
`ee11c4cf908d200176c96528e702846ef3e2caba7e356fc0e4c03bde17ae782f`.
To próba programu, niezależna od obsługi SRV przez Survex.

Trzy izolowane projekty `.wpj` wskazują dokładne eksporty biblioteki. Pracowano
na kopiach w krótkim katalogu `/private/tmp/p04-walls`; nie zmieniano projektu
kataster ani źródeł. Okno programu, przycisk Compile i raport współrzędnych
obsłużono pomocnikiem `doc/pockettopo/helpers/pockettopo_ui.swift` oraz
AppleScript/System Events po wyraźnej zgodzie użytkownika. CUA nie rozpoznawało
procesu Wine. Pomocnik wybierał PID Walls; obrazy dotyczą wyłącznie jego okien.

| Projekt | Zakres | Nazwane stacje | Maks. różnica składowej od rachunku analitycznego |
| --- | --- | ---: | ---: |
| [P04.wpj](P04.wpj), [TEST.SRV](TEST.SRV) | Kardynalne, średnia A1–A3, piony i zerowe powiązanie 7=8 | 9 | 0,0000002432 m |
| [TRIPS.wpj](TRIPS.wpj), [TRIPS.SRV](TRIPS.SRV) | Różne deklinacje, jawne syntetyczne korekty, odrębne 0 i 0.0 | 4 | 0,0000004815 m |
| [LONG.wpj](LONG.wpj), [LONG.SRV](LONG.SRV) | Graniczne ID, aliasy Walls pzik0zj i p1z141z3 | 4 | 0,0000004815 m |

Każdy projekt skompilował się i otworzył przegląd mapy, bez zaobserwowanego
komunikatu błędu lub ostrzeżenia. Raport **Connected vectors with file
references**, 6 miejsc dziesiętnych, bez ograniczenia do ramki/flag/notatek:
[cardinal](cardinal-listing.txt), [trips](trips-listing.txt),
[long](long-listing.txt). Oryginalne pliki `.LST` skopiowano bajtowo pod
rozszerzeniem `.txt`, ponieważ repozytorium ignoruje wyniki `.LST`.
Obrazy: [cardinal](cardinal-listing.png), [trips](trips-listing.png),
[long](long-listing.png). [validation.json](validation.json) zawiera wszystkie
współrzędne, oczekiwania, tolerancję i hashe eksportów. Eksporty odtworzono po
końcowych zmianach kodu i porównano bajtowo z kompilowanymi plikami.

Tolerancja **0,0000011 m** obejmuje zapis współrzędnych do sześciu miejsc
oraz niewielki błąd zmiennoprzecinkowy; obserwowane odchylenia mieszczą się
w połowie jednostki ostatniej cyfry raportu. Nie oznacza to takiej dokładności
pomiaru terenowego. Współrzędne są lokalne, względem stacji 0, true north;
projekty nie mają georeferencji ani fixów. Te same analityczne oczekiwania
sprawdzono w testach SRV/SVX przez Survex.

Raporty Walls nie zawierają anonimowych domiarów. Ta próba potwierdza ich
przyjęcie przez kompilator, ale **nie deklaruje kontroli ich współrzędnych w
Walls**; pełne wektory domiarów sprawdzają testy Survex. Próba nie porównuje
algorytmów wyrównania pętli Walls i Survex. +8° i −12° są świadomie zadanymi
wartościami testowymi, nie ustaleniem historycznej deklinacji. Długość nazw
Walls, brak kolizji i rozróżnienie 0/0.0 sprawdzono na rzeczywistych listach.

## Odtworzenie

Otworzyć kolejno trzy `.wpj`, kliknąć Compile, następnie ikonę raportu stacji
i wektorów na pasku narzędzi. Wybrać Connected vectors i 6 miejsc dziesiętnych,
zapisać wynik pod nową ścieżką. Porównać z wersjonowanymi listami; data raportu
i ścieżka lokalna mogą się różnić. Pełnej kompilacji Walls nie zastępuje poniższy
odczyt: sprawdza on zachowane listy i ich zgodność z bieżącym eksporterem.
Uruchomić z katalogu głównego repo przez `uv run --python 3.12 python`:

```python
import hashlib
import importlib.util
import json
from pathlib import Path
from jktz.pockettopo import ProcessingPlan, RepeatConfirmation, export_surveys
spec = importlib.util.spec_from_file_location('geometry', 'tests/test_pockettopo_compilation.py')
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
root = Path('doc/pockettopo/evidence/p04/walls')
data, _ = g.native_source('api-cardinal')
plan = ProcessingPlan(hashlib.sha256(data).hexdigest(), (RepeatConfirmation((4, 5, 6), 'P01 explicit synthetic A1/A2/A3 fixture'),))
cases = [
 ('cardinal', 'TEST.SRV', export_surveys(data, plan=plan), g.cardinal_expected()),
 ('trips', 'TRIPS.SRV', export_surveys(g.native_source('api-trips-ids')[0], correction_policy=g.explicit_test_policy(g.native_source('api-trips-ids')[0])), g.trips_expected(long_names=False)),
 ('long', 'LONG.SRV', export_surveys(g.long_id_source(), correction_policy=g.explicit_test_policy(g.long_id_source())), g.trips_expected(long_names=True)),
]
rows=[]
for name, srvfile, result, expected in cases:
 assert (root / srvfile).read_bytes() == result.srv.encode('ascii'), srvfile
 mapped = {r['walls_name']:r['source_text'] for r in result.report['station_map']}
 actual={}
 for line in (root / f'{name}-listing.txt').read_text(encoding='ascii').splitlines():
  fields = line.split('\t')
  if len(fields) >= 5 and fields[0] == '' and fields[1] in mapped:
   actual[mapped[fields[1]]] = tuple(map(float, fields[2:5]))
 assert actual.keys() == expected.keys(), (actual, expected)
 error=max(abs(a-b) for station in actual for a,b in zip(actual[station],expected[station]))
 assert error <= 0.0000011, (name,error)
 rows.append({'case':name, 'srv_sha256':hashlib.sha256((root/srvfile).read_bytes()).hexdigest(),'source_sha256':result.report['provenance']['sha256'],'named_stations':len(actual),'max_component_error_m':error,'tolerance_m':0.0000011,'actual':actual,'analytical_expected':expected})
result={'date':'2026-09-25','walls_build':'2.3.0-beta.1 2025-09-13','walls_exe_sha256':'ee11c4cf908d200176c96528e702846ef3e2caba7e356fc0e4c03bde17ae782f','reference_frame':'local true north, no geographic reference, no fixes','coordinate_decimal_places':6,'cases':rows,'limitations':['Native reports omit anonymous splays; their vectors are independently tested through Survex, not claimed verified by these native listings.','No equality claim for native vs Survex loop-adjusted coordinates.','Synthetic correction overrides are test choices, not historical declinations.']}
(root/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
print(json.dumps(rows,indent=2))

```
