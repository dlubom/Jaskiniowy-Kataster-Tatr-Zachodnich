# Wzorce regresyjne PocketTopo

Wybrany zestaw z [PR #129](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/pull/129),
zamrożony w rewizji `3e3daa4156c6e6e79dce5203d8bb8e36122d571f`.
Wszystkie 112 plików wymienionych w `SHA256SUMS` zachowuje oryginalne bajty.
104 pliki są wejściami testów, osiem dokumentuje pochodzenie oczekiwań.
Zwykłe testy nie wymagają sieci ani checkoutu archiwalnego brancha.

| Katalog | Pochodzenie i zastosowanie |
| --- | --- |
| `p01/cases` | Sześć niezależnych wzorców utworzonych w PocketTopo 1.372: cztery przez API aplikacji i dwa przez GUI. `.top`, natywne DXF i zamrożone `expected.json` sprawdzają surowe pola i każdy wierzchołek. |
| `repeat-candidates` | Trzy rzeczywiste źródła, ich natywne DXF i `source-records.json` z inspekcji wykonanej przed parserem konwertera. `manifest.json` przypina źródłowe ścieżki i obiekty Git. |
| `shadow` | Źródło Shadow i dwa natywne DXF do sprawdzania każdego wierzchołka, osnowy i domiarów. |
| `p05/native` | Syntetyczne pętle, odnogi, Flip i XSection zapisane przez API PocketTopo; DXF, współrzędne TSV oraz paleta aplikacji stanowią niezależne odniesienie. |
| `p05/examples` | 52 PNG wygenerowane przez konwerter w P05 dla 13 źródeł. To wzorce regresji renderowania, nie niezależne eksporty PocketTopo. |
| `p01/renderer` | SVG próby resvg 0.48.1 i dwa PNG dla różnych rozdzielczości. Archiwalne odpowiedniki Linux były identyczne bajtowo z zachowanymi plikami macOS. |
| `helpers` | Niezmienione źródła dwóch eksperymentów C# z literalnymi wejściami API PocketTopo; nie są silnikiem konwersji ani częścią zwykłego pytest. |

DXF wyeksportowano w skali 1:500, z osobnymi warstwami pomiarów i przekrojów,
bez etykiet i siatki. Oczekiwań nie regenerujemy badanym parserem. Daty
urządzenia i kandydaci na powtórzenia nie stanowią potwierdzenia terenowego.

## Źródła i historia

Materiały terenowe pochodzą z `dlubom/test2`, commit
`4c00c008a8dd441d70f9c62aa376c20b5914c7e0`. Autorzy i licencja tych materiałów
są nieustaleni; licencja JKTZ nie nadaje im nowej licencji.
Shadow pochodzi ze ścieżki `502-Schattenhohle/20120816-Shadow/shadow.top`,
obiekt Git `b12e45894175bce110722b6f6e37ec318294e6c8`. Pozostałe trzy ścieżki,
rozmiary, obiekty Git i SHA-256 zawiera [manifest](repeat-candidates/manifest.json).

Pełne opisy źródeł, eksperymentów, interfejsu aplikacji i eksportów:

- [P01: pochodzenie i procedura](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/blob/3e3daa4156c6e6e79dce5203d8bb8e36122d571f/doc/pockettopo/evidence/p01/README.md),
  [niezależne oczekiwania](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/blob/3e3daa4156c6e6e79dce5203d8bb8e36122d571f/doc/pockettopo/evidence/p01/EXPECTATIONS.md).
- [Trzy źródła terenowe](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/blob/3e3daa4156c6e6e79dce5203d8bb8e36122d571f/doc/pockettopo/evidence/repeat-candidates/README.md)
  i [Shadow](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/blob/3e3daa4156c6e6e79dce5203d8bb8e36122d571f/doc/pockettopo/evidence/shadow/README.md).
- [P05: natywne odniesienie projekcji](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/blob/3e3daa4156c6e6e79dce5203d8bb8e36122d571f/doc/pockettopo/evidence/p05/NATIVE.md)
  i [manifest aplikacji oraz eksportów](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/blob/3e3daa4156c6e6e79dce5203d8bb8e36122d571f/doc/pockettopo/evidence/p05/native/manifest.json).

W archiwum pliki mają ten sam przyrostek ścieżki pod
`doc/pockettopo/evidence/`; jedynie `helpers/` pochodzi z
`doc/pockettopo/helpers/`. [Instrukcja odtworzenia archiwum](../../../doc/pockettopo/README.md)
nie wymaga przełączania bieżącego brancha.

## Integralność i utrzymanie

Z tego katalogu: `shasum -a 256 -c SHA256SUMS` (Linux: `sha256sum -c SHA256SUMS`).
Test `test_frozen_fixture_manifest_is_complete_and_matches_hashes` sprawdza
pełny zestaw i hashe, aby usunięcie `.top` nie zmniejszyło po cichu liczby
przypadków zbieranych przez glob. `.gitattributes` wyłącza normalizację końców
linii dla wzorców również na Windows.

Nie umieszczaj README ani manifestu wewnątrz `p01/cases`: testy traktują każdy
jego bezpośredni element jako przypadek. Nowe wzorce i świadome zmiany
oczekiwań wymagają osobnego uzasadnienia i aktualizacji sum kontrolnych.
