# Zoska-Zagonna Studnia - paczka zrodlowa 01

- **Status materiału:** dostępny
- **Pochodzenie danych:** Paweł Ramatowski, przekaz 19.11.2013 wcześniejszego materiału D. Fuji (forward z 24.01.2012); rola przekazującego, nie autorstwo wszystkich pomiarów
- **Autorzy pomiarów:** D. Fuja, B. Zwijacz-Kozica, K. Dudziński, P. Orawiec, W. Goźdź, A. Lezlii, Z. Tabaczyński, J. Wilk (zespoły poszczególnych kampanii opisane poniżej)
- **Daty pomiarów:** 1996 (bez przypisania wszystkich rekordów do dnia), 1996-08-15 (Zagonna wg PIG), 2004-10-27/2004-10-29, 2004-11-11, 2005-03-24
- **Data pozyskania:** 2013-11-19
- **Dodał do _RAW:** Dariusz Lubomski
- **Licencja źródłowa:** nieznane
- **Kompletność:** Komplet czterech zachowanych załączników przekazu: XLS i trzy CDR; brak pierwotnych notatek terenowych. XLS zawiera 106 głównych rekordów (w tym 3 powierzchniowe i 1 szacunek) oraz pomocniczy wiersz obliczeniowy 175.

## Zawartość

- `Zośka szkic.cdr`
- `pomiary zośki aktualne na 2004-11-11.xls`
- `zośka plan.cdr`
- `zośka przekrój.cdr`

## Kampanie, daty i przyrząd

- XLS `pomiary!A10` opisuje pierwszy blok jako „pomiary z 1996” D. Fuji i B. Zwijacza-Kozicy. Nie przypisuje wszystkich 62 rekordów do 28.07.1996. PIG `T.E-12.58` dokumentuje kilka akcji tego roku; pomiary Zagonnej 15.08.1996 wykonali K. Dudziński, D. Fuja, P. Orawiec i B. Zwijacz-Kozica.
- XLS `B114/D114`: 27–29.10.2004, W. Goźdź, A. Lezlii, Z. Tabaczyński.
- XLS `B135/D135`: 11.11.2004, D. Fuja i Janusz Wilk; `B145/D145`: 24.03.2005, D. Fuja.

Daty operacyjne `#date` w SRV zachowano; daty 28.07.1996 dla całego pierwszego bloku i 27.10.2004 dla zakresu 27–29.10 są dotychczasowymi reprezentantami dat dla deklinacji, nie dowodem przypisania każdego odcinka do konkretnego dnia. Nowe metadane zachowują dokładność źródła.

Nie ustalono jednego przyrządu dla wszystkich kampanii. Starszy indeks `_RAW/README.md` wskazywał Topofil, natomiast PIG `T.E-12.58` opisuje Topo-Vulcan w dokumentacji wcześniejszych pomiarów. XLS nie rozstrzyga przyrządu każdej kampanii. Dlatego `INSTRUMENT` ma wartość `nieznane`; obu opisów nie ujednolicono przez zgadywanie.

## Wyliczone dowiązanie podstawy kominów — #150

W arkuszu `pomiary` wiersz `B147=31G` ma `J147:L147=(-49.50,-15.14,-149.28)`, a `B154=31G-32G` ma `J154:L154=(-54.79,-13.42,-152.24)`. Różnica od 31G do podstawy kominów wynosi `dy=-5.29 m, dx=+1.72 m, dh=-2.96 m`. Komentarz J154 autora pola „Fuja” opisuje przesunięcie dna sali około 6 m na zachód i 3 m w dół od punktu pod liną. Pomiary gałęzi 46–50 jawnie zaczynają się w A155 od `31G-32G`.

J/K/L to lokalne y/x/h obliczane w XLS bezpośrednio z azymutów (`dy=poziom*sin(A)`, `dx=poziom*cos(A)`). Odtworzono pochodny wektor jako DAV w dotychczasowej magnetycznej interpretacji SRV i kontekście sekcji 2005; sam XLS nie definiuje niezależnie datum ani true/grid north. Nie potraktowano tego wyliczenia jako nowego odczytu terenowego ani osobno datowanego pomiaru.

Różnica nazwanych pozycji daje DAV 6.3011 m/288.0115°/−28.0186°. Przy dokładności zapisu XYZ 0.01 m zaokrąglono do 6.30 m/288.0°/−28.0° (różnica 2.6 mm). W SRV zachowano dotychczasowy kierunek `31G-32G -> 31G`, czyli 6.30 m/108.0°/+28.0°. Zastępuje to wcześniejszy zerowy wektor; pięć właściwych odczytów komina pozostaje bez zmian.

Wiersze 174/175 zawierają pomocnicze 0/1 i zgodne obliczenia, ale nie mają formuł łączących je z 147/154. Nie uznano tych pomocniczych nazw za equate. Podstawą są dwa jawnie nazwane położenia i komentarz J154.

Źródłowa długość nie sumuje pomocniczego wiersza 175. Tag `#S L` wyłącza wyliczony odcinek z długości w Survex. W Walls L jest segmentem umownym do pominięcia/odłączenia przy podsumowaniu; sam tag nie gwarantuje niezmienionej surowej długości sieci.

## Zachowana historia źródeł

Trzy powierzchniowe rekordy XLS A92:E94 zostały usunięte z aktywnego SRV przy porządkowaniu fixów (`6561bab`, główna historia `5021fd9`); oryginał XLS je zachowuje. Szacunek 3 m z A141:E141 jest nadal jawnie opisany w SRV jako „bez pomiaru na oko”. Nazwa XLS „aktualne na 2004-11-11” jest oryginalna; plik zawiera także sekcję 24.03.2005.

Wszystkie cztery pliki są bajtowo identyczne z oryginalnymi załącznikami przekazu 19.11.2013. Materiały CDR odczytywane przez importer mogą mieć brakujące obiekty i rozjechany tekst; nie są niezależnym pomiarem terenowym.

## Suma długości w oryginalnym XLS

Zapisany wynik `pomiary!L4` wynosi 634.26 m. Formuła `C133=SUM(C118:C131)` pomija odcinek `19G–20G` z wiersza 117 (2.30 m); wynik C133 jest składnikiem sumy przez M133. Suma 103 zachowanych rekordów podziemnych, w tym jawnego szacunku 3 m, wynosi 636.56 m. Różnica 2.30 m wynika z zakresu formuły, a nie z brakującego odcinka SRV. Nie obejmuje trzech odcinków powierzchniowych ani obliczeniowego dowiązania podstawy kominów. Oryginalny XLS i wszystkie odczyty pozostawiono bez zmian.
