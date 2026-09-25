# P05 — natywne wzorce projekcji

Data: **2026-09-25**, PocketTopo **1.372**, assembly `1.3.7.0`.

[Helper C#](../../helpers/pockettopo_projection_fixtures.cs) tworzy literalnie
zadane syntetyczne pomiary w modelu z zainstalowanego `PocketTopo.exe`.
Natywne `DataSet.Write` zapisuje `.top`; świeży model otwiera go przez
`DataSet.Read`, a `Survey.WriteText` i `DXFWriter.WriteDXF` eksportują dane.
Własny parser ani konwerter nie uczestniczą w tworzeniu wzorców. Wszystkie
trzy odczyty powiodły się, a sześć DXF zawiera końcowe `EOF`.

Helper nie tworzy `MainForm`, nie wyświetla okna i nie wywołuje zapisu konfiguracji.
Pracuje w osobnym procesie, używa niewyświetlanych `Control` jako zależności
`Mapping`, a jednostki ustawia tylko w polach pamięci procesu. Nie edytuje
istniejących materiałów ani aktywnego projektu GUI. Tak jak helper P01,
odmawia nadpisania istniejącego wyjściowego `.top`.

## Pliki i jednostki

W [native/](native/) każdy przypadek ma `.top`, natywny TXT, plan DXF, przekrój
DXF oraz `native-coordinates.tsv` odczytany reflection z obiektów aplikacji
**po** natywnym eksporcie. TSV zapisuje składowe całkowite w milimetrach:
`x` rośnie na wschód, `y` na południe, `h` w dół, `d` poziomo w przekroju
rozwiniętym. `start_*` wskazuje rzeczywisty obiekt początku użyty przez aplikację;
`num` jest identyfikatorem zdefiniowanego końca, może różnić się od `to` przy
wiązaniu pomiaru od tyłu. `dx/dy/dh/dd` są pomocniczymi składowymi modelu,
nie zinterpretowanymi na nowo rekordami źródłowymi.

DXF ma skalę **1:500** i opcje Shots/XSections oraz osobne warstwy.
Transformacja punktu szkicu to `(x / 500, -y / 500)`; dla przekroju analogicznie
`(d / 500, -h / 500)`. Nie wykonano osobnej operacji `CloseLoops`.
Hash aplikacji, helpera i wyników jest w [native/manifest.json](native/manifest.json),
a pliki danych mają również [native/SHA256SUMS](native/SHA256SUMS).

| Przypadek | Literalne wejście i sprawdzana własność |
| --- | --- |
| `loop` | 0→1: 10 m N; 1→2: 6 m E; 2→0: 11 m / 210°; 2→3: 3 m S / +30°, Flip. Niezerowe niedomknięcie oraz odnoga po pętli. |
| `branch` | 0→1, odwrócone przyłączenie 2→1 z Flip, druga odnoga 1→3, dalsze odnogi 2→4 i 3→5, dwa domiary; Flip kolejnego odcinka jest niezależny. |
| `xsection` | Trip z jawną deklinacją +5°; dwa odcinki i siedem domiarów N/E/S/W, NE +30°, SW −30°, pion +90°. W obu widokach po pięć XSection: kierunki −1, 0, 8192, 16384, 32768. |

Daty, komentarze i liczby są wyłącznie wejściem eksperymentu, bez twierdzeń
o historycznych pomiarach terenowych.

## Ustalenia potwierdzone współrzędnymi

1. **Pętla bez wyrównania zachowuje niedomknięcie.** `loop` umieszcza stację 1
   w `(0, −10000)`, stację 2 w `(6000, −10000)`, a koniec pomiaru 2→0 w
   `(500, −474)` mm. Początkowy obiekt stacji 0 zostaje w `(0, 0)`.
   Końcowe `d=27000` nie jest cofane do `d=0`. Wymuszenie wspólnej współrzędnej
   dla obu końców pętli ukryłoby niedomknięcie.
2. **Flip dotyczy znaku rozwiniętej długości danego odcinka.** Przy odwróconym
   przyłączeniu 2→1, aplikacja zaczyna od znanej stacji 1 (`d=10000`) i nadaje
   stacji 2 `d=6000`: odwraca plan i wysokość, lecz zachowuje `dd=−4000`
   wynikające z Flip. Kolejny 2→4 bez Flip zwiększa `d` do `7732`.
3. **Pozioma składowa domiaru w przekroju zależy od kierunku odcinka
   definiującego stację.** Jest to poziomy zasięg domiaru pomnożony przez
   cosinus różnicy jego surowego azymutu i skierowanego od punktu macierzystego
   azymutu odcinka definiującego; znak uwzględnia Flip tego odcinka.
   Nie jest to zawsze pełna pozioma długość domiaru ani średnia kierunków
   odcinków spotykających się w stacji. W `branch` domiar 1 / 2 m / 45° / +30°
   kończy się przy `d=11224`, `h=−1000`. Domiary korzenia bez definiującego
   kierunku mają zerową składową poziomą przekroju.
4. **XSection z kierunkiem −1 przedstawia rzut poziomy domiarów**:
   `(cx + dx, cy − dy)`, z korektą deklinacji używaną przez plan.
   Pozostałe kierunki są pionową płaszczyzną projekcji. Dla azymutu `a`,
   kierunku `q`, poziomego zasięgu `H` oraz pionowej składowej `V`, punkt ma
   postać `(cx + H·sin(a−q), cy−V)`. Natywne pionowe XSection korzysta
   z **surowego azymutu**, bez dodawania korekty tripu. W eksperymencie +5°
   domiar E / 3 m daje przy kierunku 0 przesunięcie `(3000, 0)`; jego rzut
   poziomy daje `(2989, 261)` w osiach szkicu. Kierunek 8192 odpowiada 45°.
5. **Łącznik XSection biegnie od jego centrum do stacji w wybranym widoku**.
   Natywny DXF umieszcza go na warstwie Sketch jako DASH, domiary na XSect,
   a znacznik centrum jako CIRCLE. Kolejność pięciu sekcji i kolejność ich
   domiarów odpowiadają wejściu helpera.

Aplikacja wykonuje rachunek w całkowitych milimetrach i kątach 65536 jednostek
na obrót. `Angle.ToRect` zaokrągla składowe do najbliższego mm przez dodanie
połowy jednostki przed przesunięciem stałoprzecinkowym; pomocnicze
`Projection.SideProjection` dla pojedynczego kierunku pomija to dodanie,
więc iloczyn cosinusa jest zaokrąglany w dół. Różnica jednego mm między nimi
jest widoczna dla domiaru 45° w `branch`.

Pomocnicza inspekcja metod assembly: `Survey.SetupShot` RVA `0x574c`,
`Survey.SetupXsect` `0x5d38`, `Survey.EvalData` `0x5f14`,
`Projection.SideProjection` `0x4a94`, `Station.WriteXSectDXF` `0x17300`,
`Angle.ToRect` `0xf6fc`. Te adresy służą do odtworzenia badania tej konkretnej
wersji; zdekompilowany kod i aplikacja nie są publikowane w repozytorium.
Zachowania flagi `projected`, wyrównania pętli i wszystkich możliwych porządków
rekordów nie należy uważać za sprawdzone samymi tymi trzema przypadkami.

## Paleta

[native/palette.tsv](native/palette.tsv) pochodzi bezpośrednio z
`MainForm.<kolor>.Color` istniejącej aplikacji, bez tworzenia formularza.

| Nazwa | sRGB |
| --- | --- |
| black | `#000000` |
| gray | `#b0b0b0` |
| brown | `#a52a2a` |
| blue | `#0000ff` |
| red | `#ff0000` |
| green | `#00c000` |
| orange | `#ffa500` |

Wszystkie kolory mają alpha 255. Jest to paleta natywna, bez estymacji ze
zrzutu ekranu lub zastępowania domyślnymi kolorami CSS.

## Reprodukcja

Środowisko: macOS arm64, istniejący prefix Wine Staging 11.7 z Microsoft
.NET 2.0.50727. Uruchomić z katalogu repozytorium, wybierając nowy katalog
wynikowy. Kompilacja helpera i eksporty nie wymagają interakcji z GUI.

```sh
env WINEPREFIX="$HOME/.local/share/pockettopo/wineprefix" WINEDEBUG=-all \
  MVK_CONFIG_LOG_LEVEL=0 wine \
  'C:\windows\Microsoft.NET\Framework\v2.0.50727\csc.exe' \
  /nologo /target:exe /r:System.Windows.Forms.dll /r:System.Drawing.dll \
  '/out:Z:\tmp\PocketTopoProjectionFixtures.exe' \
  "Z:${PWD//\//\\}\\doc\\pockettopo\\helpers\\pockettopo_projection_fixtures.cs"

env WINEPREFIX="$HOME/.local/share/pockettopo/wineprefix" WINEDEBUG=-all \
  MVK_CONFIG_LOG_LEVEL=0 wine /tmp/PocketTopoProjectionFixtures.exe \
  "$HOME/.local/share/pockettopo/app/PocketTopoV1372/PocketTopo.exe" \
  'Z:\tmp\pockettopo-p05-native-new'
```
