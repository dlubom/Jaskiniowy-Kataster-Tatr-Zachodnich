# Czarna — dwa główne ciągi do przeglądu

Stan: 2026-09-17. Baza PR: `446edc4` (`origin/master`).

W `KATASTER.wpj` są jednocześnie **cała dotychczasowa sieć oparta na Borowcu**
i **osobny, roboczy ciąg główny Ryszarda Kujata 0–76 z Partiami Tehuby 6–a–b**.
To propozycja do oceny, bez rozstrzygnięcia, który pomiar ma być podstawowy.

Nowy ciąg ma własny prefiks `Czarna:CiagSkany`. Jego jedyne połączenie
z istniejącą siecią zapisano osobno w [CZ_GL_N.SRV](CZ_GL_N.SRV): K0 ustawiono
przy `Czarna:M:otwor1`. **To założenie przeglądowe dla nakładki, nie potwierdzony
zerowy domiar.** Dziennik opisuje K0 jako „Otwór”, ale nie identyfikuje punktu
GNSS. Połączenie nie tworzy pętli, więc nie powoduje wzajemnego wyrównywania
obu głównych ciągów. Nie dodano żadnego wewnętrznego utożsamienia ich stacji.

## Co można obejrzeć

Otwórz `KATASTER.wpj`, rozwiń „Jaskinia Czarna”, a następnie
„Ciag glowny Kujata - wariant roboczy do oceny”. Oba pomiary są dołączone.
W Walls ich widocznością i kolorem można sterować oddzielnie w Segments;
wyłączenie widoczności segmentu nie zmienia danych pomiarowych.

Kujat dodaje **78 odcinków / 1122,50 m** (1109,70 m głównego ciągu
+ 12,80 m Tehuby), a plik ustawienia początku jeden zerowy wektor.
**To powtórny pomiar przebiegu, nie przyrost długości jaskini.** Zbiorcza suma
aktywnych odcinków i eksporty zawierają oba ciągi; nie używaj tej sumy jako
nowej długości Czarnej. Nie dublowano odgałęzień z istniejących plików.

## Podłączenia

Wszystkie dotychczasowe pliki i ich podłączenia pozostają niezmienione.
Kontrola źródeł nie znalazła odpowiedników 11 wewnętrznych punktów Borowca
w nowym dzienniku Kujata. Bliskie położenie, podobny profil lub równy numer
nie są dowodem tożsamości fizycznego stanowiska.

| Punkt Borowca | Obecne podłączenie | Plik:wiersz | Przy nowym Kujacie |
| --- | --- | --- | --- |
| 0W | główny otwór; pomiar Kostki przez wspólny fix | CZ_B_DAV.SRV:51; CZ_Z_S.SRV:26 | K0 przy otworze tylko jako jawne założenie |
| 6 | Stromy Meander; powtórzenie 6–7 | CZ_N_S.SRV:165,229 | brak potwierdzonego odpowiednika |
| 7 | powtórzenia 6–7–8 | CZ_N_S.SRV:229–230 | brak |
| 8 | powtórzenia i gałęzie Stromego Meandra | CZ_N_S.SRV:230–232,237 | brak |
| 9 | powtórzenie 8–9 i gałęzie Stromego Meandra | CZ_N_S.SRV:231,239–240 | brak |
| 14 | Kominy nad Salą Łukową | CZ_N_S.SRV:126 | brak |
| 15 | Herkules i Kominy nad Salą Łukową | CZ_N_S.SRV:98,115,125 | brak |
| 30 | powtórzenie 31–30; Studnia pod Kałużą | CZ_N_S.SRV:148–149 | brak |
| 31 | powtórzenie 31–30 | CZ_N_S.SRV:148 | brak |
| 42 | Partie Wawelskie przez Komin Żłobisty | CZ_W_S.SRV:35 | K55 podobny geometrycznie, bez dowodu tożsamości |
| 65 | boczny korytarz nad Brązowym Progiem | CZ_K_S.SRV:97 | brak |
| 70 | Sala Bernarda, III otwór i Korytarz Mamuci | CZ_K_S.SRV:67–68 | brak |
| — | własne Partie Tehuby | CZ_GL_R.SRV, 6→a→b | dołączone bez dodatkowej hipotezy |

