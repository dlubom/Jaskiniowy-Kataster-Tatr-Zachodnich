# Czarna — kontrola odczytu Claude Opus 5

Data porównania: 2026-09-16. Punkt odniesienia: `fc33499bc127d784e8e0638ad3e45af9a3d85834`.
Porównano [wynik przekazany przez użytkownika](ODCZYTY_MODELI/claude_opus_5.md)
z roboczym `CZ_GL_R.SRV`, oboma wynikami Gemini i dotychczasową dokumentacją.
„Claude Opus 5” jest oznaczeniem podanym przez użytkownika; nie otrzymano
logu sesji, identyfikatora modelu ani faktycznie użytego promptu.

## Co wnosi ten wynik

**Nie znaleziono podstaw do zmiany żadnego D/A/V ani rozstrzygnięcia czterech
dotychczasowych niepewności.** Wynik daje nowe propozycje odczytu cyfr,
ale ich kontrola na fotografiach nie uzasadnia przyjęcia ich do geometrii.
Zachowuje komplet odcinków i poprawne pary stanowisk; nie zawiera nowych
pomiarów, daty, instrumentu ani fizycznych punktów dowiązania.

**Przydatny rezultat kontroli to korekta naszego pomocniczego odczytu
Lh20→21: 10,23 → 10,73 m.** Taką wartość podawały już oba Gemini, więc
nie jest to informacja występująca po raz pierwszy u Opusa. Dopiero ten etap
potwierdził ją ponownie na fotografii i usunął błędny przykład „arytmetyki
źródła” z raportu. Zmieniono komentarz, bez wpływu na pomiary i geometrię.

Dla czterech wcześniej spornych pól:

- **29→30 D=13,80 m**: zgodne z obecną preferencją i Flashem; kolejny
  zgodny odczyt, bez nowej informacji pozwalającej usunąć alternatywę 13,60.
- **39→40 A=35°**: nowa propozycja. Ponowne oględziny nie dają podstaw
  do zastąpienia nią preferowanego 75° ani dodania jej do analizy wariantów.
  Dotychczasowa alternatywa 25° pozostaje jawna.
- **49→50 A=88°**: wariant już uwzględniony w analizie 16 kombinacji,
  nie nowe rozstrzygnięcie. Nowy czytelnik skanu również wskazał 88°,
  co wzmacnia potrzebę zachowania tej alternatywy. Główny czytelnik nadal
  widzi podstawy do 68°; nie zmieniono preferencji roboczej.
- **71→72 V=+1°**: wariant również znany; samo wskazanie Opusa nie
  rozstrzyga znaku. Pozostaje robocze −1° i jawna alternatywa +1°.

## Pokrycie i metoda

Wynik ma **115 wierszy, 78 unikalnych odcinków i 37 powtórzeń** z drugiej
fotografii tej samej rozkładówki. Pierwsze D/A/V powtórzonych wierszy są
zgodne; nie są to 37 dodatkowych obserwacji ani niezależnych pomiarów.
Nazwy plików w nagłówkach Opusa odpowiadają zdjęciom `123052`, `123533`
i `123630`, choć ich zapis różni się od oryginalnych nazw w `_RAW/02`.

Porównano wszystkie 234 pola D/A/V na 78 unikalnych parach. Pierwsza liczba
w komórce jest odczytem głównym, liczby po `[?]` zachowano jako alternatywy.
Kreskę azymutu pionu 57→58 znormalizowano do braku wartości. Nie przenoszono
alternatyw z kolumny Δh do pola V: np. Opus ma dla 38→39 V=+62°, a −15,44
wyłącznie jako alternatywę w kolumnie Δh.

| Wynik | Flash | Pro | Opus |
| --- | ---: | ---: | ---: |
| Oczekiwane pary punktów | 78/78 | 77/78 | 78/78 |
| Różnice pierwszych D/A/V względem `fc33499` | 2 | 10 | 21 |
| Dodatkowa błędna para | — | 18→20 zamiast 19→20 | — |

U Opusa to **21 pól na 20 odcinkach: 8 D, 6 A i 7 V**. Trzy komórki
zawierają także wartość SRV jako alternatywę; po ich uwzględnieniu pozostaje
18 konfliktów na 17 odcinkach. Są to liczniki rozbieżności, nie liczba
udowodnionych błędów ani ogólny ranking modeli. Historyczne 3/11 różnic Gemini
dotyczą bazy `b36d312`, sprzed zmiany A39 z 25° na 75°.

Wobec SRV, czterech zapisanych wariantów i obu Gemini **17 pierwszych wartości
na 16 odcinkach jest nowych**. Nowa jest też alternatywa V65→66=−25°.
„Nowe” oznacza tu jedynie wcześniej niewystępującą propozycję transkrypcji.
Pełne różnice, literalne komórki, numery linii i SHA-256 wejść zapisano
w [POROWNANIE_OPUS.json](ODCZYTY_MODELI/POROWNANIE_OPUS.json).

