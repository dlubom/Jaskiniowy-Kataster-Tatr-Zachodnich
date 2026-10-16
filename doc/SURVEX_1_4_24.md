# Przejście na Survex 1.4.24

Survex 1.4.24 z 2026-10-16 naprawia potwierdzony przez autora błąd wag
pionów z 1.4.23 oraz uwzględnia zbieżność siatki przy jawnym `DECL=`.
CI i stabilny Docker używają oficjalnego wydania, przypiętego
w `.github/survex-version`. Szczegóły: [NEWS upstream](https://github.com/ojwb/survex/blob/878202413cac5cbf41b88ee82c0cab72b97725ce/NEWS).

## Tymczasowa deklinacja dla bloków bez daty

W 48 plikach zastąpiono historyczne `DECL=0.819D` przez `DECL=0`.
Poprzednia wartość pochodziła z kompensacji zbieżności siatki projektu,
wprowadzonej w [PR #116](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/pull/116#issuecomment-4527978604)
w celu zachowania orientacji przy usuwaniu ostrzeżeń o brakujących datach.
Nie była ustaloną deklinacją magnetyczną pomiaru. Po poprawce w 1.4.24
pozostawienie jej powodowałoby dodatkowy obrót.

**`DECL=0` jest jawnym założeniem tymczasowym.** Daty pomiarów trzeba
potwierdzić u osób, które kartowały dane partie, lub w ich dokumentacji.
Po ustaleniu daty odpowiedniego bloku należy zastąpić to założenie przez
`#date`, zgodnie z konwencją projektu. Sam brak ostrzeżeń nie potwierdza
poprawnej orientacji magnetycznej.

Każdy zmieniony wpis ma komentarz i wpis `PROCESSING`. Zakres obejmuje
47 plików przetwarzanych przez główny WPJ oraz wcześniej wyłączony
`sniezna/LITWOR.SRV`; jego włączenie do projektu pozostaje bez zmian.
W czterech plikach Bandziocha (`BK-B2D-G`, `BK-C2D-G`, `BK-C2D-S`,
`BK-BCG-G`) zero dotyczy początkowych bloków bez daty; późniejsze `#date`
dalej uruchamiają wyznaczanie deklinacji z IGRF.

Wszystkie dotychczasowe daty, odczyty, identyfikatory stacji, otwory,
WPJ i `_RAW` zachowano bajtowo. Pozostałe jawne wartości `DECL=` są
poza zakresem tej zmiany. Pliki oczekujące na potwierdzenie dat można
wylistować z katalogu głównego:

```sh
rg -l -F 'tymczasowym zalozeniem DECL=0' Poligony -g '*.SRV' -g '!**/_RAW/**'
```

## Potwierdzenie poprawki pionu

Minimalny przykład `plumb.srv`, zapisany poza projektem:

```text
#units meters order=DAV A=D V=D decl=0
#fix 0 0 0 0
#fix 2 10.2 0 10
0 1 10 -- 90
1 2 10 90 0
```

Uruchom każdą wersją, podając pełną nazwę pliku wynikowego, np.:

```sh
cavern -o /tmp/plumb-1.4.24.3d /tmp/plumb.srv
dump3d --legs -D /tmp/plumb-1.4.24.3d
```

| Współrzędne stacji 1 (E, N, Z), m | 1.4.22 | 1.4.23 | 1.4.24 |
| --- | --- | --- | --- |
| Wynik | 0,09; 0,00; 10,00 | 0,12; 0,00; 10,00 | 0,09; 0,00; 10,00 |

Względna wariancja kątowa pionu wróciła z `0.5` do `0.25` wariancji
zwykłego kąta. Kontrola zwykłych odcinków daje tę samą geometrię we wszystkich
trzech wydaniach. Kontrola miękkich fixów RMS zachowuje wynik 1.4.23:
naprawa pionu zachowuje nową skalę domyślnych wariancji względem jawnych
niepewności fixów.

## Geometria całego JKTZ po zmianie

Porównano dane bazowe z `990302b` / PR #139 przed zmianą (`b384abd`)
z wariantem 48 wpisów `DECL=0`. Snapshot otworów jest ten sam.
Wariant końcowy kompiluje się w 1.4.24 bez błędów i ostrzeżeń:
18540 stacji, 18662 odcinki, 198 pętli, 76 komponentów. Nazwy i flagi
stacji oraz wszystkie źródłowe połączenia są zachowane.
Długość przed wyrównaniem wynosi 70053,50 m, po wyrównaniu 69943,68 m.

| Porównanie z końcowym wariantem 1.4.24 + `DECL=0` | Zmienione nazwane stacje | Maks. różnica, m |
| --- | ---: | ---: |
| 1.4.24 z dawnym `DECL=0.819D` | 6910 | 10,057 |
| Kontrolne zachowanie dawnej orientacji tych 48 wpisów, te same wagi 1.4.24 | 1118 | 0,0142 |
| 1.4.22, dane bazowe | 1345 | 1,293 |
| 1.4.23, dane bazowe | 6227 | 3,049 |

Rozdzielczość współrzędnych `.3d` wynosi 1 cm. Kontrola dawnej orientacji
używała diagnostycznego buildu 1.4.24, z wyłączoną korektą zbieżności
wyłącznie dla dawnych `DECL=0.819D`. Wszystkie pozostałe deklinacje, daty,
wagi i solver zachowano. Różnica od zera wynika z tego, że historyczne
0,819° było zaokrągleniem zbieżności około −0,819498°.
Dokładne odtworzenie geometrii wcześniejszych wersji dodatkowo zależy od
pozostałych jawnych `DECL=` i zmian wag. Diagnostyczne źródła i binaria
usunięto po badaniu; instalacja i CI używają oficjalnego kompilatora.

Wybrano jawne zero do czasu odzyskania dat. Porównanie 446 rekordów
wyrównywanych ciągów w `.err` daje RMS przesunięcia 5,178 m, wobec 5,131 m
przy pozostawionym `0.819D` w 1.4.24. Są to statystyki wyrównania ciągów,
a nie 446 niezależnych pętli ani dowód dokładności w terenie. Rozstrzygnięcie
orientacji wymaga dat i pochodzenia pomiarów. Pełne logi i inwentarz kontroli
bajtowej zachowano poza śledzonymi plikami repozytorium.

Kompilacja Survex nie zastępuje sprawdzenia w natywnym Walls.
Brak pliku SRV, choć od 1.4.24 jest ostrzeżeniem Survexa, nadal blokuje
pełną walidację JKTZ.
