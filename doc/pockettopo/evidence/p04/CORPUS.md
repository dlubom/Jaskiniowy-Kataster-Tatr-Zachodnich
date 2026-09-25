# P04 — kompilacja i rozliczenie korpusu

Wyniki dotyczą domyślnego eksportu: zapisane jawne korekty, bez automatycznego
uśredniania, bez zastępowania brakujących korekt zerem, bez aktywnych fixów.
Źródło to przypięta rewizja `4c00c008a8dd441d70f9c62aa376c20b5914c7e0`
repozytorium `dlubom/test2`. Kontrola przed odczytem potwierdziła **262/262
obiekty Git**, odpowiadające **258 unikalnym plikom**. Pełne ścieżki, SHA-256,
Git blob SHA-1, rozliczenie rekordów, skróty eksportów oraz komunikaty
kompilatora zawiera [corpus.json](corpus.json). Polecenia są w
[REPRODUCE.md](REPRODUCE.md).

| Rozliczenie rekordów | Liczba |
| --- | ---: |
| Źródłowe i ujęte w śladzie | 37 801 |
| Wyeksportowane osobno | 37 362 |
| Zatrzymane z przyczyną | 439 |
| Automatycznie potwierdzone grupy powtórzeń | 0 |

Przyczyny zatrzymania: 358 zerowych rekordów bez dwóch nazwanych końców,
64 rekordy bez tripu i bez jawnej korekty, 5 odcinków do tej samej stacji,
11 rekordów z oboma końcami niezdefiniowanymi oraz 1 pochylenie poza zakresem.
Żaden rekord nie znika ze źródła ani raportu. Liczba 439 obejmuje 375 przypadków
zatrzymanych już w P03 oraz dodatkowe 64 z nierozstrzygniętą korektą P04.

| Wynik Survex 1.4.22 | SRV | SVX |
| --- | ---: | ---: |
| Kompilacja bez ostrzeżeń | 249 | 249 |
| Kompilacja z ostrzeżeniem o odłączonych składowych | 7 | 7 |
| Brak aktywnych pomiarów; kompilacji nie deklarujemy | 2 | 2 |
| Błąd kompilacji niepustego eksportu | 0 | 0 |

W siedmiu źródłach kompilator zgłasza `Survey not all connected to fixed
stations`. Zachowano ostrzeżenia i nie dodano fikcyjnych powiązań ani fixów.
Dotyczą one następujących plików (pełne ścieżki w JSON):

- `20100804-Meander_Zachodni4/ciekawa zach208a (7).top`
- `20110806-Partie_Krokodylka/123qwe (2).top`
- `20110806-Partie_Krokodylka/123qwe.top`
- `20110806-Partie_Krokodylka/krokodylek.top`
- `20120803-Ciek_pod_wisz_polka/ciek-pod-wisz-polka.top`
- `20130807-Dziki_Zachod/EROR 7AUG13 Zachodni przodek.top`
- `20210812-Przekorna_Studnia/przekorna.top`

Dwa źródła bez aktywnych odcinków to `amazonka kontynuacja jn or  v1.top`
(z dwiema spacjami przed `v1`) i `amazonka kontynuacja jn or v2.top`.
Zachowany eksport tekstowy i raport nie są dowodem niepustej geometrii.

Dla **256 par skompilowanych eksportów** porównano zbiór nazwanych stacji
obecnych w wyniku, odwrócony do surowych identyfikatorów PocketTopo, oraz ich
współrzędne po odjęciu umownego początku układu. Wyniki SRV/SVX są identyczne w precyzji
centymetrowej `dump3d` (**maksymalna różnica 0,0 m**). To porównanie dwóch
czytników formatów w tym samym Survex, w tym dla sieci z pętlami. Nie jest
niezależnym dowodem poprawności danych terenowych ani wynikiem rzeczywistego
Walls. **Tylko 249 par zawiera wszystkie wyeksportowane nazwane stacje.**
Siedem wyników z ostrzeżeniami jest częściowych: `.3d` pomija łącznie
**90 nazwanych stacji** odłączonych składowych (sumowane osobno dla każdego
źródła). JSON zapisuje ich surowe ID i status `consistent_partial`; zgodność
dwóch niepełnych wyników nie potwierdza kompletności.
[Próby ograniczeń kompilatora](COMPILER_LIMITS.md) pokazują ten sam efekt
na minimalnych wejściach. Powyższa kontrola korpusu dotyczy nazwanych stacji; domiary mają osobne
analityczne testy małych wzorców.

[geometry.json](geometry.json) zachowuje niezależne oczekiwania analityczne
czterech małych przypadków: potwierdzone A1–A3, domiar odwrócony, trzy różne
korekty z brakującym tripem oraz długie identyfikatory. Porównano każdy nazwany
punkt, kierunek i długość domiaru, piony oraz tożsamość dwóch stacji zerowego
powiązania. Plain `0` i major.minor `0.0` mają oddzielne współrzędne; długie
identyfikatory Walls odzyskuje się przez mapę nazw. Wybrane korekty Auto `+8°`
i brakującego tripu `−12°` należą wyłącznie do jawnych testów syntetycznych.

[fixture-checks.json](fixture-checks.json) opisuje 13 eksportów dowodowych:
9 pierwotnych wzorców P01/P02 oraz 4 jawne warianty testowe. Jedenaście par
kompiluje się bez ostrzeżeń. Dwa wzorce GUI nie mają tripu, więc ich jedyny
odcinek pozostaje zatrzymany do wyjaśnienia korekty; nie stosowano zastępczego
zera. Każdy katalog zawiera `source.json`, `conversion-report.json`, oba
formaty i — gdy istniała aktywna geometria — pełne wyniki `cavern`/`dump3d`.

Zaobserwowane w początkowej próbie odrzucenie połączonego polecenia
`*calibrate tape compass clino 0` naprawiono przez osobne dyrektywy długości
i kątów. Świeże dowody powyżej pochodzą z poprawionego eksportera. Testy
kompilacji pozostają regresją tego rzeczywistego błędu składni.
