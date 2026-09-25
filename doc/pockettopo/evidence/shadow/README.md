# Shadow — źródło i natywne eksporty PocketTopo

Pakiet dowodowy researchu z **2026-09-25**, przygotowany w rzeczywistym
PocketTopo **1.372** przez Wine. Zachowuje oryginał, bezpośrednie eksporty
aplikacji i obrazy jej okien. Nie jest wynikiem przyszłego konwertera JKTZ.

## Pochodzenie

- Źródło: [dlubom/test2 — 502-Schattenhohle/20120816-Shadow/shadow.top](https://github.com/dlubom/test2/blob/4c00c008a8dd441d70f9c62aa376c20b5914c7e0/502-Schattenhohle/20120816-Shadow/shadow.top).
- Przypięty commit: `4c00c008a8dd441d70f9c62aa376c20b5914c7e0`.
- Obiekt Git źródła: `b12e45894175bce110722b6f6e37ec318294e6c8`.
- Materiał roboczy pochodził z wcześniej zachowanej kopii Shadow w lokalnym
  repozytorium `caves_paint`. W tej sesji porównano bajty z ponownie pobraną
  próbką wskazanego źródła `test2`: zawartości są identyczne.
- Do otwarcia użyto kopii w osobnym katalogu. Po eksporcie nadal była
  identyczna bajtowo ze źródłem; do tego pakietu skopiowano ją bez zmian.
- Autorzy pomiarów i szkiców: nieustaleni. Trip zapisuje `2012-08-16` oraz
  deklinację `0°`; są to wartości źródłowe, nie niezależnie potwierdzona data
  ani korekta historyczna.
- Licencja źródłowa: **nieustalona**. Sprawdzone repozytorium `test2` nie
  wskazywało licencji. Zachowanie dowodu i wygenerowanie eksportów nie nadaje
  oryginalnym pomiarom ani szkicom nowej licencji; nie oznaczamy ich jako CC
  BY-SA tylko dlatego, że znajdują się w repozytorium JKTZ.

Procedura pracy z aplikacją jest w
[POCKETTOPO_MACOS.md](../../POCKETTOPO_MACOS.md), a interpretacja i dalsze
ograniczenia w [RESEARCH.md](../../RESEARCH.md).

## Zawartość i suma kontrolna

| Plik | Rozmiar, bajty | Rola |
| --- | ---: | --- |
| [shadow.top](shadow.top) | 45 983 | Niezmienione źródło v3 |
| [shadow-pockettopo.txt](shadow-pockettopo.txt) | 1 941 | Menu → Export → Text |
| [shadow-nativeP.dxf](shadow-nativeP.dxf) | 193 920 | Menu → Export → Graphics, plan |
| [shadow-nativeS.dxf](shadow-nativeS.dxf) | 66 118 | Menu → Export → Graphics, sideview |
| [pockettopo-native-sketch.png](pockettopo-native-sketch.png) | 14 089 | Fragment szkicu widoczny w aplikacji; nie pełny eksport rysunku |
| [pockettopo-graphics-options.png](pockettopo-graphics-options.png) | 10 754 | Stan dialogu Graphics podczas eksportu |

SHA256 zachowanych plików, policzone po skopiowaniu:

```text
a6554019285dcc50feadb672867c40e5bef0686551060da1670b49cde0bcfb4c  shadow.top
d579e549fedb33c7609e47b09401b030b5164db3093014f2ce3fd04cf3c7d45d  shadow-pockettopo.txt
f7af47fafcea84971fe9b03b18ed79a9bd1e24f3e192cbd1110a87c88585eabe  shadow-nativeP.dxf
f0780c305decac0f540542f254c3e7928d0df7743ba9db7061da905ec06b50eb  shadow-nativeS.dxf
a7676a730c15f1ebd868902d06c1a42a1067dc24e28b3a1e1938eb5a34851199  pockettopo-native-sketch.png
0fc24e0fdac665becfcf2e58357bb0cd4d17476cb5e7a6ff71215c81bc64f481  pockettopo-graphics-options.png
```

Kontrolę bajtów można powtórzyć poleceniem `shasum -a 256` uruchomionym dla
wymienionych plików i porównać z tabelą. Nie normalizować końców linii TXT/DXF
ani nie zapisywać `.top` po otwarciu przy samym odtwarzaniu tej próby.
`.gitattributes` oznacza źródło i natywne eksporty jako dane binarne dla Gita:
zachowuje także oryginalne CRLF i dopełnienia kolumn, bez normalizacji
i automatycznego scalania tekstu. Zmiany dowodów sprawdzamy przez pochodzenie
i sumy kontrolne.

## Ustawienia Graphics

Write Plan i Write Side włączone; suffix odpowiednio `P` i `S`; skala 1:500.
Shots i Xsections włączone, dla obu Separate Layers włączone. Labels, Grid,
All Data i All Colors wyłączone. Stan utrwala zrzut dialogu. Eksport zawiera
warstwy `Sketch`, `Shots` i `XSect` — nazwa ostatniej warstwy nie dowodzi,
że `.top` zawiera obiekt XSection.

## Wykonana kontrola

Kontrola odczytu `.top` używała struktur ze specyfikacji v3 i surowych wartości,
nie tekstowego eksportu jako źródła pomiarów. TXT odczytano według stałych
kolumn aplikacji, DXF jako pary kodu grupy i wartości. Wyniki:

- Źródło: 32 rekordy — 30 nazwanych odcinków osnowy, 1 dodatni domiar,
  1 zerowy rekord początkowy; 31 różnych nazwanych stacji. Brak referencji
  i obiektów XSection; 1 trip z datą i deklinacją podanymi wyżej.
- **Wszystkie 32 rekordy TXT** mają zgodne FROM/TO oraz identyczne dystanse.
  Kąty są zgodne z `raw × 360 / 65536` przy natywnym zaokrągleniu do 0,01°.
  Największa różnica: azymut `0,0048681640625005684°`, pochylenie
  `0,004985351562499574°`. Nie użyto tych zaokrąglonych liczb do poprawiania
  oryginalnych odczytów.
- Oba DXF mają poprawne pary kod/wartość, nagłówek `AC1002`, `$INSUNITS=4`
  i końcowe `EOF`. Zliczenia encji poniżej zgadzają się z licznościami źródła.

| Widok | Rysunek źródłowy | Encje szkicu w natywnym DXF | Dodatkowe encje DXF |
| --- | --- | --- | --- |
| Plan | 191 kresek / 4150 punktów | 189 POLYLINE, 4148 VERTEX, 2 POINT | 31 LINE, 30 CIRCLE |
| Sideview | 48 kresek / 1330 punktów | 48 POLYLINE, 1330 VERTEX | 31 LINE, 30 CIRCLE |

Dwie kreski planu mają po jednym punkcie, dlatego aplikacja wyeksportowała
je jako `POINT`, a nie `POLYLINE`. To wyjaśnia różnicę liczby polilinii bez
zakładania utraty danych.

## Granice dowodu i następny krok

**Nie wykonano jeszcze pełnego porównania współrzędnych i kolorów DXF
z każdym źródłowym wierzchołkiem ani audytu geometrii podkładu pomiarowego.**
Zgodność liczności nie dowodzi prawidłowej orientacji, skali, rozwinięcia,
rozwiązywania pętli czy wszystkich ustawień projekcji. Obraz okna pokazuje
jedynie fragment szkicu.

Przed użyciem jako pełnego wzorca geometrycznego trzeba odczytać każdą encję,
ustalić transformację jednostek/osi i porównać wierzchołki, kolejność oraz
kolory, a następnie osnowę, domiary i rozwinięcie. Shadow nie pokrywa wielu
tripów, niezerowej deklinacji, flipped, referencji ani XSection; do tych
przypadków potrzebne są osobne minimalne źródła zapisane w PocketTopo.
