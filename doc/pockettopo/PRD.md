# PocketTopo: konwersja pomiarów i ekstrakcja szkiców

Stan: **2026-09-25 — P00–P06 zakończone; CLI i skill gotowe**.
Branch roboczy: `codex/pockettopo-convert`, początek: `a6c235c898eed57902a2d6ba18db60917e01faee`.

## Wznowienie po wyczyszczeniu kontekstu

1. Przeczytaj `AGENTS.md`, ten PRD i sprawdź `git status` oraz bieżący branch.
2. **P06 zakończone.** Użycie opisuje [instrukcja CLI](CLI.md) i
   [skill pockettopo-convert](../../.agents/skills/pockettopo-convert/SKILL.md).
   Nie powtarzaj researchu i implementacji P00–P05.
3. Wyniki końcowe, ograniczenia i odtworzenie: [dowody P06](evidence/p06/README.md).
   Historia wcześniejszych decyzji pozostaje w dowodach P01–P05 poniżej.
4. Zakończono zakres tego PRD. Włączenie konkretnego pakietu do aktywnego
   katastru, niezależne ustalenie dat/CRS i dalsze rozszerzenia wymagają
   odrębnego zadania. Nie traktuj ukończenia narzędzia jako potwierdzenia
   kompletności wszystkich konwersji źródeł.

## Cel i ustalone wybory

Skill w **tym repozytorium** ma konwertować PocketTopo `.top` v3 do Walls
`.SRV` i Survex `.svx`, poprawnie uśredniać potwierdzone powtórzenia oraz
wydobywać plan i przekrój rozwinięty do SVG i PNG. Jakość oznacza zachowanie
znaczenia danych i możliwość sprawdzenia każdej transformacji.

Użytkownik wybrał oba warianty rysunków: **same kreski** oraz **szkic z punktami
i liniami pomiarowymi**, z osobnymi warstwami SVG. Rekomendowany silnik to własny
parser i eksportery; istniejące konwertery są narzędziami porównawczymi.
[Research](RESEARCH.md) zachowuje uzasadnienie, źródła i wykryte ograniczenia.

PocketTopo służy do przygotowania wzorców i porównań. Docelowy konwerter działa
bez Wine i GUI. Obecny helper macOS jest pomocą badawczą, nie silnikiem eksportu.

## Zakres wyniku

Dla pojedynczego wejścia powstaje osobny katalog zawierający:

| Wynik | Zawartość |
| --- | --- |
| `.SRV`, `.svx` | Te same pomiary po jawnie opisanym przetwarzaniu |
| 4 × SVG, 4 × PNG | Plan/przekrój × kreski/kreski z pomiarami |
| `source.json` | Wszystkie zdekodowane rekordy i surowe wartości |
| `conversion-report.json` | Pochodzenie, ustawienia, grupy średnich, nazwy, ostrzeżenia i kompletność |

Raport zawiera co najmniej SHA-256 wejścia, wersję narzędzia, indeksy rekordów
wchodzących do każdej średniej, komentarze, mapę nazw, źródłowe i użyte daty/korekty
oraz uzasadnienie każdego niewłączenia rekordu do aktywnych pomiarów.
Nie nadpisujemy wejścia ani `_RAW`; błędy nie zostawiają częściowo podmienionego
pakietu. Istniejący katalog wyjścia wymaga jednoznacznej polityki kolizji.

Poza zakresem: `.cal`, kalibracja urządzeń, interpretacja szkicu jako gotowej mapy,
łączenie niezależnych pomiarów, automatyczne dopisywanie do `KATASTER.wpj`
i aktualizacja otworów GPS. Integracja aktywnego SRV z katastrem jest odrębnym
krokiem, zgodnym z istniejącymi narzędziami metadanych.

## Reguły poprawności

### Pomiary i średnie

- Zachowujemy całkowite mm, jednostki kątowe, ticks, identyfikatory, flagi,
  komentarze i kolejność. Obliczenia poprzedzają formatowanie i zaokrąglenie.
