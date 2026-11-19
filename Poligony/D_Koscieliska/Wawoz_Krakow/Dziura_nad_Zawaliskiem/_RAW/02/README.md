# Dziura nad Zawaliskiem — roboczo przypisane pomiary DOC

- **Status materiału:** częściowy
- **Pochodzenie danych:** Oryginalny załącznik od Z. Tabaczyńskiego do D. Lubomskiego z 11.04.2014, zatytułowany „pomiary w Rzędach Tomanowych.doc”.
- **Autorzy pomiarów:** Nieustaleni; materiał przekazał Z. Tabaczyński.
- **Daty pomiarów:** nieznane
- **Data pozyskania:** 2014-04-11
- **Dodał do _RAW:** Dariusz Lubomski, 2026-11-09
- **Licencja źródłowa:** nieznane
- **Kompletność:** Pełny DOC: 5 + 5 + 2 rekordy jaskiniowe i 4 powierzchniowe. Przypisanie tabeli do tej jaskini jest najsilniejszą hipotezą; brak jawnej legendy nazw i numerów otworów oraz oryginalnej książeczki.

## Zawartość

- `2014-04-11/pomiary w Rzędach Tomanowych.doc` — pełny niezmieniony dokument źródłowy.

## Najbardziej logiczna identyfikacja — robocza

**Szczelina nad Zawaliskiem → Dziura nad Zawaliskiem (T.F-10.18)**, obiekt GPS
`KSW-0063`. To mocny wniosek z porównania źródeł, nie odnalezione
potwierdzenie aliasu przez autora. Numer w metadanych SRV oznacza tę hipotezę.

Kolejne odcinki ku NNE, NNW, stromy odcinek ku WSW i rozwidlenie w punkcie 3 odpowiadają planowi oraz rozwiniętemu przekrojowi. Suma 22,98 m odpowiada 23 m w opisie; położenie punktu 4 odpowiada oznaczeniu −10,8 m. Porównano literalne DAV z wydrukowaną siatką planu 0–10 m,
bez dopasowania skali, obrotu czy przesunięcia do poligonu.
Podstawy: [PDF autora](../01/README.md) oraz plan/przekrój PIG
(1236/1237, podpis Z. Tabaczyński, 2000) w
[rekordzie T.F-10.18](https://jaskiniepolski.pgi.gov.pl/Details/Information/1728).
PDF i rysunki są opracowaniami tego samego autora, nie niezależnymi pomiarami.

[Roboczy DNZ_ROB.SRV](../../DNZ_ROB.SRV) zawiera 5/5 odcinków
tej tabeli. Cztery dowiązania powierzchniowe pozostają osobno w DOC;
[hipoteza numeracji i jej problemy](../../../../../D_Tomanowa/Rzedy_Tomanowe/Dziura_X/_RAW/01/README.md#dowiązania-powierzchniowe--hipoteza).

## Niezgodności tego ciągu

Odcinek 3→5: DAV 7,73 / 343 / +51 daje ΔN = 4,6521, ΔE = −1,4223, ΔH = 6,0073 m; DOC podaje 4,26 / −1,34 / 6,00 m. Końcowe współrzędne poziome różnią się o około 0,411 m. Nie ma podstawy do wyboru innego odczytu D, A lub V. Głębokość 10,8647 m z DAV różni się od 10,84 m w obliczeniach DOC. Opis PDF/PIG podaje dla wejściowego korytarza kierunek ku S, podczas gdy plan i azymuty prowadzą zasadniczo ku N; nie odwrócono azymutów.

## Zakres transkrypcji i ograniczenia

Plik SRV jest wyłącznie roboczym zapisem: metadane mieszczą się w komentarzu
blokowym, a wszystkie dyrektywy i pomiary są poprzedzone `;`. Nie ma wpisu
w `KATASTER.wpj`, fixa ani utożsamienia stacji. Zachowano źródłowe numery
stacji i literalne D/A/V; przecinki dziesiętne zastąpiono kropkami.
Kolumny przyrostów i współrzędnych z DOC są obliczeniami, nie dodatkowymi
pomiarami. Oryginał pozostaje niezmieniony.

Sam DOC nie podaje daty, zespołu ani odniesienia azymutów. Metadane pliku
z 16.06.2002 nie są datą pomiaru. PDF opisuje pomiar 11.11.2000 przez
P. Gruszkę i Z. Tabaczyńskiego przyrządem Topo-Vulcan; przypisanie tych
metadanych do tabeli DOC wymaga potwierdzenia. Dlatego w roboczym SRV
pozostają `nieznane`, bez `#date` i bez wymyślonej deklinacji.

[GPS v2.0.2](https://github.com/dlubom/gps-kataster-obiektow-tatr/releases/tag/v2.0.2)
wybiera dla KSW-0063 i KSW-0103 identyczne nieweryfikowane współrzędne TPN:
lat 49.2311111198, lon 19.89472216, wysokość 1802.850138 m, bez określonej
dokładności. Nie rozdzielają one wejść. Alternatywne rekordy PIG również
mają wspólną pozycję poziomą, lecz wysokości 1810/1800 m. PDF podaje zarazem
relację „około 5 m” między otworami. Nie zastąpiono GPS ani nie przesunięto
otworów na podstawie wygodniejszego wariantu.

## Warunki włączenia do modelu

Potwierdzić alias i metadane tabeli, ustalić powiązanie numerów otworów
z nazwami i stacjami oraz uzyskać rozdzielone, udokumentowane zakotwiczenie
w katalogu GPS. Rozbieżności obliczeń wyjaśnić z autorem lub książeczką,
zachowując odczyty źródłowe. Dopiero wtedy rozstrzygnąć aktywację SRV.

Pełne kopie DOC w katalogach nazw roboczych i rozpoznanych jaskiń stanowią
jeden przekaz. SHA-256: `c9b62bf58212ca7ac70896cf098786c06be0217ad6b1ad42963b0bc8802e1ee1`.
