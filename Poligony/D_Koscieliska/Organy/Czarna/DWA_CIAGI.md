# Czarna — dwa główne ciągi do przeglądu

Stan: 2026-09-19. Baza PR: `446edc4` (`origin/master`).

W `KATASTER.wpj` są jednocześnie **cała dotychczasowa sieć oparta na Borowcu**
i **osobny, roboczy ciąg główny Ryszarda Kujata 0–76 z Partiami Tehuby 6–a–b**.
To propozycja do oceny, bez rozstrzygnięcia, który pomiar ma być podstawowy.

Nowy ciąg ma własny prefiks `Czarna:CiagSkany`. Początek K0 ustawiono
przy `Czarna:M:otwor1` w [CZ_GL_N.SRV](CZ_GL_N.SRV) jako założenie do oceny.
Na polecenie użytkownika dodano aktywne **hipotetyczne utożsamienie
Kujat 74 = Borowiec 70 = dawny Kujat 13** w osobnym
[CZ_GL_P.SRV](CZ_GL_P.SRV). Dzięki niemu nowy ciąg korzysta z istniejącego
dojścia Kujata do III otworu. **To założenie tożsamości stanowisk, nie nowy
pomiar ani odczyt nawiązania z dziennika.** Tworzy jedną dodatkową pętlę
i zmienia wyrównanie wspólnej sieci; dane dawnych pomiarów pozostają bez zmian.

## Co można obejrzeć

Otwórz `KATASTER.wpj`, rozwiń „Jaskinia Czarna”, a następnie
„Ciag glowny Kujata - wariant roboczy do oceny”. Oba pomiary są dołączone.
W Walls ich widocznością i kolorem można sterować oddzielnie w Segments;
wyłączenie widoczności segmentu nie usuwa go z obliczeń. Aby wyłączyć
hipotetyczne połączenie, **wyłącz z kompilacji osobną pozycję
„HIPOTEZA Kujat 74 = Borowiec 70 - dojscie do III otworu” (`CZ_GL_P`)**.
Pozostaw `CZ_GL_R` i `CZ_GL_N` włączone; wróci układ dwóch ciągów bez
wewnętrznego połączenia. Skrypt audytu odtwarza oba warianty niezależnie.

Kujat dodaje **78 odcinków / 1123,10 m** (1110,30 m głównego ciągu
+ 12,80 m Tehuby) oraz dwa zerowe wektory: ustawienie początku i hipotezę K74=B70.
**To powtórny pomiar przebiegu, nie przyrost długości jaskini.** Zbiorcza suma
aktywnych odcinków i eksporty zawierają oba ciągi; nie używaj tej sumy jako
nowej długości Czarnej. Nie dublowano odgałęzień z istniejących plików.

## Podłączenia

Wszystkie dotychczasowe pliki i ich podłączenia pozostają niezmienione.
Kontrola źródeł nie znalazła odpowiedników 11 wewnętrznych punktów Borowca
w nowym dzienniku Kujata. Bliskie położenie, podobny profil lub równy numer
nie są dowodem tożsamości fizycznego stanowiska. Użytkownik zlecił jednak
przyjęcie rozsądnego połączenia do przeglądu; poniżej wyraźnie odróżniono je od dowodu.

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
| 70 | Sala Bernarda, III otwór i Korytarz Mamuci | CZ_K_S.SRV:67–68 | **hipoteza K74=B70**, osobno w CZ_GL_P |
| — | własne Partie Tehuby | CZ_GL_R.SRV, 6→a→b | dołączone bez dodatkowej hipotezy |

List Kujata w `_RAW/02/20220325_124826 list Kujata.jpg` potwierdza jego
**dawny punkt 13 = Borowiec 70** i wyjście drugiego ciągu z Borowca 65.
Dotyczy to partii końcowych w `CZ_K_S.SRV`, a nie nowego dziennika 0–76.
Fotografia `20220325_124904.jpg` potwierdza te opisy. Nowy dziennik oznacza
K64 jako rejon krawędzi Studni Imieninowej, zejście K65–66 i K76 jako
„Koniec Kolorado”. **K76 nie jest III otworem.** W rejonie Studni Imieninowej
profile różnią się lokalnie o około 20–30 m; nie rozstrzygnięto przyczyny.

