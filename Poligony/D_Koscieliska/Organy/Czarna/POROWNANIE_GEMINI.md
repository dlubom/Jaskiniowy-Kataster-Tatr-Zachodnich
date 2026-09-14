# Czarna — kontrola odczytów Gemini i nazw partii

Data: 2026-09-13. Porównano dwa wyniki przekazane przez użytkownika:
[Flash](ODCZYTY_MODELI/gemini_flash_3.8.md) i [Pro](ODCZYTY_MODELI/gemini_pro.md).
Kopie są zachowane bez zmian; pochodzenie, SHA-256 i metoda porównania są
w [indeksie odczytów](ODCZYTY_MODELI/README.md).

## Co te wyniki wnoszą

**Flash jest bardziej przydatny w tej konkretnej parze wyników:** ma mniej
rozbieżności w D/A/V, zachowuje właściwą numerację oraz częściej zaznacza
alternatywy. Nie jest to ogólny ranking modeli ani pomiar ich dokładności.
Podstawą rozstrzygnięcia pozostaje fotografia, nie zgodność z naszym SRV.

Najważniejszy nowy wynik to wspólne wskazanie **A=75° dla 39→40**.
Ponowny odczyt tego fragmentu przez dodatkowego czytelnika, bez znajomości
SRV ani Gemini, również dał 75°. Na obrazie pierwsza cyfra ma grafię
zbliżoną do siódemki w azymucie 75° w poprzednim wierszu. To uzasadnia
zmianę preferowanej wartości roboczej z 25° na 75°. Dolny brzeg fotografii
pozostaje rozmyty: zachowano 25° jako alternatywę i oznaczenie `DO_WERYFIKACJI`.
Nie wykorzystano GNSS ani dopasowania geometrii do wyboru cyfry.

Pozostałe D/A/V pozostawiono bez zmian. Odczyty Flash i dodatkowego czytelnika
wzmacniają 29→30 D=13,80 m; oba Gemini i odczyt obu zdjęć wzmacniają
71→72 V=−1°. Dla 49→50 Pro podaje 68°, a Flash 58°; ponowne oględziny
przemawiają za 68°, lecz pierwotną alternatywę 88° nadal zachowano w analizie.
Zbieżność odczytów modeli nie jest równoznaczna z niezależnym potwierdzeniem
pomiaru terenowego ani podstawą do usunięcia wszystkich niepewności.

## Pokrycie i wszystkie różnice głównych wartości

Punkt odniesienia tej tabeli: `CZ_GL_R.SRV` z `b36d312` (przed zmianą A39).
Zestawiono wszystkie pola D/A/V, a nie tylko cztery wcześniej sporne.
Nie wliczano kolumn obliczeniowych Lh/Δh ani uwag do poniższych liczników.

| Właściwość | Flash | Pro |
| --- | ---: | ---: |
| Wiersze pomiarów, z powtórnymi zdjęciami | 115 | 115 |
| Unikalne pary punktów | 78 | 78 |
| Pary powtórzone na drugim zdjęciu | 37 | 37 |
| Poprawne pary z oczekiwanego zestawu | 78/78 | 77/78 |
| Różnice pierwszych wartości D/A/V na wspólnych parach | 3 | 11 |

Flash w jednej z trzech różnic podaje także wartość zgodną z bazą jako
możliwą korektę. Jeśli uwzględnić tę alternatywę, zostają dwa konflikty
wartości. Liczników tych nie należy przedstawiać jako liczby błędów:
wspólne 75° modeli jest przykładem odczytu, który pomógł poprawić nasz zapis.

