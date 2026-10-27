# Rozdzielenie numeracji Pośredniej w systemie Wysoka–Za Siedmiu Progami

Data opracowania: 2026-10-27. Baza: `a41faea66c3c3170a96010ef7314b375875cfced`
(master, JKTZ v1.4.10). Zmiana dotyczy siedmiu konfliktów opisanych w
[issue #9](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/issues/9).
Jest niezależna od uśrednienia POW_ORM w PR #145.

## Charakter zmiany i niepewność

**Jest to rekonstrukcja tożsamości stacji, bez pierwotnego protokołu pomiarowego.**
Komentarze SRV, opis jaskini, domknięcia surowych wektorów i porównanie z planem
silnie wspierają interpretację, że numery `W7-500`…`W7-507` użyto dla dwóch
różnych części systemu: Za Siedmiu Progami i Pośredniej. Dotychczasowy wspólny
prefiks `Wysoka7Progow` utożsamiał te punkty, wymuszając wspólne końce rozbieżnych
odczytów. Ich wspólna geometria po wyrównaniu nie była dowodem zgodności DAV.

Przyjęto odrębne nazwy `W7-P500`…`W7-P507` dla wskazanych poniżej dziewięciu
rekordów Pośredniej. `P` jest oznaczeniem wprowadzonym w tej rekonstrukcji;
nie pochodzi z odnalezionego oryginału. Pośrednia pozostaje dowiązana do Wysokiej
przez istniejącą celową Zacisku Agnieszki do `W7-2`. Nie dodano zerowych więzów
między starymi i nowymi nazwami. **Geometria zmienia się celowo**, ponieważ
rozłączono osiem wcześniej utożsamionych par punktów.

W `_RAW/01` nadal brak materiałów źródłowych. Status `niedostępny`, autorzy,
daty oraz instrument pozostają nieznane. Aktualizacja README paczki opisuje
wyłącznie niepewność opracowania; nie stanowi odzyskania protokołu. Nie zmieniono
żadnych materiałów archiwalnych RAW. Oryginalne aktywne zapisy są odtwarzalne
z podanej rewizji Git.

## Dokładne mapowanie

Wiersze odnoszą się do bazy `a41faea`, przed dodaniem wpisu PROCESSING.
Pliki znajdują się w `Poligony/D_Koscieliska/Wys_Grzbiet/Wysoka-7_Progow/`.
Wszystkie trzy literalne pola DAV w tabeli zachowano bez zmian.

| Plik:wiersz w bazie | Stacje przed | Stacje po | D [m] | A [°] | V [°] |
| --- | --- | --- | ---: | ---: | ---: |
| III.SRV:85 | W7-501 → W7-502 | W7-P501 → W7-P502 | 7.3 | 309 | -18 |
| III.SRV:86 | W7-502 → W7-503 | W7-P502 → W7-P503 | 2.03 | 28 | -45 |
| III.SRV:87 | W7-503 → W7-504 | W7-P503 → W7-P504 | 3.9 | 315 | -3 |
| III.SRV:88 | W7-504 → W7-505 | W7-P504 → W7-P505 | 3.1 | 0 | -90 |
| III.SRV:89 | W7-505 → W7-506 | W7-P505 → W7-P506 | 5.9 | 52 | 36 |
| III.SRV:90 | W7-506 → W7-507 | W7-P506 → W7-P507 | 8 | 245 | 55 |
| III.SRV:92 | W7-501 → W7-2 | W7-P501 → W7-2 | 2.5 | 126 | -14 |
| III.SRV:100 | W7-505 → W7-505/1 | W7-P505 → W7-505/1 | 4 | 228 | -13 |
| PIONY.SRV:535 | W7-500 → W7-501 | W7-P500 → W7-P501 | 7.2 | 72 | -13 |

`W7-505/1` jest unikalnym liściem występującym tylko w jednym rekordzie.
Zachowuje nazwę i zostaje połączony wyłącznie z nowym `W7-P505`; nie jest mostem
do starego `W7-505`. Nie wydłużano go do `W7-P505/1`, aby respektować limit
ośmiu znaków nazwy stacji Walls.

Pozostawiono bez zmian przypisanie Za7: III:44–45 i 48–58, boczną pętlę
PIONY:527–532 oraz gałęzie IV:205–207. Nie zmieniono liczby ani kolejności
odczytów, jednostek, prefiksów, `DECL=0`, dat, fixów lub flag otworów. Odczytów
nie uśredniano i nie usuwano. Poza nazwami skorygowano komentarze o rzekomych
powtórzeniach, UPDATE_DATE i PROCESSING obu SRV.

## Podstawy rekonstrukcji

1. **Zacisk Agnieszki i trzy otwory Pośredniej.** III:92 opisuje połączenie
   `501→2` jako Zacisk Agnieszki. III:90 i 100 opisują otwór górny i dolny,
   PIONY:535 — środkowy. Odpowiada to odrębnej, trzyotworowej Pośredniej
   połączonej przez Agnieszkę z korytarzem wejściowym Wysokiej w
   [opisie PIG, T.F-09.12](https://jaskiniepolski.pgi.gov.pl/Details/Information/1665).
2. **Pętla należy do pierwszego szeregu.** Surowe przesunięcie
   `501→512→…→516→505` z PIONY:527–532 różni się od III:48–51 (`501→…→505`)
   o ENU=(0,056968; 0,059886; 0,011739) m, czyli **0,083483 m w 3D**.
   Porównanie tej samej pętli z III:85–88 daje **24,090521 m**.
   Dlatego nie przeniesiono całego sąsiedniego bloku PIONY do Pośredniej.
3. **Wysokości Pośredniej.** Bez dopasowania do planu, poprzez zapisane
   `0→1→2`, odwróconą celową Agnieszki i kotwicę W7-0=1486,69 m, otrzymuje się
   otwory: dolny 505/1=1477,26 m, środkowy P500=1486,77 m, górny P507=1488,18 m.
   Różnica górny–dolny wynosi **10,920954 m**; opis podaje 11 m.
   Wyliczenie różnicy to `4 sin(13°) + 5.9 sin(36°) + 8 sin(55°)`.
   Pionowy odcinek 504→505 = 3,1 m jest osobną zgodnością z opisowym progiem 3 m.
   Wysokości opisowe nie były więzami kompilacji ani nowymi fixami.
4. **Górne partie Za7.** Opis wymienia górną salę, około 10 m poziomego
   odgałęzienia ENE i powrót górnego ciągu do Korytarza Połączeniowego.
   IV:518→519 ma 10,5 m/66°/0°, a dojście IV:514→518 ma 8,2 m/110°/76°.
   Jest to charakterystyczna zgodność pomocnicza z pozostawioną pętlą.

Powyższe przesunięcia surowe liczono z DAV przez
`E=D cosV sinA`, `N=D cosV cosA`, `U=D sinV`, przy istniejącym DECL=0.
Zgodność geometryczna wspiera podział, ale sama nie potwierdza terenowej
tożsamości poszczególnych stacji.

## Porównanie z planem i ograniczenia

Kopię testową porównano w QGIS 4.0.1 z planem PIG, grafika 2958
(Napierała 1994, wektoryzacja Grodzicka 2009), raster 001665 Georeferencera v0.7.2,
SHA-256 `8b3e209b5a17860901dbe0576a1af52dc30c85eb5e7c8c707a37934de1be93ef`.
Sieć Survex przeliczono z EPSG:32634 do EPSG:2180 bez ręcznego przesunięcia,
obrotu lub zmiany skali; obie strony korzystają z kotwicy W7-0/KSW-0189.
Porównano tylko rzut, bez dolnego przekroju W–E. Rozdzielone szeregi układają się
w odpowiadających im odrębnych partiach planu. Wariant wizualny pochodził z bazy
z uśrednionym POW_ORM; zmiana ta dotyczy innego, rozłącznego systemu jaskiń.
Osobną bazę master sprawdzono ponownie przy wdrożeniu opisanym poniżej.

Orientacja rastra ma status `historical_tfw`, `unknown/unverified`; dokładność
kotwicy i datum pionowe nie są tu weryfikowane. Nie wykonywano nowej kalibracji
planu ani transformacji wysokości. Jest to dowód pomocniczy, nie terenowe
potwierdzenie numeracji.

Nie rozstrzygnięto wszystkich rozbieżności:

- Protokół M. Napierały z 1989 r., wskazany w literaturze jako 127-stronicowy rękopis
  KKS Katowice, nie został odzyskany. Korzystanie z niego opisuje J. Szczygieł
  w [materiałach 45. Sympozjum Speleologicznego, s. 96](https://speleo.ptpk.org/08wydawnictwa/sympozjum_45.pdf#page=96).
- Opis Pośredniej wymienia łączące się odnogi; dziewięć przypisanych rekordów
  nie odtwarza tej pętli. Suma długości z dowiązaniem Agnieszki to 43,93 m,
  wobec opisowych 46 m. Kierunki zakrętów odpowiadają opisowi tylko przybliżenie.
- Pozostała pętla Za7 przez 201 i 12/28 ma około **8,325 m** niewyrównanego błędu
  domknięcia. Rekonstrukcja nie potwierdza poprawności całej sieci ani jej
  bezwzględnych wysokości. Różnica 500−200 z surowych DAV to12,615 m,
  ale wysokości obu otworów pełnego modelu nadal odbiegają od historycznych.
- Opis PIG sam ma omyłki: w części dojściowej środkowy i górny otwór Pośredniej
  oznaczono 07; opis wnętrza rozróżnia 06/07. We wstępie powtórzono dla Pośredniej
  numer inwentarzowy Za7, a właściwy rozdział podaje T.F-09.14.
- Nieznane daty i instrument oraz zastępcze DECL=0 pozostają nierozstrzygnięte.
  Nie wykorzystano zgodności z planem do zmiany odczytów, kalibracji czy fixów.

Opis PIG odczytano także z archiwalnego rekordu
`doc/jaskinie_polski_pig_dump.jsonl`; indeksowana strona zwróciła zgodny fragment.
Własne kopie testowe, QGIS i szczegółowe logi są lokalnymi dowodami w
`.verification/`, ignorowanymi przez Git. Niniejszy dokument utrwala mapowanie,
metodę i ograniczenia potrzebne do przeglądu zmiany w świeżym klonie.

## Walidacja końcowych danych

Świeże porównanie wykonano na osobnej bazie master `a41faea`, z jej oryginalnymi
66 rekordami POW_ORM i tym samym wersjonowanym snapshotem otworów. Wyników
globalnych nie należy mieszać z wcześniejszym wariantem zawierającym PR #145.

| Kontrola | Baza | Po rozdzieleniu |
| --- | ---: | ---: |
| Źródłowe odczyty Wysokiej | 1405 | 1405 |
| Zmienione rekordy / nowe nazwy | — | 9 / 8 |
| Powtórzone pary nazw źródłowych Wysokiej | 7 | 0 |
| Survex: stacje / odcinki / pętle projektu | 18551 / 18685 / 210 | 18559 / 18685 / 202 |
| Survex: długość przed wyrównaniem | 70048,90 m | 70048,90 m |
| Survex: długość po wyrównaniu | 69940,69 m | 69972,62 m |
| Walls: ostrzeżenia duplikatów całego projektu | 62 | 55, wszystkie POW_ORM |
| Walls: ostrzeżenia Wysokiej w pełnym audycie | 7 | 0 |
| Walls: pętle H/V projektu, Geometry Review | 260/260 | 252/252 |
| survex-duplicates: pary całego projektu | 62 | 55 |
| survex-duplicates: pary Wysokiej | 13 | 6 |

- **Survex 1.4.24:** obie kompilacje z `--warnings-are-errors` zakończone kodem 0;
  pełne `uv run jktz-validate` PASS, łącznie z aktualnością snapshotu GPS,
  kontrolą danych i eksportami. Liczba i kolejność wszystkich 1405 odczytów
  Wysokiej, literalne pola DAV i pozostałe pola pomiarów zachowane. Dyrektywy
  ciała obu plików i pozostałych pięciu SRV identyczne. Nie dodano equates.
  Pierwszy lokalny przebieg wypisał pojedynczy błąd zapisu DBF mimo końcowego
  PASS. Identyczne dane w świeżym ponownym przebiegu przeszły wszystkie12
  kroków bez tego diagnostyku ani innych komunikatów ERROR; przyczyny
  pierwszego błędu nie ustalono. Zachowano oba logi, a wynik pełnych eksportów
  oparto na czystym powtórzeniu (`validation-retry.log`).
- **Walls v2.3.0-beta.1, build 2025-09-13:** zwykła pełna kompilacja PASS.
  Pełny ścisły audyt z `Look for Duplicates` ma wynik **FAIL z 55 istniejącymi
  ostrzeżeniami POW_ORM**, bez ostrzeżeń Wysokiej. Ścisły izolowany zakres
  siedmiu końcowych SRV Wysokiej i istniejącego fixu W7-0: **PASS, zero
  ostrzeżeń**. Potwierdzono nowe NT, ukończenie kompilacji i niezmienność wejść.
  Pierwsza izolowana próba zatrzymała się na spóźnionym oknie Tip of the Day;
  identyczne dane w świeżej ponownej próbie przeszły kontrolę. Nie zmieniano
  sterownika ani danych, aby uzyskać PASS.
- **survex-duplicates v1.0.0**, commit `c1e59ebd15ff41aef46f453d57100e58772c8c71`:
  próg 5% krótszego odcinka, `--exclude-splays --include-duplicates`.
  Po pełnych nazwach końców usunięto dokładnie siedem badanych par; nie dodano
  żadnych nowych, a pozostałe 55 par zachowano. Sześć innych par Wysokiej
  wymaga osobnej analizy. Brak par nie potwierdza poprawności rekonstrukcji.

CSV Survex zapisuje współrzędne co 0,01 m. Spośród 12117 wspólnych nazwanych
stacji zmieniło się 1361, wszystkie w `Wysoka7Progow`; maksimum 3D wynosi
**35,37 m dla W7-507**. Nie usunięto żadnej pierwotnej nazwy; dodano osiem
`W7-P500`…`W7-P507`. Stacje pozostałych jaskiń pozostają identyczne na tej
rozdzielczości. Jest to zamierzona zmiana tożsamości i wyrównania, a nie
deklaracja równoważności geometrii lub poprawy jej dokładności o daną wartość.

Dowody lokalne: `.verification/2026-10-27-posrednia-renumbered/` —
`baseline-state.json`, `selected-source-map.json`, `comparison.json`, `verify.py`,
`baseline/`, `head/`, `validation.log`, `validation-retry.log`, `walls-summary.json` oraz raporty
natywnego Walls. Kopie projektów Walls spakowano do ZIP i zweryfikowano hashe,
zachowując jawne result.json i driver.log. Ten ignorowany katalog nie jest
częścią PR ani wydań; tabela powyżej utrwala sprawdzone wyniki w repozytorium.