## Wszystkie różnice D/A/V i kontrola fotografii

S1 oznacza `123052` i pomocnicze `123533`; S2 oznacza `123630`.
Kolumna kontroli opisuje odczyt fotografii, bez dobierania cyfr do rachunków,
Borowca, GNSS lub domknięcia. Nierozstrzygnięte odczyty pozostają robocze.

| Odcinek / pole | SRV | Opus | Kontrola źródła i decyzja |
| --- | ---: | --- | --- |
| 7→8 A | 71° | 74° | S1: końcowa cyfra 1; zachowano 71°. |
| 24→25 V | +43° | +13° | S2: widoczna 4; zachowano +43°. |
| 28→29 V | +45° | −45° | S2: widoczny plus; Opus odwraca znak. |
| 36→37 V | +3° | +5° [? +3°] | S2: +3°; sam Opus zachowuje tę alternatywę. |
| 37→38 V | +24° | +29° [? +24°] | S2: +24°; sam Opus zachowuje tę alternatywę. |
| 38→39 D | 17,50 m | 17,10 m | S2: 17,50; brak podstaw do 17,10. |
| 38→39 V | −62° | +62° | S2: widoczny minus; Opus odwraca znak. |
| 39→40 A | 75° | 35° | S2: rozmyty dolny brzeg; zachowano preferencję 75° i wcześniejszą niepewność. |
| 42→43 A | 95° | 91° | S2: druga cyfra ma grafię 5; zachowano 95°. |
| 44→45 D | 6,70 m | 6,20 m | S2: 6,70; porównanie grafii 7 z sąsiednimi liczbami. |
| 48→49 A | 74° | 24° | S2: 74; pierwsza cyfra jak w innych zapisach 7. |
| 49→50 A | 68° | 88° | S2: nadal robocze 68°; 88° jest już znaną alternatywą. |
| 53→54 D | 19,30 m | 15,30 m [?] | S2: 19,30; widoczny zapis 9, bez podstaw do zmiany. |
| 55→56 D | 5,90 m | 5,80 m | S2: 5,90; zachowano dotychczasowy odczyt. |
| 59→60 D | 17,60 m | 12,60 m | S2: po porównaniu glifów preferowane 17,60; 12,60 nie wykluczono całkowicie. |
| 60→61 A | 47° | 43° | S1: czytelne 47°. |
| 62→63 D | 3,50 m | 3,10 m | S1: 3,50; 3,10 występowało już jako alternatywa Flasha. |
| 71→72 V | −1° | +1° | S1: znak pozostaje niepewny; +1° jest już znanym wariantem. |
| 73→74 D | 17,00 m | 12,00 m | S1: 17,00; 12,00 występowało już u Pro. |
| 74→75 D | 17,00 m | 12,00 m [? 17,00 m] | S1: preferowane 17,00; wartość również w alternatywie Opusa. |
| a→b V | −37° | −32° | S1: preferowane −37; −32 to słabszy odczyt, bez podstaw do korekty. |

Nowa alternatywa **V65→66=−25°** nie znajduje wsparcia w grafii: zapis
przemawia za −75°. Nie wyjaśnia ona zatem różnicy profilu Kujat–Borowiec
przy Studni Imieninowej. Dwa odwrócone przez Opusa znaki na S2 pokazują,
dlaczego nie należy bez kontroli importować całej transkrypcji.

**D59→60 wymaga ostrożnego opisu:** nowy czytelnik początkowo wybrał
12,60 m, a dopiero po porównaniu grafii 7 w `17,50` (47→48) i `270`
(58→59) z cyfrą 2 w `12,20` (39→40) wskazał 17,60 m jako bardziej
prawdopodobne. Brakuje wyraźnej dolnej podstawy typowej dla 2. Nie stanowi
to pewnego wykluczenia 12,60. Nie przyjęto nowego wariantu ani nie uznano
naszego D=17,60 za udowodniony błąd. Ta słabsza hipoteza oraz V a→b=−32
są zachowane w niniejszym raporcie; nie należą do dotychczasowych 16 wariantów.

## Kolumny pomocnicze i dopiski

Osobno porównano wszystkie Lh/Δh, bez włączania ich do powyższych liczników.
Na **156 unikalnych polach** znaleziono **27 różnic na 24 odcinkach**
(10 Lh i 17 Δh); trzy zawierają wartość SRV jako alternatywę. Szczegóły
w sekcji `auxiliary_comparison` wspólnego JSON odnoszą się do bazy sprzed
korekty komentarza. Nie wliczano sum ani dopisków na marginesach.

Ponownie sprawdzono cztery miejsca, w których wszystkie trzy modele
proponowały ten sam odczyt różny od naszego komentarza:

