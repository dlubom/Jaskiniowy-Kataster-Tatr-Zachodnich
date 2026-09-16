# Jaskinia Czarna — stan prac i dalsze kroki

Aktualizacja: 2026-09-16. Gałąź robocza: `codex/czarna-digitalizacja`,
utworzona z `origin/master` na `446edc4`.
Dokument służy wznowieniu pracy bez historii rozmowy. Aktualizuj go po każdym
zakończonym etapie, razem z dowodami, wykonanymi sprawdzeniami i następnym krokiem.

## Cel i zakres uprawnień

Celem jest rozpoznanie i odczyt archiwalnych pomiarów Czarnej, a następnie
porównanie ich jakości z pomiarami Borowca przy wykorzystaniu precyzyjnych
pomiarów otworów. Dopiero na podstawie źródeł i kontrolowanego porównania
można wybrać podstawowy ciąg i sposób włączenia go do sieci.

Autorem dziennika 0–76 i 6–a–b jest **Ryszard Kujat**. Użytkownik potwierdził
to 2026-09-13, wskazując nazwę fotografii z dopiskiem `Kujat`. Usunięto
nieuzasadnioną hipotezę innego autorstwa. Data i instrument pozostają nieustalone;
daty listu dotyczącego innych partii nie przypisuj temu dziennikowi.

Użytkownik upoważnił do utworzenia gałęzi oraz commitów i pushów, najpierw
dotychczasowej digitalizacji, następnie dokumentacji stanu w osobnym commicie,
a dalej do ulepszania danych i analizy. Nie upoważnił do merge, tagu ani release.
Publikację i CI potwierdzaj dla rzeczywistego SHA; nie traktuj zamiaru jako wyniku.
CI uruchamia się dla push na master lub PR, nie dla samego push tej gałęzi.
Dotychczasowe polecenie nie obejmuje PR; nie zgłaszaj nieuruchomionego CI jako sukcesu.

## Punkt wejścia dla kolejnego agenta

1. Przeczytaj główny [CLAUDE.md](../../../../CLAUDE.md) i lokalny [AGENTS.md](AGENTS.md).
2. Sprawdź `git status --short --branch`, `git log -5 --oneline` oraz zakres zmian.
3. Przeczytaj [raport digitalizacji](DIGITALIZACJA_RAPORT.md) i [CZ_GL_R.SRV](CZ_GL_R.SRV).
   Wpływ czterech niepewnych odczytów opisuje [analiza wariantów](WARIANTY_ODCZYTU.md)
   z kompletem wyników w [JSON](WARIANTY_ODCZYTU.json).
   Najnowszy etap to [kontrola wyniku Claude Opus 5](POROWNANIE_OPUS.md):
   bez zmiany D/A/V, z korektą komentarza Lh20→21 na 10,73 m.
   Wcześniej wykonano [porównanie przebiegu Kujat–Borowiec](POROWNANIE_BOROWIEC.md)
   z nakładką planu i profilu oraz [porównanie Gemini](POROWNANIE_GEMINI.md).
   Wyniki dostarczone przez użytkownika zachowano w [ODCZYTY_MODELI](ODCZYTY_MODELI/README.md).
4. Sięgaj do rzeczywistych skanów wskazanych w raporcie; tabele i OCR są wtórne.
5. Przeczytaj [raport deklinacji](BOROWIEC_DEKLINACJA_RAPORT.md) jako zapis wcześniejszego
   eksperymentu. Jego wyników nie uznawaj za ponownie zweryfikowane ani za ocenę nowego ciągu.

## Ukończone etapy i obecny stan

- Pierwszy etap opublikowano jako `74723744834ee9badf4b5334f9319de651c73c6c`
  (`Czarna: zinwentaryzuj skany i dodaj roboczy odczyt ciagu glownego`).
  Obejmuje `CZ_GL_R.SRV` i `DIGITALIZACJA_RAPORT.md`. Niezależny przegląd
  nie wykazał usterek P1/P2; potwierdził izolację danych i sumy odcinków,
  ale nie powtarzał wszystkich odczytów skanów.
