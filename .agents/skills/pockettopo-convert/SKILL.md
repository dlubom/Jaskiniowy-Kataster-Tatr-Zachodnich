---
name: pockettopo-convert
description: Inspect or convert PocketTopo v3 .top survey files into an audited Walls SRV, Survex SVX, and layered plan/extended-section SVG and PNG package. Use for source-preserving PocketTopo conversion, not automatic cave registration.
---

Konwertuj pojedynczy `.top` v3 przez `uv run jktz-pockettopo` z katalogu
głównego repozytorium. Używaj istniejącego CLI; helpery badawcze PocketTopo,
Wine i GUI nie są silnikiem konwersji. Zachowaj wejście i materiały `_RAW`.

Przeczytaj [instrukcję CLI](../../../doc/pockettopo/CLI.md), aby sprawdzić
zależności, opcje, format decyzji i pola raportu. Dla problemów formatu sięgnij
do [kontraktu v3](../../../doc/pockettopo/FORMAT_V3.md); dla położenia szkiców
do [polityki projekcji](../../../doc/pockettopo/PROJECTION.md).

## Odczyt i decyzje

```sh
uv run jktz-pockettopo inspect /path/to/source.top
```

Odczytaj oba pola JSON: `source` i `report`. `inspect` nie zapisuje pakietu
ani nie uruchamia renderera/kompilatora. Jego kod `0` oznacza poprawny odczyt
i przygotowanie raportu, także przy wstrzymanych pomiarach. Sprawdź
`completeness`, `record_trace`, `groups`, `trips` i `limitations`.

- Zachowuj niepotwierdzone odczyty osobno. Ta sama para nazw, podobne liczby,
  geometria lub domknięcie nie dowodzą powtórzenia. Potwierdzaj tylko kolejne
  odczyty tej samej nazwanej pary w znanym tripie, na podstawie niezależnego
  źródła. Nie usuwaj automatycznie wartości odstających.
- Daty tripów są datami urządzenia o niepotwierdzonej wiarygodności; palmtop
  mógł zresetować zegar. Nie używaj ich ani dat z nazw plików do wyliczenia
  deklinacji. Odtworzenie zapisanej korekty, również zera, nie potwierdza jej
  historycznej poprawności. `Auto` i brak tripu pozostają nierozstrzygnięte
  bez uzasadnionej korekty.
- Nie zakładaj CRS dla referencji E/N/Z, tożsamości stacji na podstawie
  geometrii ani położenia rozłącznych części. `side` jest przekrojem
  rozwiniętym, a `flipped` jego kierunkiem lewo/prawo.

Jeżeli są udokumentowane decyzje, zapisz osobny JSON zgodny z
[formatem decyzji](../../../doc/pockettopo/CLI.md#jawne-decyzje). Wymagane
`source_sha256` wiąże go z dokładnymi bajtami wejścia. Opcjonalne tablice
`confirmations`, `exclusions`, `corrections` wymagają uzasadnień w `reason`.
Indeksy są od zera; `trip_index: -1` oznacza brak tripu. Nie wymyślaj dowodów
dla uzyskania kompletnego eksportu. Bez dowodu pozostaw ograniczenie w raporcie
i kontynuuj tworzenie dostępnego pakietu. Sprawdź decyzje przez
`inspect ... --decisions /path/to/decisions.json` przed konwersją.

## Zapis pakietu

`convert` wymaga resvg **0.48.1**, `cavern` i `dump3d`. Skorzystaj z
[instalacji i pochodzenia renderera](../../../doc/pockettopo/CLI.md#przygotowanie);
nie zastępuj go inną wersją ani nie pomijaj PNG.

```sh
uv run jktz-pockettopo convert /path/to/source.top \
  --output /tmp/pockettopo-result \
  --resvg /path/to/resvg
```

Dodaj `--decisions`, jeśli przygotowano uzasadnione decyzje. `--resvg` można
pominąć, gdy `RESVG` lub `PATH` wskazuje właściwy program. Domyślnie skala
wynosi 40 px/m, tło `#ffffff`; opcje `--pixels-per-metre` i `--background`
pozwalają je zmienić. W raporcie sprawdź również faktyczną skalę po limitach
rozmiaru obrazów.

Cel musi być nowym katalogiem w istniejącym rodzicu, poza `_RAW`.
Istniejący plik, pusty katalog, dowiązanie i cel utworzony równocześnie przez
inny proces zawsze powodują odmowę nadpisania. Dla kolejnej próby wybierz
nową nazwę; nie usuwaj wcześniejszego wyniku tylko po to, aby ponowić komendę.

Po poprawnym wywołaniu `convert`:

- **`0`**: opublikowano cały pakiet, `conversion_complete` jest `true`.
- **`2`**: opublikowano cały pakiet do audytu, `conversion_complete` jest
  `false`. Wyjaśnij wstrzymane rekordy, kompilację i ograniczenia rysunków.
  Sam błąd składni argumentów również zwraca `2`, ale nie tworzy pakietu.
- **`1`**: błąd odczytu, decyzji, renderera lub zapisu; nowy pakiet nie został
  opublikowany. Usuń przyczynę w dozwolonym zakresie i zachowaj wcześniejsze
  wyniki. Błąd środowiska nie dowodzi uszkodzenia danych.

## Sprawdzenie i przekazanie

Sprawdź 12 plików: `survey.SRV`, `survey.svx`, `source.json`,
`conversion-report.json` i po SVG/PNG dla `plan-sketch`, `plan-measurements`,
`side-sketch`, `side-measurements`. Odczytaj raport, szczególnie
`exports.validation`, `package.drawing_notices` i `completeness`.
Kompilator bez ostrzeżeń nie wystarcza, jeżeli brakuje stacji/odcinków lub
geometria obu formatów się różni. Obejrzyj cztery PNG pod kątem osi, skali,
kolorów, obcięcia, pustych szkiców i oznaczeń ograniczeń.

Przekaż ścieżkę pakietu, SHA-256 wejścia, kod zakończenia i konkretne
ograniczenia. Rozróżnij komplet plików od kompletności aktywnych pomiarów
i walidacji. Survex kompiluje oba formaty; nie nazywaj tego testem w Walls.
Nawet pełny wynik nie potwierdza historii, dat, powtórzeń ani CRS.

Zakończ po zamówionej inspekcji lub konwersji. Pakiet nie rejestruje jaskini,
nie ustala GPS i nie edytuje `KATASTER.wpj`. Jeżeli użytkownik zamówił także
włączenie do projektu, przejdź do [add-cave](../add-cave/SKILL.md) z zachowanym
raportem i źródłem; aktywny SRV wymaga osobno kanonicznych metadanych i zasad
nazewnictwa z `AGENTS.md`.