### Dlaczego wybrano K74, a nie K70

Punktem docelowym jest **B70**, ponieważ list Kujata wiąże właśnie z nim
stary punkt 13, od którego istnieje zmierzone dojście przez Salę Bernarda
do północnego otworu. Nowy K74 jest w tym rejonie, a dalsze K74–76 prowadzą
do Colorado, podobnie jak B70–73. Długości tych końcowych odcinków wynoszą
odpowiednio 43,00 m i 45,31 m.

Porównanie bez łącznika, po przyjęciu daty i przy obu fixach,
dla aktualnego roboczego D39→40=12,80 m:

| Punkt nowego Kujata | Odległość 3D od B70 |
| --- | ---: |
| K70 | 70,28 m |
| K71 | 53,29 m |
| K72 | 33,82 m |
| K73 | 16,18 m |
| **K74** | **2,99 m** |
| K75 | 19,46 m |
| K76 | 45,22 m |

Dla K74 różnica wynosi +1,90 m E, −0,29 m N i −2,29 m Z
(1,92 m poziomo). To przesłanka do wyboru **kandydata**, nie potwierdzenie
stanowiska. Borowiec w tym porównaniu jest już wyrównany do obu otworów.
Przy liczeniu obu tras niezależnie tylko od głównego otworu różnica K74–B70
wynosi **13,06 m 3D**. Nie należy przedstawiać 2,99 m jako niezależnego
niezamknięcia dwóch pomiarów.

Numeracja nie jest zgodna jeden do jednego. Nie połączono K70 z B70 ani
K76 z III otworem. Nie skanowano możliwych połączeń w poszukiwaniu
najmniejszego błędu GNSS: K74 wybrano w sąsiedztwie udokumentowanego
odejścia B70, a dopiero potem policzono niezamknięcie. Brak szkicu lub
opisu utożsamiającego K74 z B70 pozostaje jawnym ograniczeniem.
Inne lokalne podłączenia nadal mają numery Borowca; nie dopisano im
odpowiedników Kujata. Wspólna sieć jest teraz połączona także przez B70.

## Błędy — wspólna definicja i ograniczenia

Kontrola GNSS polega na pozostawieniu fixa głównego otworu i zdjęciu **tylko
fixa III otworu**, a następnie porównaniu wyliczonej pozycji III otworu
z jego współrzędnymi kontrolnymi. Podano `pozycja obliczona − GNSS`
w siatce UTM 34N. Zachowano aktualne daty i korekty wszystkich istniejących
plików; nie dopasowywano deklinacji do zamknięcia.
Poniższa tabela opisuje aktywny wariant D39→40=12,80 m.

| Wariant kontroli | ΔE | ΔN | ΔZ | Poziomo | 3D |
| --- | ---: | ---: | ---: | ---: | ---: |
| Dotychczasowa sieć bez K74=B70 (kontrola porównawcza) | −7,47 m | +7,19 m | +2,85 m | 10,37 m | **10,75 m** |
| Wspólna sieć z hipotezą K74=B70 | −3,16 m | +3,32 m | +0,14 m | 4,58 m | **4,59 m** |
| Izolowany Borowiec + dawne dojście Kujata | −6,92 m | +9,05 m | +2,87 m | 11,39 m | **11,75 m** |
| Izolowany nowy Kujat + dawne dojście, warunkowo K74=B70 | +1,15 m | +0,06 m | −2,08 m | 1,15 m | **2,38 m** |

Trasa Borowca 0W→B70→dawny Kujat 12→III otwór ma **1164,62 m /
84 mierzone odcinki**, a względne niezamknięcie 3D wynosi **1,01%**.
Trasa nowego Kujata K0→K74→dawny Kujat 12→III otwór ma **1178,16 m /
87 mierzonych odcinków** i warunkowe niezamknięcie **0,20%**.
Nie wliczano zerowych łączników do liczby mierzonych odcinków.

