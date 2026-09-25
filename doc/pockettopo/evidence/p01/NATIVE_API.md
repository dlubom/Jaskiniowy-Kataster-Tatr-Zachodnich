# P01 — wzorce przez natywny model PocketTopo

Data próby: **2026-09-25**. Ta kategoria źródła jest odrębna od przypadków
`gui-*` utworzonych ręcznie w oknie aplikacji.

## Pochodzenie i zakres

[Helper C#](../../helpers/pockettopo_fixtures.cs) ładuje istniejący
`PocketTopo.exe` i tworzy jego rzeczywiste obiekty `Trip`, `Station`, `Reference`,
`Mapping`, `Drawing`, `Polygon`, `XSection` i `DataSet` przez reflection.
Wartości wejściowe są literalnie zapisane w metodach `Cardinal`, `TripsAndIds`,
`References` i `Drawings`; nie pochodzą z odczytu pliku `.top` ani przyszłego parsera.

**Pliki `.top` zapisuje wyłącznie `PocketTopo.DataSet.Write`.** Helper nie zawiera
`BinaryWriter` ani własnego kodera formatu. Przed eksportem otwiera zapisany plik
przez `DataSet.Read` w świeżym modelu, następnie wywołuje `Survey.WriteText`
i `DXFWriter.WriteDXF`. Wszystkie cztery odczyty zakończyły się powodzeniem.
Eksporty TXT używają metrów i stopni; DXF: skala 1:500, Shots i XSections,
obie osobne warstwy, bez Labels/Grid/All Data/All Colors.

Nie powstaje okno `MainForm`; niewyświetlane obiekty `Control` dostarczają jedynie
rozmiary wymagane przez `Mapping`. Helper nie wywołuje `Application.Run`, `Show`,
`Config.Open` ani zapisu ustawień w rejestrze. `Config.metric` i `Config.angle`
otrzymują wartości tylko w procesie helpera. Statyczne `XSection.survey` jest
ustawiane tak, jak robi to zwykły konstruktor `MainForm`.

| Przypadek | Ręcznie zadane wejście |
| --- | --- |
| `api-cardinal` | 11 pomiarów: N/E/S/W, potwierdzone trzy odczyty 358°/2°/pomiar wsteczny 180°, pion ±90°, splay, zerowe powiązanie, roll 0/64/128/192/255; oba szkice puste |
| `api-trips-ids` | 3 tripy: +5°, −3,5° i Auto; dokładne ticks z resztą 7/9/1 × 100 ns; plain `0` versus `0.0`, `12.65535`, niezdefiniowany cel, indeks tripu −1, Flip, komentarz UTF-8 dłuższy niż 127 bajtów |
| `api-references` | Dwie jawne referencje tej samej stacji: E/N poza Int32, wartości ujemne oraz dodatnie, ujemne Z; żaden CRS nie jest przypisany |
| `api-drawings` | W każdym widoku 7 otwartych linii po 3 punkty, wszystkie kolory, singleton oraz XSection z direction −1 i 16384; Flip i oddzielne przesunięcia Mapping |

Te dane są syntetyczne. Daty, referencje, powtórzenia i komentarze nie stanowią
dowodu jakiegokolwiek terenowego pomiaru. Dwie referencje w `api-references`
sprawdzają zapis wartości, nie tworzą sensownego ustalenia położenia jaskini.

## Cztery bajty po schemacie

W kodzie zarządzanym aplikacji 1.372 metoda `DataSet.Write` (token `0x06000317`,
RVA `0x218f0`) po zapisaniu `sideview` wywołuje `BinaryWriter.Write(Int32 0)`.
Dlatego kanoniczny wynik tej wersji zawiera **dokładnie `00 00 00 00` po obu
rysunkach**. Są to osobne cztery bajty, a nie pomylony znacznik końca rysunku.

`DataSet.Read` (token `0x06000318`, RVA `0x219c0`) po drugim rysunku ustawia
sukces i zamyka strumień. Nie odczytuje końcowych bajtów. Potwierdzono to
niezależnie na kopiach natywnego `api-cardinal.top` (465 bajtów, opublikowany
schemat kończy się na offsecie 461):

| Sufiks po schemacie | Natywny odczyt 1.372 |
| --- | --- |
| dokładnie 4 zera | przyjęty |
| brak sufiksu | przyjęty |
| 1, 2, 3 lub 8 zer | każdy przyjęty |
| `01 23 45 67` | przyjęty |
| ASCII `TAIL-IS-NOT-READ` | przyjęty |
| obcięcie o kolejny bajt, usuwające końcowe `0` sideview | odrzucony |

Ponowny **natywny** zapis trzech wejść (kanonicznego, bez sufiksu, z niezerowym
sufiksem) dał za każdym razem wynik **identyczny bajtowo z kanonicznym plikiem**.
Sufiksy testowe utworzono tylko na kopiach tymczasowych. Oryginały `cases/`
pozostały nienaruszone.

Wniosek dla ścisłego parsera P02: dopuścić koniec dokładnie po opublikowanym
schemacie albo dokładnie cztery zera. Każdy inny sufiks zgłaszać jako błąd;
tolerancja czytnika aplikacji nie uzasadnia pomijania nieznanych danych.

## Deklinacja automatyczna

W `Trip.Write` (token `0x0600019e`, RVA `0x12bbc`) tryb `automatic=true`
zapisuje **Int16 −32768 (`00 80`)**. `Trip.Read` (token `0x0600019f`,
RVA `0x12c1c`) rozpoznaje tę wartość, ustawia tryb automatyczny i zeruje wewnętrzne
`declCorr`. To **nie jest −180°**. Native TXT dla `api-trips-ids` pokazuje `Auto:`.

P02 musi zachować surowy sentinel i osobny tryb. Wyświetlone przez aplikację
`Auto: 0.00` bez referencji nie potwierdza jawnej zerowej korekty, wiarygodnej
daty ani CRS. Samo odczytanie sentinela nie zezwala na automatyczne użycie IGRF.

## Ważne szczegóły walidacji

- `ID(string)` i natywny serializer dają plain `0` → `−2147483647`,
  `0.0` → `0`, brak ID → `−2147483648`.
- `Angle(degrees, 360)` zaokrągla do jednostek 65536/obrót. Dla 358°/2°
  zapis to signed −364/+364; +10°/−10° to +1820/−1820.
- Przy obecnym komentarzu native `Station.Write` ustawia bit `2`. Flipped
  z komentarzem daje flagi `3`; kierunek pomiaru wstecznego wynika z FROM/TO,
  nie z Flip.
- Native DXF dzieli współrzędne szkicu w mm przez skalę 500 i zmienia znak Y.
  Przykład: `(−6000, −2000)` → `(−12, 4)`.
- `DXFWriter.WriteDXF` wewnętrznie przechwytuje wyjątki i może pozostawić ucięty
  plik bez zgłoszenia błędu wywołania. Helper sprawdza końcowe `EOF`.
  Niepełne próby powstałe przy uruchamianiu helpera nie trafiły do `cases/`.

## Reprodukcja

Środowisko: macOS arm64, Wine Staging 11.7, istniejący prefix z Microsoft .NET
2.0.50727. Wykonywalny helper oraz próbki pośrednie pozostają poza repozytorium.
Uruchamiać z katalogu repozytorium, używając nowego katalogu wynikowego.
Helper odmawia nadpisania istniejącego pliku `.top`.

```sh
env WINEPREFIX="$HOME/.local/share/pockettopo/wineprefix" WINEDEBUG=-all \
  MVK_CONFIG_LOG_LEVEL=0 wine \
  'C:\windows\Microsoft.NET\Framework\v2.0.50727\csc.exe' \
  /nologo /target:exe /r:System.Windows.Forms.dll /r:System.Drawing.dll \
  '/out:Z:\tmp\PocketTopoFixtures.exe' \
  "Z:${PWD//\//\\}\\doc\\pockettopo\\helpers\\pockettopo_fixtures.cs"

env WINEPREFIX="$HOME/.local/share/pockettopo/wineprefix" WINEDEBUG=-all \
  MVK_CONFIG_LOG_LEVEL=0 wine /tmp/PocketTopoFixtures.exe \
  "Z:${HOME//\//\\}\\.local\\share\\pockettopo\\app\\PocketTopoV1372\\PocketTopo.exe" \
  'Z:\tmp\p01-native-new'
```

Tryby diagnostyczne tego samego helpera:

```text
PocketTopoFixtures.exe --read PocketTopo.exe input.top
PocketTopoFixtures.exe --rewrite PocketTopo.exe input.top output.top
```

Do powtórzenia tabeli sufiksów wystarczy kopia `api-cardinal.top`, usunięcie jej
ostatnich czterech bajtów i doklejenie dokładnie sufiksu z tabeli. Kod wyjścia
`--read` wynosi 0 dla przyjęcia i 2 dla odrzucenia. `--rewrite` odmawia nadpisania
wyjścia. Nie umieszczać wariantów diagnostycznych obok otwieranego w GUI oryginału.

[Dowód maszynowy](native-api-evidence.json) zapisuje SHA-256 aplikacji i helpera,
hashe plików wzorcowych, dokładne wyniki wszystkich prób sufiksów, natywne
komunikaty i adresy metod. Pełnej aplikacji ani jej zdekompilowanego kodu nie
kopiujemy do repozytorium. Oczekiwania i porównanie rekordów oraz współrzędnych
znajdują się w [EXPECTATIONS.md](EXPECTATIONS.md) i `validation.json`.