| Pole / odcinek | Baza `b36d312` | Flash | Pro | Kontrola fotografii i decyzja |
| --- | ---: | --- | --- | --- |
| A 1→2 | 93° | 93° | 83° | Obie fotografie potwierdzają 93; zachowano. |
| Para 19→20 | 19→20 | 19→20 | **18→20** | Na skanie jest 19→20. Pro zmienia topologię. |
| A 20→21 | 115° | 115° | 145° | 115, zapis pogrubiony; środkowa cyfra nie ma poprzeczki 4. |
| D 24→25 | 11,10 m | **21,10 [? skorygowane na 11,10]** | 21,10 | Odczyt fotografii: 11,10. Nie ma dowodu, że 21,10 było wcześniejszą wartością. |
| D 28→29 | 20,50 m | 20,50 | 20,40 | Na skanie 20,50, podobne 50 jak dwa wiersze niżej. |
| D 29→30 | 13,80 m | 13,80 | 13,30 | Preferowane 13,80; nadal analiza alternatywy 13,60. |
| D 32→33 | 10,50 m | 10,50 | 10,30 | Preferowane 10,50; grafia 5 podobna do sąsiednich wierszy. |
| A 39→40 | 25° | 75° | 75° | Nowa preferencja robocza **75°**; 25° zachowane jako niepewna alternatywa. |
| V 43→44 | +5° | +5° | +15° | Na obrazie +5; Pro dodaje cyfrę 1. |
| V 46→47 | −19° | −19° | −15° | Na obrazie −19; zachowano. |
| A 49→50 | 68° | 58° | 68° | Preferowane 68; 58 Flasha nie znajduje wsparcia w grafii pierwszej cyfry. |
| D 62→63 | 3,50 m | 3,50 [? 3,10] | 3,30 | Wyraźniejsze zdjęcie `123052` pokazuje 3,50. |
| D 73→74 | 17,00 m | 17,00 | 12,00 | Na `123052` widać ukośną kreskę 7; zachowano 17,00. |

Flash podaje także alternatywę A=118° dla 3→4 i V=−71° dla 65→66.
Ponowne oględziny wspierają odpowiednio 48° i −75°; sam wpis modelu nie
uzasadnia dodania kolejnych wariantów do diagnostyki. Oba modele zachowały
odczyty 55→56 D=5,90 m, 59→60 D=17,60 m, 74→75 D=17,00 m oraz pion
57→58. Kreski azymutu pionu są tylko różnymi reprezentacjami braku wartości.

## Kolumny obliczeniowe i uwagi — przykłady problemów

- Pro w 24→25 podaje Lh=15,44 i Δh=14,39, podczas gdy widać 8,11 i 7,56.
  Wartości Pro odpowiadają w przybliżeniu przeliczeniu jego błędnego D=21,10.
  To wskazuje na możliwe uzupełnienie rachunkiem; z samego wyniku nie można
  ustalić, w jaki sposób model je wytworzył.
- Pro w 43→44 zastępuje widoczne Lh=20,70 i Δh=1,75 przez około 20,00 i 5,35,
  spójne z jego +15°. Pokazuje to, dlaczego nie należy odtwarzać odczytu
  instrumentu z pomocniczej arytmetyki.
- Pro przenosi uwagę „Studnia Duszka…” do 2→3. Notatki o Studni Imieninowej
  są na drugiej stronie, w rejonie 64–66. Flash też błędnie rozwija tę nazwę
  jako „Studnia Dwóch / Ducha”. Z fotografii odczytano „Studnia Imieninowa”.
- „Koniec Kolorowego Oka” Flasha i „Koniec Kolor. salki” Pro nie odpowiadają
  dopiskowi. Ponowny odczyt obu zdjęć: „Koniec Kolora- / do.”, czyli Kolorado.
- Flash odczytuje „Partie Tehuby”; Pro podaje „Partie Tetydy”. Wcześniejsze
  nasze „Tehmy” także było błędne. Poprawiono nazwę w komentarzach SRV.

Nie wykonano tu pełnej ponownej transkrypcji wszystkich Lh/Δh i dopisków.
Przykłady wykazują problemy, ale nie są kompletnym rankingiem jakości uwag.
Kopie modeli pozostają niezmienione i nie są importowane bezpośrednio do Walls.

## Nazwy, topologia i historia pomiarów