- Pełny obrót to **65536** jednostek kąta i **256** jednostek roll.
- Łączymy tylko potwierdzone, kolejne odczyty tej samej nazwanej pary w tej samej
  sesji. Nazwy i zbliżona geometria same nie dowodzą powtórzenia. Zmiana sesji,
  splay, zerowe powiązanie i rozdzielona seria przerywają grupowanie.
- Kierunek wyznacza pierwszy odczyt. Zamienione FROM/TO normalizujemy przez
  `azymut + 180° mod 360` i zmianę znaku pochylenia.
- Azymut: `degrees(atan2(Σsin(a), Σcos(a))) mod 360`, sumowanie `math.fsum`.
  Długość i podpisane pochylenie −90°…+90°: średnia arytmetyczna po normalizacji.
  Średnia wektorów 3D nie zastępuje tego kontraktu.
- `358°/2° → 0°`; `0°/180° → brak określonej średniej`. Raportujemy liczność
  i rozrzut/resultant length. Nie usuwamy automatycznie odstających odczytów;
  progi niejednoznaczności i pomiary pionowe wymagają jawnych testów.
- Nie utożsamiamy `0` z `0.0`; nazwa nie jest liczbą zmiennoprzecinkową.
  Ograniczenia nazw Walls/Survex rozwiązujemy zachowaniem dosłownej nazwy tam,
  gdzie możliwe, albo odwracalnym mapowaniem bez kolizji.
- Splays, zerowe powiązania i rekordy nieaktywne nie znikają z modelu źródłowego.
  Nieznane elementy nie mogą prowadzić do pozornie kompletnego eksportu.

### Daty, deklinacja i współrzędne

**Informacja użytkownika:** palmtopy Dell miały słabe baterie podtrzymania zegara.
Data trip z `.top`, szczególnie wyglądająca na reset, jest **poszlaką**, nie dowodem
daty pomiaru. Zachowujemy ją osobno od daty ustalonej z niezależnych źródeł,
z podstawą ustalenia i statusem wiarygodności. Nie zastępujemy jej automatycznie
datą z nazwy pliku. Sama nie uruchamia obliczenia deklinacji z IGRF.

Wierny eksport zachowuje zapisane korekty, bez uznawania zera za historyczne
potwierdzenie poprawności. W Walls z jawnym `DECL` zapisujemy datę w komentarzu
lub metadanych, bez kombinacji `#date`/`DECL` zakazanej przez `AGENTS.md`.
Włączenie do JKTZ wymaga ustalenia daty i polityki korekt. E/N/Z w `.top`
nie określają CRS: nie zakładamy WGS84/UTM ani nie tworzymy aktywnych fixów
bez wyjaśnienia układu. Zachowujemy źródłowe referencje i raportujemy ograniczenie.

Ustalenie P01: surowa deklinacja `-32768` oznacza **tryb Auto**, a nie −180°.
Zachowujemy ją i tryb oddzielnie. Natywne `Auto: 0.00` bez referencji nie
upoważnia do przyjęcia jawnego zera ani automatycznego wyliczenia IGRF.

### Szkice

- Zachowujemy każdy wierzchołek, kolor, kolejność, otwarte polilinie i pojedyncze
  punkty. Nie wygładzamy i nie domykamy kresek; kolor nie definiuje symbolu mapy.
- `sideview` to przekrój rozwinięty. `flipped` oznacza jego kierunek lewo/prawo,
  a nie pomiar wsteczny. XSection zachowuje pozycję, stację i kierunek projekcji.
- Szkic jest stały; nie przesuwamy go, aby dopasować do przeliczonej osnowy.
  Pętle, rozgałęzienia i przekroje wymagają porównania z aplikacją.
- Mapping widoku przechowujemy jako metadane, nie jako zmianę geometrii źródła.
- SVG rozdziela szkic, osnowę, domiary, punkty/opisy i przekroje na warstwy.
  PNG powstaje z tego samego SVG; renderer, rozdzielczość i tło są jawne.
- Pusty szkic daje jawny status i oznaczony pusty wynik, bez wymyślania obrysu.

## Architektura i plan etapów

