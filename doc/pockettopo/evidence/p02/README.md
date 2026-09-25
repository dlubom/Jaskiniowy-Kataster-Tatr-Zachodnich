# P02 — ścisły parser i model źródła

**Zakończone 2026-09-25 na `codex/pockettopo-convert`.** Następny etap: **P03**.

Implementacja znajduje się w [`src/jktz/pockettopo/`](../../../../src/jktz/pockettopo/).
Ten etap udostępnia bibliotekę odczytu. Średnie, eksportery, `source.json`,
pakiet wynikowy i CLI pozostają w P03–P06 zgodnie z [PRD](../../PRD.md).

## Użycie biblioteki

Z katalogu głównego repozytorium, po `uv sync --locked --python 3.12`:

```sh
uv run --python 3.12 python - <<'PY'
from jktz.pockettopo import read_top

source = read_top("doc/pockettopo/evidence/p01/cases/api-trips-ids/api-trips-ids.top")
print(source.shots[0].from_id.text, source.shots[0].to_id.text)  # 0 0.0
print(source.trips[2].declination_raw, source.trips[2].declination_mode)  # -32768 auto
print(source.ending)  # zero_trailer
PY
```

`parse_bytes(data, *, limits=ParseLimits(...))` przyjmuje zawartość `bytes`;
`read_top(path, *, limits=...)` odczytuje plik w trybie binarnym. Obie funkcje
zwracają kompletny `TopFile` albo zgłaszają `ParseError` (podklasę `ValueError`).
Błąd zawiera `code`, `offset` liczony od zera i `context`, np.
`shots[0].trip_index`. Błędy systemu plików pozostają `OSError`.
Nie ma operacji zapisu ani zwracania częściowego modelu po błędzie.

## Zachowane dane i granice interpretacji

Model składa się z niezmiennych dataclass i krotek. Przechowuje kolejno tripy,
pomiary, referencje, overview oraz wszystkie elementy obu rysunków. Każda
liczba źródłowa pozostaje całkowita: signed Int16/Int32/Int64 oraz Byte.
Nie przelicza kątów, ticks ani współrzędnych przez float.

- `StationId.raw`, `.kind` i `.text` rozróżniają undefined, plain oraz major.minor.
  Zwykłe `0` i `0.0` pozostają różnymi stacjami.
- `Trip.declination_raw` zachowuje również sentinel `-32768`; dodatkowe
  `.declination_mode` odróżnia `auto` od `explicit`. Model nie ustala daty
  pomiaru ani korekty IGRF na podstawie zegara urządzenia.
- `Shot.trip_index=-1` pozostaje brakiem sesji. `comment=None` oznacza brak
  pola, a `comment=""` obecne puste pole. `.flipped` opisuje bit Flip;
  parser nie odwraca odcinka i nie uśrednia powtórzeń.
- E/N/Z pozostają podpisane, bez przypisania CRS; kolejne referencje tej samej
  stacji nie są scalane. Ujemne długości, nietypowe ticks i pochylenia poza
  zakresem terenowym są zachowywane jako surowe liczby, bez uznania ich za
  prawidłowy pomiar. Ich ocena należy do przetwarzania i raportowania.
- `Polygon` zachowuje każdy punkt, kolor i kolejność; brak automatycznego
  domknięcia. Pusta lista punktów jest dopuszczalnym strukturalnie rekordem,
  a singleton pozostaje singletonem. `XSection` zachowuje pozycję, ID i kierunek.
  Nie narzucamy kierunkowi nieudokumentowanego limitu 65535: przyjmujemy `-1`
  albo dowolny nieujemny Int32. Mapping nie przesuwa geometrii.
- `TopFile.ending` rozróżnia `eof` i `zero_trailer`. Dozwolone są tylko
  dwa zakończenia ustalone w P01. Zachowanie surowego pliku nadal jest niezbędne:
  model nie jest obietnicą binarnie identycznej ponownej serializacji.

## Ścisłość i budżety odczytu

Parser odrzuca nieznaną wersję, flagi spoza bitów 0/1, typ elementu spoza
0/1/3, błędny indeks tripu, skalę spoza 10–50000 i kolor spoza 1–7.
Sprawdza ucięcia, ujemne liczniki, minimalną wymaganą liczbę pozostałych bajtów,
przepełnienia długości napisów oraz ścisłe UTF-8. Długość napisu to
nieujemny Int32 zapisany grupami po 7 bitów, najwyżej w pięciu bajtach;
piąty bajt może przenosić wyłącznie trzy bity wartości.

