# PocketTopo: użycie CLI

`jktz-pockettopo` odczytuje jeden plik PocketTopo **v3** (`.top`). `inspect`
pokazuje źródło i plan eksportu, a `convert` zapisuje osobny pakiet pomiarów,
szkiców i raportów. Konwerter działa bez PocketTopo, Wine i GUI.

## Przygotowanie

Uruchamiaj polecenia z katalogu głównego repozytorium:

```sh
uv sync --locked --python 3.12
uv run jktz-pockettopo --help
uv run jktz-pockettopo convert --help
```

`inspect` wymaga wyłącznie zależności Pythona. Do `convert` potrzebne są:

- **resvg dokładnie 0.48.1** — pobierz odpowiednie archiwum z
  [wydania 0.48.1](https://github.com/linebender/resvg/releases/tag/v0.48.1),
  sprawdź SHA-256 archiwum i programu według
  [instrukcji dla macOS arm64 i Linux x86_64](RENDERER.md),
  rozpakuj i wskaż program przez `--resvg` lub zmienną `RESVG`.
  [Instrukcja sprawdzenia renderera](RENDERER.md#sprawdzenie-wzorca-png)
  opisuje sprawdzenie wersji i wzorcowego PNG; CI korzysta z
  [przypiętej akcji instalacji](../../.github/actions/install-resvg/action.yml).
- **Survex 1.4.12 lub nowszy**, programy `cavern` i `dump3d` — zobacz
  [instalację Survex](https://survex.com/download.html). Domyślnie CLI szuka
  ich w `PATH`; osobne ścieżki podaje się przez `--cavern` i `--dump3d`.

Sprawdź wersje wybranych programów:

```sh
/path/to/resvg --version
cavern --version
dump3d --version
```

## Odczyt bez zapisu pakietu

```sh
uv run jktz-pockettopo inspect /path/to/source.top
```

Na standardowe wyjście trafia JSON z dwoma polami: `source` zawiera wszystkie
zdekodowane rekordy i wartości surowe, a `report` opisuje grupy, korekty,
mapowanie nazw, decyzje eksportu i ograniczenia. `inspect` nie uruchamia
renderera ani kompilatora i nie zapisuje plików. Można zachować jego wyjście
przekierowaniem powłoki do osobnego pliku.

**Kod 0 z `inspect` nie oznacza kompletnej konwersji.** Odczytaj
`report.completeness`, `report.record_trace`, `report.trips` i
`report.limitations`, także gdy polecenie zakończyło się poprawnie. Rekordy
wstrzymane nadal mogą istnieć; kompilacja i rysunki nie zostały sprawdzone.

## Konwersja

Wskaż nieistniejący katalog wewnątrz istniejącego katalogu nadrzędnego:

```sh
uv run jktz-pockettopo convert /path/to/source.top \
  --output /tmp/pockettopo-result \
  --resvg /path/to/resvg
```

Wynik zawiera dokładnie 12 plików:

| Pliki | Znaczenie |
| --- | --- |
| `survey.SRV`, `survey.svx` | Pomiary aktywne, komentarze źródłowe i decyzje eksportu |
| `plan-sketch.svg`, `plan-sketch.png` | Plan: same kreski szkicu |
| `plan-measurements.svg`, `plan-measurements.png` | Plan: szkic z osnową, domiarami i punktami |
| `side-sketch.svg`, `side-sketch.png` | Przekrój rozwinięty: same kreski szkicu |
| `side-measurements.svg`, `side-measurements.png` | Przekrój rozwinięty: szkic z pomiarami |
| `source.json` | Pełny zdekodowany materiał, także rekordy nieaktywne |
| `conversion-report.json` | Pochodzenie, decyzje, ustawienia, kompilacja i kompletność |

SVG zachowują osobne warstwy. PNG powstają z tych samych SVG, bez zależności
od fontów systemowych. Pusty szkic ma jawny status i oznaczony pusty wynik.
Konwerter nie przesuwa oryginalnych kresek w celu dopasowania ich do osnowy.

| Opcja | Domyślnie | Znaczenie |
| --- | --- | --- |
| `--output KATALOG` | wymagane dla `convert` | Nowy katalog wynikowy |
| `--decisions PLIK.json` | brak decyzji | Jawne potwierdzenia, wyłączenia i korekty |
| `--min-resultant LICZBA` | `1e-12` | Próg nieokreślonego azymutu średniej; zakres `[1e-12, 1)` |
| `--resvg PROGRAM` | `RESVG`, potem `resvg` w `PATH` | Renderer 0.48.1 |
| `--cavern PROGRAM` | `cavern` | Kompilator obu formatów |
| `--dump3d PROGRAM` | `dump3d` | Odczyt skompilowanej geometrii |
| `--pixels-per-metre LICZBA` | `40` | Żądana skala obrazów; dodatnia, skończona, najwyżej `1e9` |
| `--background KOLOR` | `#ffffff` | `#RRGGBB` albo `transparent` |

`inspect` przyjmuje tylko `source`, `--decisions` i `--min-resultant`.
Kolor w powłoce zapisuj w cudzysłowie, np. `--background '#ffffff'`.
Limit 4096 pikseli na wymiar i 16 milionów pikseli może zmniejszyć żądaną
skalę; faktyczne wymiary i skalę zapisuje
`drawings.artifacts.<wariant>.viewport` w raporcie.

## Jawne decyzje

Plik UTF-8 JSON musi zawierać `source_sha256`: dokładnie 64 małe znaki
szesnastkowe, zgodne z bajtami wejścia. Odczytaj hash z
`report.provenance.sha256` polecenia `inspect`. Nie przenoś decyzji na inne
wejście bez ponownego sprawdzenia źródła.

Poniższy minimalny plik jest związany wyłącznie ze wzorcem
[`gui-cardinal/source.top`](../../tests/fixtures/pockettopo/p01/cases/gui-cardinal/source.top)
i nie dodaje żadnych decyzji:

```json
{
  "source_sha256": "27b93102584d76840192d97e242cc30df38edbc551da244a033773095ae87bfb",
  "confirmations": [],
  "exclusions": [],
  "corrections": []
}
```

Trzy tablice są opcjonalne. Każdy ich element ma dokładnie wskazane pola:

| Tablica | Pola elementu | Warunki |
| --- | --- | --- |
| `confirmations` | `indices`: tablica liczb całkowitych; `reason`: tekst | Co najmniej dwa kolejne, rosnące indeksy odczytów tej samej nazwanej pary w znanym tripie; dowód powtórzenia w `reason` |
| `exclusions` | `index`: liczba całkowita; `reason`: tekst | Świadome wyłączenie z aktywnych pomiarów; rekord pozostaje w źródle i raporcie |
| `corrections` | `trip_index`: liczba całkowita; `degrees`: liczba; `reason`: tekst | Jawna korekta w stopniach od −180 do 180, z niezależnym uzasadnieniem |

Indeksy odczytów i tripów są **od zera**. `trip_index: -1` oznacza odczyty
bez przypisanego tripu. `reason` musi być niepustym uzasadnieniem, nie samą
etykietą decyzji. Grup nie wolno nakładać ani łączyć z wyłączeniami; splay,
zerowe powiązanie i zmiana tripu przerywają grupowanie. Nieznane lub
zduplikowane klucze JSON, błędne typy, liczby nieskończone, niewłaściwe indeksy
i niezgodny SHA-256 powodują odrzucenie decyzji.

```sh
uv run jktz-pockettopo inspect /path/to/source.top --decisions /path/to/decisions.json
uv run jktz-pockettopo convert /path/to/source.top \
  --decisions /path/to/decisions.json \
  --output /tmp/pockettopo-reviewed \
  --resvg /path/to/resvg
```

Domyślnie odczyty pozostają osobne. Zbieżne nazwy, geometria, domknięcie
i wygląd szkicu nie są dowodem powtórzenia. Potwierdzone serie są uśredniane
przed zaokrągleniem: długość i podpisane pochylenie arytmetycznie, azymut
kołowo, po normalizacji kierunku względem pierwszego odczytu. `flipped`
dotyczy przekroju rozwiniętego, a nie kierunku pomiaru.

Zapisana jawna korekta jest odtwarzana, również zero; to nie potwierdza jej
historycznej poprawności. Tryb `Auto` i brak tripu wymagają uzasadnionej
korekty, inaczej odczyty niezerowe są wstrzymane. Data tripu może pochodzić
z resetu zegara palmtopa: CLI nie ustala daty pomiaru, nie zastępuje jej datą
z nazwy pliku i nie uruchamia IGRF. Referencje E/N/Z pozostają w raporcie
bez zakładania CRS i bez aktywnych fixów.

## Kody zakończenia i bezpieczny zapis

| Kod | Wynik |
| --- | --- |
| `0` | `inspect`: odczyt i przygotowanie raportu się udały. `convert`: zapisano 12 plików, `completeness.conversion_complete` jest `true`. |
| `1` | Błąd wejścia, decyzji, renderera lub zapisu. Nowy katalog wynikowy nie został opublikowany; istniejący cel pozostaje nietknięty. |
| `2` | Po poprawnym wywołaniu `convert`: zapisano wszystkie 12 plików, ale `conversion_complete` jest `false`. Odczytaj raport. Błędna składnia argumentów CLI również zwraca `2`, lecz nie tworzy pakietu. |

Pakiet z kodem `2` może zawierać wstrzymane pomiary, celowo wyłączone rekordy,
ograniczenia nakładania osnowy albo nieudaną walidację kompilacji. Brak
`cavern`/`dump3d`, ostrzeżenia, timeout, przerwanie kompilatora, brak stacji
lub niezgodna geometria nie są sukcesem kompilacji, nawet gdy zapisano
wszystkie pliki. Brak lub niewłaściwa wersja resvg uniemożliwia pełny pakiet
i kończy się kodem `1`.

Walidator kompiluje SRV i SVX **osobno w Survexie**. W każdym wyniku sprawdza
obecność nazwanych stacji, liczbę linii dla odrębnych par stacji, domiary i powiązania zerowe;
potem porównuje położenia stacji oraz linie obu wyników w tolerancji zapisu 3D.
Powtórzenia tej samej pary mogą zostać scalone przez kompilator. Zbieżne
współrzędne dwóch różnych par same nie dowodzą takiego scalenia.

Polityka kolizji jest stała: **odmowa nadpisania**. Dotyczy pliku, pustego
katalogu, dowiązania symbolicznego (także zerwanego) i celu utworzonego przez
inny proces podczas konwersji. Rodzic katalogu wynikowego musi istnieć.
Wyjście w `_RAW` jest zabronione, również przez dowiązanie; odczyt źródła
z `_RAW` jest dozwolony. Aby powtórzyć próbę, wybierz nową nazwę wyjścia.
Odczyt źródła jest ograniczony do 64 MiB plus bajt rozpoznający przekroczenie
limitu; większy plik jest odrzucany przed dekodowaniem.

Wszystkie pliki są przygotowywane w katalogu tymczasowym na tym samym
systemie plików, a następnie publikowane jednym atomowym przeniesieniem
bez zastępowania celu. Obsługiwane są macOS, Linux i Windows; brak takiej
operacji powoduje odmowę zapisu. Nagłe zakończenie procesu może pozostawić
ukryty katalog roboczy, ale nie częściowo opublikowany pakiet.

## Odbiór wyniku

Zacznij od `completeness` i `limitations`. Prześledź `record_trace`, `groups`,
`trips`, `station_map`, `references`, `exports.validation` oraz
`drawings.geometry` i `package.drawing_notices`. Raport kompilacji obejmuje
ostrzeżenia, stacje, odcinki, domiary oraz porównanie geometrii obu formatów.
`package.artifacts` zawiera rozmiary i SHA-256 jedenastu pozostałych plików;
raport nie zawiera własnego hasha.

Obejrzyj wszystkie cztery PNG: osie, skalę, kolory, puste widoki, ostrzeżenia
i obcięcie. Położenie rozłącznych części oraz nierozstrzygnięte przekroje
pozostają ograniczeniem; nie poprawiaj ich przez przesuwanie szkicu.
Szczegóły opisuje [polityka projekcji](PROJECTION.md).

Nawet `conversion_complete: true` potwierdza tylko zadeklarowaną konwersję
i jej kontrole. Nie potwierdza dat, powtórzeń, CRS ani historii pomiaru.
Oba formaty są kompilowane przez Survex; to nie jest test uruchomienia w Walls.
Zobacz [ograniczenia kompilacji](COMPILER_LIMITS.md).

Pakiet roboczy nie jest automatycznie dodawany do katastru. Włączenie aktywnego
SRV, nadanie nazwy zgodnej z projektem, metadane, GPS i wpisy `KATASTER.wpj`
to odrębny zakres według [AGENTS.md](../../AGENTS.md) i
[skilla add-cave](../../.agents/skills/add-cave/SKILL.md).
