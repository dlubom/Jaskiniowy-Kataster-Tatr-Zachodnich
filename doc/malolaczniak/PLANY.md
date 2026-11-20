# Co widać na planach Małołączniaka

[Wykaz źródeł i odcinków dodanych do SRV](README.md#uzupełnienia-poligonu)

## Przemkowe Partie

**Czy dochodzi nowy korytarz?** Każdy z 277 strzałów sekcji On Station ma odpowiednik w PRZEMKOW.SRV. Ciąg `BW27 → PP26 → … → PP1` to obecny `b27 → P26 → … → P1`. Rysunek pokazuje go od Samarii przez charakterystyczne dwa zakręty przy Korku, dalej przez zacisk Magducha ku Kominowi Biwakowemu. W projekcie są również cztery odrębne serie Przemko z lat 2013–2015, dowiązane przez `Przemkow:pNkk19`. [Porównanie od Samarii](plany/samaria.png) · [Opis przejścia, PIG](https://jaskiniepolski.pgi.gov.pl/Details/Information/496)

**Grady czy stopnie?** W `PRZEMP.POM` sporny jest wyłącznie upad. Na przykład 4,76 m z P21 do P20 odczytano jako +75° w CDI i SRV. Przy gradach jest to +67,5°. Dla całej serii lepszym odtworzeniem obliczeń Bolka są grady. Największa różnica końca pojedynczego wektora względem jego ASC wynosi 0,013 m dla gradów i 0,705 m dla stopni. Na końcu ciągu (`P1`) wariant gradowy wypada 2,66 m dalej na zachód, 0,38 m na północ i 0,24 m wyżej niż stopniowy. Azymuty pozostają w stopniach.

W 31 wariantach usuwano po jednym odcinku od b27 do P1. Liczba pętli była taka sama jak w modelu wejściowym. W pierwszych 30 próbach odcinała się dalsza część poligonu, w ostatniej znikała końcowa stacja P1. Zmiana samych upadów daje bajtowo identyczny raport wyrównania Survex. Pętle w dalszych partiach przesuwają się wraz z dojściem.

Na arkuszu systemu oba warianty są początkowo odsunięte od właściwego rozwidlenia o około 21 m. Po wspólnym przesunięciu `b27` o 2,75 m na zachód i 21,18 m na północ do Samarii (kolumna 6900, wiersz 3778 rastra 000490) średnia odległość 21 ręcznie wskazanych miejsc osi korytarza od linii SRV wynosi 1,32 m dla stopni i 1,14 m dla gradów. Po przesunięciu tej samej kotwicy o dodatkowe 2 m na północ wyniki wynoszą 0,69 i 0,73 m. Tak mała różnica zmienia znak w granicach odczytu z planu. Kartow3 użył gradów przy obliczaniu ASC. Jednostka na przyrządzie pozostaje otwarta. [Punkty odczytu i sposób powtórzenia próby](samaria.tsv)

**Druga seria, PA → PH.** W CDI 2489–2496 i w SRV sześć ukośnych upadów po pomnożeniu przez 0,9 daje niemal dokładnie pełne stopnie. Współrzędne w `QQQ.BEZ` i jego eksporcie `SYSTEM5.ASC` pozwalają sprawdzić tę serię oddzielnie od `PRZEMP.POM`.

| Odcinek SRV | Upad CDI i SRV | Upad z różnicy XYZ, w zaokrągleniu |
| --- | ---: | ---: |
| PA → P28 | +75,56° | +68° |
| P28 → PG | +54,44° | +49° |
| PG → P29 | −76,67° | −69° |
| P29 → P30 | −90° | −90° |
| P30 → P31 | 0° | 0° |
| P31 → P32 | −82,22° | −74° |
| P32 → P33 | −25,56° | −23° |
| P33 → PH | −87,78° | −79° |

Na P33 → PH (24,20 m) błąd końca wektora względem XYZ wynosi 3,71 m przy −87,78° i 0,008 m przy −79°. Cztery ukośne odcinki leżą na pętli od PG przez P29 i pMM23 do PG (43 odcinki, 271,74 m). Niedomknięcie 3D wynosi 9,09 m w obecnym SRV i 9,17 m po zastosowaniu czterech upadów z Kartow3. Dla serii PA → PH w archiwum brakuje pliku POM.

**Sprawdzenie całej sekcji.** PIG podaje 1587 m skartowanych Przemkowych Partii i 234,2 m deniwelacji. Suma 277 długości w SRV wynosi 1587,21 m. W osobnej kompilacji Survex 1.4.24 z jednym lokalnym dowiązaniem b27 skrajne stacje to P54 i pNkk19. Obecny zapis daje 234,69 m deniwelacji. Zmiana pierwszych 31 upadów również daje 234,69 m, ponieważ przesuwa obie skrajne stacje. Po zmianie sześciu upadów PA → PH wynik to 234,06 m. Przeliczenie wszystkich 277 upadów jako gradów daje 221,92 m (222,12 m po zachowaniu pionów). Od PC do pKB0 ciąg Komina Biwakowego wznosi się o 90,84 m wobec 91 m w opisie PIG. Przeliczenie wszystkich upadów tej drogi dałoby 85,90 m. Liczby PIG mogą pochodzić z tego samego kartowania. [Opis Jaskini Śnieżnej, PIG](https://jaskiniepolski.pgi.gov.pl/Details/Information/496)

Z pozostałych 238 odcinków Przemkowych Partii 59 ma w `QQQ.BEZ` odpowiadającą parę punkt–poprzednik. Przy obecnych stopniach 55 mieści się w 0,035 m. Na dwóch odcinkach od SZ58 do SZ56 wektory występują w odwrotnej kolejności. Na SZ54 → SZ53 różni się długość, a na SZ15 → SZ16 azymut. W osobnej Białej Wodzie 35/35 wektorów SRV odtwarza współrzędne `QQQ.BEZ` z różnicą do 0,0011 m. Cztery późniejsze serie Przemko1–4 w paczce `_RAW/03` mają w swoich eksportach własne deklaracje `A=D V=D`.

**Pętla pSZ21.** W pliku `PP_M.POM` oba sporne odczyty należą do pętli przez 21 odcinków. Dla łatwego porównania azymuty poniżej podano od `pSZ11` do `pSZ9`. Źródło mierzyło przeciwnie, od `SZ9` do `SZ11`, i podaje 170°. Płaski rzut planu nie daje w tym miejscu opisanych stacji.

| Azymut pSZ11 → pSZ9 | Długość pSZ4 → pSZ3 | Długość pętli | Niedomknięcie 3D | Względne |
| ---: | ---: | ---: | ---: | ---: |
| 250° (SRV i CDI) | 7,96 m | 95,76 m | 6,19 m | 6,46% |
| 350° (odwrócony POM) | 7,96 m | 95,76 m | 10,54 m | 11,00% |
| 250° | 7,94 m (POM) | 95,74 m | 6,18 m | 6,45% |
| 350° | 7,94 m | 95,74 m | 10,53 m | 11,00% |

Zamiana azymutu na wersję Bolka pogarsza wynik o 4,35 m. Zmiana samej długości o dwa centymetry poprawia go o jeden centymetr. Żadna z prób nie uzasadnia podmiany tych odczytów.

## Partie Głodnych i Sala Piotrusia

Arkusz ma osobną, podpisaną wstawkę **„Nad dnem Mokrej Czterdziestki”**. W głównym rysunku przy studni widać m.in. Obejście Gliwickie. Bezpośrednie nałożenie współrzędnych na ten fragment daje mylący obraz Sali Piotrusia w Suchym Ciągu. Na wstawce przyłożono środek symbolu P.36 do stacji 52/53. Jedno przesunięcie o 0,60 m na wschód i 90,55 m na północ, bez obrotu i zmiany skali, zastosowano do obu serii. [Wstawka z obydwoma poligonami](plany/mokra-wstawka.png)

- **Partie Głodnych.** Od dna studni (`53`) do końcówki `pg17` poligon przesuwa się o 29,38 m na północ i wznosi o 59,66 m. Trafia w północną końcówkę przy znakach zapytania. Zgadza się również boczne rozgałęzienie we wschodnią stronę. Niektóre odcinki wychodzą poza obrys. Opis eksploracji podaje wspinaczkę równoległą do Mokrej Czterdziestki do około 60 m. Najbliższy wcześniejszy odcinek modelu jest od `pg17` odległy o 24,00 m w przestrzeni. [Historia eksploracji PIG](https://jaskiniepolski.pgi.gov.pl/Details/Information/490)
- **Sala Piotrusia.** Od krawędzi studni (`52`) poligon biegnie przez rejon podpisany „Sala Piotrusia” do południowej salki. `sp13` leży przy końcu jej obrysu, 19,66 m poniżej krawędzi. Boczne `sp12` wypada kilka metrów poza wschodnią ścianą na rysunku. W rzeczywistych współrzędnych rzut `sp12` mija wcześniejszy odcinek `Ciag:75–76` o **0,03 m**, lecz ten odcinek biegnie tam **173,62 m niżej**. Obie serie mają po jednym dowiązaniu źródłowym do studni. Na końcach nie ma udokumentowanego połączenia.

## Pozostałe ciągi Wielkiej Śnieżnej

Dla ciągów o dwóch dowiązaniach sprawdzono koniec poligonu przed związaniem go z drugim stanowiskiem. Jaskiniowy rysunek obejmuje również odsunięte wstawki. Dopasowanie położenia i nazw rozwidleń w źródłach ma tu większą wagę niż samo przecięcie kreski na mapie.

| Ciąg | Jak ustalono dowiązanie | Co włączono |
| --- | --- | --- |
| Nad Kotlinami | Po obu stronach `NK24` zgadzają się kolejność i geometria stacji 22–23–24–25–26. `SYSTEM5.ASC` zawiera osobny łańcuch NK24–24A–24B–24C. Przykładowo 24–25 ma 4,14 m w CDI i 4,20 m w SRV. W położeniu bezpośrednim detal wpada w niezarysowaną część arkusza. | 3 odcinki od 24, 9,10 m. |
| Węgierski Labirynt | W CDI odchodzi od `WD96` i dochodzi do `W$10`. W SRV są to `g96` i `w10` w dwóch ciągach. Przy osadzeniu tylko na g96 koniec wypada 0,49 m od w10 w 3D. Poziomy przebieg i odgałęzienie ku północy widać na wstawce „Nad Wodociągiem”. PIG także opisuje górny ciąg między rejonem Połączenia i Wodociągiem. [Wstawka](plany/labirynt-wstawka.png) · [PIG](https://jaskiniepolski.pgi.gov.pl/Details/Information/496) | 9 odcinków, 61,13 m, z odnogą do WL200. |
| Krucha Dwudziestka | CDI prowadzi od `K20.0` przez `K20.2` aż do `WD80`. Odcinki dojściowe WD83–82–81–80 rozpoznano w g83–82–81–80. W MAIN przy g82 jest opis „nad krucha 20”. Bolek nazywa obie serie K20 i KXX Kruchą Dwudziestką i zapisuje pion `KXX0 → K20.2` o długości 2,50 m. Na planie brak numerów tych stacji i powrotnego dowiązania końca KXX. | 10 odcinków K20, 62,17 m, oraz 10 KXX, 36,00 m. Nagłówek KXX ma deg/grad. |
| Ciąg Wodny i Boczny Ciąg | Cały CW od WD73 do WD58 ma w SRV odpowiednik `g73 → 2o1 → … → 2o9 → g58`. W pierwotnym wykazie pominięto aliasy CW1–9. BC jest osobnym ciągiem od WD69 do CW4. Przed przywiązaniem drugiego końca do `2o4` różnica wynosi 0,94 m w 3D. W źródle ostatni odczyt ma kierunek `CW4 → BC601`. [Porównanie CW, BC i wcześniejszego SRV](plany/wodociag.png) | 28 odcinków BC, 128,23 m. Odnogi boczne i kierunki pomiaru zachowano. CW jest już aktywny. |

W czterech dodanych seriach (CDI 98–100, 976–984, 1019–1028 i 1050–1077) różnice XYZ między punktami i poprzednikami z `Bolek/SYSTEM5.ASC` odtwarzają po zaokrągleniu 50 trójek długość–azymut–upad CDI. Łącznie to 260,63 m. Różnica końca żadnego wektora nie przekracza 0,005 m. Zgodność wskazuje na wspólną podstawę części opracowań. Dariusz Bartoszewski i Wiktor Bolek mogli współpracować przy ich przygotowaniu. Kierunek przepływu danych pozostaje nieustalony. KXX pochodzi z osobnego POM.

Trzy pojedyncze odczyty CDI, `NK3 → NK3A` (11,23 m), `NK55 → NK55A` (19,49 m) i `NK70 → NK70A` (4,50 m), mają rozpoznane początki. Brakuje określenia funkcji ich końców. Mogą to być np. domiary w obrębie studni. Pozostają w archiwum. W meandrze za Kolankiem Bolek wprost łączy MPK0 z PK23. Znaleziono wspólny początek starej serii PK0 i aktywnego KO000. Po osadzeniu na nim PK23 leży 5,93 m od KO186 i 6,03 m od KO165 w 3D. Żadnej z tych nazw nie potwierdza źródło. [Rejestr odczytów Bolka](POM.tsv)

## Jaskinia przy Przechodzie

Nowy wiersz `jp20 → jp0′` ma **4,20 m, 78,11°, −22,39°**. Przebiega wewnątrz narysowanej Sieni i kończy się na symbolu dolnego otworu 1. W eksporcie UTM `jp0` ma E 421678,27, N 5454886,12, a `jp0′` E 421678,26, N 5454886,13. Wysokość obu wynosi 1589,15 m na siatce centymetrowej. Tylko `jp0` ma przypisaną współrzędną katalogową. Pozostałe pary z apostrofem wspierają interpretację powrotu do znanego punktu. `jp1/jp1′` dzieli 0,01 m, a `jp7/jp7′` i `jp10/jp10′` pokrywają się do 0,01 m w 3D. Stacje zachowują nazwy z CDI. Dodane 4,20 m to długość odcinka pomiarowego w znanej sali. [Plan Izabelli Luty z poligonem](plany/przechod.png) · [Opis trzech otworów w PIG](https://jaskiniepolski.pgi.gov.pl/Details/Information/1573)

Cztery pozostałe zapisy CDI powtarzają aktywne `jp4–jp5` (7,50 m), `jp5–jp6` (5,74 m), `jp11–jp12` (4,67 m) i `jp601–jp602` (1,73 m). Po jednym odczycie każdej z tych par już wchodziło do poligonu.

## Kozia

**Liczba brakujących pomiarów wynosi zero.** Przykładowo w SRV idziemy `k077 → k078 → k079`. Pierwszy odcinek ma 1,66 m, 266,86°, −9°, a drugi dokładnie wraca. Stacje 077 i 079 zachowują oddzielne nazwy w tym samym miejscu. CDI zapisuje `k079 → k078 → k079`, więc od k077 nie ma przejścia do dalszego ciągu. Drugi przypadek działa identycznie. SRV prowadzi `k144 → k145 → k146`, CDI `k146 → k145 → k146`. Pierwszy odcinek ma 5,99 m, 260,94°, +59,43°. Oba powroty są w SRV oznaczone segmentem L.

| Wariant nazw FROM | Stacje połączone z otworem I | Osobne grupy stacji |
| --- | ---: | --- |
| Obecny SRV | 490 | — |
| Tylko pierwszy początek z CDI | 374 | 116 |
| Tylko drugi początek z CDI | 484 | 6 |
| Oba początki z CDI | 374 | 110 i 6 |

Trasa `k001 → k9619` między otworami ma w każdym wariancie te same 118 odcinków (713,92 m). Po zdjęciu wyłącznie kotwicy II położenie końca z poligonu wynosi E 420613,77, N 5454574,83, H 1824,02 m. GPS II daje E 420615,93, N 5454575,62, H 1839,47 m. Różnica GPS minus poligon to **+2,16 m E, +0,79 m N, +15,45 m H**, czyli 2,30 m w poziomie i 15,62 m w 3D. GPS daje II o 2,48 m wyżej od I, poligon o 12,97 m niżej. Przyjęto pozycje Best z GPS v2.1.3. Domiary od stanowisk GNSS wynoszą 11,66 m do otworu I i 5,80 m do II. Źródło deklaruje dokładność GNSS poniżej 0,10 m. Katalog nie podaje oddzielnych dokładności poziomej i pionowej dla końców domiarów. Oba rekordy po korekcie obliczeń z 16 listopada mają status „nieweryfikowany”. Historyczny plan opisuje II jako −2,8 m. Poprzednie porównanie poziome 0,60 m dotyczyło starszych współrzędnych. Na planie stacja końcowa wypada przy symbolu II w granicach dokładności rysunku. Pozycje otworów nie rozstrzygają, od których stacji rozpoczynały się dwa nawroty. [GPS v2.1.3](https://github.com/dlubom/gps-kataster-obiektow-tatr/releases/tag/v2.1.3)

## Nová Kresanica

Tutaj pytanie dotyczy **kształtu korytarza wokół stacji**. Wszystkie 155 odcinków osi zachowuje swoje nazwy, długości i kierunki. Program On Station zapisuje przy stacji cztery odległości kolejno do stropu, spągu, lewej i prawej ściany. W pliku Walls te same liczby domyślnie oznaczały lewo, prawo, górę i dół. Na narysowanym planie wejścia stacje `0=1` oraz `2=3` leżą w wąskiej szczelinie. W profilu studni z 2002 r. są ponumerowane stanowiska 78, 79 i 80. Między 79 i 80 jest pion 25,65 m. Właśnie tam boczna odległość rzędu 25 m i pionowe wymiary rzędu zaledwie kilku metrów dawały błędny obraz szybu. [Plan i przekrój z 1990 r., druk s. 12](https://sss.sk/wp-content/uploads/2022/10/Jaskyniar_SSS_1991.pdf#page=13) · [Profil z 2002 r., druk s. 28](https://sss.sk/wp-content/uploads/2022/01/Spravodaj_SSS_2003_3.pdf#page=29)

| Stacja | Cztery liczby w źródle (m) | Szerokość × wysokość przed | Szerokość × wysokość zgodnie z CDI |
| --- | --- | --- | --- |
| nvk0, otwór | 0,00 / 2,80 / 0,30 / 0,30 | 2,80 × 0,60 m | **0,60 × 2,80 m** |
| nvk1, poniżej otworu | 4,00 / 6,00 / 0,30 / 0,50 | 10,00 × 0,80 m | **0,80 × 10,00 m** |
| nvk78, Czarna Studnia | 6,00 / 25,00 / 0,00 / 4,00 | 31,00 × 4,00 m | **4,00 × 31,00 m** |

W siedmiu SRV `LRUD=F:UDLR` przypisuje źródłowe odległości do właściwych kierunków. Implementacja `CFileHelper::ReadWalls` i `WriteWalls` w On Station (`filehelper.cpp`, źródłowy ZIP SHA-256 `d4ee9ef9ca47a90351c236dc1968a746ca48654e5a74c429284b179fb0e66510`) potwierdza kolejność U,D,L,R w CDI. Jeden z 142 przekrojów ma ten sam wynik dla obu kolejności.

W Walls 2.3.0-beta.1 (build 2025-09-13) odczytano wszystkie 142 rekordy LRUD z `KATASTER.NTA`, po identyfikatorach stacji z `KATASTER.NTP`. Przypisania do L/R/U/D zgadzają się przed korektą z domyślnym porządkiem Walls, a po korekcie z CDI, do 0,00001 m. Dla nvk78 wynik po korekcie to 0 / 4 / 6 / 25 m. Survex 1.4.24 sprawdza składnię dyrektywy i pomija odległości LRUD w modelu. [Porównanie wszystkich przekrojów](przekroje.tsv) · [Kolejność LRUD w podręczniku Walls](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/blob/234cd571cd05154e4fd83f37cd6e795242faa85c/doc/Walls_manual.md#L4747-L4756) · [Obsługa LRUD w Survex](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/blob/234cd571cd05154e4fd83f37cd6e795242faa85c/doc/Survex_manual/walls.rst#L131-L132) · [Natywny artefakt Walls](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/actions/runs/44627923772/artifacts/14579203993)

## Śnieżna Studnia

Luźny `Bolek/$STUD.BEZ` i wewnętrzny `KARTOW.ARJ/$STUD.BEZ` mają po 22 290 bajtów. **Luźna kopia jest dokładnie tym, co otrzymuje się po zastąpieniu wszystkich 172 bajtów 0x00 wewnętrznego pliku bajtem 0x20 (spacją).** Żaden inny bajt się nie różni. Podmiana objęła też pola liczb Real48. Źródłem obliczonych pozycji jest wersja wewnętrzna, zgodna z 742/742 wierszy tekstowego eksportu w granicach jego zaokrąglenia.

| Współrzędna zmieniona w luźnym BEZ | Stacje (bez początkowego znaku $) |
| --- | --- |
| X o +8 m | 699, 1006, 1522, 1533 |
| Z o +1 m | 930, 1630 |
| X o ok. +0,031 m | 43, 44, 123, 629, 3646, 3647 |
| Y o ok. +0,016 m | 232, 539, 692, 696, 841, 3008, 3026 |

Na przykład od `ss1531` do `ss1533` wewnętrzny BEZ daje składowe +9,396 m na wschód i −3,420 m na północ. Luźna kopia przesuwa koniec o dodatkowe 8 m na wschód. Wszystkie 741 odcinków CDI ma odpowiedniki w SS.SRV.

## Inne rozbieżności w sekcjach On Station

Pełny rejestr obejmuje 3729 strzałów. Dla porównanych par podaje liczby z SRV po sprowadzeniu do kierunku CDI i różnicę końców wektorów w metrach. Znak „—” oznacza brak wyniku w danej kolumnie porównania bazowego. W ostatniej kolumnie podano późniejsze ustalenia. Dla Wrocławskich Kominów są tam także właściwe pary, wartości SRV w kolejności D/A/V i różnice wektorów. [Rejestr CDI](CDI-SRV.tsv) · [Rejestr POM](POM.tsv)

| Sekcja lub miejsce | Przykład i wynik sprawdzenia |
| --- | --- |
| Nad Kotlinami / Jasny Awen | W kierunku JA20 → NK4 CDI daje 10,83 m, 334,13°, −28,28°. Odwrócony zapis SRV daje 14,50 m, 159°, −24°. Przy zwolnieniu fixu Jasnego Awenu i zachowaniu innych kotwic przewidywany otwór mija katalogowy poziomo o 8,41 m z CDI i 14,42 m z SRV. SRV określa odcinek jako domiar wyliczony. Katalogowy otwór pochodzi z rekordu TPN bez określonej dokładności. Pozostawiono oba wyniki do weryfikacji domiaru. |
| Partie za Kolankiem | W CDI PK0 i KO000 są dwiema nazwami końca identycznego odcinka od NK77. Z kolei `O$014 → KO231` ma długość zero. SRV prowadzi z KOKO13 prosto do KO231. Dodanie obu wpisów jako nowych pomiarów powtórzyłoby istniejące dowiązania. |
| Suche Ciągi / Biała Woda / Błotne Łaźnie | SC15–16 ma 15,67 m w CDI i 16,00 m w SRV, a różnica wektora wynosi 0,39 m. W Białej Wodzie nawet największa różnica dla dopasowanej pary wynosi 0,014 m. W Błotnych Łaźniach BL35–SF064 ma 21,41 m wobec 22,07 m i inne kąty, łącznie 1,22 m różnicy końca. Zachowano oba opracowania. |
| Śnieżna / Warszawskie Kaskady | CDI ma bezpośredni WK009–WK010 11,18 m. W SRV są wk9–wk9a (1,60 m pionu) i wk9a–wk10 (9,90 m). Bezpośredni wektor CDI niemal odtwarza przejście przez wk9a. Dodatkowy strzał powieliłby połączenie. |
| Kominy Krakowskie | `KK6D–KK6E` ma w CDI 12,64 m, 11,01°, +27,02°. Od początku historii SRV jest 27,63 m, 11°, +27°. Kartow3 daje 12,64 m z różnic XYZ. Na planie obie linie biegną w tym samym kierunku w rejonie I Progu, bez jednoznacznego oznaczenia końca na którymkolwiek poziomie. Punkt k6e jest końcowy. Brak niezależnego pomiaru długości. |
| Wrocławskie Kominy | W CDI WR500–501 (5,30 m, 229,97°, 0°) i WR502–503 (26 m pionu) odpowiadają przebiegowi przy wr86–87 i wr88–89 w SRV. Same liczby 500–503 trafiają tam na inną gałąź. W pętli z69–z77–z450…–z69 suma surowych wektorów SRV daje błąd 4,32 m na 166,20 m. Po zastąpieniu tylko części od z77 przebiegiem CDI błąd rośnie do 28,54 m. Cała pętla z odczytów CDI domyka się do 0,003 m na 208,35 m i ma odmienne wektory również po drugiej stronie. Łączenie tych opracowań odcinek po odcinku dawałoby sztuczne błędy. |
| Wodociąg | Nazwa WDS9W odpowiada położeniu I9 między I8 i I10, a WD83–WR0 zaczyna WROCL jako g83–z0. Przykład większej różnicy w rozpoznanym CW to CW6–CW7, 3,82 m i 229,99°, wobec 2o6–2o7, 3,80 m i 262°. Numeracja i powrót do g58 rozstrzygają przebieg ciągu. Brak potwierdzenia azymutu tego jednego strzału. |
| Galeria Krokodyla | CDI i obliczone XYZ wspierają gk7–gk314 (0,99 m, 103,16°, +37,19°). Starszy wyłączony pomiar miał 0,80 m, 10°, 0°. W odnodze między %GKx i %D2 CDI ma m.in. %D4–%D3, 5,81 m i +78,56°. W SRV między gk33 i gk46 występują inne stacje i dwa małe piony. W POM KROKOD_3 pięć końcówek z cudzysłowem lub apostrofem i dwie przy M1 w KROKOD_5 wymagają określenia roli. Liczby zgodnych odczytów w poszczególnych POM podaje [opis archiwów](README.md). |
| Amoki / HIPOTETICAL | CDI 2133 ma **ujemną długość** −25,50 m przy +90°, SRV dodatnią 25,50 m przy +100 gradach. Dosłowne przeliczenie zmienia stronę pionu o 51 m, czego plan poziomy nie rozróżni. W 55 nazwach FROM średnik jest częścią zapisu, np. `;p9 → 36`. W drugiej sekcji pierwszy odczyt W$44–p2 (6 m pionu) różni się od aktywnego dowiązania. Osobna linia SK23–SKTT, 120 m, jest w źródle oznaczona jako hipotetyczna. |
| Wielka Litworowa | CDI wprost nazywa Lt1 otworem. Po osadzeniu na obecnym LT58 oba ciągi schodzą przez studnię wlotową. Pierwszy strzał CDI ma 13,15 m, 90°, −81,25°, SRV 13,20 m, 52°, −81°. Dalej różnią się miejsca stacji i podział studni. Zgodność 242 wektorów między Kartow3 i CDI dotyczy starszego opracowania. Nałożenie wszystkich 244 strzałów na obecny poligon dublowałoby co najmniej część korytarzy. [Początek obu pomiarów na osobnym planie Litworowej](plany/litworowa.png) |
| Koprowa Studnia / Lodowa Małołącka | Obie jaskinie mają ponowne pomiary. W Koprowej pierwszy odcinek CDI ks0–ks1 ma 2,23 m, 200,39°, −24,06°, a SRV zaczyna się od ks0–ks10, 1,28 m, 224,1°, −36,9°. W Lodowej CDI zaczyna się od lm0–lm1 (4,51 m, 93,81°, 0°), SRV od 0–1 (3,24 m, 60°, −43°). Zbiory różnią się już ustawieniem pierwszej stacji wewnętrznej. |
| Zaspałkowa Szczelina | Para zss0–zss1, 4,42 m, występuje powtórnie w CDI. W aktywnym poligonie ten odcinek występuje raz. |
| Jędrusiowa Dziura (T.E-12.43) | CDI wskazuje jd0 jako otwór Jędrusiowej Dziury na wys. 1592,80 m. Osiem odcinków jd0–jd8 ma razem 123,85 m i prowadzi 44,00 m w dół. W katalogu otwór to MLZ-0039. Istniejący PZRYJEDR.SRV tego samego systemu zaczyna się przy drugim otworze, MLZ-0002. CDI nie podaje dowiązania między jd8 a stacjami tego pliku. [Opis i plan systemu](https://jaskiniepolski.pgi.gov.pl/Details/Information/1581) |
| Niebieska Studnia (T.E-12.02) | Jedyny wektor nist1–nist0, 46,70 m przy +67°, wznosi się o 42,99 m do ustalonego punktu nist0. GPS identyfikuje otwór MTW-0036. PIG podaje 42 m głębokości i opisuje zejście kolejno przez próg, przełaz i dwie studnie. Wektor oddaje skalę głębokości. Jego dwa końce nie odtwarzają przebiegu tego zejścia. [Opis i przekrój](https://jaskiniepolski.pgi.gov.pl/Details/Information/1533) |

## Metoda i wpływ na model

Użyto rastrów EPSG:2180 bezpośrednio z Georeferencera v0.7.11 i geotransformacji z ich nagłówków. SHA-256 paczki to `4817b7c3aefa0e81eafcff4b0d49173691ab7b13637491f66a3f5848b79be823`. Stacje z kompilacji Survex 1.4.24 przeliczono z EPSG:32634. Po lewej na ilustracjach znajduje się wycinek planu, po prawej ten sam wycinek z linią pomiarową. Wstawki i przesunięcie do Samarii opisano wprost. Zachowano orientację opublikowanych rastrów, której Georeferencer przypisuje status `unverified`. Wymiary odczytane ręcznie z rysunku zależą od grubości kreski i wyboru punktu. [Wydanie Georeferencera](https://github.com/dlubom/Georeferencer/releases/tag/v0.7.11)

Wycinki pochodzą z planów PIG. Wielką Śnieżną opracowali Czesław Szura i Marcin Gala, a arkusz w 2011 r. zestawili J. Grodzicki i Czesław Szura. W podstawach arkusza wymieniono także szkice W. Bolka, więc zgodność obrazu z archiwum nie oznacza dwóch niezależnych pomiarów terenowych. Autorami pozostałych planów są Czesław Szura (Wielka Litworowa), Stanisław Kotarba (Kozia), Izabella Luty (przy Przechodzie) oraz Michał Parczewski i Filip Filar (Śnieżna Studnia). [Wielka Śnieżna](https://jaskiniepolski.pgi.gov.pl/Details/Information/490) · [Wielka Litworowa](https://jaskiniepolski.pgi.gov.pl/Details/Information/491) · [Kozia](https://jaskiniepolski.pgi.gov.pl/Details/Information/1478) · [Przy Przechodzie](https://jaskiniepolski.pgi.gov.pl/Details/Information/1573) · [Śnieżna Studnia](https://jaskiniepolski.pgi.gov.pl/Details/Information/1538)

Survex 1.4.24 z GPS v2.1.3 wykazał względem stanu sprzed audytu (`204c0ef`) **89 dodatkowych odcinków (459,83 m), 87 nowych nazwanych stacji i dwie nowe pętle**. Po wyrównaniu pętli współrzędne 2711 wcześniejszych stacji Wielkiej Śnieżnej zmieniły się na siatce 0,01 m. Największe przesunięcie to 0,203 m na g69. Poza systemem współrzędne wcześniejszych stacji pozostały identyczne. [Zakresy dodanych odcinków](README.md#uzupełnienia-poligonu)
