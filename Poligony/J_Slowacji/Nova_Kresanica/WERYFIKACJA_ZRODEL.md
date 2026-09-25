# Weryfikacja źródeł — Nova Kresanica

Audyt: 2026-09-25. Stan wejściowy: czysty `master`, commit
`7d8058a12c173bb012556273622de1a9f00d4c59`. Zakres odczytu: repozytorium
i jego historia, wskazane konta Gmail, Google Drive i OneDrive, lokalny zrzut
PIG oraz odnalezione publikacje. Audyt nie obejmuje wysyłania korespondencji ani
przeglądania innych prywatnych kont. Dla wersji po zmianie numery wierszy i
SHA-256 aktywnych SRV są w [rejestrze porównania](POROWNANIE_2009_3D.csv).

## Identyfikacja i stan wejściowy

`KATASTER.wpj:44–66` zawiera książkę `Nova Kresanica` (`.NAME NK`) i siedem
aktywnych plików: `WSTCZ`, `CZSR`, `STDDZ`, `ODZVAL`, `CZST`, `SAPOD`, `KOM`.
Wszystkie używają `#prefix NovaKresanica`, `#units meters order=AVD`, kątów w
stopniach, `#date 2007-01-03` i `SOURCE_REF "_RAW/01"`. Otwór `nvk0` jest
w `WSTCZ.SRV`, a `Poligony/OTWORY.SRV.j2` wiąże go z obiektem GPS `SK-0001`;
wersjonowana migawka zawiera `E19.91418777 N49.22918839 2016m`.
Rekord `SK-0001/m-001` w lokalnym projekcie GPS ma te same liczby, metodę
`source_record`, status `nieweryfikowany`, nieznane datum wysokości i opis
„maintainer-supplied”; nie wskazuje pierwotnego raportu GPS ani metody
pomiaru. Zgodność liczb z M02 nie dowodzi niezależnego potwierdzenia.
`WPJ:NK` jest identyfikatorem projektu, nie potwierdzonym numerem inwentarzowym.
W lokalnym zrzucie polskiego PIG nie ma trafienia `Kresanic*`; chodzi o obiekt
po słowackiej stronie Tatr. Polska nazwa w materiałach wtórnych to
„Nowa Krzesanicka”.

