# Teren widoku 3D JKTZ

Jeden poziom z14 dla CaveView 2.9.0: 65 kafli, `divisions: 128`, krok około
12,47 m przy 49,25°N, łącznie 2 163 330 B. Zasięg pełnych kafli:
**19,797363–20,083008°E, 49,210420–49,282140°N**.

Źródła i wysokości:

- [NMT GUGiK](https://www.geoportal.gov.pl/pl/dane/numeryczny-model-terenu-nmt/):
  53 arkusze ALS2012, 1 m, EPSG:2180, PL-KRON86-NH;
  `H_EVRF2007 = H_KRON86 + dH` z oficjalnej siatki GUGiK.
- [DMR 5.0 GKÚ Bratislava](https://www.skgeodesy.sk/gku/produkty-sluzby/na-stiahnutie/zbgis.html):
  numeryczne wycinki WCS 5 m, EPSG:25834, elipsoidalne h GRS80;
  `H = h − ζ(PL-geoid2021)`.
- DMR 5.0 i [modele transformacji GUGiK](https://www.gov.pl/web/gugik/modele-danych)
  są dostępne na [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
  Przetworzenie obejmuje transformację wysokości, próbkowanie i kwantyzację.

Wysokości wynikowe: PL-EVRF2007-NH. Poprawne próbki PL mają pierwszeństwo,
SK uzupełnia ich brak. Bez wypełniania NoData i dopasowania do otworów;
`terrainDatumShift: false`. Nie oszacowano różnic realizacji/epoki ETRS89 w SK.
Niezależna kontrola wysokości nie obejmuje całego obszaru. W kontrolach
odchylenie uproszczonej siatki od rastra dochodzi do 13,28 m na stromym terenie,
a różnice źródeł przy przejściu PL/SK do 4,74 m.

Format DTM: 129×129 uint16 little-endian, wiersze od północy do południa,
wysokość w metrach = wartość /16. Wspólne krawędzie są identyczne.
[tileSets.json](tileSets.json) jest konfiguracją renderera,
[source-manifest.json](source-manifest.json) zapisuje pochodzenie i SHA-256 wejść,
a [SHA256SUMS](SHA256SUMS) — sumy plików tego zestawu.
