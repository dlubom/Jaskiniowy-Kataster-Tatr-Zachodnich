# Przejście na Survex 1.4.24

Survex 1.4.24 z 2026-10-16 naprawia potwierdzony przez autora błąd wag
pionów z 1.4.23. CI i stabilny Docker używają oficjalnego wydania, przypiętego
w `.github/survex-version`. [NEWS upstream](https://github.com/ojwb/survex/blob/878202413cac5cbf41b88ee82c0cab72b97725ce/NEWS)
opisuje także korektę zbieżności siatki dla jawnego `DECL=`.

## Potwierdzenie poprawki pionu

Zapisz poza projektem jako `plumb.srv`:

```text
#units meters order=DAV A=D V=D decl=0
#fix 0 0 0 0
#fix 2 10.2 0 10
0 1 10 -- 90
1 2 10 90 0
```

Uruchom każdą wersją, podając pełną nazwę pliku wynikowego, np.:

```sh
cavern -o /tmp/plumb-1.4.24.3d /tmp/plumb.srv
dump3d --legs -D /tmp/plumb-1.4.24.3d
```

| Współrzędne stacji 1 (E, N, Z), m | 1.4.22 | 1.4.23 | 1.4.24 |
| --- | --- | --- | --- |
| Wynik | 0,09; 0,00; 10,00 | 0,12; 0,00; 10,00 | 0,09; 0,00; 10,00 |

Względna wariancja kątowa pionu wróciła z `0.5` do `0.25` wariancji
zwykłego kąta. Kontrola zwykłych odcinków daje tę samą geometrię we wszystkich
trzech wydaniach. Kontrola miękkich fixów RMS zachowuje wynik 1.4.23:
naprawa pionu nie cofa zmiany skali domyślnych wariancji pomiarów względem
jawnych niepewności fixów.

## Wynik dla całego JKTZ

Porównano te same pliki pomiarowe i snapshot otworów z commitu
`990302b` lokalnymi wersjami 1.4.22, 1.4.23 i 1.4.24. Każda kompilacja
zakończyła się bez błędów i ostrzeżeń. Liczby stacji (18540), odcinków (18662),
pętli (198) i komponentów (76) są jednakowe; nie przybyły ani nie ubyły
nazwane stacje, a ich flagi pozostały takie same.

| Długość, m | 1.4.22 | 1.4.23 | 1.4.24 |
| --- | ---: | ---: | ---: |
| Przed wyrównaniem | 70053,50 | 70053,50 | 70053,50 |
| Po wyrównaniu | 69943,68 | 69945,04 | 69943,37 |

Względem 1.4.23 zmieniło się 7448 nazwanych stacji. Największa różnica
wynosi **10,413 m** dla `Wysoka7Progow:W7-144`:
E/N/Z z `419496,55 / 5453965,50 / 1613,79` na
`419495,60 / 5453955,13 / 1613,78` m. Względem 1.4.22 największa
różnica wynosi **10,067 m**. Rozdzielczość porównania `.3d` to 1 cm.

Większa różnica pochodzi z osobnej naprawy `DECL=`: Survex uwzględnia teraz
zbieżność siatki również przy jawnej deklinacji, przeliczając kierunki do
siatki wynikowego układu UTM. Sama naprawa wag pionów nie może więc
przywrócić całej geometrii 1.4.22.

Potwierdzono to kontrolną kompilacją oficjalnych źródeł 1.4.24. Niezmieniony
build odtworzył pełny dump instalacji lokalnej, poza polami czasu. Następnie
wyłączono tylko dodane wywołanie `get_convergence()` przy `DECL=`. Względem
1.4.22 pozostało wtedy 26 różnic po 1 cm, wyłącznie w Bandziochu Kominiarskim,
gdzie występują jawne RMS fixów. Ten mechanizm wag potwierdza osobny test
miękkich fixów. Wariant diagnostyczny nie jest używany w instalacji ani CI;
jego tymczasowe źródła i binaria usunięto po badaniu.

To wyjaśnienie różnicy wersji, bez oceny dokładności rzeczywistych pomiarów.
Aktualizacja nie zmienia plików SRV, WPJ, otworów ani `_RAW`. Brak pliku SRV,
choć od 1.4.24 jest ostrzeżeniem Survexa, nadal blokuje pełną walidację JKTZ.