- Dokumentację celu i przekazania pracy opublikowano osobno jako
  `6fe56a8f8e8961d7528c48df208de7f0f7b6fc5d`
  (`Czarna: zapisz cel, stan prac i instrukcje kontynuacji`). Oba pierwsze
  commity potwierdzono na zdalnej gałęzi; sam push nie uruchomił CI.
- Inwentaryzacja źródeł jest ukończona: rozróżniono brakujące odczyty, kopie
  fotografii, już cyfrowe pomiary i odczytane partie oczekujące na dowiązanie.
- Brakujący dziennik obejmuje 76 odcinków 0–76 i dwa odcinki 6–a–b.
  Zdjęcia `123052` i `123533` pokazują te same strony; `123630` zawiera środek ciągu.
- `CZ_GL_R.SRV` zawiera 78 roboczo odczytanych odcinków, zweryfikowanych przez
  dwóch niezależnych czytelników. Cztery odczyty pozostają nierozstrzygnięte.
- Robocza suma wynosi 1122,50 m: 1109,70 m ciągu głównego i 12,80 m odgałęzienia.
  To suma pomiarów w tym pliku, nie przyrost długości całej jaskini.
- Plik używa `Czarna:CiagSkany`, `order=DAV`, metrów i stopni. Nie ma daty,
  fixów ani utożsamień. `DECL=0` jest wyłącznie roboczym brakiem korekty.
- SRV pozostaje poza `KATASTER.wpj`. Stacja 0 jest opisana jako „Otwór”,
  a 76 jako „Koniec Colorado”; plik nie jest gotowym trawersem do III otworu.
- Sprawdzono lokalne walidatory oraz kompilację parserem Walls w Survex 1.4.22:
  79 stacji, 78 odcinków, 0 pętli. Nie wykonano kompilacji w aplikacji Walls.
- Pełna walidacja po aktualizacji gałęzi: 156 testów, Ruff, sprawdzenie 87 fixów
  GPS z v1.0.2 oraz wszystkie 12 etapów `jktz-validate` zakończyły się sukcesem.
- Ukończono analizę wszystkich 16 kombinacji niepewnych odczytów: CLI
  `jktz-czarna-warianty`, testy, raport i wynik JSON z SHA-256 wejścia.
  Każdą kombinację sprawdzono niezależną kompilacją Survex 1.4.22;
  48/48 składowych E/N/Z zgadza się w granicach zaokrąglenia do 0,01 m.
  Największy pojedynczy wpływ ma 39→40 (9,86 m); najdalsza para wariantów
  różni się o 12,12 m. To wpływ transkrypcji, nie ocena jakości pomiaru.
  Niezależny przegląd narzędzia nie wykazał usterek P1/P2; nie był kolejnym
  odczytem skanów. Kontrole publikacji tego etapu zapisano poniżej.
  Pierwszą wersję analizy opublikowano jako
  `b36d312a9b551116ce983aff976815df8320e59f`; potwierdzono zdalne SHA,
  CI nie uruchomiło się od pushu.
- Porównano dwa dostarczone wyniki Gemini z tą zamrożoną wersją SRV.
  Flash ma 3 różnice pierwszych wartości D/A/V (jedna zawiera także poprawny
  odczyt jako alternatywę); Pro ma 11 oraz błędną parę 18→20 zamiast 19→20.
  Są to rozbieżności względem bazy, nie liczby błędów. Dodatkowe oględziny
  skanów przez dwóch czytelników i agenta głównego sprawdziły sporne wiersze.
- Zmieniono preferowaną roboczą wartość A39 z 25° na 75° na podstawie grafii
  skanu, wspartej dwoma Gemini i dodatkowym odczytem bez dostępu do tych wyników.
  Zachowano 25° jako alternatywę oraz cztery oznaczenia niepewności.
  Pozostałe D/A/V pozostają bez zmian. JSON i testowa wartość bazowa narzędzia
  zostały uaktualnione; drugi bit wariantu oznacza teraz 0=75°, 1=25°.