PIG używa nazwy **Partie Tehuby** i umieszcza wejście w Sali Ewy i Hanki.
Colorado jest odnogą Sali Św. Bernarda; droga do północnego otworu prowadzi
przez Próg Latających Want. Opis potwierdza, że koniec Colorado nie jest
punktem III otworu. [Opis PIG](https://jaskiniepolski.pgi.gov.pl/Details/Information/1445).

Jakub Nowak zestawia historyczne „Techuba” z późniejszym „Partie Tehuby”,
a także warianty Komin Wariatów / Komin Wiatrów oraz Komin Smoluchowskiego /
Studnia Smoluchowskiego. „Techuba” nie jest więc zwykłą literówką.
Źródło: „Jaskinie” 69 (2012), s. 29,
[lokalny PDF](_RAW/03/Czarna%20-%20Jaskinie%2069.pdf), pierwsza strona PDF;
[wydanie PZA](https://nowe.pza.org.pl/jaskinie/kwartalnik/jaskinie__69_2012.pdf).

Wybrane informacje z historii dokumentacji według PIG:

| Pomiar | Autorzy / datowanie |
| --- | --- |
| Główny otwór → Colorado | Naukowe Koło Geodetów AGH, kierownik Władysław Borowiec, 1972–1973 |
| Ciągi szkieletowe nawiązane do Borowca | Ryszard Kujat, 1975; część ciągów o nieznanej dacie |

Źródło: [PIG, „Historia dokumentacji”](https://jaskiniepolski.pgi.gov.pl/Details/Information/1445).
Ta historia nie datuje automatycznie dziennika 0–76 ani jego odgałęzienia
6–a–b. Dwa odcinki tego odgałęzienia nie są dokumentacją całych Partii Tehuby.

**Autorem dziennika odczytanego do `CZ_GL_R.SRV` jest Ryszard Kujat.**
Użytkownik potwierdził to 2026-09-13, wskazując nazwę fotografii
`20220325_123052 ciąg gł Czarna 1_Kujat.jpg`. To źródło przypisania autora
w metadanych `TEAM`; wcześniejsze przypuszczenie o innym zespole wycofano.
Data i instrument pozostają nieustalone. Autorstwo Kujata nie oznacza,
że ten konkretny dziennik pochodzi z 1975 r. lub z roku listu.
Następny krok to ustalenie daty, orientacji i fizycznych punktów nawiązania,
zwłaszcza w rejonie Sali Św. Bernarda i Studni Imieninowej.

## Wpływ na pliki i dalszą analizę

- Zachowano obie transkrypcje oraz porównanie do zamrożonego `b36d312`.
- W roboczym SRV zmieniono tylko jedną wartość D/A/V: A39 z 25° na 75°.
  Poprawiono nazwę Tehuby, komentarz niepewności i datę aktualizacji.
- Cztery pola nadal pozostają oznaczone do weryfikacji. Diagnostyka zachowuje
  te same 16 kombinacji fizycznych, ale bit dotyczący A39 zmienił znaczenie:
  `0` oznacza teraz 75°, a `1` — 25°. Nie porównuj samych identyfikatorów
  wariantów pomiędzy wersjami; sprawdzaj parametry i SHA-256.
- Nowe wyniki i niezależną kontrolę opisuje [analiza wariantów](WARIANTY_ODCZYTU.md).
  Zmiana preferencji nie zmienia największej odległości między wariantami
  (12,12 m) ani nie dowodzi lepszej jakości trawersu terenowego.
- Oryginały `_RAW`, aktywne pomiary, WPJ i współrzędne otworów pozostają bez zmian.

Walidacja: **197 testów**, Ruff, kontrola 87 fixów GPS v1.0.2 i wszystkie
12 etapów `jktz-validate` — sukces. Osobne 16 kompilacji Survex potwierdziło
wszystkie współrzędne w granicach zaokrąglenia do 0,01 m. Niezależny przegląd
całego etapu nie wykazał usterek P1/P2; szczegóły zapisano w `STAN_PRAC.md`.