[Relacja Juraja Szunyoga w *Spravodaj SSS* 3/2002, s. 36](https://sss.sk/wp-content/uploads/2022/01/Spravodaj_SSS_2002_3.pdf)
wspomina wysokość otworu 2016 m. Jest to zgodny kontekst publikacyjny,
nie niezależny raport GPS ani dowód metody wyznaczenia wysokości.

| Plik | Aktywne odcinki | Wiersze z LRUD |
| --- | ---: | ---: |
| WSTCZ.SRV | 50 | 44 |
| CZSR.SRV | 31 | 29 |
| STDDZ.SRV | 12 | 12 |
| ODZVAL.SRV | 10 | 9 |
| CZST.SRV | 26 | 25 |
| SAPOD.SRV | 22 | 19 |
| KOM.SRV | 4 | 4 |
| **Razem** | **155** | **142** |

Nie ma aktywnych strzałów do `-`, wyłączonych wierszy pomiarowych ani
niepodłączonych plików tej jaskini w bieżącym katalogu. Komentarze dotyczą
otworu, wątpliwej daty i nieznanych mierniczych. Przed audytem `_RAW/01`
zawierał wyłącznie poprawny składniowo `README.md` ze statusem `niedostępny`.

## Łańcuch źródeł i poszukiwania

| ID | Materiał i pochodzenie | Rola, integralność i ograniczenie |
| --- | --- | --- |
| P00 | [Peter Holúbek, „Jaskyňa Nová Kresanica”, *Jaskyniar* 1991, drukowane s. 11–12](https://sss.sk/wp-content/uploads/2022/10/Jaskyniar_SSS_1991.pdf) | Wczesny, podpisany opis i plan z przekrojem historycznego pomiaru. Na planie są daty i nazwiska mierniczych, lecz nie ma tabeli liczbowych obserwacji `D/A/V` ani LRUD. Pobrany PDF: 6 673 112 B, SHA-256 `62ea952e284c8ac504a5f84cfc62aa05e3a9a37c0daf9ccb76295acc84b4c17c`. Obejrzano obie strony jako obrazy; brak potwierdzonego mapowania jego stanowisk na obecne SRV. |
| P01 | [Juraj Szunyog, „Jaskyňa Nová Kresanica má hĺbkový rekord v Červených vrchoch”, *Spravodaj SSS* 3/2003, drukowane s. 27–29](https://sss.sk/wp-content/uploads/2022/01/Spravodaj_SSS_2003_3.pdf) | Relacja z pomiarów 16 listopada i 14 grudnia 2002 r. oraz profil „Objavy 2002” z numerami stanowisk 70–101, „Čierna studňa” i punktem −183,44 m. Obejrzano tekst i rysunki; nie ma tabeli wektorów ani LRUD. PDF 4 666 911 B, SHA-256 `7244dcdb5c7c65ba701f210014ba0dcd20ed43f2b527e095c235ea1f604aef51`. |
| H01 | Najstarszy ślad Git: commit `5952fd2530024e37bed9821d38b1e307eacdf2e1` z 2014-11-26, dawne `Jaskinie-poligony/Jaskinie Słowacji/Nova Kresanica/` | Siedem już przepisanych SRV. Wszystkie 155 wierszy pomiarowych, w tym pola LRUD, jest bajtowo identycznych z wejściem audytu. Git nie zawiera wcześniejszego dziennika ani Theriona; nazwy i bajty dawnych SRV nie dowodzą ich pierwotnego pochodzenia. |
| M01 | Gmail, mail Juraja Szunyoga z 2013-10-30, wiadomość `142095778756e615`, załącznik `cave.3d` | Nadawca opisuje go jako centerline dla Survex i pisze, że dane ma w Therion. Pełny oryginalny załącznik wydobyto z raw MIME, bez podglądu/OCR: 5237 B, SHA-256 `24a17df9a260fbedc9eb48666d4fb48bc5bbcb8786003ede425d374fda5fad8b`. Identyczne bajty zachowano w [`_RAW/02/cave.3d`](_RAW/02/cave.3d). To skompilowana geometria w formacie v4, nie odczyty terenowe. |
| M02 | Gmail, wątek „Pytanko”, 2014-12-24 – 2015-01-14, m.in. wiadomości `14acdb0852c0ebb5` i `14ae2ee5b621d1a4` | Darek Lubomski pisał 2015-01-09, że ma pomiary od Juraja Szunyoga, lecz nie ma współrzędnych otworu. Redakcja „Jaskiń” przekazała prośbę przez Dominikę do Petera Holúbka; 2015-01-13 Paulina przesłała otrzymane współrzędne WGS84 `49,22918839 / 19,91418777`, a Darek potwierdził ich dodanie. Nie ma bezpośredniej wiadomości Petera, potwierdzenia autora lub metody pomiaru, wysokości ani raportu GPS. |
| M03 | Gmail, wiadomość `149f0e1f28196ae9` z 2014-11-27 i załączniki Bartoszewskiego `zmiany_darek.zip` (`141ea420dba749ae`) oraz `495-Interessante.zip` (`1493c2c4c522fca8`) | Darek Lubomski napisał, że pomiary Novej Kresanicy miał Darek Bartoszewski; to relacja o posiadaniu plików, bez załącznika lub łańcucha przekazania. Oba ZIP mają po pięć SRV dotyczących innych prac; sprawdzenie nazw i treści członków nie ujawniło `kresan`, `nvk` ani `nk_0`. SHA-256 ZIP: odpowiednio `fc39e30fbed9d30d8bb16b565b2a33fd3cb0576bb70cbe59b845f1f50fe62b64` i `b778163ec8d1fcdc9c85d9e4d161fc93a535f6403611b5a527e7ed8eecf42cfc`. Nie są potwierdzonym źródłem Novej Kresanicy. |
| M04 | Gmail, wiadomość z 2014-06-21 `146bdfcac1eab978` z adresu `info@air-sport.pl` | Przekazuje współrzędne czterech innych jaskiń, odczytane z fotomapy Geoportalu na prośbę Darka; nie wymienia Novej Kresanicy. Nie jest dowodem pochodzenia jej otworu. |
| M05 | Gmail, mail Darka Lubomskiego do Krzysztofa Dudzińskiego z 2013-11-22, `1427ec96379b0a2f`, załącznik `cave(1).3d` | Darek pisał, że Juraj Szunyog przysłał mu jedynie wynikowy plik 3D. Załącznik 5237 B, SHA-256 `24a17df9a260fbedc9eb48666d4fb48bc5bbcb8786003ede425d374fda5fad8b`, jest bajtowo identyczny z M01. To potwierdza przekazanie tego samego modelu Dudzińskiemu, bez nowego źródła obserwacji lub LRUD. |
| M06 | Gmail, wątek z Jurajem Szunyogiem `141eea09acaf335f`, odpowiedź Darka z 2013-10-30 `1420af3db65aeb23` | Po otrzymaniu M01 Darek poprosił o plik źródłowy Survex (w mailu zapisany jako „srx file”), który chciał przekonwertować do Walls. W przeszukanym Gmailu nie ma odpowiedzi Juraja; jedyny jego mail zawiera M01. To nie wyklucza przekazania źródła innym kanałem. |
| G01 | Projekt GPS, [rekord `SK-0001/m-001` w commicie `a3dd1a6`](https://github.com/dlubom/gps-kataster-obiektow-tatr/blob/a3dd1a671d3d93cd6958242fc68ddcf1d37cf846/data/objects/SK/SK-0001.yml) | Aktywny obiekt GPS z lat/lon `49.22918839 / 19.91418777` i wysokością `2016.0`; źródło oznaczone jako przekazane przez opiekuna projektu, `verification_status: nieweryfikowany`, `elevation_datum: unknown`, bez załącznika. Nie dowodzi terenowego pomiaru ani autorstwa Dudzińskiego. |
| O01 | OneDrive, `Moje pliki/Pulpit_2021_głownie_Hagen/Jaskiniowy-Kataster-Tatr-Zachodnich-master/Jaskinie-poligony/Jaskinie Slowacji/Nova Kresanica`, 2020-06-10 | Siedem plików SRV o tych samych nazwach co w repozytorium, w katalogu kopii projektu. OneDrive nie udostępnił podglądu SRV ani pobranego pliku, więc nie stwierdzono zgodności bajtowej. Samo położenie wskazuje kopię JKTZ, nie niezależny plik autora. |
| O02 | OneDrive, `!Bajzel/Pomiary/Pomiary.zip` (2014-05-12, 86,8 KB) i `jaskinie pliki.zip` (2014-05-13, 22,7 KB) | Ogólnie nazwane archiwa; podgląd nie podał listy plików, a próby pobrania obu zakończyły się przekroczeniem czasu w przeglądarce. Zawartość pozostaje **niesprawdzona**. Rozwinięty folder `jaskinie pliki` zawiera tylko inne nazwy, co nie rozstrzyga zawartości ZIP. |
| D01 | Google Drive, skan `Skrypt_SKTJ_scan_2010.pdf`, ID `0B5DlYSWcJLlwaEpqRFVkMVlLR28`, drukowana s. 3 | Materiał wtórny: 820 m i 183 m. Pobrane 27 748 175 B, SHA-256 `40b6235de45ea7258f66286afde061068c22e3767eba2120cb4ba8a46b991219`. Sprawdzono obraz strony; brak pomiarów wierszowych. |
| D02 | Google Drive, `062_TRK.pdf`, ID `1Cyixf6tORhMoiAKTkVH7bNDaX3vpAMqN`, s. 3 | Podobny, późniejszy tekst z tymi samymi statystykami; nie jest niezależnym potwierdzeniem D01. Pobrane 137 642 B, SHA-256 `8492e5f511a93502d8bb6765baee7619b9bf668ac72d92eace6dadf4276347c8`. |
| D03 | Google Drive, Gradziński i in., *Przegląd Geologiczny* 57(8), 2009, s. 676; ID `0B5DlYSWcJLlwbTVQN0J3NU5RUmc` | Kontekst publikacyjny: 820 m i 200 m; bibliografia odsyła do Holúbek–Šmoll 1995. Pobrane PDF SHA-256 `2f264cdd855f464f94146a1408e84af71ecbde5fb2b39f18d717a55fba2c597a`. Nie zawiera wierszy obserwacyjnych użytych do SRV. |

W Gmailu sprawdzono `Nova Kresanica`, `Nová Kresanica`, `Kresanica`,
`Nova_Kresanica`, `NK_01`, `nvk`, nazwiska Szunyog, Šmoll, Holúbek i
Bartoszewski, nazwy formatów `.th`, `.th2`, `.thconfig`, `.svx`, `.srv` oraz
załączniki; istotne wyniki nie miały następnej strony. Dodatkowy przegląd
załączników Gmail z lat 2013–2015 według rozszerzeń dał 6 wiadomości z
`.svx`, 0 z `.th`, 18 z `.srv` i 11 z `.3d`; pliki innych jaskiń nie są
źródłami Novej, a dwa wystąpienia `cave.3d` to identyczne bajty M01/M05.
Wyszukiwania daty `2007-01-03` razem z nazwą jaskini lub nadawcą
Bartoszewskim oraz frazy `Kresanica` z `LRUD` nie dały trafień. Przejrzano
wszystkie 22 odebrane i 31 wysłanych wiadomości z adresem Dudzińskiego
`info@air-sport.pl`, ich cytowane wątki i załączniki. Jego jedyny mail z
liczbowymi współrzędnymi GPS (M04) dotyczy innych jaskiń; mail o Novej
`14285d1dd1eacd4f` nie zawiera współrzędnych. W Google Drive sprawdzono
te nazwy, `Krzesanicka`, siedem nazw sekcji i nazwiska. W OneDrive
wyszukano warianty nazwy, autorów, nazwy sekcji oraz `.th`, `.svx`, `.srx`
i `cave.3d`; wynik O01 jest kopią projektu, a O02 pozostał nieodczytany.
Nie znaleziono pierwotnego Theriona ani dziennika. Wynik dotyczy dostępnej
zawartości tych kont i przejrzanych plików, nie innych archiwów lub osób.
Przeszukano również członków 13 archiwów ZIP dostępnych w historii Git;
trafienia dotyczą innych jaskiń, bez zidentyfikowanego źródła Novej
Kresanicy. To ograniczony wynik wyszukiwania, nie dowód nieistnienia
nieodnalezionych albo inaczej nazwanych materiałów.
M02 przypisuje przekazanie posiadanych pomiarów Szunyogowi, natomiast M03
wskazuje Bartoszewskiego jako posiadacza. Obie relacje mogą opisywać różne
etapy przekazania, lecz nie ma plików ani korespondencji, które potwierdzają
ich połączenie.

Publikacja P00 podaje dla opisanego wtedy stanu długość 247 m, głębokość
72,5 m i wysokość otworu 2016,5 m. Podpis planu przypisuje pomiar
16 czerwca 1990 r. Holúbkowi i Šmollowi, a pomiar nocą z 7 na 8 lipca
1990 r. Holúbkowi, Staroňowi i Kleskeňowi. Plan zawiera numery stanowisk
(m.in. 131–159 i 181–194), zarys korytarzy i przekroje, ale nie zawiera
wartości poszczególnych odcinków. Jest to **osobny historyczny stan pomiaru**:
bez dziennika albo udokumentowanego przejścia numeracji nie da się przypisać
jego dat,
mierniczych ani wartości do żadnego z obecnych 155 wierszy. Wysokości
2016,5 m z publikacji nie użyto do zmiany aktywnego otworu GPS.

Publikacja Juraja Szunyoga w [*Spravodaj SSS* 3/2002, s. 36–38](https://sss.sk/wp-content/uploads/2022/01/Spravodaj_SSS_2002_3.pdf)
opisuje eksplorację i odkrycie nowych partii w 2002 r.; jest dowodem historii
prac, a nie daty każdego z 155 pomiarów. P01 podaje konkretnie, że
16 listopada 2002 r. Szunyog i Ľubomír Očkaik zaczęli mierzyć nowe partie,
a Peter Vaněk później pomógł przy Čiernej studni; tego dnia zmierzono
76,11 m. Podczas następnej akcji 14 grudnia zmierzono dalszą studnię;
autor podaje łącznie 163 m z obu akcji, długość jaskini 641 m i punkt
na głębokości 183,44 m. Rysunek „Objavy 2002” oznacza stacje 70–101:
numery i przebieg odpowiadają zakresowi aktywnego `ODZVAL.SRV` od `nvk70`
oraz `CZST.SRV` od `nvk76`. Suma ich wszystkich aktywnych długości wynosi
163,17 m, zgodnie z zaokrąglonym 163 m w relacji. To mocny kontekst
historyczny dla tych odcinków, lecz rysunek nie przypisuje każdego wiersza
do jednej z dwóch dat ani nie pozwala odczytać `A/V/D` i LRUD.
[*Spravodaj SSS* 1/2008](https://sss.sk/wp-content/uploads/2011/10/Spravodaj-2008-1.pdf)
wspomina zamiar przedstawienia Novej Kresanicy wraz z innymi jaskiniami
w Therion; nie udostępnia pliku źródłowego ani liczbowych LRUD. [Wykaz SSS](https://sss.sk/tabulka-najhlbsich-jaskyn-na-slovensku/)
podaje 183 m głębokości, a [wykaz długości SSS](https://sss.sk/tabulka-najdlhsich-jaskyn-na-slovensku/)
820 m. [Artykuł w *Spravodaj SSS* 4/2025, s. 16–20](https://sss.sk/wp-content/uploads/2026/03/Spravodaj_4_2025.pdf)
opisuje późniejsze odkrycie i długość ponad 1 km. Te dane dotyczą różnych
stanów publikacji i eksploracji. Model M01 ma zakres wysokości węzłów od
−151,57 do +31,87 m, czyli 183,44 m. Przy tej samej starszej długości
820 m artykuł D03 z 2009 r. podaje 200 m, a inne zestawienia 183 m.
Przyczyna rozbieżności **200 m wobec 183,44 m pozostaje nierozstrzygnięta**;
nie wolno z niej wyprowadzać poprawki wektora. Zgodność 820 m z sumą
aktywnych `D = 820,03 m` nie potwierdza pojedynczych cyfr SRV.

## Porównanie wszystkich rekordów

Do odczytu M01 użyto `dump3d --legs` z Survex 1.4.22. Model zawiera dokładnie
155 `LEG` i 163 zapisy `NODE`; nie zawiera `XSECT`/LRUD ani dat przypisanych
pomiarom. Nagłówek pliku podaje `v4`, a lokalna specyfikacja
[`3dformat-old.htm`](../../../doc/Survex_manual/3dformat-old.htm) dopuszcza
rekordy `XSECT` z wymiarami L/R/U/D dopiero od wersji 5. Dlatego brak LRUD
w M01 wynika z ograniczenia formatu i **nie dowodzi**, że wartości w SRV
pochodziły z osobnego pliku. Mogły być w jego wejściu przed kompilacją albo
w innym materiale; tego nie rozstrzygnięto. Nagłówek
`DATE Wed,2009.10.21 ...` dotyczy wytworzenia pliku,
zgodnie z sekcją „File Header” w lokalnym
[`3dformat-old.htm`](../../../doc/Survex_manual/3dformat-old.htm), a nie dnia
pomiaru. W porównaniu użyto jawnej **hipotezy**: końcowy identyfikator stacji
`NK_XX.27` odpowiada `nvk27`. Końce każdego odcinka dobrano po współrzędnych
w obrębie jego segmentu. Hipoteza daje 155/155 jednoznacznych par, bez par
nadmiarowych po żadnej stronie. Zbieżność numerów i topologii nie jest
niezależnym dowodem tożsamości stacji.

Pełny [rejestr 155 wierszy](POROWNANIE_2009_3D.csv) podaje dosłowny aktywny
wiersz (`srv_record_raw`, wraz z separatorem LRUD), liczbowe `A/V/D`, numer
linii oraz SHA pliku, dosłowny wpis `LEG` z `dump3d`, odpowiadający odcinek
modelu, przeliczone z jego współrzędnych długość/azymut/inklinację i różnice.
W 23 wierszach oryginalny `LEG` ma kierunek przeciwny do aktywnego SRV:
`model_from` i `model_to` zachowują kolejność z `dump3d`, a
`model_dx_m/dy_m/dz_m` są skierowane jak `srv_from → srv_to`. Kolumna
`model_leg_reversed` ujawnia odwrócenie potrzebne do przeliczenia kierunku.
Model ma współrzędne zaokrąglone do 0,01 m, a w zamkniętej pętli zapisuje
wynik wyrównania. Stąd:

- 149/155 długości różni się najwyżej o 0,01 m; kolejna
  (`WSTCZ.SRV:61`, `nvk27a–nvk28a`) różni się o 0,01041 m, zgodnie z możliwym
  efektem zaokrąglenia węzłów.
- Pozostałe pięć różnic długości (od 0,04348 do 0,16916 m) przypada na
  `SAPOD.SRV:37–42`, pętlę `nvk111–112–113–114–115–116–111`.
  Suma surowych wektorów SRV nie zamyka się o 0,8068 m; w modelu pętla jest
  wyrównana. Szósty jej odcinek ma różnicę długości 0,00111 m, choć zmienił
  kierunek po wyrównaniu. Nie jest to podstawa do wyboru innej cyfry.
- 142 aktywne wpisy LRUD: **0/142** ma odpowiednik liczbowy w M01, ponieważ
  jego format v4 nie zapisuje tych wymiarów. Model nie potwierdza ich wartości
  ani nie wskazuje, z jakiego źródła zostały przepisane. Najstarszym
  odnalezionym zapisem tych 142 wartości są już przepisane SRV w H01 z 2014 r.
  M05 potwierdza, że w 2013 r. użytkownik miał tylko wynikowy plik 3D od
  Szunyoga; droga, którą wartości LRUD trafiły do SRV przed commitem H01,
  pozostaje nieudokumentowana. Nie wynika z tego istnienie osobnego pliku
  źródłowego — mogło chodzić o późniejsze przekazanie lub ręczne opracowanie.
  W `WSTCZ.SRV` jeden separator LRUD jest tabulatorem;
  dopuszczenie spacji zamiast przecinków wynika z rozdziału „LRUD Passage
  Dimensions” lokalnego `doc/Walls_manual.md` (Walls v2, Build 2016-11-18),
  więc nie dokonano zgadywanej poprawki.

Pokrycie bezpośrednim źródłem odczytów terenowych wynosi **0/155 odcinków i
0/142 LRUD**. P00 dokumentuje dawny plan i przekroje bez liczbowych
rekordów, więc jest osobnym wariantem bez potwierdzonego odpowiednika
wierszowego w aktywnych SRV. Pokrycie porównaniem topologii z pochodnym
modelem wynosi **155/155 odcinków**, a wszystkie 155 `LEG` modelu mają
odpowiednik w SRV.
Nie są to równoważne poziomy potwierdzenia. Rozkład `D/A/V` w aktywnych
wierszach jest zgodny ze składnią `order=AVD`; kompilacja przechodzi bez
ostrzeżeń. Dalsze rozstrzygnięcie wymaga pierwotnego Theriona, szkiców lub
dziennika i potwierdzonego mapowania stacji.

## Daty, autorstwo i decyzje

W commitcie H01 wszystkie siedem plików miało `#date 2007-01-03` z komentarzem
`data prawdopodobnie bledna`. Nie znaleziono oryginału potwierdzającego dzień
pomiaru obecnych siedmiu plików. P00 podaje daty dwóch pomiarów z 1990 r.
dla historycznego planu. P01 dokumentuje pomiary z 16 listopada i
14 grudnia 2002 r. w zakresie o numeracji zbliżonej do `ODZVAL` i `CZST`,
lecz nie przypisuje poszczególnych aktywnych wierszy do konkretnego dnia.
Data nagłówka M01 to czas kompilacji 2009-10-21, data maila to czas przekazania
2013-10-30, a późniejsze publikacje opisują eksplorację lub statystyki.
Żadna z nich nie potwierdza `2007-01-03` dla aktywnych SRV. Dlatego w
metadanych siedmiu SRV zmieniono `SURVEY_DATE` z `2007-01-03` na `nieznane`,
a w `_RAW/01/README.md`
datę pomiarów oznaczono jako nieustaloną. Poprzednia wartość jest zachowana
tutaj i w historycznym `#date`.

`#date 2007-01-03` pozostawiono bez zmiany jako **odziedziczone, niezweryfikowane
założenie obliczeniowe**, ponieważ wpływa na automatyczną deklinację w
projekcie (`.REF`, „Derive from #Date”; zob. lokalny `doc/Walls_manual.md`,
sekcje „Declinations – Derive from #Date” i „#Date Directive”). Usunięcie
daty albo podstawienie innej deklinacji bez pierwotnego pomiaru zmieniłoby
geometrię arbitralnie. Metadane `TEAM` i `INSTRUMENT` nadal są `nieznane`;
Juraj Szunyog jako nadawca modelu, Darek Bartoszewski jako wskazany posiadacz
pomiarów i autorzy publikacji nie zostali automatycznie wpisani jako mierniczy.
Mierniczych historycznego planu P00 zapisano wyżej, bez przenoszenia ich do SRV.
`SOURCE_REF` pozostał przy `_RAW/01`, bo `_RAW/02` nie jest pierwotnym
źródłem obserwacji.

## Walidacja i wznowienie

| Obszar | Stan | Dowód i granica |
| --- | --- | --- |
| Integralność M01 | Potwierdzone w podanym zakresie | SHA-256 oryginalnego załącznika i `_RAW/02/cave.3d` jest identyczny. |
| Plan P00 | Zweryfikowany jako osobny stan | Tekst i podpis obejrzane w PDF, daty i mierniczy dotyczą planu z 1990 r.; bez tabeli liczbowej i mapowania stanowisk nie weryfikuje wierszy SRV. |
| Szkic P01 | Zweryfikowany jako stan z 2002 r. | Dwa dni pomiarowe i stanowiska 70–101; brak tabeli obserwacji i rozdziału wierszy między daty. |
| Archiwa OneDrive O02 | Niesprawdzone | Podgląd ZIP nie ujawnił członków, pobranie obu przekroczyło limit czasu; nie wykluczono źródła w ich zawartości. |
| Pomiary | Częściowe | 155/155 par w modelu i niezmieniony tekst pomiarów od 2014 r.; 0/155 cyfr sprawdzonych z pierwotnym zapisem. |
| LRUD | Niesprawdzone źródłowo | 142 wpisy w SRV; model v4 nie mógł ich zachować, więc jego brak danych nie rozstrzyga pochodzenia. |
| Data i autorzy | Częściowe | Znane dni i niektórzy mierniczy historycznych zakresów P00/P01; brak dat i ekip dla poszczególnych aktywnych wierszy. `#date` nadal wpływa na model. |
| Metadane | Potwierdzone składniowo | Parsery `parse_srv_metadata` i `parse_raw_metadata`; treść źródłowa pozostaje ograniczona. |
| Kompilacja i eksporty | Potwierdzone w podanym zakresie | `uv run jktz-validate`: 12/12 etapów, bez ostrzeżeń kompilacji; Survex 1.4.22 i GDAL 3.13.1. To nie weryfikuje źródłowych cyfr. |
| Natywne Walls GUI | Niesprawdzone | Brak kontroli wyświetlenia w Walls; Survex nie dowodzi identycznego zachowania Walls. |

Kompilację bazową i końcową wykonano osobno poleceniem
`cavern -w -o <plik-w-/private/tmp> KATASTER.wpj`, z tymi samymi wejściami
pomiarowymi i ustawieniami. `dump3d --legs` dał w obu wynikach **identyczne
37 099 wierszy `LEG`/`NODE`**; porównano je bajtowo po usunięciu nagłówków
czasu wygenerowania. SHA-256 każdej listy geometrii:
`c62258c275603699ba3d3062dd40963228d3fbddfa2372d135bf02e76455eb11`.
Pełny `jktz-validate`
przeszedł po pobraniu wydania GPS `v1.0.2` z GitHub. Pierwsze uruchomienie
bez sieci zatrzymało się na pobieraniu wydania, nie na błędzie danych.
`git diff --check` również przeszedł. Plik `_RAW/02/cave.3d` wymagał
wyjątku w `.gitignore`, gdyż globalne `*.3d` ukrywało go przed walidatorem;
wyjątek dotyczy wyłącznie archiwalnych `.3d` w `Poligony/**/_RAW/`.

Ostatni ukończony zakres to odczyt dostępnej poczty, Google Drive i OneDrive,
historia Git, oględziny publikacji P00/P01, porównanie każdego odcinka z M01
i korekta niepewnej daty w metadanych. Warto odzyskać do inspekcji dwa
nieodczytane archiwa O02. Następny krok po uzyskaniu źródła: pozyskać
oryginalne pliki Therion od posiadacza danych (tropy: Juraj Szunyog,
Darek Bartoszewski) oraz, jeśli dostępny, dziennik do planu P00;
zachować ich bajty w odrębnych paczkach `_RAW`, a następnie sprawdzić kolejno
155 `A/V/D`, 142 LRUD, dowiązania, daty, mierniczych i rzeczywistą
deklinację. Do tego czasu nie zmieniać cyfr pomiarowych ani otworu na
podstawie samych długości, pętli lub publikacji.