- Poprawiono błędną nazwę „Tehmy” na „Tehuby”. PIG i artykuł J. Nowaka
  rozróżniają współczesne Partie Tehuby oraz historyczną nazwę Techuba.
  Źródła zapisano w `POROWNANIE_GEMINI.md`. Etap Gemini opublikowano jako
  `f8832488a906fe98f38c3bebcbd45c9691369711`; zdalne SHA potwierdzono,
  sam push nie uruchomił CI.
- Po korekcie użytkownika wpisano Ryszarda Kujata do `TEAM` nowego SRV
  i dokumentacji. Nie zmieniono żadnego D/A/V. Odświeżono SHA-256 w analizie
  wariantów i ponowiono 16 kompilacji kontrolnych z identyczną geometrią.
- Porównano 76 odcinków Kujata z 74 odcinkami głównego ciągu Borowca,
  bez dopasowywania obrotu i skali. Długości różnią się o 0,97%, kierunki
  początku–końca o 0,60°. Plan i większość profilu wskazują ten sam ciąg główny.
  Numeracja i rozmieszczenie stacji są różne; nie ma tabeli potwierdzonych
  tożsamości fizycznych stanowisk. Istotna lokalna różnica pionowa występuje
  przy K64–71 / B52–64, w rejonie Studni Imieninowej. Szczegóły, metoda,
  źródła i ograniczenia: `POROWNANIE_BOROWIEC.md` oraz powiązany JSON i wykres.
- Oryginały `_RAW`, istniejące aktywne pomiary i współrzędne otworów zachowano.
  Pełna historia późniejszych zmian i publikacji znajduje się w git.
- Porównano wynik opisany przez użytkownika jako Claude Opus 5: 78/78 par,
  21 różnic D/A/V na 20 odcinkach względem `fc33499`; 18 konfliktów po
  uwzględnieniu alternatyw. Nie są to liczniki udowodnionych błędów.
  Kontrola fotografii nie uzasadnia zmiany D/A/V. Wskazanie A49→50=88°
  przez Opusa i nowego czytelnika wspiera zachowanie już znanej alternatywy;
  V71→72 nadal nie rozstrzygnięto. Nie pozyskano daty ani dowiązań.
- Przy kontroli pełnych Lh/Δh poprawiono nasz pomocniczy odczyt Lh20→21
  z 10,23 na 10,73 m. Wartość była już w obu Gemini; teraz potwierdzono
  ją z fotografii. Poprawiono komentarz SRV i usunięto ten błędny przykład
  „arytmetyki źródła” z raportu. D/A/V i geometria są identyczne.
- Słabsze hipotezy Opusa D59→60=12,60 m i V a→b=−32° zachowano
  w raporcie do kontroli na lepszym materiale. Porównanie grafii przemawia
  nadal za 17,60 m i −37°. Nie dodano tych hipotez do 16 wariantów;
  cztery formalnie oznaczone niepewności nie są gwarancją czytelności
  wszystkich pozostałych cyfr. Pomocnicze Δh58→59 także pozostaje niepewne.

## Cztery odczyty do potwierdzenia

| Odcinek | Pole | Roboczo | Alternatywa |
| --- | --- | --- | --- |
| 29–30 | D | 13,80 m | 13,60 m |
| 39–40 | A | 75° | 25° |
| 49–50 | A | 68° | 88° |
| 71–72 | V | −1° | +1° |

Nie wybieraj odczytu przez dopasowanie do GNSS, starego poligonu ani rachunków
na kartce. Komentarze `Lh_scan` i `dh_scan` zawierają błędy źródła i nie sterują
geometrią. Kreska azymutu pionu 57–58 (`--`, V=−90°) nie jest piątym spornym wierszem.

## Znane problemy istniejących danych

- Kujat 6500–6509: dziewięć wartości już przeliczonych na stopnie aktywny SRV
  ponownie interpretuje jako grady. To potwierdzony błąd jednostek.
- Kujat 6501–6502: oryginał 11,09 m, przepisana tabela i SRV 11,90 m.
  Przed zmianą ustal, czy późniejsza tabela dokumentuje świadomą korektę.
