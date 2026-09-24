# Bramki jakości kodu Pythona

Progi w `pyproject.toml` są wspólne dla lokalnych poleceń i CI.

| Kontrola | Próg | Zakres |
| --- | --- | --- |
| Ruff i pytest | bez błędów | `src`, `scripts`, `.agents/skills`, `web`; testy w `tests` |
| Pokrycie linii | co najmniej 95% | cały powyższy kod, także nieimportowane pliki |
| Pokrycie gałęzi | co najmniej 90% | decyzje i alternatywne ścieżki wykonania |
| CRAP | najwyżej 25 na funkcję | funkcje, metody i funkcje zagnieżdżone |
| Testy mutacyjne | co najmniej 81% w **każdym** wybranym module | SRV, RAW, zapis atomowy, wejścia GPS i stan jednostek Walls |
| Kompletność zakresu | bez pominiętych plików i całkowicie nieprzetestowanych funkcji | żywy kod Pythona w repo; archiwalne `_RAW` nie są narzędziami |

Test inventory porównuje śledzone i nowe nieignorowane pliki `.py` z zakresem
kontroli; nowy plik poza dozwolonymi katalogami zatrzymuje bramkę. Raport musi
zawierać każdy plik źródłowy oraz każdą funkcję objętą analizą złożoności.
Funkcja z zerową liczbą wykonanych wierszy blokuje wynik niezależnie od
globalnego pokrycia i CRAP. Lista zmierzonych plików jest zapisana w `quality.json`.

Pokrycie nie dowodzi poprawności. Testy sprawdzają wynik i skutki uboczne:
zachowanie bajtów, brak zapisu po błędzie, granice wartości, odrzucenie wadliwych
danych, stan parsera oraz statusy procesów. Sieć i programy zewnętrzne zastępujemy
kontrolowanymi odpowiedziami w testach jednostkowych. Rzeczywiste kompilacje
i eksporty pozostają zadaniem `jktz-validate` na Linux i Windows.

## Uruchomienie

```bash
uv sync --locked --python 3.12
uv run jktz-quality
uv run jktz-mutation
uv run jktz-validate
```

`jktz-quality` wykonuje Ruff, nowy pomiar pytest z gałęziami, raport HTML/JSON
i sprawdzenie progów. `jktz-mutation` usuwa roboczy katalog `mutants/`, wykonuje
pełny przebieg wybranego zakresu z maksymalnie czterema procesami i sprawdza
wynik. Nie używa wyników poprzedniego przebiegu jako dowodu poprawności.
Raporty trafiają do `logs/quality/`; CI zapisuje je jako artefakty na 14 dni.

Mutmut wymaga POSIX i Python >= 3.10; lokalnie używaj Linux, macOS lub WSL,
a kanoniczny przebieg CI działa na Python 3.12/Linux. Pozostały kod nadal
deklaruje Python >= 3.9. Nieobsługiwane środowisko zwraca błąd, nie sukces.
Zależności są przypięte przez `uv.lock`; adapter wyników mutmut jest związany
z wersją 3.8.0 i wymaga sprawdzenia przy jej aktualizacji.

## CRAP bez dopasowywania kodu do wyniku

Stosujemy `C² × (1 − p)³ + C`, gdzie `C` jest złożonością cyklomatyczną Radon,
a `p` to mniejsza z wartości pokrycia linii i gałęzi danej funkcji (0–1).
Przy braku gałęzi decydują linie. Jest to konserwatywny wariant CRAP:
dużo wykonanych linii nie zasłania nieprzetestowanych rozgałęzień.
Przy pełnym pokryciu CRAP jest równy złożoności; funkcja o złożoności >25
nie może przejść przez samo dodanie testów.

25 to próg ostrzegający przed skupieniem ryzyka, nie nakaz dzielenia każdej
dłuższej funkcji. W istniejącym kodzie najpierw uzupełniamy test brakującego
kontraktu i poprawiamy odtworzony błąd. Sama metryka nie uzasadnia refaktoryzacji
ani zmiany danych pomiarowych.

