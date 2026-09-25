# Konwerter PocketTopo

`uv run jktz-pockettopo` odczytuje PocketTopo v3 i tworzy osobny pakiet
SRV/SVX, planu i przekroju SVG/PNG oraz raportów JSON. Działa bez aplikacji
PocketTopo i Wine. Zachowuje źródłowe odczyty i jawnie raportuje decyzje,
wstrzymane rekordy oraz ograniczenia. Pakiet wymaga osobnego opracowania
przed włączeniem pomiarów do katastru.

| Dokument | Zakres |
| --- | --- |
| [CLI](CLI.md) | Instalacja, `inspect`, `convert`, decyzje, wyniki i kody zakończenia |
| [FORMAT_V3](FORMAT_V3.md) | Struktura binarna i interpretacja surowych pól |
| [PROJECTION](PROJECTION.md) | Osnowa, przekrój rozwinięty, Flip, domiary i XSection |
| [COMPILER_LIMITS](COMPILER_LIMITS.md) | Kontrole Survex i granice zgodności SRV/SVX |
| [RENDERER](RENDERER.md) | Przypięty resvg, sumy kontrolne i sprawdzenie PNG |

Kod utrzymujemy w [src/jktz/pockettopo](../../src/jktz/pockettopo), CLI w
[src/jktz/cli/pockettopo.py](../../src/jktz/cli/pockettopo.py), a testy
w `tests/test_pockettopo_*.py`. Mały zestaw wejść i oczekiwanych wyników
używany przez testy znajduje się w
[tests/fixtures/pockettopo](../../tests/fixtures/pockettopo):

- `p01/cases`, `p05/native`, `repeat-candidates`, `shadow`: źródła `.top`,
  eksporty natywne i dane potrzebne do niezależnych porównań;
- `p01/renderer`: syntetyczny SVG i referencyjne PNG renderera;
- `p05/examples`: wybrane wzorce wyników rysunkowych.

Pliki wejściowe i wzorce są dostępne lokalnie po sklonowaniu repozytorium;
zwykły `pytest` nie pobiera archiwum badań. Pochodzenie, zachowane materiały
uzupełniające i sprawdzanie sum opisuje
[README wzorców](../../tests/fixtures/pockettopo/README.md).
Zewnętrzne narzędzia wymagane przez testy integracyjne opisują [CLI](CLI.md)
i [reguły jakości](../PYTHON_QUALITY.md).

Nazwy `p01` i `p05` zachowują pochodzenie wzorców. Nie oznaczają bieżącego
stanu prac. Reguły walidacji repozytorium opisuje
[PYTHON_QUALITY.md](../PYTHON_QUALITY.md); historyczne wyniki nie zastępują
kontroli aktualnego kodu.

## Archiwum badań P00–P06

Pełne materiały badań, eksperymentalne skrypty, raporty, zrzuty GUI i duże
pakiety wynikowe pozostają w niezmienionym commicie
[`3e3daa4156c6e6e79dce5203d8bb8e36122d571f`](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/tree/3e3daa4156c6e6e79dce5203d8bb8e36122d571f/doc/pockettopo)
dotychczasowej gałęzi i [PR #129](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/pull/129).
To archiwum prac; nie jest wydaniem ani tagiem.

Punkty wejścia do archiwum:

- [PRD i historia etapów](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/blob/3e3daa4156c6e6e79dce5203d8bb8e36122d571f/doc/pockettopo/PRD.md),
  [badania źródeł](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/blob/3e3daa4156c6e6e79dce5203d8bb8e36122d571f/doc/pockettopo/RESEARCH.md);
- [dowody P01–P06 i źródła wzorców](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/tree/3e3daa4156c6e6e79dce5203d8bb8e36122d571f/doc/pockettopo/evidence),
  [helpery eksperymentów](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/tree/3e3daa4156c6e6e79dce5203d8bb8e36122d571f/doc/pockettopo/helpers);
- [PocketTopo i Wine na macOS](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/blob/3e3daa4156c6e6e79dce5203d8bb8e36122d571f/doc/pockettopo/POCKETTOPO_MACOS.md).

Dokumenty archiwalne opisują ówczesny kod, ścieżki i środowisko. Ich daty,
metryki i statusy odnoszą się wyłącznie do zapisanej próby. Odtworzenie
historycznych skryptów wymaga kodu z tego samego commitu.

Odczyt konkretnego pliku oraz odtworzenie całego drzewa do nowego katalogu,
bez przełączania bieżącej gałęzi ani zmiany plików roboczych:

```sh
git fetch --no-tags origin 3e3daa4156c6e6e79dce5203d8bb8e36122d571f
git show 3e3daa4156c6e6e79dce5203d8bb8e36122d571f:doc/pockettopo/PRD.md
pockettopo_archive=$(mktemp -d "${TMPDIR:-/tmp}/jktz-pockettopo-archive.XXXXXX")
git archive 3e3daa4156c6e6e79dce5203d8bb8e36122d571f | tar -x -C "$pockettopo_archive"
```

Pliki historyczne są w `$pockettopo_archive`, w tym komplet
`doc/pockettopo/evidence`. Polecenie `fetch` pobiera obiekt do lokalnej bazy
Git; nie przesuwa bieżącej gałęzi ani gałęzi archiwalnej.
