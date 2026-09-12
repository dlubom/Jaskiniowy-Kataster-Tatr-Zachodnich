# Jaskinia Czarna — audyt skanów i stan digitalizacji

Data: 2026-09-12. Stan wejściowy: `feff15dc568695cff5322e44232ed59c8d214eed`.
Audyt lokalnego checkoutu; lokalny `origin/master` był o jeden commit dalej,
ale jego różnica nie obejmowała materiałów Czarnej. Nie aktualizowano checkoutu.

## Wynik

**Brakującym odczytem jest dziennik ciągu głównego 0–76 oraz odgałęzienie
6–a–b („Partie Tęhmy”) w `_RAW/02`. Łącznie 78 odcinków.**
To inny zestaw liczb i stanowisk niż współrzędne Borowca oraz pomiary partii
końcowych Kujata obecne już w SRV. Trzy zdjęcia dokumentują cztery strony
zeszytu: dwie fotografie pokazują tę samą rozkładówkę.

Przygotowano [CZ_GL_R.SRV](CZ_GL_R.SRV), zawierający roboczy odczyt całych
78 odcinków. Cztery wiersze mają nierozstrzygnięte cyfry lub znak i jawne
warianty w komentarzach. Plik nie został dodany do `KATASTER.wpj`.
Istniejące pomiary, współrzędne otworów i materiały `_RAW` pozostały bez zmian.

**Nie potwierdzono autora ani daty dziennika ciągu głównego.** Dopisek
`Kujat` w nazwie jednej fotografii nie stanowi takiego potwierdzenia.
List Kujata z 3 marca 1981 r. opisuje partie końcowe i boczny ciąg od punktu
65 Borowca, a nie dziennik 0–76. Na obecnym etapie określenia „powtórny”
i „nowszy niż Borowiec” pozostają hipotezami wymagającymi ustalenia pochodzenia.

## Co pokazują poszczególne skany `_RAW/02`

W tabeli skróty nazw zaczynają się od czasu fotografii; pełne nazwy znajdują
się w [indeksie paczki](_RAW/02/README.md).

| Plik | Faktyczna zawartość obrazu | Stan przed audytem / dalsze działanie |
| --- | --- | --- |
| `20220325_123052 ciąg gł Czarna 1_Kujat.jpg` | Prawa strona: 0→1 do 18→19. Lewa: 60→61 do 75→76 oraz 6→a→b. Kolumny: stanowisko, cel, azymut, kąt pionowy, odległość rzeczywista, odległość pozioma, Δh; uwagi terenowe. | Brak odczytu tych 37 odcinków w dotychczasowych SRV i arkuszach Czarnej. Teraz roboczo w `CZ_GL_R.SRV`. |
| `20220325_123533 ciąg gł Czarna 1a.jpg` | Druga fotografia dokładnie tych samych stron i wierszy co `123052`. | Materiał pomocniczy do odczytu, nie dodatkowy ciąg. |
| `20220325_123630 ciąg gł Czarna2.jpg` | Lewa strona: 19→20 do 39→40; prawa: 40→41 do 59→60. | Brak odczytu tych 41 odcinków. Teraz roboczo w `CZ_GL_R.SRV`. |
| `20220325_124334 Czarna_ pomiary Kujata1.jpg` | Przepisana tabela A/V/D partii końcowych; początek ciągu 0–26 i odgałęzienia 1200–1213. | Zdigitalizowana w `Czarna pomiary Kujata.xlsx`, `czarna-kujat.srv` oraz aktywnym `CZ_K_S.SRV`. |
| `20220325_124400 Czarna_ pomiary Kujata2.jpg` | Dalsza część tej tabeli: odgałęzienie 2500–2507 i 6500–6509. | Zdigitalizowana w tych samych plikach; są błędy opisane niżej. |
| `20220325_124850.jpg` | Oryginalny odręczny zapis tych samych partii Kujata. W ciągu 6500–6509 widać pierwotne grady i dopisane przeliczenia na stopnie. | Źródło kontrolne dla już odczytanych pomiarów, nie kolejny brakujący ciąg. Ważniejsze od przepisanej tabeli przy rozstrzyganiu różnic. |
| `20220325_124826 list Kujata.jpg` | List podpisany R. Kujat, Kraków 3.03.81. Opisuje dwa zespoły ciągów, jednostki i nawiązania do Borowca. | Dokument pochodzenia i interpretacji, bez dodatkowej tabeli pomiarów. Data listu nie jest datą wykonania pomiaru. |
| `20220325_124904.jpg` | Krótki opis: Otwór Północny → Sala Bernarda → korytarz główny ciągu dalszego, nawiązanie do p. 70; drugi ciąg od p. 65 nad Brązowym Progiem. | Notatka opisowa do partii Kujata, bez nowych wartości pomiarowych. |
| `20220325_124553 punkty Borowca1.jpg` | Tabela współrzędnych 75 punktów: 0W, 00, 01…73; kolumny Y, X, H. | Przepisana do `Punkty Borowca.xlsx`; z różnic współrzędnych utworzono 74 wektory. |
| `20220325_124555 punkty Borowca2.jpg` | Druga fotografia tej samej kartki i tych samych 75 punktów. | Materiał pomocniczy, nie druga część tabeli. W punkcie 64 wykryto rozbieżność z arkuszem. |