List Kujata w `_RAW/02/20220325_124826 list Kujata.jpg` potwierdza jego
**dawny punkt 13 = Borowiec 70** i wyjście drugiego ciągu z Borowca 65.
Dotyczy to partii końcowych w `CZ_K_S.SRV`, a nie nowego dziennika 0–76.
Fotografia `20220325_124904.jpg` potwierdza te opisy. Nowy dziennik oznacza
K64 jako rejon krawędzi Studni Imieninowej, zejście K65–66 i K76 jako
„Koniec Colorado”. **K76 nie jest III otworem.** W rejonie Studni Imieninowej
profile różnią się lokalnie o około 20–30 m; nie rozstrzygnięto przyczyny.

Zatem wariant Kujata nie ma jeszcze przeniesionych partii Wawelskich,
Nowaka ani dojścia do III otworu. Do przeniesienia potrzebne są szkice,
domiary lub rozpoznanie konkretnych stanowisk. Pozostają dostępne przy Borowcu.

## Błędy — wspólna definicja i ograniczenia

Kontrola GNSS polega na pozostawieniu fixa głównego otworu i zdjęciu **tylko
fixa III otworu**, a następnie porównaniu wyliczonej pozycji III otworu
z jego współrzędnymi kontrolnymi. Podano `pozycja obliczona − GNSS`
w siatce UTM 34N. Zachowano aktualne daty i korekty wszystkich istniejących
plików; nie dopasowywano deklinacji do zamknięcia.

| Wariant kontroli | ΔE | ΔN | ΔZ | Poziomo | 3D |
| --- | ---: | ---: | ---: | ---: | ---: |
| Obecna sieć (Borowiec + istniejące partie, w tym powtórzenia Nowaka) | −7,47 m | +7,19 m | +2,85 m | 10,37 m | **10,75 m** |
| Izolowany Borowiec + stare partie końcowe Kujata (`CZ_B_DAV` + `CZ_K_S`) | −6,92 m | +9,05 m | +2,87 m | 11,39 m | **11,75 m** |
| Nowy Kujat 0–76 | — | — | — | — | **niewyznaczalny bez drugiego dowiązania** |

W drugim wierszu trasa 0W→B70→dawny Kujat 12→III otwór ma **1164,62 m /
84 odcinki**; względne niezamknięcie 3D to **1,01%**. To kontrola całej trasy
z dojściem, nie dokładność samego instrumentu Borowca. Pierwszy wiersz jest
wynikiem sieci z dodatkowymi pomiarami i jej wewnętrznym wyrównaniem.
Współrzędne `dump3d` są zaokrąglone do 0,01 m; podane wyniki nie mają
milimetrowej precyzji. Współrzędnych kontrolnych GNSS nie audytowano ponownie
pod kątem dokładności ani zgodności punktu terenowego z historyczną stacją.

Przy obu fixach Survex raportuje dla części III otwór→B42 przesunięcie
wyrównania **2,44 m / 340,98 m = 0,71%**. Nie jest to powyższe niezamknięcie
całej trasy ani błąd Kujata. Nowy dziennik jest drzewem bez pętli:
brak obliczalnego zamknięcia nie oznacza błędu 0 m.

Dodatkowe porównanie kształtu, bez dat, obrotu, skali i wyrównania:
po ustawieniu obu początków w (0,0,0), końce K76 i B73 różnią się o
**9,40 m poziomo / 10,57 m w 3D**. To różnica dwóch niepotwierdzonych jako
tożsame końców, nie błąd zamknięcia. Nowy Kujat zachowuje `DECL=0` jako
roboczy brak korekty; data i orientacja pozostają nieustalone.

## Źródło odczytu i nierozstrzygnięte wartości

