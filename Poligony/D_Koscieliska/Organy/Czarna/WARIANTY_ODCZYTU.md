# Czarna — wpływ niepewnych odczytów na koniec ciągu

Aktualizacja obliczeń i niezależnej weryfikacji: 2026-09-13, po porównaniu Gemini.
Pierwszą wersję analizy wykonano 2026-09-12.
Źródło: [CZ_GL_R.SRV](CZ_GL_R.SRV), odcinki 0–76.
Analiza dotyczy czterech nierozstrzygniętych odczytów opisanych w
[raporcie digitalizacji](DIGITALIZACJA_RAPORT.md). Nie wykorzystuje GPS
ani współrzędnych Borowca do wyboru cyfr.

## Wynik i kolejność dalszej kontroli

**Najpierw należy wyjaśnić azymut 39→40.** Jego dwa odczyty powodują
około 9,86 m różnicy na końcu ciągu. Największa odległość między końcami
wszystkich 16 analizowanych wariantów wynosi około 12,12 m.
To zakres wynikający z podanych alternatyw transkrypcji, nie przedział
ufności ani oszacowanie całkowitej dokładności pomiarów terenowych.

| Priorytet kontroli | Odcinek i alternatywa | Przesunięcie końca w 3D | Co zmienia się w geometrii |
| --- | --- | ---: | --- |
| 1 | 39→40: A 75° → 25° | 9,86 m | Położenie poziome od stacji 40 do końca. |
| 2 | 49→50: A 68° → 88° | 2,39 m | Położenie poziome od stacji 50 do końca. |
| 3 | 71→72: V −1° → +1° | 0,70 m | Wysokość od stacji 72 do końca; położenie poziome bez zmiany. |
| 4 | 29→30: D 13,80 → 13,60 m | 0,20 m | Długość i małe przesunięcie przestrzenne od stacji 30. |

Po [ponownym odczycie i porównaniu Gemini](POROWNANIE_GEMINI.md) przyjęto
75° jako preferowany roboczy A39, zachowując 25° jako alternatywę. Zmiana
opiera się na grafii skanu, nie na wpływie na wynik. Pozostałe D/A/V zachowano.

## Warunki eksperymentu

- Początek: stacja 0 w lokalnym `(0,0,0)`.
- Koniec: stacja 76, opisana w źródle jako „Koniec Colorado”. Nie jest to
  punkt III otworu. Dwa odcinki boczne 6→a→b nie należą do trasy 0–76.
- Metry, azymut i upad w stopniach; roboczy brak korekty `DECL=0`.
- Brak fixów GNSS, pętli, wyrównania i połączenia z aktywnym katastrem.
- E oznacza lokalną oś wschodnią wynikającą z zapisanych azymutów, N lokalną
  północną, Z wysokość względną. Nie są to współrzędne UTM ani GNSS.
- Uwzględniono tylko cztery wymienione alternatywy. Nie uwzględniono błędów
  instrumentów, ustawienia punktów, nieznanej daty, deklinacji ani orientacji.

Dla każdego odcinka liczone są przyrosty:

```text
dE = D * cos(V) * sin(A)
dN = D * cos(V) * cos(A)
dZ = D * sin(V)
```

Kąty przed funkcjami trygonometrycznymi są zamieniane na radiany.
Przyrosty sumowane są wzdłuż jednoznacznego łańcucha 0–76. Przesunięcia
wariantów liczone są względem wersji roboczej; porównanie każdej pary
wariantów określa największą odległość pomiędzy ich końcami.

## Odtworzenie wyników

Pełne współrzędne, parametry wszystkich wariantów, przesunięcia E/N/Z,
poziome i 3D oraz największą odległość zawiera
[WARIANTY_ODCZYTU.json](WARIANTY_ODCZYTU.json). Wynik wylicza narzędzie
[czarna_variants.py](../../../../src/jktz/czarna_variants.py).
Z katalogu głównego repozytorium:

```sh
uv sync --locked
uv run jktz-czarna-warianty --output Poligony/D_Koscieliska/Organy/Czarna/WARIANTY_ODCZYTU.json
uv run pytest -q tests/test_czarna_variants.py
```

