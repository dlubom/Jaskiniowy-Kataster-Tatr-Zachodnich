# Rzeczywiste wzorce: trójki odczytów i oba szkice

Próba 2026-09-25 uzupełnia P01, nie zmienia jego zamrożonych wzorców.
Źródło: `dlubom/test2`, commit `4c00c008a8dd441d70f9c62aa376c20b5914c7e0`.
Ścieżki oryginalne, SHA-256 i definicja wyszukiwania:
[raport doboru](../../REPEAT_CANDIDATES.md) i [JSON](../../REPEAT_CANDIDATES.json).
Autorzy i licencja źródłowa: nieustalone. Licencja JKTZ nie zastępuje licencji
materiałów zewnętrznych. Dat tripów nie uznano za potwierdzone daty terenowe.

| Przypadek | Rekordy TXT | Serie po 3 | Kreski | Wierzchołki plan / bok |
| --- | ---: | ---: | ---: | ---: |
| zach0dni2 | 11 | 3 | 70 | 692 / 220 |
| okna | 14 | 4 | 36 | 226 / 131 |
| DS201208 | 25 | 8 | 70 | 459 / 812 |

## Pozyskanie i zawartość

Każdy katalog zawiera niezmieniony oryginał `.top`, natywny `native.txt`,
`nativeP.dxf` i `nativeS.dxf`, oraz `source-records.json`: odczyt surowych pól
według [FORMAT_V3](../../FORMAT_V3.md), niezależny od przyszłego konwertera.
JSON jest wynikiem inspekcji, nie natywnym eksportem. Nie zastępuje oryginału.

PocketTopo **1.372**, Wine **11.7**, macOS, natywny .NET 2.0.
Otwierano tylko izolowane kopie robocze, bez zapisywania TOP. Menu Export → Text
oraz Export → Graphics: plan i bok, skala **1:500**, Shots i Xsections w osobnych
warstwach; Labels, Grid, All Data, All Colors wyłączone.
[Zrzut opcji](export-options.png). Pliki TXT/DXF zachowują oryginalne CRLF.
P/S oznacza odpowiednio plan/przekrój rozwinięty; obrazy zach0dni2 pokazują
fragment obu widoków w aplikacji, nie cały zakres rysunku.

## Kontrola i odtworzenie porównania

[validation.json](validation.json) zawiera wyniki dla każdego źródła/widoku.
[manifest.json](manifest.json) przypina ścieżki i identyfikatory Git blob.
[SHA256SUMS](SHA256SUMS) zabezpiecza wszystkie artefakty poza samym manifestem.
Kontrola integralności: `shasum -a 256 -c SHA256SUMS` w tym katalogu.

1. Porównać SHA-256 TOP z raportem doboru oraz Git blob z przypiętego drzewa.
2. Odczytać binarne struktury w kolejności FORMAT_V3; liczności oraz surowe
   rekordy i wierzchołki zachowuje `source-records.json`.
3. Porównać każdą pozycję TXT: identyfikatory (także niezdefiniowane),
   D = mm/1000 do 3 miejsc; A = (raw modulo 65536)×360/65536 i V = raw×360/65536
   do 2 miejsc; indeks tripu (TXT od 1), flip i komentarze. Daty, deklinacja
   i komentarze wszystkich trzech tripów również zgodne. Brak komentarza tripu
   jest pustym polem bez cudzysłowów. W komentarzach zach0dni2 CRLF w TOP
   odpowiada literalnemu `\r` w TXT; JSON zachowuje oryginalne CRLF.
4. Z sekcji ENTITIES DXF odczytać kolejne POLYLINE/VERTEX/SEQEND i POINT warstwy
   Sketch. Dla każdego wierzchołka sprawdzić X = rawX/500, Y = −rawY/500
   w milimetrach DXF, kolejność, liczbę i brak flagi zamknięcia polilinii.
   Paleta TOP→ACI: 1→0, 2→9, 3→32, 4→5, 5→1, 6→3, 7→30.
   Tolerancja porównania 0.000001 mm; uzyskany maksymalny błąd **0**.

Wynik: **50 rekordów, 3 tripy, 176 kresek, 2540 wierzchołków**, zgodność
wszystkich pól ujawnianych w TXT oraz współrzędnych, kolorów i kolejności szkiców.
Pozostałe encje DXF (osnowa) policzono, ale nie zatwierdzono ich geometrii.
Natywne uśrednianie PocketTopo nie jest wzorcem algorytmu średnich PRD.
15 serii potrójnych to kandydaci na powtórzenia instrumentu; ich kolejność
nie potwierdza niezależnie intencji autora. Nie uśredniano aktywnych pomiarów.
To nie jest zaliczenie docelowej bramki całego korpusu ani wykonanie P02.

Kontrola repozytorium: `uv run jktz-quality` — 385 testów, 96.08% linii,
93.40% gałęzi, wynik pozytywny (2026-09-25). Kod Pythona nie zmienił się
w tym uzupełnieniu; wyniki mutacji P01 pozostają w jego raporcie.