- Borowiec, punkt 64: skan X=2222,84, ręczny arkusz X=2222,94. Poprawka wymaga
  ponownego wyprowadzenia dwóch sąsiednich wektorów; nie zmienia sumy za punktem 65.
- Błędne `SOURCE_REF`: Borowiec i Kujat powinny wskazywać `_RAW/02`, Wawel
  i Nowak `_RAW/03`. README `_RAW/01` podaje 1972 zamiast cyfrowej daty 2011-10-02.
- 41 pomiarów Nowaka i jeden Wawelu są już odczytane, lecz wykomentowane
  z powodu dowiązania lub wątpliwego połączenia. Nie digitalizuj ich od nowa.

## Najbliższy krok i warunki porównania

1. Wróć do źródeł według wpływu niepewnego odczytu: 39→40 A, 49→50 A,
   71→72 V, 29→30 D. Gemini i ponowne oględziny wzmacniają obecne preferencje,
   ale czterech niepewności jeszcze nie usunięto; potrzebne może być lepsze zdjęcie,
   oryginalny dziennik lub niezależny zapis obserwacji. Nie wybieraj cyfr
   według uzyskanego domknięcia. Analiza 16 wariantów jest już wykonana.
   Wynik Opusa nie rozstrzygnął tych pól. Przy lepszym materiale sprawdź
   także D59→60, V a→b i pomocnicze Δh58→59 zgodnie z `POROWNANIE_OPUS.md`.
2. Sprawdź przebieg obu pomiarów w rejonie Studni Imieninowej, szczególnie
   zejście K65→66 i odcinek Borowca ku B60. Nakładka planu jest zbieżna,
   ale profile różnią się lokalnie o około 20–30 m. Nie rozstrzygnięto, czy
   to inny poziom/droga czy problem danych. Ustal fizyczne odpowiedniki
   na podstawie szkiców i opisów; podobieństwo geometryczne nie jest dowiązaniem.
   Autorstwo Kujata jest ustalone, data i instrument nadal nie. Znane błędy
   istniejących pomiarów rozpatruj osobno: jednostki 6500–6509 oraz 11,09/11,90 m.
3. Ustal wspólne fizyczne punkty i domiary do GNSS: `KSW-0201` odpowiada
   `Czarna:M:otwor1`, `KSW-0240` — `Czarna:Kujat:0`. Centymetrowa dokładność
   pochodzi z informacji użytkownika; źródłowych raportów GNSS jeszcze nie audytowano.
4. Zweryfikuj zerowe utożsamienia GPS z `Borowiec:0W` i `SzKostka:1.92`.
   Ten ostatni opisano przy kracie, około 50 cm od batinoxa. Równe nazwy/numeracja
   nie dowodzą identyczności punktów. Ustal też połączenie dziennika z III otworem.
5. Porównaj izolowane sieci przy jednym ustalonym otworze, potem wyrównanie
   przy obu fixach. Bieżąca sieć miesza Borowca z powtórzeniami Nowaka 6–7,
   7–8, 8–9 i 30–31. Oddziel korektę wynikającą z daty od empirycznego obrotu.
6. Włączenie do głównego WPJ następuje po świadomym wyborze wariantu i dowiązań;
   sama poprawność składni ani mniejszy błąd po dopasowaniu nie wystarczają.

## Weryfikacja pierwszej wersji wariantów (`b36d312`) — 2026-09-13

- `uv run pytest -q`: **196 testów zaliczonych**, w tym 40 dotyczących
  geometrii wariantów, kontraktu wejścia i zachowania źródła przez CLI.
- `ruff format --check src scripts tests` oraz `ruff check src scripts tests`:
  sukces, 67 plików zgodnych z formatem.
- `jktz-render-otwory --check`: sukces, GPS v1.0.2, 87 fixów.
- Wszystkie 12 etapów `jktz-validate`: sukces, w tym kompilacja bez ostrzeżeń
  i eksporty. Główny model nadal ma 18512 stacji i 18639 odcinków;
  roboczy `CZ_GL_R.SRV` pozostaje poza nim.
