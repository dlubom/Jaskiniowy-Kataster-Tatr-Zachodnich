# PocketTopo: konwersja pomiarów i ekstrakcja szkiców

Stan: **2026-09-25 — P01 zakończone, następny etap P02 (parser i model)**.
Branch roboczy: `codex/pockettopo-convert`, początek: `a6c235c898eed57902a2d6ba18db60917e01faee`.

## Wznowienie po wyczyszczeniu kontekstu

1. Przeczytaj `AGENTS.md`, ten PRD i sprawdź `git status` oraz bieżący branch.
2. **Następne zadanie: P02 — ścisły parser i model.** Nie powtarzaj researchu
   narzędzi ani tworzenia wzorców P01.
3. Przeczytaj [format v3](FORMAT_V3.md), [wyniki P01](evidence/p01/README.md)
   i [oczekiwania dla każdego rekordu](evidence/p01/EXPECTATIONS.md).
   Wzorce `cases/*/expected.json` są niezależne od przyszłego parsera.
   Dostęp do aplikacji opisuje [instrukcja macOS](POCKETTOPO_MACOS.md).
4. Po etapie aktualizuj tabelę postępu i dowody walidacji w repozytorium,
   aby kolejna sesja nie zależała od historii rozmowy ani plików w `/tmp`.

Polecenie do wznowienia:

> Kontynuuj na `codex/pockettopo-convert` według `doc/pockettopo/PRD.md`.
> Wykonaj P02: ścisły parser i model na podstawie FORMAT_V3.md oraz wzorców P01.
> Zachowaj surowe wartości i niezależne oryginały, sprawdź błędy wejścia,
> zapisz wyniki walidacji oraz postęp w PRD. Zakończ po P02.

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
Proponowane komendy `uv run jktz-pockettopo inspect ...` i `convert ...`
**jeszcze nie istnieją**. Nie budujemy łańcucha `.top → zaokrąglony SRV → średnie`.

| Etap | Wynik i warunek zakończenia | Stan |
| --- | --- | --- |
| P00 Research i dostęp | Źródła, decyzje, natywny eksport Shadow i instrukcja wznowienia zapisane w repo | Gotowe |
| P01 Wzorce aplikacji | 6 małych `.top` (2 GUI, 4 natywny model/API), TXT/DXF, oczekiwania każdego pola, końcowe 4 zera i Auto; resvg sprawdzony na macOS/Linux | Gotowe — [dowody](evidence/p01/README.md) |
| P02 Parser i model | Ścisły odczyt wszystkich struktur; testy błędów, zakresów i niezależnych wzorców | Następny |
| P03 Średnie i raport | Grupy potwierdzonych powtórzeń, matematyka, ślad każdego rekordu i testy graniczne | Do zrobienia |
| P04 SRV/SVX | Zachowanie semantyki, kompilacja obu formatów i porównanie geometrii; sprawdzenie w Walls | Do zrobienia |
| P05 SVG/PNG | Oba widoki i warianty, XSection, warstwy, renderer bez GUI; kontrola punktów i obrazów | Do zrobienia |
| P06 CLI i skill | Atomowy pakiet wynikowy, instrukcje skilla, niezależna próba użycia i pełna walidacja | Do zrobienia |

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
DXF pozostaje do wykonania. Szczegóły i pliki: [dowód Shadow](evidence/shadow/README.md).

P01 rozstrzygnęło zakończenie: PocketTopo 1.372 zapisuje Int32 `0` po drugim
rysunku, lecz jego czytnik ignoruje cały sufiks. Kontrakt P02 dopuszcza dokładnie
EOF po schemacie albo dokładnie cztery zera; pozostałe sufiksy są błędem.
[Dowód natywnego API](evidence/p01/NATIVE_API.md) opisuje również sentinel Auto.
[Renderer resvg 0.48.1](evidence/p01/renderer/README.md) dał identyczne PNG na
macOS i Linux; integracja w konwerterze/CI pozostaje P05/P06.

Do rozstrzygnięcia w etapach: podkład w pętlach/rozgałęzieniach, ogólna projekcja
XSection z domiarami, progi niejednoznaczności średniej, fonty/paleta rysunków
oraz format profilu metadanych dla aktywnego JKTZ. Natywny DXF uśrednia własnym
algorytmem i nie zastępuje kontraktu średnich P03. Pełny korpus 258 plików
oraz audyt współrzędnych Shadow pozostają do wykonania w dalszych etapach.
Nie deklarować pełnej zgodności przed spełnieniem kryteriów odbioru.
