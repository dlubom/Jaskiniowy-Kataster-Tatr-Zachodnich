# Kontrola obrazów P05

Obejrzano PNG wygenerowane przez resvg 0.48.1 na macOS oraz obrazy wzorców
P01 zapisane z aplikacji. Porównanie wizualne dotyczy kierunków osi, kolejności,
kolorów, widoczności singletonów, pustego wyniku i obcięcia. Nie zastępuje
pełnego porównania współrzędnych DXF ani niezależnych testów pikseli.

- `api-drawings/plan-measurements.png` i `side-measurements.png`: siedem
  otwartych kresek, singletony, Flip drugiego odcinka, etykiety i oba łączniki
  XSection. Ułożenie zgodne z `p01/cases/api-drawings/ui-plan.png` i `ui-side.png`;
  źródłowe przesunięcie Mapping nie przesuwa geometrii eksportu.
- `native-xsection/side-measurements.png`: domiary w pięciu przekrojach,
  piony i ukośne kierunki są widoczne w całości; widoczny status pustego szkicu.
- `shadow/plan-measurements.png`: zachowana pełna rozpiętość rysunku,
  osnowa, domiar, numery stacji oraz źródłowe dopiski. `CHECK OVERLAY` jawnie
  sygnalizuje zatrzymany przez P03/P04 zerowy rekord stacji z nią samą.
- `gui-colors/plan-sketch.png`: singletony wszystkich kolorów i źródłowa
  kolejność nakładania. Przy 40 px/m punkty są małe; środek i promień
  są dokładne, a SVG umożliwia dalsze powiększanie.
- `gui-cardinal/plan-sketch.png`: widoczny napis `EMPTY SKETCH`, bez fikcyjnego
  obrysu. Wariant z pomiarami ma oddzielne warstwy i oznaczenie niepełnej osnowy.

Testy dekodują PNG niezależnie przez standardową bibliotekę Pythona (CRC,
zlib, filtry PNG) i sprawdzają: siedem dokładnych sRGB, osie i skalę,
środki punktów, źródłową kolejność nakładania, brak domknięcia otwartych linii,
białe oraz przezroczyste tło i pusty obwód obrazu. Osobna regresja kontroluje
pełny malowany zasięg znacznika XSection przy minimalnym marginesie.

Testy porównują też wszystkie 52 zachowane obrazy z ponownym renderowaniem
tego samego wejścia. Wymagane CI Linux ma przypięty resvg i nie może pominąć
tej kontroli. Zgodność bajtowa obejmuje również własne etykiety wektorowe.
Wynik zdalnego uruchomienia należy wiązać z końcowym SHA commita.