- Osobno porównano 16 wariantów z Survex; szczegóły, SHA-256 i tabela
  kontrolna są w `WARIANTY_ODCZYTU.md`. Maksymalna różnica składowej wynosi
  0,004899 m przy wyniku Survex zaokrąglonym do 0,01 m.
- Oryginalne materiały, aktywne SRV, WPJ i otwory nie zostały zmienione.
  Identyfikator commitu zawierającego ten etap odczytasz przez
  `git log -1 --format=%H -- src/jktz/czarna_variants.py`.
  Zdalne opublikowanie sprawdzaj przez porównanie z `git ls-remote origin
  refs/heads/codex/czarna-digitalizacja`; CI nie uruchamia się od tego pushu.

## Weryfikacja porównania Gemini — 2026-09-13

- **197 testów zaliczonych**, w tym 41 testów diagnostyki wariantów.
  Dodany przypadek sprawdza odmowę zastosowania nowej bazy do starego A39=25°.
- Ruff format i check: sukces, 67 plików. Kontrola otworów: sukces,
  87 fixów z GPS v1.0.2. Wszystkie 12 etapów `jktz-validate`: sukces.
- Potwierdzono bajtową zgodność obu kopii Gemini z plikami w Pobranych oraz
  ich SHA-256. Bazę `POROWNANIE.json` sprawdzono względem `git show b36d312`.
- Dokładnie jedna wartość D/A/V zmieniona: A39 25° → 75°. Wszystkie 16
  geometrii po aktualizacji ma dokładnie te same współrzędne co odpowiadające
  im wcześniejsze warianty, tylko inne identyfikatory i odniesienie delt.
- Ponownie skompilowano wszystkie 16 wariantów w Survex 1.4.22 bez ostrzeżeń.
  Zgodność 48/48 składowych, maksymalna różnica 0,004899 m przy zaokrągleniu
  `dump3d` do 0,01 m. SHA wejścia jest w raporcie wariantów i JSON.
- Niezależny przegląd całego etapu nie wykazał usterek P1/P2. Nie był kolejnym
  pełnym odczytem wszystkich skanów ani oceną dokładności terenowej.
- Etap obejmuje zmianę SRV, odczyty Gemini, raport porównania, odświeżone
  warianty i dokumentację. Jego commit wskazuje
  `git log -1 --format=%H -- Poligony/D_Koscieliska/Organy/Czarna/POROWNANIE_GEMINI.md`;
  stan zdalny sprawdzaj poleceniem `git ls-remote` podanym wyżej.

## Weryfikacja autorstwa i porównania z Borowcem — 2026-09-13/14

- Niezależne obliczenia potwierdziły długości, kierunki, korelacje kształtu,
  przykłady par odcinków i bilanse wysokości opisane w `POROWNANIE_BOROWIEC.md`.
  Wykres sprawdzono wizualnie; współrzędne i SHA-256 źródeł są w JSON.
- Drugi przegląd nie wykazał istotnych usterek obliczeń. Poprawiono dwie
  nieścisłości opisu: autorstwo dotyczy dziennika, a uwagi o Studni Imieninowej
  są na fotografii i w raporcie Gemini, nie przy tych wierszach SRV.
- Potwierdzono semantycznie niezmienione **78 D/A/V** względem `f883248`.
  Wynik JSON 16 wariantów zmienił tylko SHA wejścia. Ponowne kompilacje
  Survex dały zgodność 48/48 składowych, maksymalna różnica 0,004899 m.
- **197 testów zaliczonych**, Ruff format i check: sukces, 67 plików.
  Kontrola 87 fixów GPS v1.0.2 oraz wszystkie 12 etapów `jktz-validate`:
  sukces. Główna sieć nadal ma 18512 stacji i 18639 odcinków.
- `_RAW` Czarnej, aktywny Borowiec, WPJ i otwory są niezmienione względem
  początku gałęzi. Nowy SRV pozostaje poza WPJ; nie dodano fizycznych dowiązań.
