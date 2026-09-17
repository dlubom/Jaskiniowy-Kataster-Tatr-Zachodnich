# Niezależna weryfikacja rachunków i rankingu

Data: 2026-09-17. **Wynik: brak rozbieżności w sprawdzonym zakresie.**
Kontrola używała osobnego skryptu Python i biblioteki standardowej; nie importowała
`jktz.czarna_crosscheck`, `jktz.czarna_model_readings` ani innych modułów repozytorium.

Sprawdzono **78 unikalnych wierszy**, wszystkie 390 pól wejściowych, 14 wspólnych
wyłączeń rankingu oraz 15 punktów kontrolnych. Odtworzono również 423 zapisy wierszy
modeli (3 × 115 w Markdown, 78 w pierwotnym SRV), ich numery linii, pierwsze wartości,
alternatywy i powtórzenia. Weryfikacja obejmowała **937 rekordów rachunkowych**,
80 zachowanych literalnych adnotacji i **16912 porównań**.
SHA-256 wejść wskazanych w wyniku zgadzają się z plikami i `git show`.

| Transkrypcja | Pierwsze wartości | Z alternatywami | Różne | Brak pól |
| --- | ---: | ---: | ---: | ---: |
| Codex, pierwotny SRV `7472374` | 375/376 | 375 | 1 | 0 |
| Gemini Flash 3.8 | 370/376 | 373 | 6 | 0 |
| Gemini Pro | 348/376 | 348 | 23 | 5 |
| Claude Opus 5 | 337/376 | 343 | 39 | 0 |

Liczniki osobno dla D/A/V/Lh/Δh również się zgadzają. Pro podaje `18→20`;
`19→20` jest brakującą parą, więc pięć pól pozostaje w mianowniku. Powtórnej
fotografii nie liczono ponownie. Ocena obejmuje 76 pól D, 76 A, 76 V, 76 Lh
oraz 72 Δh. Brak azymutu pionu 57→58 jest zgodnym zapisem `null`, nie błędem.
Bieżący SRV ma 376/376 względem ocenianej referencji; nie uczestniczy w rankingu.

Wszystkie 78 zestawów `D cos(V)`, `D sin(V)`, `sqrt(Lh²+Δh²)` (niezależne
sprawdzenie `hypot`) oraz `atan2(Δh,Lh)` zgadzają się z JSON do 1e-10.
Sprawdzono też residua, oznaczenia progów i rachunki modeli z ich własnymi
kolumnami oraz z kolumnami referencji. **12 wierszy** ma oba residua ≤0,005 m;
**62** ma oba ≤0,05 m (w tym te 12); **16** przekracza próg 0,05 m.
To poprawność obliczeń, a nie potwierdzenie nieomylnych rachunków autora.

Niezależne przejście grafu od stacji 0 potwierdziło wszystkie 15 sum Δh,
sum trygonometrycznych, odchyleń względem dopisków, 14 przyrostów między
punktami kontrolnymi i granic wynikających z alternatyw Δh. Ujęto boczną drogę
`0→…→6→a→b`. Potwierdzone sumy ciągu głównego: D=1109,70 m, Lh=953,18 m,
Δh=16,47 m; gałąź 6–a–b: D=12,80 m, Lh=11,61 m, Δh=−2,22 m.
Suma trygonometryczna do 76 wynosi 17,454431319224 m.

Źródłowe pola sporne w środku dziennika sprawdziłem wcześniej wizualnie
w pełnych 41 wierszach zdjęcia `123630`; zapis tej pracy zachowuje
`odczyt_srodek.json`. Ponownie sprawdziłem ich przeniesienie do uzgodnionej
referencji i wyłączeń rankingu. Δh27→28=11,63 pozostaje niepewne. Dla 58→59
referencja używa niepewnych Lh=6,45 i Δh=−6,44, podczas gdy mój pierwszy odczyt
wynosił 6,43 i −6,48; wszystkie te warianty są zachowane. Nie przedstawiam
tej kontroli jako nowego, niezależnego odczytu pozostałych 37 wierszy fotografii
123052/123533. Ich rachunki i porównanie z literalnymi modelami sprawdzono,
a wizualna referencja pochodzi od pozostałych czytelników.

Ranking zależy od 376 rozstrzygnięć referencji i nie jest testem ogólnej jakości
modeli. Pierwotny SRV Codex jest wynikiem wcześniejszej kontroli czytelników,
a nazwy Gemini/Opus pochodzą od użytkownika. Arytmetyka nie sprawdza azymutu;
zgodność sum nie dowodzi samodzielnie poprawności każdego składnika.

## Odtworzenie kontroli

```sh
python3 Poligony/D_Koscieliska/Organy/Czarna/KONTROLA_RACHUNKOW/WERYFIKACJA_SKRYPT.txt
```

Polecenie uruchamiaj z katalogu głównego repo. `WERYFIKACJA_SKRYPT.txt` to
zamrożony kod niezależnej kontroli (stdlib; nie importuje narzędzia głównego).
Wymaga historii git zawierającej `7472374`; główne CLI jej nie wymaga, ponieważ
ma bajtową kopię starego SRV. Wynik kontrolny zapisano także w
`WERYFIKACJA_WYNIK.json`. Algorytm: odczytać referencję i wynik JSON;
oddzielnie sparsować komórki surowych tabel Markdown (znak z opcjonalną spacją,
pierwsza liczba oraz dalsze alternatywy) i SRV z `git show 7472374`; wybrać pierwszą
parę każdego modelu; ocenić identyczne niepewne pola jako wyłączone; przeliczyć
trygonometrię w stopniach; przejść po rodzicach każdej stacji do 0; porównać
sumy i granice dla wszystkich ścieżek; na końcu porównać wartości, liczniki,
listy rozbieżności, linie źródłowe i SHA-256.

Zweryfikowany stan:

- `odczyt_uzgodniony.json`: `8f2dfd8167ea7d644f3df1335d1862d50e0badca284d1f7b68758f93ad6d8cb3`.
- `wyniki.json`: `2b9201caf9d1e5ce2265b5ef0168cbe4eae7be0ea9d3415781927c4eb9f54efa`.
- Niezależny skrypt: `726bf9f6cd135f8481d5f5d3176ecb9d9324263187ca835fc189bede1a900547`.

Dodatkowy recenzent obliczył 156 składowych przez Decimal (60 cyfr) i szereg
Taylora, niezależnie od biblioteki trygonometrycznej użytej przez powyższy skrypt.
Maksymalna różnica wyniosła 3,6e−15 m; klasyfikacje progów były identyczne.
