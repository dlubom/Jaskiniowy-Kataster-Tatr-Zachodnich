# PocketTopo: granice walidacji kompilacji

Biblioteczny `export_surveys` tworzy teksty SRV/SVX i raport z
`validation=not_run_by_library`. Sam eksport nie sprawdza spójności sieci
ani nie gwarantuje pełnej geometrii. Polecenie `convert` uruchamia dodatkowo
[walidator kompilacji](../../src/jktz/pockettopo/compilation.py).

SRV i SVX są kompilowane osobno przez `cavern`, a wyniki odczytywane przez
`dump3d --legs`. To dwa wejścia do Survex, nie kontrola w programie Walls.
Wersje narzędzi, wyjście procesów i wyniki kontroli trafiają do
`exports.validation` w raporcie.

## Warunki kompletności

Kod procesu 0 nie wystarcza. Walidator wymaga braku ostrzeżeń, poprawnego
pliku 3D i kompletnego odczytu `dump3d`. Sprawdza nazwane stacje aktywnych
grup, odcinki dla odrębnych par stacji, domiary oraz zerowe powiązania.
Powtórzenia tej samej pary mogą zostać scalone przez kompilator; zbieżne
współrzędne różnych par nie dowodzą ich tożsamości ani dopuszczalnego scalenia.

Porównanie SRV/SVX obejmuje położenia wszystkich oczekiwanych stacji i
geometrię linii po odjęciu wspólnego punktu odniesienia. Tolerancja
`0.010001 m` uwzględnia centymetrowy zapis 3D i odejmowanie zaokrąglonych
współrzędnych. Nie określa dokładności pomiaru terenowego.

Brak narzędzia, timeout, sygnał zakończenia, ostrzeżenie, brakujące stacje,
niepełne lub różne odcinki oznaczają nieudaną walidację. Pusty eksport nie
jest sukcesem walidacji geometrii. W poprawnie zapisanym pakiecie takie
ograniczenie daje `conversion_complete: false` i kod CLI 2.

Walidacja obejmuje tylko pomiary aktywne. Wstrzymane i świadomie wyłączone
rekordy, osadzenie szkicu, daty, CRS oraz historyczna poprawność korekt mają
odrębne kontrole. Nawet zgodne wyniki obu formatów nie potwierdzają tych
założeń; zasady odczytu całości raportu opisuje [CLI](CLI.md).

## Historyczne przypadki graniczne

W próbach **cavern 1.4.22 na macOS** z 2026-09-25:

- rozłączna sieć, także po wstrzymaniu łącznika Auto, dawała kod 0 z
  ostrzeżeniem `Survey not all connected to fixed stations`; część stacji
  i odcinków nie trafiała do `.3d`;
- dwa niezależne początki domiarów również dawały niepełną geometrię;
- sprzeczność dodatniego odcinka z bezpośrednim lub przechodnim zerowym
  powiązaniem jego końców kończyła kompilator sygnałem SIGSEGV.

Są to obserwacje tej wersji na syntetycznych wejściach, bez deklaracji
takiego zachowania innych wersji lub programu Walls. Nie zmieniamy
pomiarów, aby wymusić kompilację. Testy nie wymagają awarii kompilatora:
nowsza wersja może bezpiecznie odrzucić sprzeczną sieć.

Dokładne wejścia, wyjścia i polecenia odtworzenia pozostają w
[archiwalnym opisie prób](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/blob/3e3daa4156c6e6e79dce5203d8bb8e36122d571f/doc/pockettopo/evidence/p04/COMPILER_LIMITS.md)
i [ich manifeście](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/blob/3e3daa4156c6e6e79dce5203d8bb8e36122d571f/doc/pockettopo/evidence/p04/compiler-limits.json).
Bieżące kontrole są w
[test_pockettopo_compilation.py](../../tests/test_pockettopo_compilation.py).