## Mutacje: zakres i interpretacja

Zakres `tool.mutmut.only_mutate` obejmuje pięć modułów chroniących dane:
`metadata/io.py`, `metadata/raw.py`, `metadata/srv.py`, `entrances/render.py`
i `validation/measurements.py`. To regularna bramka rdzenia;
**nie jest** wynikiem mutacyjnym całego repo. Skille, procesy eksportu i CLI
mają testy zachowania, pokrycie oraz CRAP; rozszerzenie mutacji o skille jest
kolejnym możliwym etapem po ocenie kosztu i ocalałych mutacji.

Mutacje nie są ograniczone do pokrytych linii. Wynik to liczba mutacji
zatrzymanych przez pytest (kod 1) podzielona przez wszystkie wygenerowane
mutacje modułu. Nie wymagamy 100%: część zmian komunikatów i mutacji
równoważnych nie zmienia kontraktu użytkowego. Pozostają w mianowniku i raporcie.

Brak metadanych, pusty zakres lub moduł bez mutacji powoduje błąd. Timeout,
awaria procesu, wewnętrzny błąd pytest, pominięcie, brak testów lub wynik
niezakończony także blokują bramkę; nie są zaliczane jako wykrycie mutacji.
`mutmut show IDENTYFIKATOR` pozwala obejrzeć zmianę bez modyfikowania źródła.
Nie używaj `mutmut apply` na źródłach do rutynowego sprawdzania wyniku.

## Egzekwowanie i zasady dla ludzi oraz agentów

Pre-commit uruchamia `jktz-quality`, pre-push pełne `jktz-validate`.
Mutacje działają jako osobny job `mutation-tests` w każdym PR do `master`.
Pakiet testowy PR zależy od bramek jakości i walidacji. Workflow wydania
również uruchamia obie bramki. Nie ma `continue-on-error` dla tych kontroli.

Hook Git można lokalnie ominąć. Blokadę scalania realizuje reguła GitHub
`Protect master`, wymagająca `python-tools`, `mutation-tests`,
`validate (ubuntu-latest)` i `validate (windows-latest)` z aktualnego PR.
Zachowane administracyjne uprawnienia obejścia reguły są jawnym wyjątkiem
platformy, nie częścią normalnej ścieżki dostarczenia zmian.

- Nie obniżaj progu, nie zawężaj zakresu ani nie dodawaj wykluczeń pokrycia
  lub mutacji wyłącznie po to, aby uzyskać zielony wynik.
- Nie zmieniaj testu na zgodny z wadliwym kodem. Najpierw ustal kontrakt
  na podstawie danych źródłowych, dokumentacji lub wywołującego kodu.
- Dodaj test odtwarzający błąd przed poprawką. Ocalone mutacje analizuj przez
  ich wpływ na zachowanie, nie przez dopasowanie testu do tekstu implementacji.
- Rozróżniaj awarię infrastruktury, niepełny przebieg i błąd produktu.
  Przejście testów lokalnych nie zastępuje CI dla końcowego SHA.
- Zmiany polityki i wyjątków muszą być jawne w PR, uzasadnione i przejrzane.

