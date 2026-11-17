# Lokalny teren pełnego KATASTER.3d

Draft z 2026-11-17 dla modelu v2.0.1 i CaveView 2.9.0. Jeden poziom **z14**,
65 kafli, `divisions: 128`, krok około **12,47 m w terenie** przy 49,25°N.
Same kafle zajmują **2 163 330 B**. Zakres pełnych kafli:
**19,797363–20,083008°E, 49,210420–49,282140°N**.

`tileSets.json` jest manifestem DTM używanym przez renderer. Każdy plik binarny
zawiera 129 × 129 próbek uint16 little-endian, wiersze od północy do południa;
wysokość w metrach = wartość / 16. Wspólne krawędzie są identyczne.
Nie ma dodatkowych poziomów ani wypełniania braków danych.

## Źródła i wysokości

- Polska: [NMT GUGiK](https://www.geoportal.gov.pl/pl/dane/numeryczny-model-terenu-nmt/),
  53 arkusze ALS z 2012 r., raster 1 m, EPSG:2180, PL-KRON86-NH.
  Zastosowano `H_EVRF2007 = H_KRON86 + dH` z oficjalnej siatki GUGiK.
- Słowacja: [DMR 5.0, GKÚ Bratislava](https://www.skgeodesy.sk/gku/produkty-sluzby/na-stiahnutie/zbgis.html),
  naziemna klasa ALS 02, kampania 2017–2022. Numeryczne wycinki WCS mają krok 5 m,
  EPSG:25834, wysokości elipsoidalne GRS80 zgodnie z
  [metadanymi](https://data.gov.sk/set/data/gmd/f3d323e2-1a59-4e20-abdd-65526038dc48).
  Zastosowano `H = h − ζ(PL-geoid2021)`.
- [Modele wysokości GUGiK](https://www.gov.pl/web/gugik/modele-danych):
  dH i PL-geoid2021, licencja [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
  DMR 5.0 również jest udostępniany na CC BY 4.0. Zmiany względem źródeł:
  transformacja wysokości, próbkowanie, triangulacja i kwantyzacja.

Docelowe wysokości są w PL-EVRF2007-NH. PL-geoid2021 obejmuje cały wycinek.
Nie oszacowano różnic realizacji/epoki ETRS89 słowackiego produktu względem
PL-ETRF2000; nie należy wnioskować o centymetrowej dokładności na Słowacji.
W miejscach nakładania się źródeł pierwszeństwo ma polski NMT, a słowacki
uzupełnia jego brak. Nie stosowano dopasowania do otworów ani stałego offsetu.
`terrainDatumShift: false`. Współrzędne i plik modelu pozostały niezmienione.

## Wynik kontroli i ograniczenia

Pełne pokrycie potwierdzono dla 18 541 stacji, 1 067 265 węzłów siatki z14
i szerszego obszaru na siatce 5 m. 279 kontroli rzeczywistych trójkątów WebGL
zgadza się z zakodowanym DTM do 0,00031 m. To kontrola renderowania:
odchylenie uproszczonej siatki od natywnego rastra dochodzi w próbkach do
13,28 m na stromym terenie. Na styku źródeł PL/SK różnice wynoszą
−4,38…+4,74 m; nie są to szczeliny między kaflami. Dokładność wysokości
w całym obszarze nie ma pełnej niezależnej kontroli terenowej.

Dokładne adresy i SHA-256 wejść zawiera [source-manifest.json](source-manifest.json),
a sumy plików tego zestawu — [SHA256SUMS](SHA256SUMS).
[Raport z kontroli i porównanie z Cesium](../../doc/reports/2026-11-17-terrain-preview.md)
oraz tabela wysokości są dostępne w repozytorium. Pełne lokalne dowody i skrypty
jednorazowego prototypu są w `.verification/2026-11-17-full-terrain/`.
Ten katalog jest ignorowany przez Git i nie występuje w świeżym klonie.

## Podgląd lokalnego draftu

Z katalogu projektu:

```sh
python3 .verification/2026-11-17-full-terrain/serve.py
```

Otwórz <http://127.0.0.1:8767/>. Serwer korzysta z gotowej lokalnej kopii strony,
CaveView i niezmienionego modelu v2.0.1. Po edycji `web/index.html` odśwież kopię
według instrukcji w `.verification/2026-11-17-full-terrain/README.md`.
Zestaw nie pobiera terenu z Cesium. Osobny
[podgląd internetowy](https://jktz-teren-z14.white-tern-1434.chatgpt.site)
wymaga konta właściciela w ChatGPT. Zmiany są w
[draft PR #165](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/pull/165);
główny publiczny widok JKTZ pozostaje bez zmian.