## Dane już cyfrowe i ich pokrycie

| Źródło | Stan w projekcie |
| --- | --- |
| `_RAW/02/Punkty Borowca.xlsx`, ręczna tabela `Arkusz1!A5:D79` | 75 współrzędnych → 74 wektory w obu `czarna-borowiec*.srv` → 74 odcinki w aktywnym `CZ_B_DAV.SRV`. Dodatkowo jest zerowe utożsamienie z punktem otworu. Konwersja istniejącej tabeli do DAV jest zgodna do dokładności zapisu 0,001; nie usuwa błędów wcześniejszej transkrypcji. |
| `CZ_B_S.SRV` | Dawna wersja RECT, w całości wykomentowana i niewpisana do WPJ. To zapis już zdigitalizowany, zastąpiony przez DAV. |
| `_RAW/02/Czarna pomiary Kujata.xlsx`, ręczna tabela `Arkusz1!A5:E59` | 55 odcinków: główna gałąź partii końcowych 0–26, 1200–1213, 2500–2507 i 6500–6509. Wszystkie wartości przeniesione do aktywnego `CZ_K_S.SRV`; 46 wierszy w części stopniowej i 9 w sekcji oznaczonej obecnie jako grady. |
| `_RAW/01/source/Czarna-zimna.top` i `Czarna-zimna_zrzut_pomiarow.txt` | Materiał od początku cyfrowy. Część Czarnej jest w `CZ_Z_S.SRV`: 93 właściwe odcinki, 41 domiarów i jedno zerowe utożsamienie, razem 135 aktywnych wierszy. |
| `_RAW/01/source/porównanie czarna - zimna.pdf` | Trzy strony zestawień graficznych planów/poligonów i połączenia powierzchniowego. Brak tabel wymagających odczytu do SRV. |
| `_RAW/03/Czarna 1979-2015.xls` | Źródło partii Wawelskich (`CZ_W_S.SRV`) i późniejszych pomiarów Nowaka (`CZ_N_S.SRV`); szczegółowe pokrycie poniżej. |
| Pięć PDF w `_RAW/03` | Artykuły, plany i przekroje z czasopisma „Jaskinie”; źródła opisowe do arkusza. Nie wykryto dodatkowego dziennika pomiarowego ciągu głównego. |

W `KATASTER.wpj:176–190` wpisane są `CZ_Z_S`, `CZ_B_DAV`, `CZ_K_S`,
`CZ_W_S` i `CZ_N_S`. Samo istnienie SRV nie oznacza, że jego pomiary
są aktywne: dotyczy to dawnego RECT Borowca i wykomentowanych partii Nowaka.

### Rozróżnienie brakującego odczytu i brakującego dowiązania w `_RAW/03`

| Zakładka arkusza | Liczba odcinków | Odpowiednik i status |
| --- | ---: | --- |
| `pod Rabkiem` | 21 | Przepisane jako komentarze w `CZ_N_S.SRV`; brak pewnego punktu dowiązania. |
| `pod Salą Francuską` | 20 | Przepisane jako komentarze w `CZ_N_S.SRV`; problem dowiązania opisany również przez autora w „Jaskiniach” 67, s. 22. |
| `do Herkulesa` | 20 | Aktywne w `CZ_N_S.SRV`. |
| `Sala Łukowa` | 16 | Aktywne w `CZ_N_S.SRV`. |
| `St. pod Kałużą` | 8 | Aktywne w `CZ_N_S.SRV`. |
| `Stromy Meander` | 81 | Aktywne w `CZ_N_S.SRV`. |
| `Wawelskie` | 100 | 99 aktywnych w `CZ_W_S.SRV`; wiersz `0→18'11` z `????` w źródle jest wykomentowany. |
| `grady - stopnie` | 100 | Ten sam zestaw Wawelskich w wersji przed przeliczeniem azymutów; nie dodatkowe 100 pomiarów. |