Obie trasy korzystają z **tych samych 110,86 m / 13 odcinków dawnego
pomiaru Kujata**. Są liczone osobno, lecz nie są całkowicie niezależnymi
pomiarami jaskini. Kontrola nowego Kujata nie zawiera wektorów Borowca:
pozostawiono tylko nowy dziennik, dwa łączniki i oryginalne 13 odcinków
od B70 przez dawny K12 do III otworu. Pozostałe dawne gałęzie pominięto
wyłącznie w tymczasowej kopii do kontroli. Sieć ta ma 0 pętli i po usunięciu
fixa III otworu nie jest wyrównywana do jego GNSS.

**2,38 m to wynik warunkowy przy K74=B70 oraz ustawieniu K0 na fixie
głównego otworu.** Nie dowodzi poprawności tych założeń, rzeczywistej daty
ani większej dokładności instrumentu Kujata. **4,59 m** dotyczy wspólnej,
wewnętrznie wyrównanej sieci i nie jest niezależnym błędem Kujata.

Przy obu fixach dodatkowa pętla przesuwa 339 dotychczasowych nazwanych
punktów na poziomie rozdzielczości `dump3d`; największe przesunięcie wynosi
**0,28 m**. Oba fixy pozostają niezmienione. To wynik wyrównania, nie edycja
starych pomiarów. Po wyłączeniu `CZ_GL_P` stare współrzędne wracają do
wartości bazowych (rozdzielczość kontroli 0,01 m).
Współrzędnych kontrolnych GNSS nie audytowano ponownie pod kątem dokładności
ani zgodności punktu terenowego z historyczną stacją.

Dodatkowe porównanie kształtu, bez dat, obrotu, skali i wyrównania:
po ustawieniu obu początków w (0,0,0), końce K76 i B73 różnią się o
**11,72 m poziomo / 12,74 m w 3D**. To różnica dwóch niepotwierdzonych jako
tożsame końców, nie błąd zamknięcia. Ten rachunek celowo pomija korekty
orientacji obu pomiarów i nie opisuje ich aktualnego położenia w projekcie.

### Eksperyment D39→40: 12,20 m i 12,80 m

Na polecenie użytkownika porównano dwie kopie danych różniące się wyłącznie
długością 39→40 w nowym dzienniku. Daty, deklinacja, oba hipotetyczne
ustawienia K0 i K74 oraz stare dojście do III otworu są identyczne.
W każdej próbie fix otworu I pozostaje aktywny, fix III jest zdjęty,
a wyliczona pozycja III jest porównywana z jego GNSS. Izolowana trasa
Kujata ma **0 pętli**, więc wynik nie zawiera wyrównania z ciągiem Borowca.

| D39→40 | ΔE | ΔN | ΔZ | Poziomo | Błąd 3D | Względem długości trasy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **12,20 m** | +0,59 m | −0,07 m | −1,91 m | **0,59 m** | **2,00 m** | 0,17% z 1177,56 m |
| 12,80 m | +1,15 m | +0,06 m | −2,08 m | 1,15 m | 2,38 m | 0,20% z 1178,16 m |

**12,20 m daje mniejszy błąd 3D o 0,38 m** i mniejszy błąd poziomy.
Zmiana długości o 0,60 m przesuwa wyliczony III otwór o
(+0,56; +0,13; −0,17) m, zgodnie z kierunkiem odcinka 39→40.
Skrypt dodatkowo sprawdza długość tego przesunięcia i jego składowe
`0,60*cos(−17°)` oraz `0,60*sin(−17°)`, a także ten sam ruch punktów
K40 i K74 oraz brak ruchu punktów poprzedzających zmieniony odcinek.
Tolerancja 0,02 m uwzględnia współrzędne zaokrąglone do 0,01 m.

