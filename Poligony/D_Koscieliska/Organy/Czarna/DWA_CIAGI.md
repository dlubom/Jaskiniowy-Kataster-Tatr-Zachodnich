# Czarna — dwa główne ciągi do przeglądu

Stan: 2026-09-19. Baza PR: `446edc4` (`origin/master`).

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
„Koniec Kolorado”. **K76 nie jest III otworem.** W rejonie Studni Imieninowej
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
**11,47 m poziomo / 12,45 m w 3D**. To różnica dwóch niepotwierdzonych jako
tożsame końców, nie błąd zamknięcia. Nowy Kujat zachowuje `DECL=0` jako
roboczy brak korekty; data i orientacja pozostają nieustalone.

## Źródło odczytu i nierozstrzygnięte wartości

[CZ_GL_R.SRV](CZ_GL_R.SRV) przeniesiono z eksperymentów zapisanych w commicie
[`c878b7b`](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/tree/c878b7b/Poligony/D_Koscieliska/Organy/Czarna).
Z 78 rekordów D/A/V **77 pozostało bez zmian**. W odcinku 49→50
azymut wynosi **88°**, zgodnie z jednoznacznym odczytem i poleceniem użytkownika
z 2026-09-19; poprzednia wartość 68° była robocza. Nie zmieniono żadnego
innego D/A/V. Uzupełniono komentarze z prawej strony tabel na fotografiach.
Oryginalne źródła w `_RAW` tej gałęzi pozostały nienaruszone.
Raporty wcześniejszych odczytów i analiz pozostają w podlinkowanej historii.

Fotografie z `_RAW/02`: `20220325_123052 ciąg gł Czarna 1_Kujat.jpg`
(0–19, 60–76 i Tehuby), `20220325_123533 ciąg gł Czarna 1a.jpg`
(drugie zdjęcie tych samych stron) oraz `20220325_123630 ciąg gł Czarna2.jpg`
(19–60). Autor Ryszard Kujat został potwierdzony przez użytkownika na
podstawie nazwy pierwszej fotografii. Daty i instrumentu nie ustalono.

Kwerenda historyczna z 2026-09-19 niezależnie potwierdziła pełne nazwisko
Ryszarda Kujata i jego przynależność do STJ KW Kraków. **Dla dziennika 0–76
około 1975 r. pozostaje hipotezą kontekstową; data pomiaru jest nieustalona.**
Rok 1975 w inwentarzu dotyczy prac przy północnym otworze i katalogowanego
dziennika, którego tożsamości z naszymi kartkami nie potwierdzono.
[Datowanie, skład osobowy i źródła](DATOWANIE_KUJATA.md) rozdzielają te dowody
od daty listu 3 III 1981. Nie zmieniono `SURVEY_DATE`, `#date` ani geometrii.

| Odcinek | Pole | Roboczo | Alternatywa |
| --- | --- | ---: | ---: |
| 29–30 | D | 13,80 m | 13,60 m |
| 39–40 | A | 75° | 25° |
| 71–72 | V | −1° | +1° |

Nie wybierano cyfr ani znaków według uzyskanego zamknięcia.
`Lh_scan` i `dh_scan` to pomocnicze odczyty obliczeń z dziennika, zawierające
niespójności źródła; nie sterują geometrią. Trzy oznaczenia nie są gwarancją
bezbłędności pozostałych cyfr. Znane starsze problemy (jednostki gałęzi
6500–6509, 11,09/11,90 m, współrzędna B64, daty przyjęte i odsyłacze metadanych)
nie są naprawiane w tym PR i nadal ograniczają ocenę historycznych danych.

## Uwagi z prawej strony pomiarów

Komentarze `UWAGA_S1/S1b` i `UWAGA_S2` w SRV zachowują opisy z kolumny
uwag. `MARGINES_` oraz komentarze podsumowań przenoszą pomocnicze dopiski
wysokościowe, także tam, gdzie brak osobnego opisu. Użyto ASCII i kropek
dziesiętnych wymaganych w SRV. Nawiasy kwadratowe oraz `?` oznaczają
niepewne fragmenty, a nie litery dopisane w źródle.

| Położenie dopisku | Odczyt opisu | Uwagi do odczytu |
| --- | --- | --- |
| 0→1 | Otwór | S1/S1b |
| 2→3 | po [doliczeniu?] 2 m | S1/S1b; środkowe słowo słabe, nie zastosowano dodatkowego przesunięcia do D/A/V |
| przy stacji 6 / wierszu 6→7 | wejście do Tehuby (6) | S1/S1b; numer 6 podany jawnie |
| 25→26 | Podnóże [D…skiego?] (−36,63) | S2; nie rozstrzygnięto nazwy |
| 37→38 | 38 (+28,09); Komin [Świerczewskiego?] | S2; nazwa jest niepewnym odczytem |
| 56→57 | Stanowisko nad [nieczytelne] Progiem | S2; odczyty „Białym” / „Błotnym” pozostają nierozstrzygnięte |
| przy stacji 64 / wierszu 63→64 | 64 – Krawędź Studni Imieninowej +51,39 | S1/S1b; numer 64 podany jawnie |
| 65→66 | Studnia Imieninowa +29,03 | S1/S1b; brak numeru w samym dopisku, przypisanie według jego położenia |
| 75→76 | Koniec Kolorado | S1/S1b; w źródle zapis przez K, łamany „Kolora / do.” |

Kontrolne wysokości i sumy zachowano jako zapisy źródłowe, **nie jako fixy
ani dane sterujące geometrią**. Poprawiana suma przed 57→58, blada liczba
przy 69→70 i zakres sumy +20,79 pozostają niepewne. Nie utożsamiano stanowisk
obu ciągów na podstawie dopisanych nazw.

A49→50=88° zastępuje robocze 68° według odczytu użytkownika, nie przez
optymalizację geometrii. Pozostały trzy formalnie nierozstrzygnięte D/A/V.
Po zmianie różnica surowych końców obu ciągów wynosi 12,45 m zamiast
10,57 m; nadal nie jest błędem zamknięcia. Błędy dojścia starej sieci do
III otworu (10,75 m i 11,75 m) pozostają takie same.

## Weryfikacja

[Skrypt audytu](WERYFIKACJA_DWOCH_CIAGOW.py) i [wynik JSON](WERYFIKACJA_DWOCH_CIAGOW.json)
zapisują SHA-256 wejść, zachowanie transkrypcji, liczniki kompilacji, kontrolę
starych współrzędnych oraz oba obliczalne niezamknięcia.

- 77 rekordów nowego dziennika zgodnych z `c878b7b`; jedyny wyjątek D/A/V
  to zatwierdzone przez użytkownika A49→50=88°. Skrypt wymaga dokładnie tej
  korekty i odrzuca inne zmiany. 205 istniejących SRV spoza `_RAW` pozostaje
  zgodnych bajtowo z bazą `446edc4`.
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