[CZ_GL_R.SRV](CZ_GL_R.SRV) przeniesiono z eksperymentów zapisanych w commicie
[`c878b7b`](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/tree/c878b7b/Poligony/D_Koscieliska/Organy/Czarna).
Przeniesiono wszystkie 78 D/A/V bez zmian; dostosowano jedynie opis włączenia
oraz metadane. Oryginalne źródła w `_RAW` pozostały nienaruszone.
Raporty wcześniejszych odczytów i analiz pozostają w podlinkowanej historii.

Fotografie z `_RAW/02`: `20220325_123052 ciąg gł Czarna 1_Kujat.jpg`
(0–19, 60–76 i Tehuby), `20220325_123533 ciąg gł Czarna 1a.jpg`
(drugie zdjęcie tych samych stron) oraz `20220325_123630 ciąg gł Czarna2.jpg`
(19–60). Autor Ryszard Kujat został potwierdzony przez użytkownika na
podstawie nazwy pierwszej fotografii. Daty i instrumentu nie ustalono.

| Odcinek | Pole | Roboczo | Alternatywa |
| --- | --- | ---: | ---: |
| 29–30 | D | 13,80 m | 13,60 m |
| 39–40 | A | 75° | 25° |
| 49–50 | A | 68° | 88° |
| 71–72 | V | −1° | +1° |

Nie wybierano cyfr ani znaków według uzyskanego zamknięcia.
`Lh_scan` i `dh_scan` to pomocnicze odczyty obliczeń z dziennika, zawierające
niespójności źródła; nie sterują geometrią. Cztery oznaczenia nie są gwarancją
bezbłędności pozostałych cyfr. Znane starsze problemy (jednostki gałęzi
6500–6509, 11,09/11,90 m, współrzędna B64, daty przyjęte i odsyłacze metadanych)
nie są naprawiane w tym PR i nadal ograniczają ocenę historycznych danych.

## Weryfikacja

[Skrypt audytu](WERYFIKACJA_DWOCH_CIAGOW.py) i [wynik JSON](WERYFIKACJA_DWOCH_CIAGOW.json)
zapisują SHA-256 wejść, zachowanie transkrypcji, liczniki kompilacji, kontrolę
starych współrzędnych oraz oba obliczalne niezamknięcia.

- 78 rekordów nowego dziennika zgodnych z `c878b7b`; 205 istniejących SRV
  spoza `_RAW` zgodnych bajtowo z bazą `446edc4`.
- Pięć kontrolnych kompilacji Survex 1.4.22 bez ostrzeżeń. Dodanie Kujata
  nie przesuwa żadnej z **12 080 dotychczasowych nazwanych stacji** przy obu
  fixach ani po zdjęciu fixa III otworu (rozdzielczość porównania: 0,01 m).
  Niezależny przegląd potwierdził też niezmieniony multizbiór punktów anonimowych.
- Sieć główna: **18 591 stacji / 18 718 odcinków**, przyrost +79/+79,
  nadal **203 pętle i 76 komponentów**. Dochodzą 78 wektorów pomiarowych
  i zerowy wektor ustawienia K0; brak nowych pętli.
- **156 testów**, Ruff format/check i wszystkie **12/12 etapów
  `jktz-validate`** przeszły, w tym 87 fixów GPS v1.0.2 i eksporty.
- Niezależny przegląd integracji nie wykazał istotnych usterek. Nie był
  ponownym odczytem wszystkich skanów. Nie kompilowano w natywnej aplikacji Walls.

Odtworzenie z głównego katalogu pełnego klonu repo (potrzebne `cavern`,
`dump3d` i obie rewizje git wymienione w JSON; bez pobierania nowych danych):

```sh
uv run python Poligony/D_Koscieliska/Organy/Czarna/WERYFIKACJA_DWOCH_CIAGOW.py /tmp/czarna-weryfikacja.json
```

Skrypt buduje kopie wejść w katalogu tymczasowym i sprawdza asercje, bez
zmiany danych źródłowych. Liczby w JSON zachowują wynik działań arytmetycznych;
ich precyzję nadal ogranicza zaokrąglenie `dump3d` do 0,01 m.
Stan CI i publikacji należy sprawdzić przy konkretnym SHA w PR; powyższe
wyniki są lokalne.
