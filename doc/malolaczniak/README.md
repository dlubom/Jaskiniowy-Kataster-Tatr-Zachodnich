# Małołączniak w On Station i Kartow3

Audyt opisuje oba archiwa zgłoszone w [issue #170](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/issues/170), ich powiązania z aktywnymi pomiarami i uzupełnienia poligonu. [Dowiązania, plany i rozbieżności](PLANY.md)

## Uzupełnienia poligonu

Dodano 89 odcinków o łącznej długości 459,83 m. Tabela prowadzi od wierszy `Shot` w `Malolaczniak.cdi` (numeracja od 1) lub rekordów w `KARTOW.ARJ` (offsety co 30 bajtów od początku POM) do odpowiednich wierszy aktywnego SRV. W obrębie zakresu zachowano kolejność źródła.

| Ciąg | Źródło | Odcinki | Aktywny SRV |
| --- | --- | ---: | --- |
| Partie Głodnych | `P_GLOD.POM`, bajty 30–480 (początki rekordów) | 16 | [MAIN.SRV 520–535](../../Poligony/D_Malej_Laki/Przechod-Kotliny/Syst_W_Snieznej/sniezna/MAIN.SRV#L520-L535) |
| Sala Piotrusia | `S_PIOTR.POM`, bajty 30–360 | 12 | [MAIN.SRV 538–549](../../Poligony/D_Malej_Laki/Przechod-Kotliny/Syst_W_Snieznej/sniezna/MAIN.SRV#L538-L549) |
| Odnoga Nad Kotlinami | CDI 98–100 | 3 | [MAIN.SRV 552–554](../../Poligony/D_Malej_Laki/Przechod-Kotliny/Syst_W_Snieznej/sniezna/MAIN.SRV#L552-L554) |
| Węgierski Labirynt | CDI 976–984 | 9 | [MAIN.SRV 557–565](../../Poligony/D_Malej_Laki/Przechod-Kotliny/Syst_W_Snieznej/sniezna/MAIN.SRV#L557-L565) |
| Krucha Dwudziestka | CDI 1019–1028 oraz `KXX.POM`, bajty 30–300 | 10 + 10 | [MAIN.SRV 568–577](../../Poligony/D_Malej_Laki/Przechod-Kotliny/Syst_W_Snieznej/sniezna/MAIN.SRV#L568-L577) oraz [MAIN.SRV 581–590](../../Poligony/D_Malej_Laki/Przechod-Kotliny/Syst_W_Snieznej/sniezna/MAIN.SRV#L581-L590) |
| Boczny Ciąg | CDI 1050–1077 | 28 | [MAIN.SRV 593–620](../../Poligony/D_Malej_Laki/Przechod-Kotliny/Syst_W_Snieznej/sniezna/MAIN.SRV#L593-L620) |
| Jaskinia przy Przechodzie | CDI 4750 | 1 | [PRZYPRZE.SRV 99](../../Poligony/D_Malej_Laki/Przechod-Kotliny/Przy_Przechodzie/PRZYPRZE.SRV#L99) |

W Novej Kresanicy zmieniono przypisanie wymiarów w 141 ze 142 przekrojów LRUD. [Przykłady i sprawdzenie w Walls](PLANY.md#nová-kresanica)

## Pochodzenie i archiwizacja

Projekt „Małołączniak” w formacie On Station opracował i przekazał Dariusz Bartoszewski. Bolek.zip zawiera wcześniejszy projekt kartograficzny Wiktora Bolka, prowadzony w jego autorskim programie Kartow3. Licencja obu archiwów to [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

| Plik | Bajty | SHA-256 |
| --- | ---: | --- |
| `Malolaczniak.zip` | 55 166 | `94442417841db60095b4848cb9b7d337ed55bb418e31121073c087cb4c988d23` |
| `Malolaczniak.cdi` | 248 837 | `ab0bb9e1c715ace3a2d4f31b3afb0f140f5c87c9b6adfa5b3f287d2d7fdfad65` |
| `Bolek.zip` | 934 446 | `992e3cf8cf36580b72f542dae6a9f52d74dc914c321bda4dd92f6f4dadb3539f` |

Kopia całego CDI w oryginalnym ZIP-ie trafiła do 16 katalogów pomiarowych. Kartow3 trafił do trzech katalogów z powiązaniami potwierdzonymi pomiarami lub współrzędnymi (Wielka Śnieżna, Wielka Litworowa i Śnieżna Studnia). W Śnieżnej są też trzy oryginalne pliki POM użyte do uzupełnienia pomiarów. Spis obejmuje 56 plików z `Bolek.zip`, 10 z `BOLEK.COD → GOLL.ARJ`, 25 z `BOLEK2.COD → KARTOW.ARJ` i jeden CDI. Każdy wiersz podaje rolę, rozmiar i SHA-256. [Spis członków](ARCHIWA.tsv)

## Jak czytać Kartow3

POM i BEZ składają się z rekordów po **30 bajtów**. Rekord pod offsetem 0 jest nagłówkiem. W POM pierwsze dwa napisy podają jednostki azymutu i upadu. W BEZ pierwszy napis to `BEZ`. W pustych polach i za końcem napisów bywają pozostałości pamięci.

| Offset w rekordzie | Długość | POM | BEZ |
| ---: | ---: | --- | --- |
| 0 | 6 | stanowisko | punkt |
| 6 | 6 | cel | poprzednik |
| 12 | 6 | odległość w m | Y eksportu ASC (składowa północna w obliczeniu wektora) |
| 18 | 6 | azymut | X eksportu ASC (składowa wschodnia) |
| 24 | 6 | upad | Z eksportu ASC |

Każdy napis ma bajt długości (0–5) i pięć bajtów miejsca na znaki. Liczby są zapisane jako Pascal Real48. Dla sześciu bajtów `b0…b5` wykładnik to `b0`, bit znaku `s` to bit 7 w `b5`, a ułamek to 39 najmłodszych bitów `b1…b5` w porządku little endian. Gdy wykładnik jest zerowy, wartość wynosi zero. W pozostałych przypadkach wzór to `(−1)^s × 2^(b0−129) × (1 + ułamek/2^39)`. [Dokumentacja reprezentacji Real48](https://docwiki.embarcadero.com/RADStudio/Florence/en/Internal_Data_Formats)

We wszystkich 18 różnych POM azymut ma nagłówek `deg`. Upad ma `deg` w dziewięciu plikach (210 nazwanych rekordów), `grad` w ośmiu (325) i wyjątkowy zapis `gra` w `PRZEMP.POM` (31). Jeden grad to 0,9°. W `KXX.POM` na przykład −16,666667 gradów odpowiada −15°, a +100 gradów oznacza pion. W 28 odcinkach Partii Głodnych i Sali Piotrusia oba kąty mają jednostkę `deg`.

Pomoc `KARTOW3.HLP` opisuje przeliczanie jednostek przy dopisywaniu serii zależnie od opcji operatora. Kod On Station (`surveyleg.cpp`) ma jedno ustawienie jednostki dla obu kątów. Pola `D` w CDI wskazują stopnie. W Amokach odcinek a4 → a5 ma w SRV 200 i −52 grady, którym w CDI 2043 odpowiadają 180° i −46,80°. W Przemkowych Partiach porównanie upadów z eksportami ujawnia dwa przypadki wymagające potwierdzenia jednostki z pomiaru terenowego. [Wyniki porównania](PLANY.md#przemkowe-partie)

Test odczytu POM daje te same nazwy i wszystkie trzy wartości na 26/26 wierszy `NASZE_PO.ASC`. Autor opisał je jako testy na bunkrze. Test BEZ daje m.in. 188/188 pozycji `SG1_1.ASC` oraz 1478/1478 `SYSTEM5.ASC` z dokładnością zaokrąglenia do 0,01 m. W `SYSTEM5.ASC` 306/306 par Galerii Krokodyla daje wektory CDI z błędem końca do 0,035 m. Przy obliczaniu różnic XYZ wykorzystano tylko jednoznaczne współrzędne poprzednika. Długość wektora lub zbieżność nazw bez wartości nie potwierdza tożsamości ciągów.

Do porównań współrzędnych Śnieżnej Studni użyto wersji BEZ z wewnętrznego ARJ, zgodnej z eksportem tekstowym. [Porównanie obu kopii](PLANY.md#śnieżna-studnia)

### Pliki pomiarowe

W dwóch warstwach archiwum są 24 wystąpienia POM. Po połączeniu kopii identycznych bajtowo pozostaje 18 plików. Ich 568 rekordów za nagłówkami obejmuje 566 nazwanych obserwacji i dwa puste rekordy (końcowy w `PP_M` i początkowy w `W80`). Nazwany zapis `EVD5 → EV1` o długości zero jest dowiązaniem. Tabela obejmuje 852 rekordy wszystkich 24 wystąpień plików, z kopiami i pustymi wierszami włącznie. Zachowuje offsety, kierunki, oryginalne wartości i jednostki oraz porównania z CDI i SRV sprzed audytu. Kolumna „Znaleziono zgodne DAV w CDI” dotyczy wyłącznie wyniku wyszukania w CDI. Docelowe wiersze SRV dla wykorzystanych POM wskazuje tabela uzupełnień powyżej. [Porównanie POM](POM.tsv)

| Plik lub grupa | Wynik |
| --- | --- |
| `P_GLOD`, `S_PIOTR` | 28/28 odczytów z dwoma pewnymi stanowiskami dowiązania przeniesiono do SRV. |
| `KXX`, `MPK` | Po 10 rekordów. Krucha Dwudziestka łączy się z `K20.2` odcinkiem 2,50 m. Meander w Partiach za Kolankiem ma zerowe dowiązanie `MPK0 → PK23`. Nazwy istnieją w BEZ. Dla KXX udało się przejść od K20.2 po odcinkach CDI do aktywnego g80. Wszystkie 10 strzałów KXX dodano do MAIN.SRV. Dla MPK nadal brakuje dowiązania PK23 do mierzonej stacji SRV. |
| `PRZEMP` | 31 par i 31 trójek liczbowych w CDI i SRV. Rozbieżność jednostki upadu opisano wyżej. |
| `PP_M` | 8/10 trójek zgodnych po uwzględnieniu kierunku. `SZ3 → SZ4` ma 7,94 m wobec 7,96 m. `SZ9 → SZ11` ma azymut 170° wobec 70° po odwróceniu zapisu CDI (250°). Upad i długość tego odcinka są zgodne. |
| `KROKOD_2`, `_3`, `_4`, `_5` | Po uwzględnieniu znaku `%` w nazwach i odwróceń zgodnych do 0,035 m jest kolejno 23/23, 0/30, 6/6 i 48/59 wektorów. W `_3` powiązano 25 par z Galerią, w `_5` 57. W `_3` odczyt `E2 → E3` ma 3,78 m, 18°, −6 gradów, a odwrócony rekord CDI 3,28 m, 21,54°, −5,77°. Pięć strzałów bocznych do stacji z apostrofem lub cudzysłowem w `_3` oraz dwa przy `M1` w `_5` nie mają rozstrzygniętej funkcji w poligonie. |
| `SG1_1`, `SG1_1'93`, `W1`, `W21`, `W7`, `W7SKRZAT`, `W80` | Brak potwierdzonego przypisania obserwacji do poligonów JKTZ. Pięć plików W występuje także w GOLL.ARJ. Przykładowo w W80 11 par numerów pasuje do CDI, ale żaden z ich wektorów nie osiąga zgodności do 0,035 m. |
| `NASZE_PO` | 26 obserwacji testowych. |

## Sekcje On Station

CDI jest tekstem Windows-1250 (`FileVersion=2.0`, `Program=On Station 3.0a`). Rekord `Shot` zapisuje długość, azymut i nachylenie w stałej kolejności, również w siedmiu sesjach z ekranowym `DataOrder=AITUDLR`. Każdy odczyt ma jednostki metry/stopnie/stopnie, oba odczyty wsteczne `NAN` i puste flagi `()`. Są też 18 lokalnych punktów ustalonych i siatka powierzchni 40 × 55 oraz komentarz `JA0,:otwor`. Pola `SurveyDate` opisują sesje pliku. W Przemkowych Partiach wpisano `1900/1/1`. Daty wykonania pomiarów wymagają odrębnego źródła.

Jedyny wpis `Comment` (CDI 161) nazywa JA0 otworem. JASNYA.SRV identyfikuje otwór jako j0. Piętnaście spośród 18 pól `ConstraintComment` przy lokalnych punktach ustalonych zawiera nazwy jaskiń lub otworów. Na przykład opis przy `Lt1` wskazuje otwór Wielkiej Litworowej, który w obecnym pomiarze ma oznaczenie LT58. Wpis przy jd0 dotyczy archiwalnego pomiaru od otworu Jędrusiowej Dziury. W sekcji Przemkowe Partie cztery osoby mają w polach `Duty` rolę `Exploration` (CDI 2445–2452).

Słownik Bolka `KARTOW.ARJ/NAZ_CP.TXT` wyjaśnia 31 oznaczeń ciągów. W Galerii Krokodyla dopisano nazwy Małe Błotko (X), Ciągi Przykrości (Y), Problem Wodny (PW), Ekstaza (E) i Ciągi Boleści (M). Stacje i trójki wartości można sprawdzić w wierszach CDI 1743, 1778, 1836, 1929 i 1954. W MAIN.SRV wskazano też, które ciągi słownik nazywa Syfonami (SF), Wodospadami (WDS), Suchym Obejściem (SO) i Ciągiem Wodnym (CW). [Spis źródeł](ARCHIWA.tsv)

Poniżej zachowano wynik pierwszego porównania każdej z 38 sekcji z bazą `204c0ef`. W rejestrze CDI wiersz SRV, kierunek, wartości i różnica opisują porównanie z bazą. Ostatnia kolumna podaje ustalenia audytu, w tym zweryfikowane dopasowanie w rejonie Wrocławskich Kominów. Wiersze dodane do poligonu mają tam status „włączono do SRV”. Ich adresy wskazuje tabela uzupełnień powyżej. Kolumna „Zgodne” wymaga zgodnych stacji i trzech wartości w jednostkach SRV, po uwzględnieniu wskazanych odpowiedników nazw lub kierunku. „Inne” obejmuje również świadomie wyłączone powtórzenia, różnice wartości, odrębne pomiary, samą zgodność liczb lub brak mapowania. W tabeli szczegółowej „wariant wartości” oznacza parę pasującą po nazwach, bez rozstrzygania tożsamości terenowej. [Rejestr 3729 rekordów CDI i odpowiadających im wierszy SRV](CDI-SRV.tsv)

| Sekcja CDI | Shot | Zgodne | Inne | Porównywane SRV |
| --- | ---: | ---: | ---: | --- |
| Nad Kotlinami | 109 | 5 | 104 | MAIN, JASNYA, KOLANKO |
| Partie za Kolankiem | 339 | 338 | 1 | KOLANKO |
| Suche Ciągi | 28 | 0 | 28 | MAIN |
| Sniezna | 159 | 6 | 153 | MAIN, WARSZAW, KRAKOW |
| Wodociąg | 207 | 5 | 202 | MAIN |
| Wrocławskie Kominy | 178 | 22 | 156 | WROCL |
| Biała Woda | 35 | 3 | 32 | PRZEMKOW |
| Błotne Łaźnie | 61 | 3 | 58 | MAIN |
| Galeria Krokodyla | 306 | 261 | 45 | SYFONKRA, KROKODYL |
| Amoki1 | 145 | 83 | 62 | AMOKI |
| Amoki2 | 80 | 79 | 1 | AMOKI |
| HIPOTETICAL | 1 | 0 | 1 | — |
| Przemkowe Partie | 277 | 277 | 0 | PRZEMKOW |
| Wielka Litworowa | 244 | 0 | 244 | LITSTARE, KOPERNIK, LITPLYTB, LTPSB, LTPWG, SBB2, SLEPE |
| Śnieżna Studnia 1 | 384 | 384 | 0 | SS |
| Śnieżna Studnia 2 | 357 | 357 | 0 | SS |
| Kozia 1 | 297 | 295 | 2 | KOZIA |
| Kozia 2 | 192 | 192 | 0 | KOZIA |
| Małołącka | 20 | 20 | 0 | MALOLACK |
| Przy Przechodzie | 65 | 60 | 5 | PRZYPRZE |
| Przy Jędrusiowej | 18 | 18 | 0 | PZRYJEDR |
| Koprowa Studnia | 16 | 0 | 16 | KOPRSTUD |
| Studnia Przy Przechodzie | 14 | 14 | 0 | STUDPRZE |
| Upłazkowa | 12 | 12 | 0 | UPLAZKOW |
| Lodowa Małołącka | 11 | 0 | 11 | LODMAL |
| Dziura pod Świstową | 1 | 1 | 0 | DZISWI |
| Wilczy Schron | 2 | 2 | 0 | WILSCH |
| Schron pod Jędrusiową | 2 | 2 | 0 | SCHJED |
| Zaspałkowa Szczelina | 5 | 4 | 1 | ZASSZC |
| Jędrusiowa Dziura | 8 | 0 | 8 | — |
| Niebieska Studnia | 1 | 0 | 1 | — |
| Wstepna czesc | 50 | 50 | 0 | WSTCZ |
| CzescSrodkowa | 31 | 31 | 0 | CZSR |
| Studnia Dzwon | 12 | 12 | 0 | STDDZ |
| Czarna Studnia | 26 | 26 | 0 | CZST |
| Sala podwójna | 22 | 22 | 0 | SAPOD |
| 20m komin | 4 | 4 | 0 | KOM |
| Odkryte z Val | 10 | 10 | 0 | ODZVAL |

W Kolanku zerowe dowiązanie `O$014 → KO231` ma odpowiednik w zapisie wspólnej stacji `KO231` w SRV. We wszystkich 277 odcinkach Przemkowych Partii potwierdzono mapowanie nazw, np. `PP26 → P26` oraz `WW5' → pWWw5`. Różnice dwóch stacji początkowych w Koziej, dalsze przypadki oraz decyzje o wykorzystaniu pomiarów opisano w raporcie. [Weryfikacja na planach i w źródłach](PLANY.md)
