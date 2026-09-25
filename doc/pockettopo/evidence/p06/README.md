# P06 — CLI, atomowy pakiet i skill

Etap zakończony. `uv run jktz-pockettopo inspect` pokazuje surowe dane
i raport, a `convert` publikuje kompletny zestaw 12 plików: SRV/SVX,
cztery SVG, cztery PNG, `source.json` i `conversion-report.json`.
[Instrukcja CLI](../../CLI.md) opisuje opcje i JSON decyzji;
[skill](../../../../.agents/skills/pockettopo-convert/SKILL.md) prowadzi
od surowego źródła przez odczyt ograniczeń do sprawdzenia wyniku.

## Wynik walidacji

- **1248 testów**, **97,78% linii / 96,22% gałęzi**, maksymalny **CRAP 25**.
  Wszystkie cztery nowe moduły mają wykonane testami funkcje; szczegółowe
  pokrycie i hashe kodu są w [zapisie bramek](repository-checks.json).
- Mutacje: **2483/2748 (90,36%)**; każdy z dziesięciu objętych modułów
  spełnia próg 81%. Zachowano cały istniejący zakres i progi.
- Pełne `jktz-validate`: wejścia GPS, metadane, pomiary, bezostrzeżeniowa
  kompilacja cavern i eksporty GDAL przeszły.
- [13 wzorców](fixture-checks.json): każdy pakiet ma 12 plików i zweryfikowany
  manifest. Wszystkie 52 SVG oraz 52 PNG są identyczne bajtowo z P05.
  [Trzy pełne pakiety](examples/) zachowują wynik kompletny (`api-drawings`),
  nierozstrzygnięte korekty (`api-trips-ids`) i niewyrównaną osnowę
  niepotwierdzonych powtórzeń (`api-cardinal`).
- [Cały korpus](corpus.json): **258 źródeł / 262 zweryfikowane obiekty Git**,
  **258 pakietów / 3096 artefaktów**, w tym 1032 SVG i 1032 PNG. Każdy plik
  został zapisany i odczytany; hashe manifestów oraz źródeł są zgodne.
  Rozliczono 37 801 rekordów, z czego 439 pozostaje zatrzymanych.

249 źródeł ma kompletną kompilację obu formatów. Siedem ma rozłączne części,
dwa nie mają aktywnej geometrii. Tylko **12 źródeł** spełnia wszystkie
warunki `conversion_complete`; **246 zwraca kod 2** z pełnym pakietem
audytowym i ograniczeniami. W korpusie 218 źródeł ma zatrzymane pomiary,
226 niewyrównane zamknięcia osnowy, a 7 lokalne początki rozłącznych części.
Te grupy mogą się nakładać. Ukończenie narzędzia nie usuwa ograniczeń źródeł.

## Kontrakt zapisu i kompletności

Polityka kolizji to zawsze odmowa: istniejący plik, dowiązanie, pusty lub
niepusty katalog pozostaje nietknięty. Każdy plik jest zapisany i opróżniony
przez `fsync` w katalogu tymczasowym na docelowym systemie plików; dopiero
potem następuje pojedyncze atomowe przeniesienie bez zastępowania celu
(macOS `RENAME_EXCL`, Linux `RENAME_NOREPLACE`, Windows `rename`).
Nie ma zastępczego niebezpiecznego przenoszenia. Awaria procesu może zostawić
ukryty katalog tymczasowy, ale nie częściowo opublikowany wynik.

Testy wymuszają awarie zapisu, `fsync`, przenoszenia, brak funkcji atomowej
oraz utworzenie konkurencyjnego celu tuż przed publikacją. Również nowy pusty
katalog nie zostaje nadpisany. Wyjście w `_RAW`, także przez dowiązanie,
jest odrzucane. Źródło jest tylko odczytywane.

Brak renderera lub błędny zapis oznacza kod **1** i brak nowego pakietu.
Ograniczenia pomiarów, rysunków lub kompilacji dają kod **2**, wszystkie
12 plików i `conversion_complete=false`. Poprawna składnia wywołania jest
warunkiem tej interpretacji: argparse także używa kodu 2 dla błędu argumentów.
Kod **0** z `convert` wymaga kompletnych aktywnych pomiarów, sprawdzonej
kompilacji i braku ograniczeń podkładu. `inspect` nie uruchamia tych kontroli.

Kompilacja obu formatów przez **Survex 1.4.22** obejmuje ostrzeżenia,
błędy/sygnały/timeout, cały dump, nazwy stacji, obecność odcinków, domiary,
powiązania zerowe i porównanie geometrii po normalizacji początku.
Kompilator może scalić niepotwierdzone równoległe odcinki; każdy oczekiwany
odcinek nadal musi być reprezentowany, a źródłowy eksport ich nie uśrednia.
Nie tworzymy sztucznych fixów. To nie jest bieżące uruchomienie Walls;
niezależne próby rzeczywistego Walls pozostają w [P04](../p04/walls/README.md).

## Niezależna próba i przegląd

Osobny wykonawca dostał tylko realistyczne zlecenie, skill, `okna.top`
i ścieżki do narzędzi. Bez czytania implementacji ani PRD utworzył pakiet,
obejrzał cztery PNG, zinterpretował kod 2 i zatrzymany rekord 0, sprawdził
geometrię oraz ponowił zapis do tego samego celu. Odmowa zachowała wszystkie
12 hashy i źródło. [Audyt, obrazy i logi](forward-test/AUDIT.md) pozostają
w repozytorium; nie wymagają przetrwania katalogu `/tmp`.

Próba skilla wykryła nieaktualne zdanie w raporcie `inspect`; poprawiono je
i niezależnie sprawdzono bez zmiany danych. Przegląd kodu wykrył względne
ścieżki programów kompilujących rozwiązywane po zmianie katalogu roboczego.
Teraz są rozwiązywane względem katalogu wywołującego; regresja uruchamia
rzeczywiste narzędzia przez względne ścieżki. Końcowa kontrola poprawek nie
wykazała dalszych problemów produkcyjnych. Struktura skilla przeszła
`quick_validate.py`.

## Odtworzenie i zakres

[Instrukcja i dokładny kod próby](REPRODUCE.md) zapisują źródła, hashe,
narzędzia i sposób regeneracji dowodów. Testy jednostkowe P06 są w
`tests/test_pockettopo_{cli,config,package,validation}.py`. CI sprawdza
kompilację i zapis na Linux/Windows; pełne połączenie z przypiętym resvg
jest wymagane na Linux. Zdalny wynik należy wiązać z konkretnym SHA brancha
[PR #129](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/pull/129);
lokalny zapis bramek nie zastępuje CI po pushu.

Pierwszy przebieg CI wykrył problem próby narzędzi przez dowiązania na
Windows. [Opis i poprawka testu](WINDOWS.md) zachowują wynik oraz jego
ograniczenia; kod produkcyjny i wyniki korpusu nie zostały zmienione.

Daty urządzenia pozostają niepotwierdzone, a jawne korekty odtworzone bez
historycznego potwierdzenia. Nie potwierdzono automatycznie żadnej serii,
CRS ani położenia rozłącznych części. Pakiety są wynikami roboczymi;
kanoniczne metadane SRV, GPS i rejestracja w `KATASTER.wpj` są osobnym zadaniem.
P00–P06 są zamknięte; niniejsze zlecenie kończy się po P06.
