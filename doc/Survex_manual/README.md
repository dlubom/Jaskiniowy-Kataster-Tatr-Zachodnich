# Lokalna dokumentacja Survexa

- Wydanie: **Survex 1.4.22**, opublikowane 2026-06-23.
- Tag: [`v1.4.22`](https://github.com/ojwb/survex/tree/v1.4.22/doc).
- Commit: `5b233b9255ef7e7c6de9400136d508db76e61e78`.
- Źródło: [oficjalne lustro ojwb/survex](https://github.com/ojwb/survex),
  wskazane na [stronie projektu](https://survex.com/cvs.html).
- Data pobrania i porównania: **2026-09-24**.
- Zakres: 21 plików `doc/*.rst`, pięć plików `doc/*.htm` wymienionych
  w [SHA256SUMS](SHA256SUMS) oraz plik `COPYING` z głównego katalogu upstream.
- Licencja upstream: [COPYING](COPYING); zachowano oznaczenia autorów.

Pliki objęte manifestem są kopiami bajt w bajt z tego commitu. Dla manuali
adres źródłowy ma postać:

```text
https://raw.githubusercontent.com/ojwb/survex/5b233b9255ef7e7c6de9400136d508db76e61e78/doc/<nazwa-pliku>
```

Dla `COPYING` pomiń `doc/`. README i SHA256SUMS są lokalnymi metadanymi.
Sprawdzenie integralności (z katalogu repozytorium, Python bez dodatkowych bibliotek):

```bash
uv run python - <<'PYCODE'
import hashlib
from pathlib import Path

root = Path("doc/Survex_manual")
for line in (root / "SHA256SUMS").read_text().splitlines():
    expected, name = line.split(maxsplit=1)
    actual = hashlib.sha256((root / name).read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit(f"Niezgodna suma: {name}")
print("Wszystkie sumy zgodne")
PYCODE
```

## Wyszukiwanie i zgodność wersji

Punktem wejścia jest [index.rst](index.rst). RST można czytać i przeszukiwać
bez budowania HTML. Znaczniki takie jak `|release|` i `|PKGDOCDIR_EXPANDED|`
są podstawiane przez upstream podczas budowania dokumentacji; katalog jest
zestawem referencyjnym, nie kompletnym projektem Sphinx.

[Manual online](https://survex.com/docs/manual/index.htm) może z czasem
opisywać nowszy program. Przy diagnozie sprawdź `cavern --version` i wybierz
dokumentację odpowiadającą tej wersji. [walls.rst](walls.rst) opisuje
ograniczenia czytnika Walls, a nie wszystkie cechy natywnego Wallsa.

## Odświeżanie kopii

1. Sprawdź [listę wydań](https://survex.com/changes.html) i wersję używaną
   w projekcie. Wybierz konkretny tag i zapisz jego commit.
2. Pobierz do katalogu tymczasowego wszystkie pliki objęte manifestem z tego
   commitu. Sprawdź również, czy upstream dodał lub usunął pliki dokumentacji.
   Przejrzyj różnice przed podmianą lokalnego zestawu.
3. Zaktualizuj ten opis i SHA256SUMS, zachowując pliki upstream bez lokalnych
   poprawek. Projektowe uwagi zapisz w [../README.md](../README.md) lub skillach.

Aktualizacja 2026-09-24 zmieniła względem poprzedniej kopii pięć plików RST
(`walls`, `datafile`, `intro`, `getstart`, `compass`) i `HACKING.htm`.
Najważniejsze uzupełnienia dotyczą modeli IGRF, `#SYMBOL`, separatora prefiksów,
`NOTE`/`NOTEALL`, częściowych wymiarów `passage` i `*infer`.