We **wspólnej, wewnętrznie wyrównanej sieci** kolejność jest odwrotna:
12,20 m daje 4,72 m błędu 3D, a 12,80 m — 4,59 m. Ta sieć łączy
rozbieżne pomiary Borowca i Kujata, dlatego jej reszta nie jest błędem
samego nowego Kujata. Do porównania odczytu w jego dzienniku służy
powyższa wydzielona trasa.

Wynik pozostaje warunkowy przy K0 na GNSS otworu I i hipotezie K74=B70;
nie dowodzi odczytu cyfry ze skanu ani poprawności nawiązań. W aktywnym
SRV zachowano wpisane przez użytkownika **12,80 m jako wartość roboczą**
z alternatywą 12,20 m. Eksperyment nie zmienia automatycznie transkrypcji.

## Przyjęta data i wpływ deklinacji

Na polecenie użytkownika z 2026-09-19 w `CZ_GL_R.SRV` przyjęto
**`#date 1975-08-20`**, pierwszy dzień akcji otwarcia północnego otworu
opisanej w „Taterniku” 4/1977, s. 184 (20–21 VIII 1975).
`SURVEY_DATE` ma tę samą wartość; komentarze wskazują, że to **data przyjęta
obliczeniowo, nie potwierdzona data dziennika 0–76**. Usunięto `DECL=0`,
aby model deklinacji wynikał z daty. `CZ_GL_N` zawiera tylko zerowy wektor;
jego ustawienie `DECL=0` nie nadaje kierunku nowemu pomiarowi.

Kontrola daty usuwa wewnętrzny łącznik K74=B70 z obu porównywanych
projektów. Porównuje wariant z datą oraz kopię,
w której tylko Kujat 0–76 wraca do `DECL=0` bez daty. Wszystkie istniejące
pomiary zachowują swoje korekty i wyrównanie. W siatce UTM 34N:

| Wielkość | Wynik |
| --- | ---: |
| Obrót kierunku K0→K76 względem wariantu `DECL=0` | +2,209° |
| Przesunięcie K76: ΔE / ΔN / ΔZ | +9,42 / −29,92 / 0,00 m |
| Przesunięcie K76 poziomo | 31,37 m |
| Odległość K76–B73 przed dodaniem daty: poziomo / 3D | 29,14 / 29,23 m |
| Odległość K76–B73 po dodaniu daty: poziomo / 3D | **2,48 / 3,41 m** |
| Różnica K76−B73 po dodaniu daty: ΔE / ΔN / ΔZ | +1,67 / −1,83 / −2,34 m |

Obrót jest efektem zastosowania daty w aktualnej kompilacji Survex,
mierzonym względem wariantu `DECL=0`; nie jest dopasowaniem do Borowca.
Osobna kompilacja samego Kujata z referencją projektu raportuje deklinację
**+1,4° dla 1975-08-20** oraz zbieżność południków **−0,8°** (obie wartości
zaokrąglone przez Survex). Dlatego obrotu w siatce +2,209° nie należy
utożsamiać z samą deklinacją magnetyczną. Ta izolowana sieć ma 0 pętli.
W tym wariancie bez łącznika zmiana daty zachowuje wysokości nowego
ciągu i współrzędne starej sieci na poziomie rozdzielczości `dump3d` (0,01 m).
Wpływ dodania łącznika i wyrównania opisano osobno powyżej.

**3,41 m jest odległością końców dwóch ciągów w projekcie, a nie błędem
zamknięcia Kujata.** Nie potwierdzono fizycznej tożsamości K76 i B73.
Wartość 12,74 m pochodzi z innego porównania: obu surowych ciągów
bez korekt orientacji, po przesunięciu początków do zera.

Aktualne połączenia:

```text
główny otwór ── Borowiec ────────────────── B70 ── dawny Kujat ── III otwór
      └─────── nowy Kujat 0–74 ── [HIPOTEZA K74=B70]
                              └── K75–76 (Colorado)
```

