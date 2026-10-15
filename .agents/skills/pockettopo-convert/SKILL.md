---
name: pockettopo-convert
description: Use when inspecting or exporting PocketTopo TOP v3 sources for a cave audit through the published pockettopo-exporter executable. Use for source-preserving conversion, not automatic cave registration.
---

Używaj gotowego binarium
[`pockettopo-exporter`](https://github.com/dlubom/pockettopo-exporter).
[Pobranie i testy](../../../doc/pockettopo/README.md). Oryginały pozostaw
bez zmian. Ustal katalog główny badanego projektu z `KATASTER.wpj`, niezależnie
od bieżącego katalogu terminala. Domyślny pakiet audytu to
`<root>/.verification/<YYYY-MM-DD>-<jaskinia>/`; wskazane przez użytkownika
miejsce ma pierwszeństwo, także fizycznie poza checkoutem. Zasady przechowania
dowodów opisuje [validate-cave](../validate-cave/SKILL.md).

## Odczyt i eksport

Przykłady wykonuj z ustalonego katalogu głównego projektu. Utwórz katalog
audytu, a każdy eksport kieruj do nowego, nieistniejącego podkatalogu.
Przy ponowieniu wybierz nową nazwę zamiast nadpisywania wcześniejszych wyników.
Datę i nazwę jaskini w przykładach zastąp właściwymi dla zlecenia.

```sh
mkdir -p .verification/2026-10-15-kalacka
pockettopo-exporter --version
pockettopo-exporter inspect /path/source.top --json
pockettopo-exporter process /path/source.top --json
pockettopo-exporter export /path/source.top --format text --output .verification/2026-10-15-kalacka/text
pockettopo-exporter export /path/source.top --format srv --output .verification/2026-10-15-kalacka/srv
pockettopo-exporter export /path/source.top --format svx --output .verification/2026-10-15-kalacka/svx
```

Zapisz wersję/binarium, SHA wejścia, komendy i kody zakończenia.
W `inspect` sprawdź `complete`, `supported`, `accounting` i `diagnostics`.
Nieobsługiwane lub niekompletne wejście opisz jako ograniczenie audytu.

Do porównania rekordów użyj `process.rows`, `groups.members` oraz
`report.json` eksportu. Raport `text` obejmuje też tripy i referencje;
raporty SRV/SVX wiążą odczyty z emitowanymi wierszami. Sprawdź hashe i `losses`.

SRV uśrednia kolejne powtórzenia i pomiary odwrotne; splaje pozostają osobne.
SVX zachowuje pojedyncze odczyty, normalizuje odwrotne do kierunku grupy
i pozostawia uśrednianie Survexowi. Przed zmianą aktywnego SRV potwierdź
powtórzenia ze źródeł. Daty urządzenia wymagają niezależnego potwierdzenia;
potwierdzony przez autora reset zegara opisz raz dla zbioru, bez ponawiania pytań.
sprawdź deklinację, aby nie naliczyć jej dwukrotnie. Średnią obejmującą różne
tripy/korekty przeliczaj z odczytów źródłowych przy zmianie deklinacji.

## Rysunki i przekazanie

```sh
pockettopo-exporter export /path/source.top --format therion --output .verification/2026-10-15-kalacka/therion
pockettopo-exporter export /path/source.top --format dxf --output .verification/2026-10-15-kalacka/plan --view plan
pockettopo-exporter export /path/source.top --format dxf --output .verification/2026-10-15-kalacka/side --view side
```

Therion daje PocketTopo interchange, a `side` przekrój rozwinięty. Obejrzyj
rysunki i ich raporty. Każdy TOP jest domyślnie izolowany; kontekst wielu
plików włączaj jawnie przez `--template-directory` zgodnie z `--help`.

Rozlicz każdy rekord według
[schematu audytu](../validate-cave/references/audit-evidence.md), zachowując
surowe ID, offsety, przekształcenia i pominięcia. Przekaż wyniki, pokrycie
i ograniczenia. Włączenie do projektu prowadzi [add-cave](../add-cave/SKILL.md).
