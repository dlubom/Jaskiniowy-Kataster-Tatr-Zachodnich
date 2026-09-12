# Jaskinia Czarna — stan prac i dalsze kroki

Aktualizacja: 2026-09-12. Gałąź robocza: `codex/czarna-digitalizacja`,
utworzona z `origin/master` na `446edc4`.
Dokument służy wznowieniu pracy bez historii rozmowy. Aktualizuj go po każdym
zakończonym etapie, razem z dowodami, wykonanymi sprawdzeniami i następnym krokiem.

## Cel i zakres uprawnień

Celem jest rozpoznanie i odczyt archiwalnych pomiarów Czarnej, a następnie
porównanie ich jakości z pomiarami Borowca przy wykorzystaniu precyzyjnych
pomiarów otworów. Dopiero na podstawie źródeł i kontrolowanego porównania
można wybrać podstawowy ciąg i sposób włączenia go do sieci.

Autor, data i instrument dziennika 0–76 pozostają nieznane. Określenia
„powtórny”, „nowszy” i „Kujata” są hipotezami, nie ustalonymi metadanymi.
Nie wyprowadzaj ich z nazwy zdjęcia ani z daty listu dotyczącego innych partii.

Użytkownik upoważnił do utworzenia gałęzi oraz commitów i pushów, najpierw
dotychczasowej digitalizacji, następnie dokumentacji stanu w osobnym commicie,
a dalej do ulepszania danych i analizy. Nie upoważnił do merge, tagu ani release.
Publikację i CI potwierdzaj dla rzeczywistego SHA; nie traktuj zamiaru jako wyniku.
CI uruchamia się dla push na master lub PR, nie dla samego push tej gałęzi.
Dotychczasowe polecenie nie obejmuje PR; nie zgłaszaj nieuruchomionego CI jako sukcesu.

## Punkt wejścia dla kolejnego agenta

1. Przeczytaj główny [CLAUDE.md](../../../../CLAUDE.md) i lokalny [AGENTS.md](AGENTS.md).
2. Sprawdź `git status --short --branch`, `git log -5 --oneline` oraz zakres zmian.
3. Przeczytaj [raport digitalizacji](DIGITALIZACJA_RAPORT.md) i [CZ_GL_R.SRV](CZ_GL_R.SRV).
4. Sięgaj do rzeczywistych skanów wskazanych w raporcie; tabele i OCR są wtórne.
5. Przeczytaj [raport deklinacji](BOROWIEC_DEKLINACJA_RAPORT.md) jako zapis wcześniejszego
   eksperymentu. Jego wyników nie uznawaj za ponownie zweryfikowane ani za ocenę nowego ciągu.

## Ukończone etapy i obecny stan

- Pierwszy etap opublikowano jako `74723744834ee9badf4b5334f9319de651c73c6c`
  (`Czarna: zinwentaryzuj skany i dodaj roboczy odczyt ciagu glownego`).
  Obejmuje `CZ_GL_R.SRV` i `DIGITALIZACJA_RAPORT.md`. Niezależny przegląd
  nie wykazał usterek P1/P2; potwierdził izolację danych i sumy odcinków,
  ale nie powtarzał wszystkich odczytów skanów.
- Inwentaryzacja źródeł jest ukończona: rozróżniono brakujące odczyty, kopie
  fotografii, już cyfrowe pomiary i odczytane partie oczekujące na dowiązanie.
- Brakujący dziennik obejmuje 76 odcinków 0–76 i dwa odcinki 6–a–b.
  Zdjęcia `123052` i `123533` pokazują te same strony; `123630` zawiera środek ciągu.
- `CZ_GL_R.SRV` zawiera 78 roboczo odczytanych odcinków, zweryfikowanych przez
  dwóch niezależnych czytelników. Cztery odczyty pozostają nierozstrzygnięte.
- Robocza suma wynosi 1122,50 m: 1109,70 m ciągu głównego i 12,80 m odgałęzienia.
  To suma pomiarów w tym pliku, nie przyrost długości całej jaskini.
- Plik używa `Czarna:CiagSkany`, `order=DAV`, metrów i stopni. Nie ma daty,
  fixów ani utożsamień. `DECL=0` jest wyłącznie roboczym brakiem korekty.
- SRV pozostaje poza `KATASTER.wpj`. Stacja 0 jest opisana jako „Otwór”,
  a 76 jako „Koniec Colorado”; plik nie jest gotowym trawersem do III otworu.
- Sprawdzono lokalne walidatory oraz kompilację parserem Walls w Survex 1.4.22:
  79 stacji, 78 odcinków, 0 pętli. Nie wykonano kompilacji w aplikacji Walls.
- Pełna walidacja po aktualizacji gałęzi: 156 testów, Ruff, sprawdzenie 87 fixów
  GPS z v1.0.2 oraz wszystkie 12 etapów `jktz-validate` zakończyły się sukcesem.