Domyślne limity są **ochroną zasobów**, nie ograniczeniami formatu:

| Limit | Wartość | Zakres |
| --- | ---: | --- |
| `max_bytes` | 67108864 | cały plik (64 MiB) |
| `max_records` | 1000000 | osobno każda tabela tripów, pomiarów i referencji |
| `max_string_bytes` | 1048576 | jeden napis UTF-8 (1 MiB) |
| `max_points` | 2000000 | suma wierzchołków polilinii obu rysunków |
| `max_elements` | 100000 | suma elementów obu rysunków |

Limity można jawnie zmienić przez `ParseLimits`; muszą być nieujemnymi
liczbami całkowitymi. `read_top` pobiera najwyżej `max_bytes + 1` bajtów,
aby wykryć przekroczenie przed nieograniczonym wczytaniem pliku.

## Dowody i odtworzenie

- [Wynik kontroli wzorców](fixture-checks.json): sześć P01 — 20 pomiarów,
  53 wierzchołki i 4 XSection; trzy rzeczywiste — 50 pomiarów i 2540 wierzchołków.
  Odrzucono wszystkie 2211 niedozwolonych ucięć P01. SHA-256 wszystkich 55
  artefaktów P01 i 21 artefaktów rzeczywistych wzorców pozostały zgodne.
- [`tests/test_pockettopo_fixtures.py`](../../../../tests/test_pockettopo_fixtures.py)
  sprawdza dosłownie każde pole sześciu wzorców P01 oraz trzech rzeczywistych
  źródeł, wraz z każdym wierzchołkiem. Oczekiwania istniały przed parserem.
  Pełne ucięcia wzorców P01 sprawdzają wyjątek dla dozwolonego EOF bez sufiksu.
- [`tests/test_pockettopo_parser.py`](../../../../tests/test_pockettopo_parser.py)
  bada granice liczb, napisy, błędy struktury, budżety i model. Syntetyczne
  bajty błędów uzupełniają natywne wzorce; nie zastępują ich jako wyroczni.
- [Korpus](CORPUS.md) i [wynik każdego źródła](corpus.json) utrwalają odczyt
  przypiętej rewizji `test2`. Zgodność strukturalna nie dowodzi poprawności
  przyszłych średnich, geometrii ani eksportów.
- [Bramki repozytorium](repository-checks.json) zapisują wyniki quality,
  mutacji i niezależnego przeglądu. Oba moduły PocketTopo są jawnie objęte
  mutacjami; wcześniejszych modułów ani progów nie usunięto.

| Kontrola | Wynik |
| --- | --- |
| Testy P02 / cały projekt | 211 / 596 zaliczone |
| Linie / gałęzie całego projektu | 96,52% / 93,82% |
| Linie / gałęzie nowego pakietu PocketTopo | 100% / 100% |
| Maksymalny CRAP całego projektu | 21,54 przy limicie 25 |
| Mutacje modelu | 37/37 (100%) |
| Mutacje parsera | 635/703 (90,33%) |
| Mutacje wszystkich siedmiu modułów | 1504/1725 (87,19%); każdy moduł ≥81% |
| Aktualność snapshotu GPS | 87 fixów, wydanie `v1.0.2`, zgodność |

Pierwsza kampania słusznie nie zaliczyła bramki: `mutmut` 3.8.0 pomija
`@property` i nie utworzył żadnych mutacji modelu. Przeniesiono interpretację
ID/Auto/Flip do zwykłych prywatnych funkcji; właściwości zachowały publiczne API.
Świeża pełna kampania objęła wszystkie cztery funkcje i przeszła. Szczegóły:
[quality.json](quality.json) i [mutation.json](mutation.json), z listą ocalałych
mutacji. Nie przypisujemy wszystkim ocalałym mutacjom równoważności.

```sh
uv run --python 3.12 pytest -q tests/test_pockettopo_parser.py tests/test_pockettopo_fixtures.py
uv run --python 3.12 jktz-quality
uv run --python 3.12 jktz-mutation
```

Testy CI korzystają z lokalnych wzorców i nie potrzebują korpusu ani sieci.
Źródeł P01, rzeczywistych `.top`, natywnych eksportów i `_RAW` nie zmieniamy.
