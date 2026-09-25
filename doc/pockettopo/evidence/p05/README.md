# P05 — szkice SVG/PNG i osnowa pomiarowa

Biblioteka `export_drawings` tworzy cztery SVG w pamięci; po wskazaniu resvg
również cztery PNG: `plan-sketch`, `plan-measurements`, `side-sketch`,
`side-measurements`. `side` oznacza przekrój rozwinięty. Wyniki i postęp
etapu są częścią repozytorium; atomowy pakiet, CLI oraz skill należą do P06.
`conversion_complete` pozostaje `false`.

Wynik końcowy: **1013 testów**, 97,50% linii / 95,83% gałęzi,
maksymalny CRAP 25. Mutacje: 2483/2748 (90,36%); każdy z dziesięciu modułów
spełnia próg 81%, nowa projekcja 623/658 (94,68%). Pełna walidacja
Survex/GDAL przeszła. Korpus: 258 źródeł, 262 zgodne obiekty Git,
1032 SVG i 1032 PNG; wszystkie 952 211 wierzchołków zachowane.
Pełne obrazy 13 wzorców są w `examples/`, a wyniki każdego źródła korpusu
w `corpus.json`. Zdalne CI należy sprawdzić dla dostarczonego commita.

## Użycie

```python
from pathlib import Path
from jktz.pockettopo import DrawingSettings, export_drawings

source = Path('doc/pockettopo/evidence/p01/cases/api-drawings/api-drawings.top')
result = export_drawings(
    source.read_bytes(),
    settings=DrawingSettings(pixels_per_metre=40),
    resvg_path='/path/to/resvg',  # dokładnie 0.48.1; bez tego tylko SVG
)
svg = result.svgs['plan-measurements']
png = result.pngs['plan-measurements']
report = result.report
```

Tak jak w P04, `plan` przyjmuje jawne potwierdzenia powtórzeń i wyłączenia,
a `correction_policy` niezależnie uzasadnione korekty związane z SHA źródła.
Domyślnie żadna seria nie jest potwierdzana. Auto i brak sesji pozostawiają
niezerowy pomiar nieaktywny. Daty urządzenia pozostają niepotwierdzone,
referencje nie ustanawiają CRS ani aktywnych fixów.

## Szkic i warstwy

Współrzędne SVG pozostają w milimetrach źródła: X w prawo, Y w dół.
Każda otwarta kreska zachowuje wszystkie wierzchołki w oryginalnej kolejności;
singleton jest widocznym kołem o środku dokładnie w punkcie źródłowym.
Nie domykamy ani nie wygładzamy linii. Indeksy elementów i kolorów są zapisane
przy obiektach SVG. Natywna paleta sRGB została odczytana bezpośrednio
z PocketTopo 1.372: [dowody natywne](NATIVE.md).

SVG ma osobne warstwy `sketch`, `survey`, `splays`, `stations`, `xsections`.
Wariant `sketch` pokazuje wyłącznie źródłowe kreski; pola XSection pozostają
w metadanych. Wariant `measurements` dodaje pomiary, nazwy stacji oraz
znaczniki, łączniki i domiary XSection. Mapping jest zapisem widoku,
nie przesunięciem wierzchołków. Pusty szkic ma jawny status `empty`
i widoczny napis `EMPTY SKETCH`; nie powstaje fikcyjny obrys.

Nazwy stacji są wektorowymi glifami 3×5 (`jktz-grid-3x5-v1`). Obrazy nie
zależą od fontów systemowych; dosłowna nazwa jest też w `title` i `aria-label`.
Wielkość napisów, szerokość linii, margines, tło i żądana skala są jawne.
Domyślnie PNG ma białe tło, 40 px/m, limit 4096 px na oś i 16 mln pikseli.
Duży szkic jest skalowany do limitu; rzeczywiste wymiary i skala pozostają
w raporcie. SVG zachowuje pełną geometrię niezależnie od rozdzielczości PNG.
Eksporter sprawdza wersję renderera, kod procesu, termin zakończenia, CRC
i kompletność PNG, rozmiar oraz ograniczoną dekompresję danych obrazu.
Uszkodzone wyjście nie jest zwracane jako gotowy wynik.

