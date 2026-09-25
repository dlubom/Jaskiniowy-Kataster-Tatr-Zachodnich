# Dokumentacja referencyjna

Ten katalog zawiera lokalne źródła do rozstrzygania pytań o składnię i dane
inwentarzowe. Wyszukaj odpowiedni fragment, a następnie przeczytaj całą sekcję.
Instrukcje projektu i jego polityka przetwarzania są w [AGENTS.md](../AGENTS.md).

| Pytanie | Źródło |
| --- | --- |
| Dyrektywy i zachowanie Wallsa | [Walls_manual.md](Walls_manual.md), kontrola z [PDF](Walls_manual.pdf) |
| Składnia Survexa: jednostki, kalibracja, daty, flagi | [datafile.rst](Survex_manual/datafile.rst) |
| Jak Survex interpretuje Walls SRV/WPJ | [walls.rst](Survex_manual/walls.rst) |
| Kompilacja i opcje cavern | [cavern.rst](Survex_manual/cavern.rst) |
| Eksport, dane 3D i wizualizacja | [survexport.rst](Survex_manual/survexport.rst), [dump3d.rst](Survex_manual/dump3d.rst), [aven.rst](Survex_manual/aven.rst) |
| Nazwy, numery i historia dokumentacji jaskiń | [JSONL PIG](jaskinie_polski_pig_dump.jsonl) |

## Walls

Źródłem Markdown jest zachowany [PDF Davida McKenziego](Walls_manual.pdf),
**Version 2.0 Build 2016-11-18**, 158 stron. To manual historyczny, a nie opis
wszystkich późniejszych kompilacji Wallsa. PDF i ilustracje pozostają bez zmian.
SHA-256 PDF: `310821c89b5ffb5cfe94135fdf9f3a1409451b97aca78e77a5e1c15fea06e7f7`.

Korekta konwersji z 2026-09-24:

- Przywrócono pominięte akapity obok ilustracji: Launch Options, wybór koloru,
  podświetlanie wektorów oraz Traverse Chains. Są na fizycznych stronach PDF
  **20, 51, 59, 137** (drukowana numeracja: **16, 47, 55, 133**).
  Odpowiednie ilustracje umieszczono przy tych akapitach.
- W rozdziale składni zabezpieczono przykłady blokami kodu. W przykładzie
  `LRUD=F` przywrócono osobną linię `---`, sklejoną wcześniej z nazwą `A0`
  (PDF: strona 72, drukowana 68). Połączono zawinięte komentarze `#symbol`
  (PDF: strona 88, drukowana 84).
- Rozdzielono pięć tabel atrybutów DBF na wiersze odpowiadające polom
  (PDF: strony 129–130, drukowane 125–126). W tabeli Name_W.DBF opisy są
  źle wyrównane już w PDF; przypisanie pełnych opisów do FILLCOLOR, POLYGONS
  i SQMETERS odtworzono z ich treści, zachowując nazwy i typy pól.

Sprawdzono tekst wyekstrahowany ze wszystkich stron oraz wizualnie strony
objęte korektami. Nie jest to pełna kontrola każdego znaku i wszystkich
ilustracji. Markdown służy do wyszukiwania; wątpliwe znaki, kolejność kolumn
lub brak fragmentu wymagają sprawdzenia PDF-u. Przykłady zachowują historyczną
notację autora, w tym wielokropki i skróty, i nie zawsze są kompletnym wejściem
kompilatora. Uwagi redakcyjne są oddzielone od treści manuala.

Dla różnic Walls–Survex sprawdź też [ograniczenia czytnika Walls](Survex_manual/walls.rst).
Wersja programu i model IGRF mają znaczenie dla deklinacji obliczanej z daty.
Poprawne odwzorowanie tekstu manuala nie dowodzi identycznego działania
różnych programów ani wersji.

## Survex

Lokalny zestaw odpowiada wydaniu **1.4.22**. Wersja, commit źródłowy, licencja,
sumy kontrolne i procedura odświeżenia są w
[Survex_manual/README.md](Survex_manual/README.md).
Pliki RST są źródłem tekstowym dokumentacji i można je przeszukiwać przez `rg`.

## PIG

[jaskinie_polski_pig_dump.jsonl](jaskinie_polski_pig_dump.jsonl) jest archiwalnym
wyciągiem z [rejestru PIG](https://jaskiniepolski.pgi.gov.pl/), nie bieżącym
źródłem pomiarów. Data ostatniego commitu nie jest datą pozyskania każdego
rekordu. Nie deklarujemy pełności względem obecnego rejestru.

Kontrola 2026-09-24: 860 linii, każda poprawnie parsuje się jako obiekt JSON;
`inventory_number` i `cave_id` są obecne i unikalne w tym pliku. To kontrola
struktury, nie prawdziwości wszystkich opisów. SHA-256 pliku:
`e8fd04a43e9520480198048a58b89e67c6ea4ce2f23d749a8c5c81c2d86ed1b0`.

Numery są odrębne: dla Dziury `inventory_number` to `T.B-14.01`, natomiast
PIG `cave_id` to ciąg znaków `001018`. Zachowuj zera początkowe.

Przykłady uruchamiane z katalogu głównego repozytorium:

```bash
rg -n -F '"T.B-14.01"' doc/jaskinie_polski_pig_dump.jsonl
rg -n -i -F 'Śnieżna' doc/jaskinie_polski_pig_dump.jsonl
```

`rg` szuka w całej linii, więc trafienie może dotyczyć wzmianki o innej jaskini
w opisie. Dokładny wybór pola, bez dodatkowych bibliotek:

```bash
uv run python - <<'PYCODE'
import json
from pathlib import Path

for line in Path("doc/jaskinie_polski_pig_dump.jsonl").read_text(encoding="utf-8").splitlines():
    cave = json.loads(line)
    if cave.get("inventory_number") == "T.B-14.01":
        print(json.dumps(cave, ensure_ascii=False, indent=2))
PYCODE
```

Nazwy i aliasy są w `name` i `other_names`. Szukaj z polskimi znakami lub
po charakterystycznym fragmencie; `Sniezna` nie pasuje do `Śnieżna`.
`authors_of_study` i `editorial` nie dowodzą autorstwa konkretnego pomiaru.
Datowanie i zespół pomiarowy ustalaj z dostarczonego materiału źródłowego.
Współrzędne aktywne pochodzą z projektu GPS i szablonu `OTWORY.SRV.j2`;
rozbieżność z PIG jest informacją do wyjaśnienia, nie podstawą automatycznej
zmiany pomiarów lub punktu otworu.
