# P04 — eksport SRV/SVX

Biblioteka eksportuje pomiary w pamięci jako `SurveyExport(source_document,
report, srv, svx)`. Zapis atomowego pakietu, CLI i skill pozostają P06;
rysunki pozostają P05. Oryginały `.top` i `_RAW` nie są zmieniane.

## API

```python
from pathlib import Path
from jktz.pockettopo import export_surveys

path = Path('doc/pockettopo/evidence/p01/cases/api-cardinal/api-cardinal.top')
result = export_surveys(path.read_bytes())
print(result.srv)
print(result.report['completeness'])
```

Domyślnie każdy niepotwierdzony odczyt jest osobną linią. Argument `plan`
przyjmuje `ProcessingPlan` z P03; `min_resultant` i `limits` zachowują jego
kontrakt. Wynik zawiera pełny dokument źródłowy i rozszerzony raport P04,
w tym mapę stacji, decyzję eksportu każdej grupy i każdego rekordu oraz numery
linii obu formatów (od 1). Błąd parsera lub planu przerywa wywołanie bez zapisu.

## Korekty i zatrzymane rekordy

Domyślna polityka odtwarza jawnie zapisaną deklinację sesji, również zero,
bez uznania jej za historycznie potwierdzoną. Korekta trafia do `#units DECL=`
lub `*declination`; azymut odczytu nie jest drugi raz korygowany w Pythonie.
Auto oraz brak sesji zatrzymują niezerowe pomiary z przyczyną. Niezależne,
udokumentowane ustalenie można przekazać jawnie:

```python
import hashlib
from jktz.pockettopo import CorrectionOverride, CorrectionPolicy, export_surveys

# Wyłącznie syntetyczny wzorzec P01, a nie ustalenie dla pomiarów terenowych.
path = Path('doc/pockettopo/evidence/p01/cases/api-trips-ids/api-trips-ids.top')
data = path.read_bytes()
policy = CorrectionPolicy(hashlib.sha256(data).hexdigest(), overrides=(
    CorrectionOverride(2, 8.0, 'Syntetyczna próba P04: jawnie wybrane +8 stopni'),
    CorrectionOverride(-1, -12.0, 'Syntetyczna próba P04: jawnie wybrane -12 stopni'),
))
result = export_surveys(data, correction_policy=policy)
```

Indeks `-1` dotyczy rekordów bez sesji. Polityka sprawdza SHA, indeksy,
unikalność, skończony zakres −180…180° i niepuste uzasadnienie. Uzasadnienie
jest twierdzeniem dostarczającego je autora; narzędzie nie potwierdza go samo.
Daty urządzenia pozostają niezweryfikowane; nie emitujemy `#date`, `*date`,
IGRF ani aktywnych fixów z referencji o nieznanym CRS.

Zera między różnymi nazwanymi stacjami tworzą powiązanie bez korekty kątowej:
SRV `A B 0 0 0`, SVX `*equate A B`. Splays mają anonimowy koniec `-`/`::`;
odwrócone źródłowe splays normalizuje P03. Flip nie odwraca pomiaru.
Oryginalne kąty, komentarze, flagi i przyczyny zatrzymania pozostają w JSON
oraz komentarzach eksportu. Zatrzymany pomiar nie dostaje aktywnej linii.

## Nazwy i precyzja

Walls zachowuje dosłowne nazwy o długości do 8 znaków; dłuższe zastępuje przez
`p` + zapis unsigned raw ID w bazie 36. Ta przestrzeń jest rozłączna ze źródłowymi
nazwami liczbowymi PocketTopo, więc nie ma obcinania ani kolizji. Mapa zawiera
surowy ID, nazwę źródłową i obie nazwy docelowe. SVX zachowuje nazwę dosłownie,
zmieniając separator hierarchii na `:` i dopuszczając kropkę w nazwie stacji.
Zwykłe `0` i `0.0` pozostają odrębne, również w rzeczywistym Walls.

D/A/V są formatowane dopiero na końcu, do 12 miejsc po przecinku, bez notacji
wykładniczej. Komentarze są odwracalnie zakodowane jako ASCII JSON, podzielone
na ponumerowane fragmenty po 160 znaków; linie mieszczą się w limicie Walls
255 znaków. Nowa linia, Unicode czy tekst dyrektywy w komentarzu nie stają się
aktywnym kodem SRV/SVX. Odczytujący fragmenty łączy ich payload w kolejności,
a następnie dekoduje JSON.

## Granica kompletności

`measurement_export_complete` oznacza reprezentację wszystkich rekordów
źródłowych w aktywnym tekście pomiarowym. Nie jest wynikiem kompilacji ani
potwierdzeniem geometrii całej sieci. Biblioteka jawnie zapisuje
`exports.validation = "not_run_by_library"`. `geometry_status` rozróżnia
`empty`, `constraints_only` oraz `nonempty`; same powiązania zerowe nie tworzą
przestrzennej osnowy. `conversion_complete` zawsze pozostaje `false` do P06.

Rozłączny ciąg może zostać pominięty przez cavern mimo kodu wyjścia 0.
Sprzeczne zera i dodatnie odcinki mogą wywołać błąd kompilatora. Nie naprawiamy
tego przez wymyślone fixy ani usunięcie danych. [Próby graniczne](COMPILER_LIMITS.md)
i [wyniki korpusu](CORPUS.md) opisują dokładnie zakres porównania. P06 musi
sprawdzać ostrzeżenia, błędy i kompletność wyjścia, a nie tylko kod procesu.

## Dowody

- [Wzorce](fixture-checks.json): 13 przypadków, w tym 9 wcześniejszych źródeł,
  potwierdzone i niepotwierdzone powtórzenia, odwrócony splay i skrajne ID.
- [Niezależna geometria](geometry.json): oczekiwania analityczne z P01,
  zgodność nazw, poprawek, pionów, domiarów i zer. Tolerancja 0,010001 m wynika
  z centymetrowego zapisu `.3d` i odejmowania zaokrąglonego początku.
- [Korpus 258 źródeł](CORPUS.md): zachowane ostrzeżenia i rozliczenie wszystkich
  rekordów, bez automatycznych potwierdzeń powtórzeń.
- [Rzeczywisty Walls](walls/README.md): izolowane projekty, raporty współrzędnych,
  obrazy okien, wersja aplikacji i sumy kontrolne.
- [Odtworzenie](REPRODUCE.md), [bramki repozytorium](repository-checks.json).

Testy: `tests/test_pockettopo_export.py` i `tests/test_pockettopo_compilation.py`.
Zwykłe testy pomijają kompilację, gdy Survex nie jest zainstalowany; krok CI
Linux/Windows ustawia `JKTZ_REQUIRE_CAVERN=1` i brak narzędzi jest wtedy błędem.
Parser, model, matematyka i grupowanie nadal należą do obowiązkowego zakresu
mutacji. Nie obniżono żadnego progu ani nie wyłączono istniejących modułów.

Podstawa składni: `doc/Walls_manual.md`, sekcje ograniczeń programu, Vector Data
Lines i #UNITS (historyczny Build 2016-11-18); `doc/Survex_manual/datafile.rst`
i `walls.rst`. Rzeczywiste wersje użyte w próbach zapisano przy dowodach.