## Osnowa, pętle i przekroje

Osnowa korzysta z aktywnych grup P03/P04, z zachowaniem oddzielnych odczytów
niepotwierdzonych. Źródłowa kolejność dołączania odcinków wyznacza pozycje;
nie wykonujemy wyrównania pętli. Każdy odcinek zachowuje zmierzony koniec,
a odchylenie od wcześniej ustalonej stacji jest osobno raportowane.
Natywny wzorzec pętli potwierdza brak wyrównania również w PocketTopo 1.372.
Rozgałęzienia, odwrócone dołączenie oraz Flip sprawdzają osobne wzorce.

Rozłączna składowa ma własne lokalne zero — jej położenie względem szkicu
pozostaje nieustalone. Nie tworzymy fixów. Ostrzeżenia osnowy i zatrzymane
rekordy powodują widoczne `CHECK OVERLAY`; szczegółowe przyczyny są w JSON
oraz metadanych SVG. Taki podkład wymaga interpretacji, mimo że szkic jest
zachowany dokładnie.

Mieszane Flip w potwierdzonej serii nie ustalają jednoznacznego rozwinięcia.
Podkład wybiera flagę pierwszego rekordu, jawnie zapisuje tę decyzję jako
niepotwierdzoną oraz wyświetla `CHECK OVERLAY`. Rozwinięcie domiarów XSection
ma limit 100 000 linii dla obu widoków łącznie; przekroczenie kończy eksport
błędem przed tworzeniem geometrii, bez częściowego wyniku.

Domiar na rozwinięciu korzysta z osi odcinka, który dołączył jego stację;
domiar na początku nie ma ustalonej osi poziomej. XSection zachowuje surową
pozycję, stację i kierunek. Poziomy (`-1`) przedstawia rzut E/N, pionowy
rzutuje składową poprzeczną do zadanego kierunku oraz wysokość. Reguły
korekt, kierunki i liczby są udokumentowane w [NATIVE.md](NATIVE.md).

Natywne PocketTopo automatycznie łączy podobne odczyty innym algorytmem.
Nie przenosimy tej decyzji do konwertera. Zgodność osnowy ma określony
zakres testów; nie obiecujemy identycznych punktów dla każdego terenowego
źródła z powtórzeniami. Dokładna zgodność szkicu nie oznacza potwierdzenia
pomiarów ani ich dopasowania do narysowanego obrysu.

## Dowody i reprodukcja

- [Natywne próby](NATIVE.md): trzy nowe źródła loop/branch/xsection,
  literalne wejścia, DXF, współrzędne i paleta PocketTopo 1.372.
- [Wzorce i audyt DXF](fixture-checks.json): wszystkie cztery SVG i PNG
  dla sześciu P01, trzech terenowych, Shadow i trzech nowych natywnych.
- [Przykładowe wyniki](examples/shadow/plan-measurements.svg) oraz raporty
  każdego wzorca w `examples/`.
- [Pełny korpus](corpus.json): 258 unikalnych źródeł, hashe czterech SVG/PNG,
  wszystkie wierzchołki, statusy oraz ograniczenia osobno dla każdego wejścia.
- [Odtworzenie](REPRODUCE.md), [bramki](repository-checks.json).
- [Kontrola obrazów](VISUAL.md): oględziny i niezależne testy pikseli;
  wszystkie 52 zachowane PNG są wzorcami porównania w wymaganym CI Linux.

Źródła terenowe i ich pochodne zachowują nieustaloną licencję opisaną
w P00/P01; obecność w tym katalogu nie nadaje im licencji JKTZ.