Dokumentacja narzędzi: [Coverage.py](https://coverage.readthedocs.io/),
[Radon](https://radon.readthedocs.io/en/stable/api.html),
[mutmut](https://mutmut.readthedocs.io/en/latest/),
[wymagane statusy GitHub](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).

## Pomiar wdrożeniowy — 2026-09-24

Przed zmianą przechodziło 168 testów; pokrycie wynosiło 78,41% linii
i 73,42% gałęzi (`src`, `scripts`, skille; skrypt `web` nie był jeszcze objęty
pomiarem). Po włączeniu całego zakresu i testów regresji: 384 testy,
96,08% linii, 93,40% gałęzi, najwyższy CRAP 21,54 przy limicie 25.
Nie dodano wykluczeń pokrycia dla osiągnięcia progów.

| Moduł mutowany | Zabite / wszystkie | Wynik |
| --- | --- | --- |
| Zapis atomowy | 33 / 39 | 84,62% |
| Metadane RAW | 104 / 114 | 91,23% |
| Metadane SRV | 303 / 368 | 82,34% |
| Renderer wejść GPS | 284 / 350 | 81,14% |
| Stan jednostek Walls | 108 / 114 | 94,74% |
| Łącznie w tym zakresie | 832 / 985 | 84,47% |

Wszystkie mutacje zakończyły się wynikiem testu; 153 przetrwały.
Nie oznacza to 153 błędów ani dowodu równoważności wszystkich ocalałych zmian.
Próg pozostawia je jawnie w raporcie do dalszej oceny.

Regresje zabezpieczają potwierdzone błędy: ciche nadpisanie powtórzonego
`object_id` w CSV GPS, nieobsłużoną brakującą komórkę CSV, niepoprawne
śledzenie trybu i stanu `#units` oraz dodawanie własnego pliku wynikowego ZIP
do archiwum. Logika przygotowania wersji i release notes przeszła z `sed`/`awk`
do testowanego polecenia Pythona. Pełna lokalna walidacja Survex/GDAL przeszła;
dane pomiarowe i archiwalne źródła nie zostały zmienione.

## Kontrola kompletności i zgodności migracji

Spis kodu obejmuje 46 plików produkcyjnych: 41 w `src`, trzy pomocniki skilli,
bootstrap i skrypt web. Wszystkie 144 nazwane funkcje/metody występują
w analizie CRAP i każda ma wykonane wiersze w testach. Zachowano sześć
wcześniejszych poleceń CLI, dodając trzy nowe; pozostały też trzy helpery
Python i dziewięć opisów skilli. Test inventory chroni ten zakres bez
zakodowania stałej liczby plików.

| Kontrakt | Dowód |
| --- | --- |
| Podmiana wersji w `INFO.txt` | porównanie bajtów z rzeczywistym `sed` dla 65 wersji z CHANGELOG i jednej etykiety PR |
| Pełna treść release notes | porównanie 65 sekcji `v*` z rzeczywistym `awk`; jedyną normalizacją są puste linie na początku |
| Markdown | regresje dla początkowego wcięcia, końcowych spacji i zwykłych H2 wewnątrz opisu |
| Wersja i artefakty workflow | testy obu ścieżek: release i PR; zachowane `body_path`, nazwy ZIP, render/check wejść, kolejność eksportu, upload i link |
| Kompletność ZIP | integracja poleceń odczytanych z workflow sprawdza dokładny zestaw plików, bajty źródeł/eksportów, wersję INFO i wykluczenia |

Testy porównawcze w `tests/test_release_metadata.py` uruchamiają stare operacje
na tymczasowych kopiach; brak `sed`/`awk` na POSIX powoduje błąd. Na Windows
brak tych opcjonalnych narzędzi pomija tylko porównanie ze starym shellem;
testy zachowania Pythona i integracji paczek działają nadal. Porównanie
odtwarza LF dawnego workflow Linux niezależnie od `core.autocrlf` checkoutu.
Puste `[Unreleased]` pozostaje dozwolone; publikowany tag nadal wymaga opisu.

Audyt znalazł i naprawił dwie regresje nowego parsera release notes: usuwanie
znaczących spacji oraz ucinanie treści na zwykłym H2. Odrzucanie brakującej,
pustej lub zduplikowanej sekcji publikowanej wersji pozostaje świadomym
zaostrzeniem. Testy integracyjne są w `tests/test_release_workflow.py`.

Te sprawdzenia potwierdzają kompletny zakres narzędzi i zbadane kontrakty.
Nie są dowodem równoważności dla wszystkich możliwych wejść; pokrycie nie
wynosi 100%, a wynik mutacyjny dotyczy wymienionych pięciu modułów.
