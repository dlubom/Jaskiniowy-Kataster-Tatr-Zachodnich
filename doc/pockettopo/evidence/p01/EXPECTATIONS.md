# P01: oczekiwania i niezależny audyt wzorców

Stan **2026-09-25**: sześć przypadków sprawdzono rekord po rekordzie.
Wynik maszynowy: [validation.json](validation.json). Każdy katalog ma
`expected.json` z dosłownymi oczekiwaniami dla źródła, kodowaniem napisów,
mapowaniem kolorów DXF i współrzędnymi prostej osnowy.

## Skąd pochodzą oczekiwania

Dla czterech `api-*` punktem wyjścia są **jawne argumenty wywołań** w
[pockettopo_fixtures.cs](../../helpers/pockettopo_fixtures.cs), odczytane
niezależnie od inspektora bajtów. Helper tworzy obiekty oryginalnej aplikacji;
serializację i eksport wykonuje PocketTopo. Oczekiwania nie są kopią zdekodowanego
`.top` ani dowodem opartym wyłącznie na odczycie i zapisie jednym narzędziem.

Dla `gui-cardinal` oczekiwano jednego ręcznie wprowadzonego odcinka
`0 → 1, 10.000 m, 0°, 0°`, widocznego w `table.png`.
Dla `gui-colors` znane były działania w GUI i końcowy szkic, lecz **dokładne
współrzędne kliknięć nie były ustalone wcześniej w mm**. Zapisano je jako
obserwację zamrożonego źródła i sprawdzono niezależnie w natywnym DXF.
Precyzyjny wzorzec wierzchołków zadanych przed zapisem stanowi `api-drawings`.
Ta różnica pochodzenia pozostaje w `expected.json`.

Próba użyła osobnego inspektora binarnego zgodnego ze schematem v3, parsera
par kod/wartość DXF i ręcznych oczekiwań. Inspektor nie jest przyszłym parserem
P02 ani zależnością projektu. Skrypt roboczy działał w `/tmp`; trwałe wyniki,
wartości oczekiwane i materiały natywne są tutaj w repozytorium.

## Zakres policzony

| Przypadek | Trip | Shot | Referencje | Wierzchołki szkicu plan / bok | XSection plan / bok |
| --- | ---: | ---: | ---: | ---: | ---: |
| [gui-cardinal](cases/gui-cardinal/expected.json) | 0 | 1 | 0 | 0 / 0 | 0 / 0 |
| [gui-colors](cases/gui-colors/expected.json) | 0 | 1 | 0 | 9 / 0 | 0 / 0 |
| [api-cardinal](cases/api-cardinal/expected.json) | 1 | 11 | 0 | 0 / 0 | 0 / 0 |
| [api-trips-ids](cases/api-trips-ids/expected.json) | 3 | 4 | 0 | 0 / 0 | 0 / 0 |
| [api-references](cases/api-references/expected.json) | 1 | 1 | 2 | 0 / 0 | 0 / 0 |
| [api-drawings](cases/api-drawings/expected.json) | 1 | 2 | 0 | 22 / 22 | 2 / 2 |

Łącznie: **6 tripów, 20 pomiarów, 2 referencje, 53 wierzchołki i 4 XSection**.
Inspektor odczytał 538 pól skalarnych/napisowych, łącznie z licznikami,
prefiksami długości i terminatorami rysunków. Każdy rekord źródła porównano
ze strukturą oczekiwaną, bez tolerancji dla wartości surowych. Ogony zapisano
osobno: wszystkie sześć plików kończy się dokładnie czterema zerami po
terminatorze sideview. Ich znaczenie i dopuszczalne zakończenia opisuje
[NATIVE_API.md](NATIVE_API.md).