Docelowo: `src/jktz/pockettopo/` (model, parser, matematyka, eksport, raport),
`src/jktz/cli/pockettopo.py` oraz `.agents/skills/pockettopo-convert/SKILL.md`.
P02 udostępnia już bibliotekę `parse_bytes` / `read_top` oraz niezmienny model.
P03 dodaje `prepare_conversion`, `ProcessingPlan`, `RepeatConfirmation` i
`Exclusion`: dokument źródłowy JSON i raport w pamięci, bez zapisu pakietu.
P04 udostępnia `export_surveys`, `SurveyExport`, `CorrectionPolicy` i
`CorrectionOverride`: teksty SRV/SVX, mapa nazw i raport decyzji w pamięci.
P05 dodaje `export_drawings`, `DrawingExport`, `DrawingSettings` i
`RenderingError`: cztery SVG i opcjonalnie cztery PNG przez resvg 0.48.1.
P06 udostępnia `uv run jktz-pockettopo inspect ...` i `convert ...`,
`load_decisions`, `validate_surveys` oraz `convert_package`. Pakiet jest
publikowany atomowo bez zastępowania istniejącego celu. Nie budujemy łańcucha
`.top → zaokrąglony SRV → średnie`.

| Etap | Wynik i warunek zakończenia | Stan |
| --- | --- | --- |
| P00 Research i dostęp | Źródła, decyzje, natywny eksport Shadow i instrukcja wznowienia zapisane w repo | Gotowe |
| P01 Wzorce aplikacji | 6 małych `.top` (2 GUI, 4 natywny model/API), TXT/DXF, oczekiwania każdego pola, końcowe 4 zera i Auto; resvg sprawdzony na macOS/Linux | Gotowe — [dowody](evidence/p01/README.md) |
| P02 Parser i model | Ścisły odczyt wszystkich struktur; 211 testów P02, pełny korpus 258/258, jakość i mutacje | Gotowe — [dowody](evidence/p02/README.md) |
| P03 Średnie i raport | Grupy potwierdzonych powtórzeń, matematyka, ślad każdego rekordu i testy graniczne | Gotowe — [dowody](evidence/p03/README.md) |
| P04 SRV/SVX | Zachowanie semantyki, kompilacja obu formatów i porównanie geometrii; sprawdzenie w Walls | Gotowe — [dowody](evidence/p04/README.md) |
| P05 SVG/PNG | Oba widoki i warianty, XSection, warstwy, renderer bez GUI; kontrola punktów i obrazów | Gotowe — [dowody](evidence/p05/README.md) |
| P06 CLI i skill | Atomowy pakiet wynikowy, instrukcje skilla, niezależna próba użycia i pełna walidacja | Gotowe — [dowody](evidence/p06/README.md) |

P01 obejmuje kierunki kardynalne i granicę północy, pomiary przód/tył, kilka tripów,
różne deklinacje, plain ID i major.minor, komentarze UTF-8, wszystkie kolory,
Flip, XSection, ujemne referencje i puste szkice. Każdy przypadek ma mały zakres
i ręcznie określony wynik; własny writer nie może być jedynym wzorcem parsera.
W P01/P05 wybrać i sprawdzić renderer PNG działający lokalnie i w CI.

## Kryteria odbioru

- Niezależne wzorce sprawdzają każdy rekord i wierzchołek, nie tylko sumę długości.
  Testy obejmują zakresy signed, identyfikatory, UTF-8/varint, ticks bez float,
  uszkodzenia, ucięcia i nieznane struktury oraz brak częściowych zapisów.
- Testy matematyczne pokrywają granice kątów, pomiary wsteczne, niejednoznaczność,
  grupowanie, sesje, pojedyncze odczyty, splays, zera i piony.
- Lokalny pełny przebieg 258 unikalnych plików `test2` z przypiętej rewizji
  raportuje wszystkie przypadki nieobsługiwane. CI korzysta z małych lokalnych
  fixture o ustalonym pochodzeniu, bez zależności od sieci.
