# Changelog

Wszystkie istotne zmiany w projekcie "Jaskiniowy Kataster Tatr" sa udokumentowane w tym pliku.

Format oparty jest o [Keep a Changelog](https://keepachangelog.com/), a wersjonowanie stosuje [Semantic Versioning](https://semver.org/).

## [v1.2.2] - 2026-03-18

Poprawa niepołączonych sekcji jaskini Miętusia Wyżnia

### Dodane
- Claude skills:
  - konwersja .svx -> .SRV
  - kompilacja cavern

### Zmienione
- Podłączenie pominiętych sekcji w jaskini Miętusia Wyżnia

## [v1.2.1] - 2026-03-18

Poprawki i rozbudowa modelu 3D online (CaveView na GitHub Pages).

### Dodane
- Teren 3D Cesium World Terrain w viewerze CaveView (token Cesium ION)
- Polskie tlumaczenie interfejsu CaveView (lang-pl.json)
- Rozbudowany popup informacyjny: opis techniczny, uklad wspolrzednych, koordynatorzy
- Popup widoczny domyslnie po zaladowaniu strony

### Zmienione
- Viewer: displayCRS ustawiony na ORIGINAL (zachowanie oryginalnych wspolrzednych UTM)
- Viewer: domyslne pochylenie kamery -35°, teren i datum shift wlaczone
- Patch CaveView 2.9.0: case-insensitive regex CRS (EPSG uppercase z Survex), fix webMeshWorker (Cesium terrain crash)
- Token Cesium ION przechowywany w GitHub Secrets zamiast hardcoded

## [v1.2.0] - 2026-03-13

### Dodane
- Flaga `#flag STATION /ENTRANCE` dla wszystkich otworow jaskiniowych (79 stacji) + 9 dodatkowych otworow
- Jaskinia Czarna (T.E-08.01) — eksperymentalne, wymaga dalszej pracy:
    - Konwersja na format dwuplikowy (_M.SRV + _S.SRV) z _RAW
    - Ciag glowny (dane Borowca) i pomiary Kujata (partie koncowe)
- Walidacja CI: wykrywanie niepodlaczonych stacji pomiarowych, cache Survex (actions/cache)
- README: sekcja o pokrewnym projekcie RadostW/jaskinie

### Zmienione
- Ptasia Studnia (T.E-11): przeniesienie z Ratusz_Mulowy/ do wlasnego katalogu Ptasia_Studnia/, pelne nazwy otworow wg PIG, wykomentowanie niepodlaczonego ciagu 10A
- Prefixy stacji: pelne nazwy jaskin CamelCase zamiast skrotow
- Zamiana spacji na podkreslniki w nazwach plikow SRV (Mala w Mulowej, Syst. Pawlikowskiego, Ptasia Studnia)
- Naprawa literowek w nazwach stacji (I.SRV, KROKODYL.SRV, SLEPE.SRV)
- Walidacja CI: obsluga roznych wersji komunikatu cavern, shell bash (fix Windows)

## [v1.1.6] - 2026-03-11

### Dodane
- Jaskinia Miętusia Wyżnia (T.D-10.01) — nowa jaskinia w Dolinie Miętusiej
    - Zrodlo: projekt Survex Speleoklub Warszawski (https://github.com/RadostW/jaskinie)
    - Pomiary z 2024-02 instrumentem DistoX2
    - 17 plików pomiarowych SRV (16 ciagow: otwor, suche dno, mylna rura i inne)
    - Pliki źródłowe w _RAW/ (18 plikow .svx + GPS)
    - Współrzędne otworu: E19.894900 N49.245399, ok. 1377 m n.p.m. (średnia z 5 GPS)

## [v1.1.5] - 2026-03-11

### Dodane
- Dane wysokosciowe Viewfinder Panoramas 1 arc-second (N49E019_VF1.hgt) do wizualizacji terenu w Survex

### Zmienione
- Licencja projektu CC BY-SA 2.0 → 4.0 — zaktualizowano LICENCE, INFO.txt, README i wszystkie pliki SRV
- Poprawki danych SRV: przecinki dziesietne → kropki (Bandzioch Kominiarski, Wysoka-7 Progow, System Wielkiej Snieznej, Mala w Mulowej, Ratusz Mulowy)
- Usuniecie artefaktow kodowania (non-ASCII → ASCII) w komentarzach plikow SRV (Bandzioch, Mylna, Wysoka-7 Progow, Mala w Mulowej, Ratusz Mulowy)

## [v1.1.4] - 2026-03-07

### Dodane
- Dane surowe (xlsx) Jakuba Nowaka dla 18 jaskin — katalogi _RAW/ z README
- .gitignore: pliki wyjsciowe Survex (*.3d, *.err)

### Zmienione
- 18 jaskin J. Nowaka: konwersja z formatu jednoplikowego na dwuplikowy (_M.SRV + _S.SRV) z pelnym blokiem metadanych
  - D. Chocholowska: Dmuchawa, Kamienne Mleko, Zbojecka Dziura
  - D. Koscieliska / Wawoz Krakowski: Gawra, Lustrzany Korytarz, Rura przy Oknie, J. nad Beczka, J. nad Percia
  - D. Koscieliska / Zar: Ciepla, Pod Zamkiem, Poszukiwaczy Skarbow, Zbojnicka Piwnica, Ziobrowa, w Zbojnickiej Turni
  - D. Tomanowa: Dziura w Stole, Szczelina nad Tomanowa I/II, J. Zawaliskowa Tomanowa
- Korekta wspolrzednych i wysokosci wg PIG (m.in. Zbojecka Dziura 1230→1143 m n.p.m.)
- Uzupelnienie brakujacych odcinkow pomiarowych (Kamienne Mleko, J. Zawaliskowa Tomanowa)
- Usuniecie artefaktow kodowania (non-ASCII → ASCII) w plikach z rejonu Zaru

## [v1.1.3] - 2026-03-06

### Zmienione
- Zoska-Zagonna Studnia: konwersja z formatu jednoplikowego (1.SRV) na nowy format dwuplikowy (ZOSKA_M.SRV + ZOSKA_S.SRV) z pelnym blokiem metadanych, datami pomiarow (poprawne obliczanie deklinacji magnetycznej) i segmentami

## [v1.1.2] - 2026-03-05

Wprowadzono wsparcie dla kompilacji Survex (cavern) na Linux i Windows.

### Dodane
- CI: walidacja cavern (Survex 1.4.20) na Linux i Windows — blokuje merge przy bledach kompilacji

### Zmienione
- Normalizacja nazw plikow SRV (24 pliki) — UPPERCASE basename + .SRV dla kompatybilnosci z Linux (case-sensitive FS)
- Usuniecie niepoprawnej dyrektywy `#<L,R,U,D>` z SWIST.SRV i KOPRSTUD.SRV
- Powierzchnia/Teren: STATUS 9 → 10 (detach, pomijane przez cavern)

## [v1.1.1] - 2026-03-02

### Dodane
- Zoska-Zagonna Studnia — archiwalne pliki źródłowe _RAW (szkice CDR, pomiary XLS)
- Harda — archiwalne pliki źródłowe _RAW (Harda_old.zip)
- Link do CHANGELOG.md w README

### Zmienione
- INFO.txt — automatyczna wersja z taga (placeholder __VERSION__ podmieniany przez GitHub Actions)
- Aktualizacja bazy jaskin PIG (jaskinie_polski_pig_dump.jsonl)

## [v1.1.0] - 2026-02-27

### Dodane
- Jaskinia Mroźna
- Claude skills:
  - add-cave - dodawanie jaskini
  - average-shots - uśrednianie wielokrotnych strzałów

## [v1.0.0] - 2026-02-26

Przejscie na wersjonowanie semantyczne (semver). Utworzenie CHANGELOG.md, automatyzacja wydan przez GitHub Actions.

### Dodane
- Zawalony Schron, Jaskinia Koszowa, Szczelina nad Lejem, Wyznia Koszowa Dziura (4 nowe jaskinie, Dolina Panszczyca / Mala Koszysta)
- Jaskinia Dziura - przeformatowanie do nowego formatu (oddzielne pliki meta i pomiary), nowa sekcja Dolina ku Dziurze w projekcie
- Pliki meta (_M.SRV) dla jaskin Systemu Jaskin Pawlikowskiego (Mylna, Oblazkowa, Raptawicka), uzupelnienie dat i metadanych pomiarow SJP
- Pliki zrodlowe _RAW dla jaskin: Kalacka, Goryczkowa, Ptasia Studnia, Marmurowa, Szczelina Mietusia, Lodowa Mietusia, Spiacych Rycerzy, Harda, Zwolinskiego, System Jaskin Pawlikowskiego, Obcasna Vyvieracka, Zimna, pod Progiem, Czerwona Studzienka, Dziurka w Trawce, w Wielkiej Turni, Mnichowa Studnia Wyznia, Studnia na Szlaku, Szara Studnia
- Plik LICENCE (Creative Commons BY-SA 2.0)
- CHANGELOG.md (ten plik) z pelna historia wersji
- GitHub Actions workflow do automatycznego tworzenia wydan (ZIP + release notes)
- CLAUDE.md z instrukcjami projektu dla Claude Code
- Dokumentacja referencyjna w doc/ (manual Walls w MD/PDF, baza jaskin PIG w JSONL)

### Zmienione
- Ujednolicono pliki WPJ/SRV do ASCII (usunieto polskie znaki)
- Skrocono sciezki katalogow (spacje -> podkreslniki, krotsze nazwy)
- Oczyszczono dyrektywy .PATH w KATASTER.wpj (usunieto zbedne sciezki powielajace rodzica)
- Ustandaryzowano dokumentacje _RAW (README.md zamiast TXT)
- Zaktualizowano SJP powierzchnia
- Przejscie na semver, uproszczenie INFO.txt, aktualizacja README.md (badge wydania, link do releases)
- .gitignore: dodano katalog logs/

## [v0.28] - 2024-05-08

- Przebudowa README.md (nowy opis projektu, ostrzezenie o dlugich sciezkach Windows)
- Dodano zrzuty ekranow: walls_2d_screen.png, walls_3d_screen.png, sketchfab_3d.png

## [v0.27] - 2020-06-20

- Wykomentowano duplikaty pomiarow w wielu jaskiniach (Wielka Sniezna, Wielka Litworowa, Wysoka Za 7 Progami, Mala w Mulowej, Przy Przechodzie, Bandzioch Kominiarski, Zaspalkowa Szczelina, Zwolinskiego)
- Dodano brakujace prefixy, note i flag dla Oblazkowej i Raptawickiej
- Poprawiono polaczenie jaskin w Systemie Jaskin Pawlikowskiego

## [v0.26] - 2020-06-08

- Dodano jaskinie Raptawicka oraz Oblazkowa, utworzono System Jaskin Pawlikowskiego (Mylna + Oblazkowa + Raptawicka)
- Usunieto polskie znaki z nazw katalogow w calym projekcie (rename ~150 plikow)
- Przebudowano drzewko KATASTER.wpj (nowa struktura regionow, poprawiono statusy podkatalogow)

## [v0.25] - 2015-07-26

- Dodano jaskinie Smocza Jama
- Rozpoczeto prace nad jaskinia Dziura (plik KUDZIURA.SRV)
- Poprawki plikow Obcasna Vyvieracka

## [v0.24] - 2015-05-30

- Dodano jaskinie Obcasna Vyvieracka, wprowadzono nowe formatowanie plikow (Obcasna Vyvieracka, Kalacka)
- Dodano note i flag dla Nova Kresanica

## [v0.23] - 2015-01-17

- Dodano ciagi w Przemkowych Partiach
- Dodano wsp. otworu jaskini Nova Kresanica

## [v0.22] - 2014-12-30

- Dodano jaskinie Nova Kresanica (brak wsp. otworu)
- Dodano fragment jaskini Czarnej z ciagiem po pow. do otworu Zimnej

## [v0.21] - 2014-10-21

- Aktualizacja dla jaskini Hardej. Nowe pomiary (Balkon, Kwadrat, Stary)

## [v0.20] - 2014-06-26

- Poprawka wsp. otworow Malej w Mulowej, Lodowej Mietusiej, Marmurowej i Studni w Kazalinicy
- Odczytal K. D. z http://mapy.geoportal.gov.pl/imap

## [v0.19] - 2014-06-16

- Dodano Jaskinie Marmurowa
- Poprawiono duplikaty pomiarow w Litworowej i Jasnym Awenie
- Dodano note i flag dla Studni przy Przechodzie
- Drobne poprawki kosmetyczne

## [v0.18] - 2014-06-09

- Dodano nowe pomiary Jaskini Lodowa Malolacka
- Aktualizacja wspolrzednych otworu Jaskini Sniezna Studnia, Jaskinia Wielka Sniezna, Lodowa Malolacka

## [v0.17] - 2014-05-21

- Dodano Meander w Malolackim Siodle, Jaskinia Mala w Mulowej oraz Jaskinia Lejbusiowa
- Dodano Ptasia Studnia (uwaga: wersja robocza)
- Drobne aktualizacje wspolrzednych i wysokosci

## [v0.16] - 2014-05-11

- Dodano Jaskinia pod Progiem, Michowa Studnia Wyznia, Studnia na Szlaku

## [v0.15] - 2014-04-21

- Dodano Jaskinie Biala, Szara Studnia, Jaskinia w Wielkiej Turni, Czerwona Studzienka, Dziurka w Trawce
- Drobne aktualizacje wspolrzednych i wysokosci

## [v0.14] - 2014-04-04

- Z http://geoportal.pgi.gov.pl dodano wspolrzedne dla jaskin: Dmuchawa, Jaskinia nad Beczka, Jaskinia nad Percia, Lustrzany Korytarz, Rura przy Oknie, Jaskinia Ciepla, Jaskinia w Zbojnickiej Turni, Zbojnicka Piwnica, Dziura w Stole, Jaskinia Zawaliskowa Tomanowa, Szczelina nad Tomanowa I, Szczelina nad Tomanowa II
- Poprawka wspolrzednych Koprowej Studni, korekta dat w Studni w Kazalnicy

## [v0.13] - 2013-12-08

- Dodano jaskinie: Spiacych Rycerzy (fragment), Jaskinia Lodowa Mietusia, Szczelina Mietusia, Zbojecka Dziura, Szczelina nad Tomanowa II (brak wsp GPS), Szczelina nad Tomanowa I (brak wsp GPS), Dziura w Stole (brak wsp GPS), Jaskinia Zawaliskowa Tomanowa (brak wsp GPS), Jaskinia Poszukiwaczy Skarbow (fragment), Jaskinia Pod Zamkiem (fragment), Jaskinia w Zbojnickiej Turni (brak wsp GPS), Zbojnicka Piwnica (brak wsp GPS), Jaskinia Ziobrowa i Jaskinia pod Niznia Zbojnicka Turnia, Jaskinia Ciepla (brak wsp GPS), Gawra, Rura przy Oknie (brak wsp GPS), Lustrzany Korytarz (brak wsp GPS), Jaskinia nad Percia (brak wsp GPS), Jaskinia nad Beczka (brak wsp GPS)
- Dodano ciag powierzchniowy od Koprowej Studni do Jaskini Swistaczej
- Nowe regiony w WPJ: Wawoz Krakow, Dolina Tomanowa, Zar
- Poprawki w Koprowej Studni i Swistaczej

## [v0.12] - 2013-12-02

- Dodano jaskinie Harda (ciag glowny), jaskinie Kamienne Mleko, jaskinie Dmuchawa (brak wsp GPS)
- Zrobiono porzadek w nazwiskach

## [v0.11] - 2013-11-27

- Coordinates UTM/UPS grid-relative; Declinations Derive from #DATE

## [v0.10] - 2013-11-24

- Dodano system Zoska - Zagonna Studnia

## [v0.09] - 2013-11-20

- Dodano jaskinie Zwolinskiego, dodano jaskinie Swistacza (brak wsp GPS), nowe pomiary Koprowej Studni

## [v0.08] - 2013-11-13

- Dodano jaskinie Kalacka, dodano jaskinie Studnia w Kazalnicy, poprawka w Koziej

## [v0.07] - 2013-11-04

- Dodano jaskinie Goryczkowa

## [v0.06] - 2013-10-18

- Przejecie koordynacji - Dariusz Lubomski
- Dodano ciag pomiarowy w Snieznej - 20130713 - autorzy pomiarow Karol Makowski, Marcin Slowik

## [v0.05] - 2012-05-14

- Dodano jaskinie Mylna

## [v0.04] - 2012-05-04

- Dodano model terenu oparty o poziomice

## [v0.03] - 2012-04-26

- Zmieniono uklad drzewka plikow; dodano powierzchnie calosci

## [v0.02] - 2012-04-25

- Ujednolicono sposob wpisania danych, usunieto polskie znaki z plikow

## [v0.01] - 2012-04-24

- Zmieniono drzewko projektu, dodano Wysoka, Bandziocha

## [v0.00] - 2010

- Projekt wstepny, brak koordynatora, dane chaotyczne