Powstała jedna dodatkowa pętla między dwoma głównymi ciągami. Oba mają
wspólne dawne dojście do III otworu. Usunięcie łącznika `CZ_GL_P` odtwarza
stan bez wewnętrznego dowiązania i bez możliwości obliczenia zamknięcia
nowego Kujata między otworami.

## Źródło odczytu i nierozstrzygnięte wartości

[CZ_GL_R.SRV](CZ_GL_R.SRV) przeniesiono z eksperymentów zapisanych w commicie
[`c878b7b`](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/tree/c878b7b/Poligony/D_Koscieliska/Organy/Czarna).
Z 78 rekordów D/A/V **76 pozostało bez zmian**. W odcinku 49→50
azymut wynosi **88°**, zgodnie z jednoznacznym odczytem i poleceniem użytkownika
z 2026-09-19; poprzednia wartość 68° była robocza. Użytkownik zmienił też
robocze D39→40 z 12,20 m na **12,80 m**, pozostawiając odczyt nierozstrzygnięty.
Nie zmieniono pozostałych D/A/V. Uwzględniono potwierdzone przez użytkownika
pomocnicze odczyty: dh27→28=11,63 m, Lh58→59=6,43 m i Lh74→75=15,40 m.
Uwagi z prawej strony tabel i przeliczone komentarze `ARYTMETYKA`
umieszczono przy właściwych wierszach; arytmetyka jest na końcu.
Oryginalne źródła w `_RAW` tej gałęzi pozostały nienaruszone.
Raporty wcześniejszych odczytów i analiz pozostają w podlinkowanej historii.

Fotografie z `_RAW/02`: `20220325_123052 ciąg gł Czarna 1_Kujat.jpg`
(0–19, 60–76 i Tehuby), `20220325_123533 ciąg gł Czarna 1a.jpg`
(drugie zdjęcie tych samych stron) oraz `20220325_123630 ciąg gł Czarna2.jpg`
(19–60). Autor Ryszard Kujat został potwierdzony przez użytkownika na
podstawie nazwy pierwszej fotografii. Daty i instrumentu nie ustalono.

Kwerenda historyczna z 2026-09-19 niezależnie potwierdziła pełne nazwisko
Ryszarda Kujata i jego przynależność do STJ KW Kraków. **Dla dziennika 0–76
około 1975 r. pozostaje hipotezą historyczną; do obliczeń użytkownik przyjął
1975-08-20.**
Rok 1975 w inwentarzu dotyczy prac przy północnym otworze i katalogowanego
dziennika, którego tożsamości z naszymi kartkami nie potwierdzono.
[Datowanie, skład osobowy i źródła](DATOWANIE_KUJATA.md) rozdzielają te dowody
od daty listu 3 III 1981. Przyjęcie `#date` nie potwierdza datowania kartek.

| Odcinek | Pole | Roboczo | Alternatywa |
| --- | --- | ---: | ---: |
| 39–40 | D | 12,80 m | 12,20 m |

Użytkownik potwierdził D29→30=13,80 m, A39→40=75° i V71→72=−1°;
ich wcześniejsze oznaczenia niepewności usunięto.

Nie wybierano cyfr ani znaków według uzyskanego zamknięcia.
`Lh_scan` i `dh_scan` to pomocnicze odczyty obliczeń z dziennika, zawierające
niespójności źródła; nie sterują geometrią. Pozostałe oznaczenie niepewności
nie jest gwarancją bezbłędności innych cyfr. Znane starsze problemy (jednostki gałęzi
6500–6509, 11,09/11,90 m, współrzędna B64, daty przyjęte i odsyłacze metadanych)
nie są naprawiane w tym PR i nadal ograniczają ocenę historycznych danych.

## Uwagi z prawej strony pomiarów

Komentarze po `Lh_scan` i `dh_scan` w SRV zachowują opisy z kolumny
uwag. `Margines:` oraz komentarze podsumowań przenoszą pomocnicze dopiski
wysokościowe, także tam, gdzie brak osobnego opisu. Oznaczenia stron
pozostały nad grupami wierszy. Użyto ASCII i kropek
dziesiętnych wymaganych w SRV. Nawiasy kwadratowe oraz `?` oznaczają
niepewne fragmenty, a nie litery dopisane w źródle.