Narzędzie czyta SRV bez jego modyfikowania. Akceptuje wyłącznie opisany
układ 78 odcinków, metrów, stopni i `DECL=0`; zmiana dyrektyw, daty pomiaru
lub czterech wartości bazowych wymaga ponownej oceny założeń. Opcja `--input`
pozwala podać inną kopię tego samego formatu, ale nie służy do analizy
dowolnego pliku Walls. Nazwę wejścia i SHA-256 zapisano w JSON.

SHA-256 pliku SRV użytego do obliczeń i niezależnych kompilacji:

```text
2c7dda785dee1444c6e99133d183640465dc7a2bd6aae9c3a480698097feb834
```

Najdalsza para to `0010` i `1101`: 12,120658 m w 3D, w tym
12,099930 m poziomo. Liczby podano z dodatkowymi cyframi, aby umożliwić
kontrolę obliczeń, a nie sugerować dokładność odczytu ani pomiaru.

## Niezależna kontrola wszystkich wariantów w Survex

Każdy wariant zapisano do osobnej tymczasowej kopii SRV, zmieniając tylko
odpowiednie pola D/A/V. Wszystkie 16 kopii skompilowano poleceniem `cavern`
(Survex 1.4.22), a położenie stacji 76 odczytano narzędziem `dump3d`.
Kompilacje zakończyły się bez błędów i ostrzeżeń. Automatyczny lokalny
początek w stacji 0 był oczekiwany przy braku fixów.

Porównano wszystkie 48 składowych E/N/Z narzędzia z wynikami tych kompilacji.
Największa różnica bezwzględna wyniosła 0,004899 m, mieszcząc się
w zaokrągleniu `dump3d` do 0,01 m. Potwierdzono identyczny SHA-256 wejścia
i zgodność czterech parametrów każdego wariantu. Oryginalny SRV nie zmienił się.
To kontrola geometrii transkrypcji; nie zastępuje ponownego odczytu źródła.

W identyfikatorze wariantu kolejne bity oznaczają użycie alternatywy
odczytu odpowiednio: **29 D, 39 A, 49 A, 71 V**. `0` zachowuje odczyt
roboczy, `1` stosuje alternatywę. Od tej aktualizacji drugi bit oznacza
**0 = 75°, 1 = 25°**; we wcześniejszej wersji było odwrotnie. Parametry
i SHA-256, a nie sam identyfikator, określają wariant. Liczby poniżej są wynikiem `dump3d`
zaokrąglonym do 0,01 m; nie oznacza to centymetrowej dokładności pomiaru.

| Wariant | E końca [m] | N końca [m] | Z końca [m] |
| --- | ---: | ---: | ---: |
| 0000 — roboczy | 770,26 | 261,48 | 17,45 |
| 0001 | 770,26 | 261,48 | 18,15 |
| 0010 | 770,76 | 259,14 | 17,45 |
| 0011 | 770,76 | 259,14 | 18,15 |
| 0100 | 763,92 | 269,03 | 17,45 |
| 0101 | 763,92 | 269,03 | 18,15 |
| 0110 | 764,42 | 266,69 | 17,45 |
| 0111 | 764,42 | 266,69 | 18,15 |
| 1000 | 770,07 | 261,43 | 17,46 |
| 1001 | 770,07 | 261,43 | 18,16 |
| 1010 | 770,57 | 259,09 | 17,46 |
| 1011 | 770,57 | 259,09 | 18,16 |
| 1100 | 763,73 | 268,99 | 17,46 |
| 1101 | 763,73 | 268,99 | 18,16 |
| 1110 | 764,23 | 266,65 | 17,46 |
| 1111 | 764,23 | 266,65 | 18,16 |

## Co dalej

Najbardziej przydatne byłoby rozstrzygnięcie grafii na skanie `123630`
w ostatnim wierszu lewej strony (39→40), a potem na prawej stronie
w wierszu 49→50. Jeśli obecne fotografie nie wystarczą, potrzebny jest
oryginalny dziennik, lepsza fotografia albo niezależny zapis tych samych
obserwacji. Dopasowanie do otworów może służyć diagnozie wariantu, ale nie
jest dowodem, jaka cyfra znajduje się na kartce.

Do czasu ustalenia pochodzenia dziennika i nawiązań nadal nie porównujemy
jego stacji 76 z punktem GPS III otworu. Bieżący stan kolejnych etapów
prowadzi [STAN_PRAC.md](STAN_PRAC.md).
