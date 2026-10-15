# Dowody i pokrycie audytu

Pełny pakiet audytu zapisuj poza checkoutem zgodnie z `SKILL.md`.
Po naprawie danych zapisz krótkie uzasadnienie w miejscu zgodnym ze zleceniem:
co zmieniono, z którego źródła i z jakim wynikiem walidacji.
Jeśli wszystkie dowody mają być poza repo, także uzasadnienie zostaje tam.
Gdy użytkownik zamówi rozbudowany raport w repo, rozwijaj istniejący
`WERYFIKACJA_ZRODEL.md`. Liczbę plików dobieraj do rzeczywistych dowodów.

## Źródła

Zapisz obiekt, zakres, datę audytu, bazowy commit i stan lokalnych zmian.
Każde źródło identyfikuj ścieżką/ID/rewizją, rolą, rozmiarem i SHA-256.
Opisz relację do `_RAW` i ograniczenia pochodzenia. Odróżniaj oryginał,
kopię, konwersję, OCR, opracowanie oraz niezależny pomiar.

## Rekordy

Duży rejestr może być CSV/JSON; małe porównanie zmieści się w raporcie.
Każdy rekord zachowuje:

- plik i miejsce źródłowe: wiersz, komórkę, indeks/offset oraz kontekst dyrektyw;
- dosłowne stacje i wartości, jednostki, raw ID i niepewne odczyty;
- odpowiednik w aktywnym pliku dla wskazanego commita/hashu;
- przeliczenie/mapowanie z podstawą oraz los: użyty, przekształcony,
  wyłączony z uzasadnieniem, wariant, rozbieżny, nieczytelny lub bez odpowiednika.

Uśrednienie ma wszystkich członków i odwrócenia oraz dowód powtórzenia.
Dla TOP zachowaj raporty binarium, wersję, SHA wejścia, linie eksportów
i `losses`; rozlicz też tripy, referencje i rysunki. Nie powielaj kompletnych
surowych pól w kilku rejestrach, jeśli jeden zapis i odnośniki dają pełny ślad.

Podaj mianowniki w obie strony, według rodzajów rekordów. Nie utożsamiaj
zgodności dostępnych rekordów z kompletnością brakującej części źródła.

## Wnioski

Oddziel obserwację, hipotezę, potwierdzoną decyzję i ograniczenie.
Dla korekty podaj starą i nową wartość oraz dokładny dowód.
Zapisz wykonane polecenia, wersje, kody zakończenia i istotne wyniki;
logi pozostają w pakiecie audytu. Rozróżnij pochodzenie, pomiary,
metadane, kompilację i faktycznie sprawdzone GUI.

Zgłoszony przez autora reset zegara opisz raz. Nie traktuj daty pliku,
publikacji ani urządzenia jako nowego potwierdzenia daty pomiaru.
W końcowej odpowiedzi wystarczą wynik, pokrycie, zmiany, istotne luki
i ścieżka do pakietu. Pytaj tylko o brakujący dowód potrzebny do decyzji.