| Położenie dopisku | Odczyt opisu | Uwagi do odczytu |
| --- | --- | --- |
| 0→1 | Otwór | S1/S1b |
| 2→3 | po [dodaniu? / obniżeniu?] 2 m | S1/S1b; odczyt nierozstrzygnięty, nie zastosowano dodatkowego przesunięcia do D/A/V |
| przy stacji 6 / wierszu 6→7 | wejście do Tehuby (6) | S1/S1b; numer 6 podany jawnie |
| 25→26 | Podnóże Węgierskiego (−36,63) | S2; nazwa odczytana przez użytkownika |
| 37→38 | 38 (+28,09); Komin Smoluchowskiego | S2; nazwa odczytana przez użytkownika |
| 56→57 | Stanowisko nad Błotnym Progiem | S2; odczyt „Błotnym” potwierdzony przez użytkownika |
| przy stacji 64 / wierszu 63→64 | 64 – Krawędź Studni Imieninowej +51,39 | S1/S1b; numer 64 podany jawnie |
| 65→66 | Studnia Imieninowa +29,03 | S1/S1b; brak numeru w samym dopisku, przypisanie według jego położenia |
| 75→76 | Koniec Kolorado | S1/S1b; w źródle zapis przez K, łamany „Kolora / do.” |

Kontrolne wysokości i sumy zachowano jako zapisy źródłowe, **nie jako fixy
ani dane sterujące geometrią**. Poprawiana suma przed 57→58, blada liczba
przy 69→70 i zakres sumy +20,79 pozostają niepewne. Nie utożsamiano stanowisk
obu ciągów na podstawie dopisanych nazw.

A49→50=88° zastępuje robocze 68° według odczytu użytkownika, nie przez
optymalizację geometrii. Nierozstrzygnięte pozostaje D39→40. Dla jego
aktywnej wartości 12,80 m różnica surowych końców obu ciągów wynosi
12,74 m; nadal nie jest błędem zamknięcia. Błędy dojścia starej sieci do
III otworu bez nowego łącznika (10,75 m i 11,75 m) pozostają wynikami
kontrolnymi. Wyniki po dodaniu hipotezy są w tabeli powyżej.

## Weryfikacja

[Skrypt audytu](WERYFIKACJA_DWOCH_CIAGOW.py) i [wynik JSON](WERYFIKACJA_DWOCH_CIAGOW.json)
zapisują SHA-256 wejść, zachowanie transkrypcji, liczniki kompilacji, kontrolę
starych współrzędnych oraz oba obliczalne niezamknięcia.

- 76 rekordów nowego dziennika zgodnych z `c878b7b`; wyjątki D/A/V
  to zatwierdzone A49→50=88° i robocze D39→40=12,80 m wpisane przez użytkownika.
  Skrypt wymaga dokładnie tych zmian i odrzuca inne. 205 istniejących SRV spoza `_RAW` pozostaje
  zgodnych bajtowo z bazą `446edc4`.
- Jedenaście kontrolnych kompilacji Survex 1.4.22 bez ostrzeżeń: układ bazowy,
  połączony i bez łącznika, wariant bez daty, trzy pełne kontrole bez fixa III
  oraz dwie izolowane trasy do III otworu; dodatkowo izolowany Kujat i wspólna
  sieć dla D39→40=12,20 m. Sprawdzono 12 080 starych nazwanych
  stacji, zgodność K74=B70 po połączeniu i zachowanie obu fixów.
- Sieć główna: **18 591 stacji / 18 719 odcinków**, przyrost +79/+80,
  **204 pętle** (wcześniej 203) i 76 komponentów. Dochodzą 78 wektorów
  pomiarowych i dwa zerowe łączniki. Dane dawnych SRV pozostają identyczne;
  ich współrzędne po wyrównaniu zmieniają się maksymalnie o 0,28 m.
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