- SVG sprawdza niezależny parser XML, PNG oglądamy pod kątem osi, skali, kolorów
  i obcięcia. Porównanie natywnych DXF obejmuje współrzędne, nie tylko liczności.
- SRV i SVX kompilują się bez ostrzeżeń i dają zgodną geometrię przy tej samej
  jawnej korekcie/CRS. Tolerancje wynikają z precyzji zapisu i zaokrągleń.
  Oddzielny test w rzeczywistym Walls potwierdza jego zgodność.
- `jktz-quality`: linie ≥95%, gałęzie ≥90%, CRAP ≤25. Parser i matematykę
  włączyć jawnie do zakresu mutacji, z ≥81% dla każdego objętego modułu;
  istniejących bramek nie obniżać. Python 3.12 jak w CI.
- Skill przechodzi walidację struktury i niezależną próbę na surowych materiałach.
  Obowiązują również zwykłe kontrole projektu przed commitem/pushem.

## Zapisane dowody i otwarte kwestie

Natywna próba Shadow: wszystkie 32 rekordy tekstowe porównane ze źródłem,
liczności szkiców zgodne, źródło identyczne bajtowo. Pełny audyt współrzędnych
DXF ukończono w [P05](evidence/p05/projection.md). Szczegóły i pliki: [dowód Shadow](evidence/shadow/README.md).

P01 rozstrzygnęło zakończenie: PocketTopo 1.372 zapisuje Int32 `0` po drugim
rysunku, lecz jego czytnik ignoruje cały sufiks. Kontrakt P02 dopuszcza dokładnie
EOF po schemacie albo dokładnie cztery zera; pozostałe sufiksy są błędem.
[Dowód natywnego API](evidence/p01/NATIVE_API.md) opisuje również sentinel Auto.
[Renderer resvg 0.48.1](evidence/p01/renderer/README.md) dał identyczne PNG na
macOS i Linux; P05 integruje bibliotekę oraz przypięty renderer w CI.

P05 rozstrzygnęło podkład w pętlach/rozgałęzieniach, projekcję XSection
z domiarami i paletę oraz przyjęło wektorowe glify etykiet. Do ustalenia
pozostaje format profilu metadanych dla aktywnego JKTZ. Natywny DXF uśrednia własnym
algorytmem i nie zastępuje kontraktu średnich P03. Odczyt pełnego korpusu 258 plików
sprawdzono w P02, a porównanie eksportów pomiarowych korpusu wykonano w P04.
Porównanie eksportów szkiców oraz audyt współrzędnych Shadow zapisano w P05.
Nie deklarować pełnej zgodności przed spełnieniem kryteriów odbioru.

Uzupełnienie P01 (2026-09-25): trzy rzeczywiste źródła z test2 zawierają 15 serii
potrójnych i oba szkice. Natywne TXT: 50 rekordów zgodnych; DXF: 2540
wierzchołków zgodnych wraz z kolorami i kolejnością.
[Dobór](REPEAT_CANDIDATES.md), [dowody i ograniczenia](evidence/repeat-candidates/README.md).
Wzorce wykorzystano w P02.

P02 (2026-09-25): niezmienny model i ścisły parser zachowują surowe wartości,
rozpoznają Auto i oba zakończenia, odrzucają błędne struktury i przekroczenia
limitów z kodem/offsetem/kontekstem. Porównano każde pole i wierzchołek dziewięciu
wzorców; 2211 ucięć sześciu P01 odrzucono. Pełny korpus: 258/258 źródeł,
262/262 zgodne obiekty Git, zero błędów; 256 zakończeń z zerami i dwa EOF.
Bramki: 596 testów, 96,52% linii / 93,82% gałęzi, maksymalny CRAP 21,54;
mutacje modelu 37/37, parsera 635/703, każdy z siedmiu modułów ≥81%.
[Dowody i instrukcja biblioteki](evidence/p02/README.md),
[korpus i reprodukcja](evidence/p02/CORPUS.md),
[wyniki bramek](evidence/p02/repository-checks.json).
Był to stan zakończenia P02; aktualny stan opisuje P03 poniżej.

