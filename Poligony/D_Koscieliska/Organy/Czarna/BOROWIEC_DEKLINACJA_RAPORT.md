# Jaskinia Czarna - ciag Borowca, deklinacja i konwersja RECT -> DAV

Data opracowania: 2026-05-10  
Zakres: ciag glowny Wladyslawa Borowca w Jaskini Czarnej, pliki `CZ_B_S.SRV` i `CZ_B_DAV.SRV`.

## Teza

Ciag glowny Borowca zostal wprowadzony do katastru jako wektory prostokatne `RECT order=ENU`.
Zrodlo w `_RAW/02/czarna-borowiec.srv` opisuje jednak lokalny uklad wspolrzednych tak, ze os `X=N`
byla przyjeta zgodnie z lokalnym poludnikiem magnetycznym. To oznacza, ze same roznice
wspolrzednych `E,N,U` nie sa od razu wektorami w siatce projektu. Trzeba je traktowac jako
pomiar w lokalnym ukladzie magnetycznym z lat 1972/73.

Teza robocza: zamiast recznie obracac wektory `RECT`, nalezy przeliczyc ciag Borowca na
standardowy format jaskiniowy `DAV` (dystans, azymut, upad), a nastepnie podac date pomiaru
albo deklinacje, zeby program przetworzyl azymuty magnetyczne.

## Dane

Pomiary Borowca:

- zrodlo robocze w repo: `CZ_B_S.SRV`,
- zrodlo archiwalne: `_RAW/02/czarna-borowiec.srv`,
- daty pomiarow opisane w pliku: luty 1972, marzec 1972, luty 1973,
- przyjeta data reprezentatywna dla nowego pliku: `1972-03-15`.

Otwory kontrolne GNSS/LiDAR z `Poligony/OTWORY.SRV`:

- `Czarna:M:otwor1`: E19.8705053667, N49.2444121431, 1323.42 m,
- `Czarna:Kujat:0`: E19.8812979507, N49.2470745479, 1403.92 m.

Parametry magnetyczne sprawdzono w kalkulatorze BGS IGRF14:

- `1972-02-15`, glowny otwor Czarnej: deklinacja `+1.273 deg E`,
- `1972-03-15`, glowny otwor Czarnej: deklinacja `+1.274 deg E`,
- `1973-02-15`, glowny otwor Czarnej: deklinacja `+1.289 deg E`,
- `1975-08-20`, III otwor Czarnej: deklinacja `+1.384 deg E`.

Konwergencja siatki zapisana w `KATASTER.wpj` przy `.REF` wynosi `-0.819 deg`. Dla pomiaru
z marca 1972 r. oczekiwany kat przejscia od azymutu magnetycznego do ukladu projektu jest
rzedu:

```text
declination - grid_convergence = 1.274 - (-0.819) = 2.093 deg
```

## Konwersja

W pliku `CZ_B_DAV.SRV` kazdy wektor `E,N,U` z `CZ_B_S.SRV` zostal przeliczony na:

```text
D = sqrt(E^2 + N^2 + U^2)
A = atan2(E, N)
V = atan2(U, sqrt(E^2 + N^2))
```

gdzie:

- `D` to dlugosc pochyla,
- `A` to azymut liczony zgodnie z konwencja jaskiniowa od polnocy, zgodnie z ruchem wskazowek zegara,
- `V` to upad, dodatni w gore.

Nowy plik ma:

```text
#prefix2 Czarna
#prefix Borowiec
#units meters order=DAV
#units A=D V=D
#date 1972-03-15
```

Oryginalny plik `CZ_B_S.SRV` zostaje jako zapis zrodlowy `RECT`, ale wszystkie jego aktywne
linie sa skomentowane, a wpis `CZ_B_S` zostal usuniety z `KATASTER.wpj`. Do projektu wlaczono
`CZ_B_DAV.SRV`.

## Eksperyment

Punktem odniesienia byl stan pierwotny, czyli ciag Borowca jako `RECT`.

### Stan pierwotny `RECT`

Survex w `KATASTER.err` pokazywal dla petli od III otworu do ciagu Borowca:

```text
Czarna.Kujat.0 ... Czarna.Borowiec.42
Original length 340.98 m, moved 15.55 m, Error 4.56%
E=23.310225, H=29.096663, V=3.052900
```

Po odpieciu fixa `Czarna:Kujat:0` i porownaniu pozycji obliczonej z poligonu do GNSS/LiDAR:

```text
dE = -12.07 m
dN = +23.76 m
dZ = +2.85 m
blad poziomy = 26.65 m
blad 3D      = 26.80 m
```