- Commit tego etapu odczytasz poleceniem
  `git log -1 --format=%H -- Poligony/D_Koscieliska/Organy/Czarna/POROWNANIE_BOROWIEC.md`.
  Publikację sprawdzaj przez porównanie ze zdalną gałęzią. Sam push tej gałęzi
  nie uruchamia CI; lokalnej walidacji nie przedstawiaj jako wyniku CI.

## Kontrola Opusa i korekta komentarza — 2026-09-16

- Pełne zestawienie 234 D/A/V oraz 156 Lh/Δh z modelem, oboma Gemini
  i zamrożonym `fc33499` zapisano w `ODCZYTY_MODELI/POROWNANIE_OPUS.json`.
  Kopia wyniku jest identyczna z Downloads; pochodzenie i SHA w indeksie.
- Nowy czytelnik odczytał sporne fragmenty przed poznaniem SRV i modeli.
  Przy D59→60 ujawniono następnie konflikt i porównano grafię; zachowano
  17,60 m jako preferencję. Dwóch czytelników potwierdziło Lh20→21=10,73.
  Nie zmieniono D/A/V; korekta dotyczy komentarza i daty aktualizacji.
- Potwierdzono identyczność 78 pomiarów i dyrektyw geometrii względem
  `fc33499`. Odświeżone JSONy wariantów i porównania z Borowcem zmieniły
  tylko SHA SRV; wyniki liczbowe i wykresy pozostają identyczne.
- Osobna kompilacja roboczego SRV: 79 stacji, 78 odcinków, 1122,50 m,
  bez ostrzeżeń. Nie powtarzano 16 kompilacji identycznych wariantów.
- **197 testów**, Ruff format/check i pełne **12/12 etapów `jktz-validate`**:
  sukces. Kontrola źródła GPS v1.0.2 potwierdziła 87 fixów. Pierwsza próba
  bramki zatrzymała się na DNS sandboxu; ponowienie z dostępem do sieci
  zakończyło się sukcesem. Nie był to błąd danych.
- `_RAW`, pozostałe SRV, WPJ i otwory są niezmienione. Praca nadal dotyczy
  izolowanego ciągu roboczego; nie ustalono daty ani fizycznych dowiązań.
- Niezależny przegląd całego etapu nie wykazał istotnych usterek. Osobny
  parser potwierdził wszystkie liczniki, alternatywy, numery linii i SHA;
  czytelnik skanów potwierdził wierny opis jego odczytów i niepewności.
- Commit etapu odczytasz przez
  `git log -1 --format=%H -- Poligony/D_Koscieliska/Organy/Czarna/POROWNANIE_OPUS.md`.
  Publikację porównaj ze zdalną gałęzią przez `git ls-remote`; lokalnej bramki
  nie przedstawiaj jako CI. Sam push tej gałęzi nie uruchamia workflow.

## Odtwarzalne narzędzia i aktualizacje

Polecenia uruchamiaj z katalogu głównego repo. Po aktualizacji gałęzi używaj
CLI z `pyproject.toml`; stare skrypty usunięto w commicie `446edc4`.

```sh
uv sync --locked
uv run jktz-czarna-warianty --output Poligony/D_Koscieliska/Organy/Czarna/WARIANTY_ODCZYTU.json
uv run pytest -q tests/test_czarna_variants.py
uv run jktz-survex-stats Poligony/D_Koscieliska/Organy/Czarna/CZ_GL_R.SRV
uv run jktz-srv-metadata hash-raw Poligony/D_Koscieliska/Organy/Czarna
uv run jktz-srv-metadata srv-update --help
uv run jktz-render-otwory --check
uv run jktz-validate
```

Pełny gate wymaga Survex, GDAL i dostępu do źródła GPS; nie ukrywaj błędów
środowiska ani nie nazywaj częściowej kompilacji pełną walidacją. Metadane
zmieniaj CLI, a materiały `_RAW` zachowuj bez zmian. Po etapie wpisz tutaj:
co zmieniono, źródło decyzji, wyniki sprawdzeń, SHA publikacji i następny krok.
Nowa niepewność pozostaje jawna. Dokument nie oznacza zaplanowanej automatycznej pracy.
