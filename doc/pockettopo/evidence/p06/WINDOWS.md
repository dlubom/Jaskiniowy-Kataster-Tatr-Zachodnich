# P06 — poprawka próby względnych ścieżek na Windows

[Pierwsze CI P06](ci-first-run.json) dla `11f6f3a` przeszło jakość Pythona,
mutacje i walidację Linux. Na Windows zwykły pełny pytest przeszedł przed
instalacją Survex, a późniejsza obowiązkowa próba narzędzi zakończyła się
wynikiem 94 poprawne, 1 pominięty (brak resvg), 1 błąd.

Błąd dotyczył wyłącznie
`test_real_relative_tool_symlinks_compile_from_temporary_working_directory`.
Test tworzył dowiązania do `cavern.exe`/`dump3d.exe` poza ich instalacją.
Zwykłe próby kompilacji przez te narzędzia przeszły, ale asercja tej próby
nie wypisywała szczegółów procesu. Log **nie rozstrzyga**, dlaczego wywołanie
przez dowiązanie zawiodło; nie przypisujemy go automatycznie brakowi DLL.

Test regresji miał sprawdzać rozwiązywanie **względnych ścieżek** przed
zmianą katalogu na tymczasowy katalog kompilacji. Teraz zmienia katalog
wywołującego na katalog instalacji i podaje względne ścieżki do oryginalnych
programów, zachowując ich otoczenie. Nie wymaga dowiązań ani ich uprawnień.
Przy błędzie wypisuje pełny raport kompilacji. Nadal uruchamia rzeczywiste
narzędzia; oddzielny test sprawdza przekazanie znormalizowanych ścieżek.

Zmiana obejmuje test i dowody. Kod produkcyjny, korpus i wyniki konwersji
pozostają identyczne. Lokalnie 38 testów walidatora i pełna bramka jakości
przeszły ponownie. Sukces Windows wymaga osobnego CI poprawionej rewizji;
wynik lokalny na macOS go nie zastępuje.