P03 (2026-09-25): jawne potwierdzenia serii i wyłączenia są związane z SHA-256
źródła; każdy rekord ma ślad i przyczynę decyzji. Brak potwierdzeń pozostawia
wszystkie odczyty osobno. Średnie normalizują kierunki, zachowują surowe wartości
i raportują R oraz rozrzuty. Domyślnie R ≤ 1e-12 oznacza nieokreślony azymut;
próg jest jawny, konfigurowalny i testowany. Piony zachowują azymut z ostrzeżeniem.
Dokument źródłowy oraz raport mają zgodną z JSON reprezentację w pamięci;
przykładowe wyniki, dziewięć raportów wzorców i reprodukcja są w repozytorium.

Korpus P03: 258 źródeł / 262 zgodne obiekty Git, wszystkie 37 801 rekordów
rozliczone, 37 426 gotowych D/A/V i 375 zatrzymanych z przyczyną; zero
automatycznych potwierdzeń powtórzeń. Bramka: 785 testów (189 nowych P03),
96,89% linii / 94,60% gałęzi, maksymalny CRAP 21,54. Mutacje: matematyka
173/182 (95,05%), grupowanie 183/183 (100%); wszystkie dziewięć modułów ≥81%,
brak niepełnych wyników. Przegląd poprawił skrajny próg R dla identycznych
kierunków oraz kolizję nazw dwóch raportów dowodowych.
[API i dowody](evidence/p03/README.md), [wyniki bramek](evidence/p03/repository-checks.json).
Następny etap: **P04**. Eksporty, CLI i atomowy pakiet wynikowy pozostają do wykonania.

Wznowienie P03 (2026-09-25): istniejące commity P02/P03 wypchnięto na `origin`
po pełnej walidacji cavern/GDAL. Powtórzono bramki jakości i mutacji oraz
odtworzono dowody na źródłach; [zapis weryfikacji](evidence/p03/REVALIDATION.md)
uzupełnia wcześniejsze wyniki. Zakres następnej pracy pozostaje P04.

Kontrola CI ujawniła problemy testów na Windows: zbyt długie identyfikatory
parametrów pytest i zależność od domyślnego kodowania przy odczycie JSON.
Dodano krótkie identyfikatory, jawne UTF-8 i regresję cp1252; aktualnie
786 testów (190 P03). Kod produkcyjny i wejścia są niezmienione.
[Dowody i wyniki](evidence/p03/WINDOWS.md). Końcowe CI dla poprawionej rewizji
`ae545cd7a7aaee91bb4c6c1fe2219550f345f096` zakończyło się sukcesem:
jakość Pythona, mutacje, walidacja Linux i Windows oraz pakiet PR — pięć zadań.
[Zapis weryfikacji CI](evidence/p03/ci-validation.json) zamyka kontrolę po
poprawkach Windows. Następny etap nadal P04.


P04 (2026-09-25): eksporty SRV/SVX zachowują niepotwierdzone odczyty osobno,
średnie z jawnych potwierdzeń P03, splays, zerowe powiązania i odwracalne nazwy.
Jawne zapisane deklinacje są odtwarzane; Auto i brak sesji wymagają niezależnie
uzasadnionej korekty związanej z SHA źródła. Daty/CRS pozostają nieustalone,
referencje nie tworzą aktywnych fixów. Raport wskazuje decyzję i linię eksportu
każdego rekordu; kompletność tekstu nie oznacza kompletności kompilacji.

Korpus: 258 źródeł / 262 zgodne obiekty Git, 37 801 rekordów rozliczonych,
37 362 aktywne i 439 zatrzymanych z przyczyną. 249 źródeł kompiluje się w obu
formatach bez ostrzeżeń, 7 ma niepołączone części (częściowa geometria), 2 nie
mają aktywnych pomiarów. Geometria stacji obecnych w 256 parach wyników jest
identyczna po normalizacji początku; nie jest to dowód obecności pominiętych
części ani potwierdzenie powtórzeń. Zachowano wyniki każdego źródła.