- Oryginały `_RAW`, istniejące aktywne pomiary i współrzędne otworów zachowano.
  Pełna historia późniejszych zmian i publikacji znajduje się w git.

## Cztery odczyty do potwierdzenia

| Odcinek | Pole | Roboczo | Alternatywa |
| --- | --- | --- | --- |
| 29–30 | D | 13,80 m | 13,60 m |
| 39–40 | A | 25° | 75° |
| 49–50 | A | 68° | 88° |
| 71–72 | V | −1° | +1° |

Nie wybieraj odczytu przez dopasowanie do GNSS, starego poligonu ani rachunków
na kartce. Komentarze `Lh_scan` i `dh_scan` zawierają błędy źródła i nie sterują
geometrią. Kreska azymutu pionu 57–58 (`--`, V=−90°) nie jest piątym spornym wierszem.

## Znane problemy istniejących danych

- Kujat 6500–6509: dziewięć wartości już przeliczonych na stopnie aktywny SRV
  ponownie interpretuje jako grady. To potwierdzony błąd jednostek.
- Kujat 6501–6502: oryginał 11,09 m, przepisana tabela i SRV 11,90 m.
  Przed zmianą ustal, czy późniejsza tabela dokumentuje świadomą korektę.
- Borowiec, punkt 64: skan X=2222,84, ręczny arkusz X=2222,94. Poprawka wymaga
  ponownego wyprowadzenia dwóch sąsiednich wektorów; nie zmienia sumy za punktem 65.
- Błędne `SOURCE_REF`: Borowiec i Kujat powinny wskazywać `_RAW/02`, Wawel
  i Nowak `_RAW/03`. README `_RAW/01` podaje 1972 zamiast cyfrowej daty 2011-10-02.
- 41 pomiarów Nowaka i jeden Wawelu są już odczytane, lecz wykomentowane
  z powodu dowiązania lub wątpliwego połączenia. Nie digitalizuj ich od nowa.

## Najbliższy krok i warunki porównania

1. Policz wpływ każdej z czterech alternatyw na lokalne współrzędne oraz
   wszystkie 16 kombinacji na koniec ciągu. Zachowaj skrypt i wyniki w repo.
   Podaj różnice E/N/Z, poziome i 3D względem wersji roboczej; bez rankingu pod GNSS.
2. Następnie rozstrzygaj źródła i znane błędy w jawnych, oddzielnych wariantach.
3. Ustal wspólne fizyczne punkty i domiary do GNSS: `KSW-0201` odpowiada
   `Czarna:M:otwor1`, `KSW-0240` — `Czarna:Kujat:0`. Centymetrowa dokładność
   pochodzi z informacji użytkownika; źródłowych raportów GNSS jeszcze nie audytowano.
4. Zweryfikuj zerowe utożsamienia GPS z `Borowiec:0W` i `SzKostka:1.92`.
   Ten ostatni opisano przy kracie, około 50 cm od batinoxa. Równe nazwy/numeracja
   nie dowodzą identyczności punktów. Ustal też połączenie dziennika z III otworem.
5. Porównaj izolowane sieci przy jednym ustalonym otworze, potem wyrównanie
   przy obu fixach. Bieżąca sieć miesza Borowca z powtórzeniami Nowaka 6–7,
   7–8, 8–9 i 30–31. Oddziel korektę wynikającą z daty od empirycznego obrotu.
6. Włączenie do głównego WPJ następuje po świadomym wyborze wariantu i dowiązań;
   sama poprawność składni ani mniejszy błąd po dopasowaniu nie wystarczają.

## Odtwarzalne narzędzia i aktualizacje

Polecenia uruchamiaj z katalogu głównego repo. Po aktualizacji gałęzi używaj
CLI z `pyproject.toml`; stare skrypty usunięto w commicie `446edc4`.

```sh
uv sync --locked
uv run jktz-survex-stats Poligony/D_Koscieliska/Organy/Czarna/CZ_GL_R.SRV
uv run jktz-srv-metadata hash-raw Poligony/D_Koscieliska/Organy/Czarna
uv run jktz-srv-metadata srv-update --help
uv run jktz-render-otwory --check
uv run jktz-validate
```

Pełny gate wymaga Survex, GDAL i dostępu do źródła GPS; nie ukrywaj błędów
środowiska ani nie nazywaj częściowej kompilacji pełną walidacją. Metadane
zmieniaj CLI, a materiały `_RAW` zachowuj bez zmian. Po etapie wpisz tutaj:
co zmieniono, źródło decyzji, wyniki sprawdzeń, SHA publikacji i następny krok.
Nowa niepewność pozostaje jawna. Dokument nie oznacza zaplanowanej automatycznej pracy.