Samo dodanie `#date` albo `#units DECL` do pliku `RECT` nic nie zmienialo, bo `RECT`
zawiera gotowe skladowe kartezjanskie. Deklinacja dziala dopiero na azymuty.

### Wariant wdrozony `DAV + #date`

Po konwersji do `DAV` i ustawieniu `#date 1972-03-15` Survex loguje:

```text
Declination: 1.3 deg @ 1972-03-15 / 6.0 deg @ 2024-12-07,
grid convergence: -0.8 deg
```

Wynik dla tej samej petli:

```text
Czarna.Kujat.0 ... Czarna.Borowiec.42
Original length 340.98 m, moved 2.44 m, Error 0.71%
E=2.937678, H=3.673245, V=1.002617
```

Po odpieciu fixa `Czarna:Kujat:0`:

```text
dE = -7.47 m
dN = +7.19 m
dZ = +2.85 m
blad poziomy = 10.37 m
blad 3D      = 10.75 m
```

To jest zasadnicza poprawa wzgledem wersji `RECT`: przesuniecie petli spada z `15.55 m`
do `2.44 m`, a niezalezna kontrola III otworu spada z `26.80 m` do `10.75 m` 3D.

### Warianty kontrolne

Reczna rotacja wektorow `RECT` byla uzyta tylko jako test hipotezy. Dla rotacji o ok.
`-2.0 deg` blad niezalezny po odpieciu III otworu spadal do ok. `5.4-5.6 m` 3D.
Ten test potwierdzil kierunek problemu, ale nie jest preferowanym zapisem danych, bo
ukrywa korekte w samych skladowych `E,N`.

W pliku `DAV` sprawdzono rowniez empiryczne ustawienia `#units DECL`. Minimum dopasowania
do III otworu wystepowalo w okolicy `DECL=2.80 deg`:

```text
DECL=2.80 deg
moved = 1.66 m
E=2.006, H=2.345, V=1.306
dE = -5.01 m
dN = -1.35 m
dZ = +2.86 m
blad poziomy = 5.19 m
blad 3D      = 5.92 m
```

Tego wariantu nie wpisano jako podstawowego, bo jest to kalibracja empiryczna na dwa
precyzyjne otwory, a nie wartosc wynikajaca wprost z modelu pola magnetycznego dla daty
pomiaru. Nalezy go traktowac jako silna wskazowke, ze poza deklinacja mogly wystapic
dodatkowe roznice orientacji lokalnej siatki Borowca albo pozniejszych nawiazan.

## Wynik

Wdrozone zostalo rozwiazanie geodezyjnie jawne:

- `CZ_B_S.SRV` pozostaje jako w calosci skomentowana wersja zrodlowa `RECT`,
- `CZ_B_DAV.SRV` zawiera ten sam ciag przeliczony na `D/A/V`,
- `KATASTER.wpj` zawiera teraz tylko `CZ_B_DAV.SRV`, bez starego wpisu `CZ_B_S`,
- jako data reprezentatywna dla ciagu Borowca przyjeto `1972-03-15`.

Wniosek merytoryczny:

1. Hipoteza o magnetycznej orientacji siatki Borowca jest potwierdzona obliczeniowo.
2. `#date` nie moze naprawic danych zapisanych jako `RECT`, ale dziala po konwersji na `DAV`.
3. Modelowa korekta oparta o IGRF14 wyraznie poprawia zamkniecie miedzy precyzyjnymi otworami.
4. Empiryczne minimum jest jeszcze lepsze niz sama korekta modelowa, ale wymaga osobnej decyzji,
   czy traktujemy je jako dopuszczalna kalibracje archiwalnego ukladu, czy jako wskazowke do
   dalszej weryfikacji w skanach i tabelach `_RAW/02/`.

Rekomendacja:

- obecny stan `DAV + #date 1972-03-15` jest lepszym, jawniejszym modelem danych niz `RECT`,
- przed wpisaniem empirycznego `DECL=2.80 deg` nalezy sprawdzic oryginalne tabele Borowca i
  pozniejsze nawiazania Kujata/Nowaka, zeby rozdzielic blad orientacji Borowca od bledow
  w pomiarach nawiazujacych.

## Zrodla

- British Geological Survey, IGRF14 calculator/API: https://geomag.bgs.ac.uk/data_service/models_compass/igrf_calc.html
- NOAA/NCEI magnetic declination calculator documentation: https://www.ngdc.noaa.gov/geomag/help/declinationHelp.html
- Dane lokalne repozytorium: `CZ_B_S.SRV`, `CZ_B_DAV.SRV`, `_RAW/02/czarna-borowiec.srv`, `Poligony/OTWORY.SRV`, `KATASTER.wpj`.