Sprawdzono wszystkie **157 encji** w 12 natywnych DXF: typ, kolejność,
kolor, współrzędne, promienie kół i obecne linie przerywane. Każdą polilinię
sprawdzono na domknięcie: brak ustawionej flagi `70 & 1`; kolejności wierzchołków
nie zmieniono. Pojedynczy wierzchołek jest natywnie eksportowany jako `POINT`.

## Pola binarne i tekst

`api-cardinal` sprawdza azymuty `0/90/180/270/358/2/180`, oba piony, ujemne
pochylenie, odczyt odwrotny, splay z niezdefiniowanym TO i zerowe powiązanie.
Roll zawiera `0/64/128/192/255`. Nie przepisujemy stopni jako liczb surowych:
pełen obrót to 65536, roll ma pełen obrót 256.

Przykładowo `358° → -364`, `2° → 364`, `10° → 1820`, `-20° → -3641`
po natywnym zaokrągleniu i zapisie signed Int16. Współrzędne, odległości,
flagi, indeks tripu, komentarze, kolejność, nagłówek i mapowania też zostały
porównane. Pełne wartości znajdują się w sześciu plikach `expected.json`.

`api-trips-ids` rozróżnia zwykłe `0` (`-2147483647`) od `0.0` (`0`),
`12.65535` (`851967`), `13.0` (`851968`) i niezdefiniowanego ID
(`-2147483648`). Występuje zarówno `tripIndex=-1`, jak i indeksy `0/1/2`.
Komentarze zachowują UTF-8, w tym tekst polski i długi komentarz z 70 znakami
`ą`: **171 bajtów UTF-8, prefiks długości `ab 01`**. Sprawdzono surowe bajty
każdego napisu i cały jego prefiks długości.

Trip ticks są dokładnie `630822816000000007`, `639259776000000009`,
`639260640000000001`; końcowe `7/9/1` oznaczają zachowane części 100 ns.
Daty 2000-01-01, 2026-09-26 i 2026-09-27 są syntetycznymi wartościami
wzorcowymi, nie dowodem dat rzeczywistych pomiarów.

Jawne deklinacje `5°/-3.5°/-2°` zapisują się jako `910/-637/-364`.
**`declination_raw=-32768` jest znacznikiem trybu automatycznego**, a nie
korektą `-180°`. Natywny TXT pokazuje tutaj `Auto: 0.00`; bez ustalonego
układu i pochodzenia korekty nie należy traktować tego zera jako potwierdzonej
deklinacji terenowej.

`api-references` zachowuje E/N Int64 przekraczające zakres Int32:
`(-4000000001, -5000000002, -1250)` i
`(6000000003, 7000000004, 1500250)` w mm. Obie referencje celowo dotyczą
stacji `0`; nie ustanawiają geodezyjnie spójnych fixów ani CRS. TXT zaokrągla
E/N/Z do 0.01 m, więc nie może zastępować danych surowych.

Natywne TXT porównano w całości semantycznej: liczba i kolejność tripów,
referencji i pomiarów; FROM/TO, D/A/V, przypisanie tripu, Flip i pełne komentarze.
Eksporty z okna aplikacji `native-ui.txt` sprawdzono tymi samymi oczekiwaniami;
różnica względem `native.txt` z API to nagłówek nazwy pliku. Aktualna lista
sprawdzonych plików jest w `validation.json`. Dla `api-drawings` zamiast
ponownego TXT wykonano eksport DXF z GUI: `native-uiP.dxf` i `native-uiS.dxf`
są identyczne bajtowo z dwoma zweryfikowanymi DXF API. Te dwa dodatkowe
pliki nie zwiększają sumy 157 encji w 12 głównych eksportach.

TXT nie zawiera roll, części ticks, mapowań ani szkiców i zaokrągla kąty.
Zgodność TXT dotyczy tylko pól, które ten format wystawia.

## Szkic i skala DXF

Wszystkie eksporty mają skalę **1:500**. Dla każdego źródłowego punktu szkicu
`(x,y)` w mm sprawdzono dokładnie:

`DXF.X = x / 500`, `DXF.Y = -y / 500`.

W `api-drawings` dla koloru `i=1…7`, `x=-6000+(i-1)*2000`, plan zawiera
`(x,-2000),(x+500,-1000),(x+1500,-1500)`; bok ma przeciwne znaki Y.
Singletony to `(-7500,3500)` czarny w planie i `(7500,-3500)` pomarańczowy
w boku. Nie dopisano wierzchołka zamykającego.

Mapowania `overview=(-1234,5678)`, `plan=(-100,200)`, `side=(300,-400)`
mają skalę 500. Natywny eksport pozostawia geometrię szkicu zgodną z powyższą
transformacją: przesunięcia zapamiętanego widoku nie przesuwają wierzchołków.

Zaobserwowana w obu niezależnych zestawach mapa indeksów PocketTopo → DXF ACI:

| Kolor PocketTopo | 1 black | 2 gray | 3 brown | 4 blue | 5 red | 6 green | 7 orange |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| DXF kod 62 | 0 | 9 | 32 | 5 | 1 | 3 | 30 |

To indeksy ACI eksportera; nie są jeszcze ustaleniem dokładnych RGB ekranu.

`gui-colors` świadomie zachowuje **9 punktów i wszystkie 7 kolorów**. Gray i
green występują po dwa razy. Najnowszy brown jest pierwszy w zapisanej liście;
orange i green nakładają się w `(6100,-1400)`. Próba GUI Undo nie usunęła
nadmiarowego green z trwałego źródła. Nie usuwamy go ani nie zmieniamy kolejności
w celu uzyskania estetyczniejszego wzorca. Całą listę zawiera `expected.json`.

## Flip, XSection i granice osnowy

`api-drawings` ma dwa odcinki po 10 m, najpierw na północ, potem na wschód.
Drugi ma Flip: w planie stacje w mm to `(0,0),(0,10000),(10000,10000)`,
a na rozwinięciu `(0,0),(10000,0),(0,0)`. Kierunek FROM/TO i azymut źródłowy
nie zostały odwrócone. Sprawdzono wszystkie współrzędne natywnych odcinków
i markerów, a nie tylko łączną długość.

Każdy widok ma XSection stacji `1`, `direction=-1`, i stacji `2`,
`direction=16384`. Zweryfikowano surowe pozycje i pola oraz natywne linie
łączące znacznik z odpowiednią stacją w danym widoku. Plan ma początki DXF
`(-10,12),(10,12)` i końce `(0,20),(20,20)`; bok ma początki
`(-10,-12),(10,-12)` i końce `(20,0),(0,0)`. **Na tych stacjach nie ma
splays**, więc ta próba nie dowodzi ogólnej projekcji geometrii przekroju.

W `api-cardinal` natywna aplikacja składa trzy powtórzenia A1/A2/A3 do jednej
osnowy. Jej plan daje `ΔN=4922 mm`, rozwinięcie `ΔH=4924 mm`, a oba
`ΔZ=868 mm`. Niezależny rachunek z zapisanych kątów daje po zaokrągleniu te
wartości: plan uśrednia składowe kierunkowe, a rozwinięcie poziome długości.
**Nie przyjmujemy tego jako wzorca średniej z PRD**: przyszły konwerter ma
średnią kołową azymutu oraz arytmetyczną D/V po normalizacji. Wszystkie 11
odczytów pozostaje w `.top`, TXT i oczekiwaniach. Pozostałą prostą osnowę,
splays, piony i zerowe odcinki również porównano współrzędna po współrzędnej.

Sześć małych przypadków nie rozstrzyga pętli, rozgałęzień, niejednoznacznych
średnich, wszystkich uszkodzeń ani projekcji pełnych XSection. Te kwestie
pozostają w odpowiednich etapach P02–P05. Wzorce nie upoważniają do zmiany
surowych pomiarów lub do automatycznego utożsamienia stacji.
