# Przejście na Survex 1.4.23

Porównanie z 2026-10-15 obejmuje te same dane projektu i oficjalne wydania
1.4.22 oraz 1.4.23. Raport historyczny dotyczy niezmodyfikowanego wydania 1.4.23.
Autor potwierdził błąd proporcji wariancji pionów; poprawka jest w 1.4.24.
Aktualny wynik opisuje [weryfikacja 1.4.24](SURVEX_1_4_24.md).

## Nowe ostrzeżenia o notatkach

1.4.23 wykrywa także zwykłe `#note`/`#flag`, których stacji nie użyto
w pomiarach ani fixach. 1.4.22 pomijał takie osierocone odwołania, jeśli
nie nadawały flag wejścia lub eksportu. W projekcie ujawniło to cztery notatki:

| Plik SRV | Nieużywana stacja |
| --- | --- |
| `BK-B2D-S` | `L019014` (także `#Flag`) |
| `LITPLYTB` | `LTII20` |
| `SBB2` | `LTsbb0`, `LTsbb26` |

Wpisy zachowano jako komentarze. Podobne nazwy istniejących stacji nie są
dowodem ich tożsamości; notatek nie przypisano do innych punktów. Wartości
pomiarów i materiały `_RAW` pozostały bez zmian. Po tej zmianie kompilacja
1.4.23 nie emituje tych ostrzeżeń.

## Różnice wyrównanej geometrii

| Wynik kompilacji | 1.4.22 | 1.4.23 |
| --- | ---: | ---: |
| Stacje / odcinki / pętle | 18540 / 18662 / 198 | 18540 / 18662 / 198 |
| Długość przed wyrównaniem | 70053,50 m | 70053,50 m |
| Długość po wyrównaniu | 69943,68 m | 69945,04 m |

Współrzędne w wyjściu `dump3d` zmieniły się dla 6225 stacji, w tym 5957
nazwanych. Wszystkie 84 punkty oznaczone `FIXED` zachowały współrzędne.
Największe przesunięcie nazwanej stacji wyniosło około **3,049 m**:
`WielkaSniezna:Wrocl:wr106`, delta E/N/Z = **−2,76 / +1,29 / +0,11 m**.
Zakomentowanie osieroconych notatek nie zmienia geometrii w ramach 1.4.23.

Przyczynę potwierdzono kontrolnymi kompilacjami oficjalnego archiwum źródeł
1.4.23. Nowy blok domyślnych wariancji w
[`walls_initialise_settings`](https://github.com/ojwb/survex/blob/3e23b190bc151592e1b65044871f1b1dec31dc79/src/datain.c)
skaluje błędy odczytów i odległości. Dla `Q_PLUMB` i `Q_LEVEL` ustawia
`angle_variance * 0.5`; wcześniejszy stosunek ich wariancji do wariancji
zwykłych kątów wynosił `0.25`. Zmienia to względne wagi przy wyrównaniu.

Testowa zmiana obu mnożników na `0.25` przywróciła poprzednią łączną długość
po wyrównaniu; pozostały różnice 1 cm dla 26 nazwanych stacji. Wyłączenie
całego nowego bloku domyślnych wariancji odtworzyło wszystkie współrzędne
stacji i odcinków z 1.4.22. To eksperyment diagnostyczny poza repozytorium;
projekt nie dostarcza zmodyfikowanego Survexa. Przyczyna różnicy jest ustalona,
a autor później potwierdził pomyłkę współczynnika 0.5 zamiast 0.25
i naprawił ją w 1.4.24.

## Minimalna reprodukcja

Zapisz poza projektem jako `plumb.srv`:

```text
#units meters order=DAV A=D V=D decl=0
#fix 0 0 0 0
0 1 10 0 90
1 2 10 90 0
2 0 14 270 -45
```

Skompiluj osobno każdą wersją, np. `cavern -o /tmp/plumb-1.4.23.3d plumb.srv`,
a następnie odczytaj wynik przez `dump3d /tmp/plumb-1.4.23.3d`.

| Stacja | 1.4.22 (E, N, Z), m | 1.4.23 (E, N, Z), m |
| --- | --- | --- |
| `1` | −0,03; 0,00; 9,98 | −0,04; 0,00; 9,98 |
| `2` | 9,94; 0,00; 9,91 | 9,93; 0,00; 9,92 |

Zmiana pionowego odczytu `90` na `89.99` daje w tym przykładzie jednakowe
współrzędne w obu wersjach, z dokładnością zapisu `.3d` (1 cm).
