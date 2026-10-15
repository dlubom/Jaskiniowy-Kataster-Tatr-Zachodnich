---
name: validate-cave
description: Use when auditing a cave's source provenance and survey records against archival originals, or recovering sources and repairing confirmed survey errors. Not for compilation alone.
---

Sprawdź pochodzenie i każdy rekord jaskini zgodnie z
[AGENTS.md](../../../AGENTS.md). Wynik ma rozliczać źródła, przekształcenia,
poprawki i konkretne luki. Zakres wyznacza zlecenie; review lub „bez zmian”
nie oznacza zgody na zmianę pomiarów ani publikację.

## Wynik i miejsce zapisu

Ustal katalog główny badanego projektu (`<root>`, zawierający `KATASTER.wpj`),
niezależnie od bieżącego katalogu terminala. Domyślnie zapisuj pełne dowody
w `<root>/.verification/<YYYY-MM-DD>-<jaskinia>/`. Wskazane przez użytkownika
miejsce ma pierwszeństwo; żądanie dowodów fizycznie poza checkoutem oznacza
zewnętrzny katalog. Logi, CSV/JSON, eksporty, obrazy i jednorazowe skrypty
należą do pakietu audytu. Utwórz jego katalog przed eksportem; każdy eksport
zapisuj w nowym, nieistniejącym podkatalogu, także przy ponowieniu próby.
W czacie podaj wynik, pokrycie, zmiany, istotne luki i link do dowodów.

`.verification/` jest lokalne, ignorowane przez Git i pomijane w ZIP wydania;
nowy klon nie zawiera tych dowodów. Przed usunięciem checkoutu lub worktree
zachowaj potrzebny pakiet w trwałej lokalizacji.

Po naprawie danych repozytorium dostaje krótkie uzasadnienie ze źródłem
obok jaskini oraz wpis `Unreleased`. Uzupełnij istniejącą notatkę; nie
twórz równoległych raportów. Jeśli zlecenie wymaga wszystkich dowodów wyłącznie
w pakiecie audytu, umieść tam także uzasadnienie. Sam review może zakończyć
się raportem w tym pakiecie. Rozbudowany raport w repo zapisuj, gdy użytkownik
go tam zamówi.
Format szczegółowego rejestru opisuje
[audit-evidence.md](references/audit-evidence.md).

## Audyt

1. Ustal obiekt, numer inwentarzowy, katalog, commit i lokalne zmiany.
   Sprawdź `KATASTER.wpj`, aktywne SRV, `SOURCE_REF`, `_RAW` i historię Git.
   W PIG wyszukuj dokładne pole; lokalny JSONL jest źródłem archiwalnym.
   Zapisz hashe oryginałów, także źródłowych README.
2. Powiąż każdy aktywny rekord ze źródłem i rozlicz każdy rekord źródłowy,
   również splaje, LRUD, dowiązania, wyłączenia i szkice. Zachowaj dosłowne
   wartości, identyfikatory, lokalizację źródła i transformacje. Sprawdź
   kolejność pól, jednostki, prefiksy, odwrócenia, korekty i aktywność.
   Podobna geometria ani długość nie dowodzą tożsamości stacji lub powtórzeń.
3. Przy odzyskiwaniu plików i wcześniejszej historii przeczytaj
   [source-recovery.md](references/source-recovery.md). Usługi dobieraj do
   wskazanego źródła; nie zakładaj Gmaila ani dodatkowego prywatnego dostępu.
   Oryginały zachowuj bez zmiany bajtów, nazw i struktury; umieszczaj je
   w `_RAW/NN`, gdy zakres obejmuje uzupełnienie źródeł w repo.
   Konwersja, OCR i transkrypcja pozostają poza `_RAW`.
4. Skany weryfikuj wzrokowo; przy nieczytelności zachowaj warianty odczytu.
   Rozróżniaj pomiar, kopię, opracowanie, nadawcę i redaktora. Zgodne
   pochodne tego samego źródła nie są niezależnym potwierdzeniem terenowym.
5. Naprawiaj tylko błędy potwierdzone źródłem i objęte zleceniem. Przy braku
   rekordu sprawdź historię i uzasadnienia wyłączenia. Nie usuwaj odczytów
   ani nie łącz stacji dla poprawy domknięcia. Zachowaj kodowanie i końce linii.

Daty zegara PocketTopo nie zastępują dat pomiaru. Jeśli autor potwierdził
nieustawiony lub zresetowany zegar, zanotuj tę przyczynę raz dla danego
zbioru i kontynuuj bez ponawiania pytania dla każdego pliku. Zachowaj
potwierdzoną datę z autora lub metadanych; daty urządzenia i nazwy plików
nie służą do samodzielnego ustalania IGRF. Nie podnoś precyzji daty.

## Narzędzia i zakończenie

- TOP: gotowe binarium według [pockettopo-convert](../pockettopo-convert/SKILL.md).
  Zachowaj SHA źródła, wersję/binarium, `inspect`, `process` i raporty
  użytych eksportów. Rozlicz offsety, grupy, pominięcia i `losses`.
- Konwersja SVX: [svx-to-srv](../svx-to-srv/SKILL.md). Potwierdzone powtórzenia:
  [average-shots](../average-shots/SKILL.md). Nowe włączenie jaskini:
  [add-cave](../add-cave/SKILL.md), tylko w zamówionym zakresie.
- Metadane: `uv run jktz-srv-metadata`; parsuj SRV i README istniejącymi API.
  `raw-set` zastępuje README, więc zachowaj dodatkowe sekcje przez `--dry-run`
  i atomowy zapis. `hash-raw` pomija README: sprawdź je osobno.
- Po zmianie danych porównaj wejścia i model przed/po według
  [verify-cave-refactor](../verify-cave-refactor/SKILL.md), uruchom
  `uv run jktz-validate` i `git diff --check`. Walidator może tworzyć ignorowane
  pliki robocze; log przechwyć do pakietu audytu. Gdy wszystkie wyniki mają
  powstać fizycznie poza checkoutem, uruchom go na kopii kandydata w katalogu audytu.
  Przy brakujących zależnościach
  użyj [docker-validate](../docker-validate/SKILL.md). Zmieniany kod podlega
  bramkom `AGENTS.md`; nie obniżaj ich dla uzyskania wyniku.

Sprawdź końcowe hashe i diff. Kompilacja Survex nie jest testem Walls;
GUI oceniaj, gdy pomaga rozstrzygnąć problem lub zostało zamówione.
Oddziel problemy środowiska od danych. Raportuj mianowniki pokrycia,
poprawki i niesprawdzone obszary, bez powtarzania pełnego dziennika w czacie.
Commit/push/PR wykonuj w uzgodnionym zakresie; audyt nie oznacza wydania.