Partie Nowaka mają więc **125 aktywnych i 41 wykomentowanych odcinków**.
Te 41 odcinków wymaga rozwiązania nawiązań, a nie ponownej digitalizacji.
W zakładce `Wawelskie` są też uwagi o dalszych dziewięciu punktach do Gzymsu
(wiersz 48) i braku ciągu do szczytu komina (wiersz 111). Sama wzmianka
nie zawiera wartości umożliwiających odtworzenie brakujących pomiarów;
potrzebne byłoby pozyskanie dodatkowego źródła.

## Błędy i istotne rozbieżności już istniejących danych

### 1. Podwójne przeliczenie gradów Kujata — błąd geometrii

W [CZ_K_S.SRV:95](CZ_K_S.SRV#L95) jest `#units A=G V=G`, natomiast dziewięć
wierszy poniżej zawiera już wartości w stopniach. Na oryginale `124850.jpg`
widać np. `63 = 56,7°` i `−3 = −2,7°`; tabela `124400.jpg` przejęła
56,7 i −2,7. Aktywny SRV interpretuje je ponownie jako grady,
czyli efektywnie 51,03° i −2,43°. Problem obejmuje wszystkie odcinki
od `Borowiec:65→6501` do `6508→6509`.

Właściwa naprawa to użycie stopni dla już przeliczonych liczb albo konsekwentny
powrót do pierwotnych gradów. List poprawnie opisuje jednostki oryginału;
nie należy przenosić tej etykiety na tabelę po przeliczeniu.
Ta gałąź jest niezamknięta: błąd zniekształca jej geometrię, ale samo jego
usunięcie nie poprawi zamknięcia trawersu między otworami.

### 2. Długość 6501→6502 Kujata: 11,09 m / 11,90 m

Oryginał `124850.jpg` ma **11,09 m**. Przepisana tabela `124400.jpg`,
arkusz (`E52` i `M52`) i [CZ_K_S.SRV:98](CZ_K_S.SRV#L98) mają **11,90 m**.
Rozbieżność powstała przed konwersją arkusza do aktywnego SRV. To konflikt
źródeł i prawdopodobna zamiana cyfr przy przepisywaniu. Pierwotna karta
przemawia za 11,09 m, ale przed zmianą aktywnego pomiaru trzeba wykluczyć
świadomą korektę w późniejszej tabeli. Oryginały `_RAW` należy zachować bez zmian.

### 3. Punkt 64 Borowca: rozbieżność 10 cm w X

Na obu fotografiach `124553` i `124555` odczytano **X=2222,84**.
W ręcznej tabeli `Punkty Borowca.xlsx!C70` jest **2222,94**.
Przenosi się to na dwa sąsiednie wektory, [CZ_B_DAV.SRV:116](CZ_B_DAV.SRV#L116)
i następny: składowa północna 63→64 powinna wynosić 1,97 zamiast 2,07 m,
a 64→65 — 9,39 zamiast 9,29 m. Należy ponownie wyprowadzić oba odcinki DAV
z poprawionej współrzędnej, zamiast ręcznie zmieniać sam azymut.
Przeciwne poprawki znoszą się za punktem 65 w prostym niewyrównanym ciągu;
ten błąd sam nie wyjaśnia metrowego niezamknięcia na końcu całego ciągu.

### 4. Błędne odsyłacze i pozorna dokładność dat

- `CZ_B_DAV.SRV` i `CZ_K_S.SRV` wskazują `SOURCE_REF "_RAW/01"`, chociaż
  odpowiadające im skany i arkusze są w `_RAW/02`.
- `CZ_W_S.SRV` i `CZ_N_S.SRV` również wskazują `_RAW/01`, zamiast źródeł
  z `_RAW/03`.
- `_RAW/01/README.md:6` przypisuje materiałowi Szymona Kostki datę
  **1972-03-15**; cyfrowy zapis pomiaru ma datę **2011-10-02**.
- `CZ_K_S.SRV:30` stosuje **1975-08-20** jako datę przyjętą, co sam opis
  pliku ujawnia. Nazwa w WPJ mówi o pomiarach „1981”, lecz 3.03.1981
  to potwierdzona data listu. Żadnej z tych dat nie wolno bez dodatkowego
  dowodu przypisać nowemu dziennikowi 0–76.
- `CZ_N_S.SRV:163` używa zbiorczej daty **2015-12-31**. Źródła opisują
  różne akcje w 2015 r., ale nie potwierdzają pomiaru dokładnie tego dnia.

Arkusze zawierają także równoległe kolumny OCR. Przykładowo dla 6508→6509
Kujata ręczne `C59=213,3` odpowiada oryginalnemu `237g`, a OCR
`K59=243,3` jest błędne. Aktywny SRV przejął właściwą liczbę 213,3,
ale dotyczy go opisany wyżej błąd jednostek. Kolumn OCR nie traktowano jako
rozstrzygającego źródła.

## Nowy odczyt `CZ_GL_R.SRV`

- Format Walls: `order=DAV`, metry i stopnie, prefiks `Czarna:CiagSkany`.
- 76 odcinków głównych: roboczo **1109,70 m**; 2 odcinki boczne: **12,80 m**;
  razem **1122,50 m**. To sumy długości odcinków, nie nowo odkryta długość jaskini.
- Zachowano oryginalne numery i wartości pomiarowe; odczytane kolumny
  obliczeniowe Lh i Δh zapisano tylko w komentarzach.
- Cztery wiersze pozostają robocze. Są aktywne wewnątrz tego pliku,
  ale opisane `DO_WERYFIKACJI`; cały plik jest poza głównym WPJ.
- `DECL=0` oznacza roboczy brak korekty azymutu. Data, deklinacja i orientacja
  nie zostały ustalone; nie wprowadzono fikcyjnego `#date`.
- Brak `#fix`, zerowych utożsamień i połączeń z innymi pomiarami.
  Stacja 0 ma w skanie opis „Otwór”, a 76 „Koniec Colorado”. **To jeszcze
  nie jest kompletny i dowiązany trawers między dwoma otworami.**

| Odcinek | Pole | Wartość robocza | Alternatywny odczyt | Źródło |
| --- | --- | --- | --- | --- |
| 29→30 | D | 13,80 m | 13,60 m | `123630`, lewa strona |
| 39→40 | A | 25° | 75° | `123630`, ostatni wiersz lewej strony |
| 49→50 | A | 68° | 88° | `123630`, prawa strona |
| 71→72 | V | −1° | +1° | `123052` i `123533`, lewa strona |

Dwa odczyty wykonano niezależnie i następnie porównano. Wiersze sporne
sprawdzono na powiększeniach; tabeli nie „domknięto” dopasowaniem do oczekiwanej
geometrii. Uzgodnione trudniejsze zapisy: 55→56 D=5,90 m,
59→60 D=17,60 m, 74→75 D=17,00 m. W 57→58 azymut jest zastąpiony kreską
przy V=−90°; w SRV użyto prawidłowego zapisu brakującego azymutu pionu `--`.

### Niespójne obliczenia w samym dzienniku

Poniższe przykłady dotyczą kolumn obliczeniowych, nie automatycznie błędnego
odczytu instrumentu. Dlatego nie zastąpiono nimi wartości D/A/V.

| Odcinek | Zapis D, V | Kolumna ze skanu | Obliczenie z D i V |
| --- | --- | --- | --- |
| 2→3 | 5,20 m, −35° | Δh=−4,97 m | −2,983 m |
| 10→11 | 5,40 m, +36° | Lh=3,28 m | 4,369 m |
| 20→21 | 12,40 m, +30° | Lh=10,23 m | 10,739 m |
| 44→45 | 6,70 m, +35° | Lh=6,46 m | 5,488 m |
| 64→65 | 8,00 m, −33° | Δh=−3,64 m | −4,357 m |
| 65→66 | 19,80 m, −75° | Δh=−18,72 m | −19,125 m |
| 74→75 | 17,00 m, −25° | Lh=14,40 m | 15,407 m |

Komentarze SRV zaznaczają także inne różnice większe niż 0,15 m.
Ten próg służy jedynie do wskazania rozbieżnych rachunków, nie jest
oceną dokładności pomiaru. Dopiski z sumami wysokości na skanach również
nie zostały przyjęte jako wiążące rzędne punktów.

## Przygotowanie porównania jakości z GNSS

W bieżącym `Poligony/OTWORY.SRV` są dwa punkty:

| Punkt Walls | Obiekt GPS | Długość / szerokość geograficzna | Wysokość |
| --- | --- | --- | --- |
| `Czarna:M:otwor1` | `KSW-0201` | 19,8705053667 / 49,2444121431 | 1323,42 m |
| `Czarna:Kujat:0` | `KSW-0240` | 19,8812979507 / 49,2470745479 | 1403,92 m |

Identyfikatory pochodzą z `Poligony/OTWORY.SRV.j2:28,33`; współrzędne
z aktualnego pliku w checkoutcie. Różnica wysokości wynosi **80,50 m**.
Podaną przez użytkownika centymetrową dokładność otworów przyjęto jako
informację wejściową; nie audytowano tutaj źródłowych raportów GNSS.

Przed wyborem pomiaru należy:

1. Ustalić identyczne fizyczne punkty i domiary do GNSS. Obecnie
   `CZ_B_DAV.SRV:51` utożsamia punkt GPS z `Borowiec:0W` zerowym wektorem,
   a `CZ_Z_S.SRV` utożsamia go z punktem `SzKostka:1.92`, opisanym przy kracie
   około 50 cm od batinoxa. Centymetrowa dokładność GNSS nie dowodzi
   centymetrowej poprawności takiego utożsamienia.
2. Ustalić pochodzenie nowego dziennika i nawiązania do odcinka prowadzącego
   do III otworu. Nie utożsamiać równych numerów z różnych ciągów.
3. Rozstrzygnąć cztery niepewne wiersze oraz przygotować poprawiony wariant
   znanych błędów Kujata i Borowca, z zachowaniem wersji źródłowej.
4. Zbudować osobne warianty sieci i liczyć błąd dojścia do drugiego otworu
   przy jednym otworze ustalonym: dE, dN, dZ, błąd poziomy i 3D, długość
   porównywanego trawersu. Dopiero później ocenić wyrównanie przy obu fixach.
5. Oddzielić hipotezę daty/deklinacji od empirycznego dopasowania orientacji.
   Obrót dobrany do obu otworów nie jest niezależnym potwierdzeniem jakości.

Obecny model zawiera już pomiary powtórzone przez Nowaka: pary Borowca 6–7,
7–8, 8–9 oraz odwrócone 31–30 (`CZ_N_S.SRV:229–231,148`). Są jednocześnie
obecne w `CZ_B_DAV.SRV`. Zatem wynik kompilacji całej bieżącej sieci
nie jest oceną samego Borowca. Przykładowo 8→9 ma u Borowca D=10,532 m,
V=36,942°, a u Nowaka D=7,79 m, V=49,6°.

[Raport deklinacji Borowca](BOROWIEC_DEKLINACJA_RAPORT.md) zawiera wcześniejsze
eksperymenty. Ich wyników liczbowych nie odtwarzano w tym audycie i nie
przenoszono jako oceny nowego dziennika. Obecny audyt nie rozstrzyga,
który pomiar należy uznać za lepszy i włączyć jako podstawowy.

## Weryfikacja wykonanej pracy

- Oględziny rzeczywistych 10 JPG `_RAW/02`, z powiększeniami i porównaniem
  powtórnych fotografii; dwa niezależne odczyty 78 odcinków nowego dziennika.
- Porównanie ręcznych tabel XLSX z istniejącymi SRV i odróżnienie kolumn OCR.
- Odczyt cyfrowych źródeł `_RAW/01` oraz oględziny PDF i arkusza `_RAW/03`.
  W `_RAW/03` zweryfikowano pokrycie wszystkich ośmiu zakładek i obejrzano
  wszystkie dziesięć stron PDF; nie wykonano pełnego automatycznego porównania
  każdej liczby XLS z SRV. Dalszy fragment TOP poza Czarną, od 1.92 w stronę
  Zimnej, nie był przedmiotem kompletnej inwentaryzacji tego audytu.
- `jktz-srv-metadata srv-set` utworzył metadane nowego SRV.
- Walidatory repozytorium dla katalogu Czarnej: metadane, nazwy plików,
  ASCII, format dziesiętny, dyrektywy i prefiksy — bez błędów.
- `cavern -o /private/tmp/czarna-main-audit/CZ_GL_R.3d
  Poligony/D_Koscieliska/Organy/Czarna/CZ_GL_R.SRV` — sukces,
  79 stacji, 78 odcinków, 0 pętli, 1122,50 m. Informacja o automatycznym
  przyjęciu lokalnego początku w stacji 0 jest oczekiwana przy braku fixów.
- Kompilację formatu Walls sprawdzono parserem Survex 1.4.22; nie wykonano
  kompilacji w aplikacji Walls ani porównania z otworami.
- Przed pierwszą publikacją na `codex/czarna-digitalizacja`, utworzonej
  z `origin/master` (`446edc4`), wykonano pełne kontrole: **156 testów**,
  `ruff format --check`, `ruff check`, `jktz-render-otwory --check`
  (GPS `v1.0.2`, 87 fixów) i wszystkie 12 kroków `jktz-validate`, w tym
  kompilację oraz eksporty — sukces. Bramka głównego projektu nie kompiluje
  roboczego SRV, dlatego jego osobną kompilację opisano wyżej.

Aktywny model pozostał bez zmian. Publikacja gałęzi nie oznacza włączenia
nowego ciągu do modelu ani rozstrzygnięcia jakości pomiarów.