Próby analityczne sprawdzają poprawki, stacje, piony, zera i splays; rzeczywisty
Walls 2.3.0-beta.1 potwierdza kompilację i współrzędne nazwanych stacji w trzech
izolowanych przypadkach. Testy kompilacji są wymagane w CI Linux/Windows.
Bramki, tolerancje, hashe i ograniczenia: [dowody P04](evidence/p04/README.md).
[Próby graniczne kompilatora](evidence/p04/COMPILER_LIMITS.md) dokumentują
pomijanie rozłącznych części mimo exit 0 oraz crash cavern 1.4.22 przy dodatnim
odcinku sprzecznym z zerowym powiązaniem. P06 musi kontrolować ostrzeżenia,
kompletność geometrii i błędy procesu; nie tworzyć sztucznych fixów.

P05 (2026-09-25): plan i rozwinięcie w wariantach same kreski / kreski
z pomiarami, osobne warstwy, natywna paleta, singletony, jawne stany pustego
szkicu i ostrzeżenia podkładu. SVG zachowuje każdy wierzchołek; PNG powstaje
z tego samego SVG przez przypięty resvg 0.48.1, bez fontów systemowych.
Nowe natywne wzorce rozstrzygają pętle, rozgałęzienia, Flip i XSection
z domiarami. Pełny audyt Shadow obejmuje oba szkice i każdą linię pomiarową.

Pełny korpus: 258 źródeł / 262 zgodne obiekty Git, 1032 SVG i 1032 PNG,
952 211 zachowanych wierzchołków, 10 XSection. Zachowano niezmienioną politykę
P03/P04: 439 rekordów nadal zatrzymanych, brak automatycznych potwierdzeń
powtórzeń i dat. Podkład nie wyrównuje pętli ani nie ustala wzajemnego położenia
rozłącznych części; takie ograniczenia są raportowane i widocznie oznaczone.
[Wyniki, obrazy, reprodukcja i bramki P05](evidence/p05/README.md).

P06 (2026-09-25): CLI `inspect`/`convert`, ścisłe decyzje JSON związane
z SHA-256 wejścia i skill `pockettopo-convert`. Każdy wynik ma 12 plików,
manifest hashy, raport procesów oraz osobne stany kompletności. Zapis odbywa
się przez atomowe przeniesienie z zakazem zastępowania celu, również przy
równoległym utworzeniu pustego katalogu. Błąd odczytu/renderera/zapisu nie
publikuje częściowego pakietu. Niepełne dane lub kontrole dają pełny pakiet
audytowy i kod 2, bez przedstawiania go jako kompletnej konwersji.

Pełny przebieg CLI: 258 źródeł / 262 zweryfikowane ścieżki Git, 258 pakietów,
3096 artefaktów (1032 SVG i 1032 PNG). Wszystkie 37 801 rekordów rozliczone;
439 nadal zatrzymanych. 249 wyników ma kompletną kompilację, ale tylko 12
spełnia wszystkie warunki `conversion_complete`; pozostałe 246 zachowuje
jawne ograniczenia pomiarów, osnowy lub kompilacji. Cztery SVG/PNG każdego
z 13 wzorców są identyczne bajtowo z P05. Niezależna próba skilla na `okna.top`
potwierdziła użycie, odczyt ograniczeń, obrazy i odmowę kolizji.

Bramki: 1248 testów, linie ≥95%, gałęzie ≥90%, CRAP ≤25; mutacje
2483/2748 (90,36%), każdy z dziesięciu modułów ≥81%; pełna walidacja
Survex/GDAL. Dokładne wartości, hashe kodu, próby awarii, przegląd i odtworzenie
są w [dowodach P06](evidence/p06/README.md). Etap zakończony; brak kolejnego
etapu implementacyjnego w tym PRD.

Kontrola CI P06: pierwszy przebieg przeszedł jakość, mutacje i Linux,
ale wykrył problem testu uruchomienia kompilatorów przez dowiązania na
Windows. Próba używa teraz względnych ścieżek do oryginalnej instalacji,
z pełną diagnostyką błędów. Produkcja i korpus bez zmian;
[dowody i zakres poprawki](evidence/p06/WINDOWS.md).