| Pole | Dotychczasowy komentarz | Wszystkie trzy modele | Oględziny i decyzja |
| --- | ---: | ---: | --- |
| Lh20→21 | 10,23 | 10,73 | Dwóch czytelników odczytało 10,73 z fotografii; poprawiono komentarz i raport. |
| Δh27→28 | +11,68 | +11,63 | Fotografia przemawia za +11,68; zachowano komentarz. |
| Δh58→59 | −6,44 | −6,43 | Końcowa cyfra przy linii tabeli jest niepewna; nowy czytelnik rozważał 3/8. Brak pewnej podstawy do korekty, zachowano dotychczasowy komentarz jako roboczy. |
| Δh a→b | −3,25 | −3,05 | Czytelne −3,25; zgodna propozycja wszystkich modeli nie odpowiada źródłu. |

W Lh20→21 porównano grafię skanu; wyniku nie wyprowadzono z D/V.
Dopiero dodatkowo sprawdzono, że `12,40 cos(30°) = 10,739 m` nie uzasadnia
wcześniejszej etykiety dużego błędu rachunkowego. Inne niespójności dziennika,
np. Δh2→3=−4,97 przy D=5,20 i V=−35°, pozostają. Pozostałe różnice Lh/Δh
porównano mechanicznie; nie jest to pełny nowy odczyt każdej cyfry źródła.

Opus nie odczytuje wiarygodniej nazw wcześniej sprawdzonych na skanach:
podaje m.in. „Partie Techniki”, „Studnia Jasiu” i „Koniec Kolorowego”.
Fotografie nadal wspierają odczyty **Partie Tehuby, Studnia Imieninowa
i Koniec Kolorado**. Nowe domysły dotyczące nazwiska/nazwy przy punkcie 26
i komina przy punkcie 38 nie są ustaleniem tożsamości stanowisk ani autora.
Autorstwo Ryszarda Kujata pozostaje ustalone przez użytkownika.

## Zakres i dalszy krok

Zarchiwizowano wynik modelu bajt w bajt poza `_RAW`, obok obu Gemini.
Kontrola obejmuje mechaniczne zestawienie pełnych tabel i ponowne oględziny
spornych fragmentów; nie jest pełną nową transkrypcją wszystkich dopisków
ani oceną jakości pomiaru terenowego. Nowy wynik nie rozwiązuje różnicy
poziomów przy Studni Imieninowej, datowania ani dowiązania do otworów.

Kolejny krok pozostaje źródłowy: czytelniejszy zapis czterech spornych pól
oraz pomocnicza kontrola D59→60, V a→b i Δh58→59 przy lepszym materiale,
następnie identyfikacja przebiegu i fizycznych stanowisk w rejonie Studni
Imieninowej. Plan dalszej pracy prowadzi [STAN_PRAC.md](STAN_PRAC.md).

## Weryfikacja etapu

- Kopia Opusa jest bajtowo identyczna z plikiem w Downloads. JSON porównania
  ma zamrożoną bazę `fc33499`, sprzed korekty Lh; nie jest przeliczany na
  każdy kolejny SRV. Wszystkie cztery SHA-256 wejść sprawdzono z plikami.
- Potwierdzono identyczne **78 D/A/V i dyrektywy geometrii** względem tej
  bazy. Jedyna korekta liczbowa to pomocnicze Lh20→21; zmieniono także
  komentarz obok i `UPDATE_DATE`, narzędziem `jktz-srv-metadata srv-update`.
- Ponownie wygenerowano JSON 16 wariantów: zmienił wyłącznie SHA wejścia.
  Tak samo odświeżono SHA Kujata w JSON porównania z Borowcem; współrzędne,
  miary porównania i wykresy pozostały identyczne. Nie ponawiano 16 kompilacji.
- Osobny `cavern` 1.4.22 dla roboczego SRV: **79 stacji, 78 odcinków,
  1122,50 m, bez ostrzeżeń**. Automatyczny początek 0 jest oczekiwany.
- **197 testów**, Ruff check i format: sukces. Pełne **12/12 etapów
  `jktz-validate`**: sukces, w tym 87 fixów z GPS v1.0.2 i eksporty.
  Pierwsza próba zatrzymała się na DNS w sandboxie; ponowienie z dostępem
  do publicznego źródła GPS zakończyło pełną kontrolę.
- `_RAW`, aktywne pomiary pozostałych sekcji, WPJ i otwory niezmienione.
  Roboczy SRV nadal pozostaje poza głównym WPJ. Wyniki powyżej są lokalną
  walidacją, nie wynikiem CI.
- Niezależny przegląd całego diffu i nowy parser potwierdziły liczniki,
  różnice, alternatywy, linie oraz SHA; bez istotnych uwag. Czytelnik zdjęć
  potwierdził, że raport wiernie zachowuje poziom pewności jego odczytów.
