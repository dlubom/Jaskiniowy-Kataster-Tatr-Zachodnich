# PocketTopo przez Wine na macOS

Sprawdzona procedura z 2026-09-25: PocketTopo **1.372**, Wine Staging **11.7**,
istniejący prefix z natywnym .NET 2.0. Służy do tworzenia niezależnych eksportów
i przypadków testowych dla [konwertera](PRD.md).
[Próba na `shadow.top` i jej wyniki](evidence/shadow/README.md) stanowią dowód
wykonania; poniższe kroki opisują sposób powtórzenia.

Użytkownik wyraźnie zezwolił w zadaniu PocketTopo na AppleScript/System Events,
zrzuty okien PocketTopo i systemowe kliknięcia. Przy kontynuacji tego zadania
nie trzeba ponawiać tej samej zgody. Obowiązują aktualne instrukcje narzędzi
i uprawnienia macOS.

## Przygotowanie i wybór procesu

Pracuj na kopii `.top` w osobnym katalogu. PocketTopo czyta również pozostałe
pliki `.top` z katalogu otwartego pliku, więc kopie zapasowe i inne przypadki
testowe muszą leżeć osobno. Zachowaj sumę SHA-256 źródła i sprawdź ją ponownie
po eksporcie.

Zainstalowany launcher to `~/.local/bin/pockettopo`. Używa:

- programu `~/.local/share/pockettopo/app/PocketTopoV1372/PocketTopo.exe`;
- prefixu `~/.local/share/pockettopo/wineprefix`;
- Wine z `/Applications/Wine Staging.app`.

Uruchom launcher tylko wtedy, gdy PocketTopo jeszcze nie działa. W próbie
uruchomienie wymagało wykonania poza sandboxem. Potwierdź obecność okna;
samo istnienie procesu nie dowodzi, że aplikacja poprawnie wystartowała.
Nie zatrzymuj całego `wineserver`, który może obsługiwać inne aplikacje.

Odczytaj aktualny PID, zamiast zapamiętywać numer z poprzedniej sesji:

```sh
pgrep -fl '^/Users/dariuszlubomski/.local/share/pockettopo/app/PocketTopoV1372/PocketTopo[.]exe([[:space:]]|$)'
TARGET_PID="$(pgrep -f '^/Users/dariuszlubomski/.local/share/pockettopo/app/PocketTopoV1372/PocketTopo[.]exe([[:space:]]|$)')"
```

Jeżeli wynik zawiera więcej niż jeden PID, wybierz właściwy proces przed dalszym
działaniem. Helper nie przyjmuje listy PID. Proces PocketTopo jest rejestrowany
przez macOS jako `wine`, bez bundle ID. `Wine Staging.app` jest osobnym
launcherem; w tej konfiguracji wybór przez CUA nie dawał dostępu do okna
PocketTopo. Dlatego sprawdzona metoda wskazuje proces przez PID.

## Helper i obrazy własnych okien

Skompiluj [pockettopo_ui.swift](helpers/pockettopo_ui.swift), z katalogu repozytorium:

```sh
POCKETTOPO_TOOLS="$(mktemp -d /tmp/pockettopo-ui.XXXXXX)"
swiftc -module-cache-path "$POCKETTOPO_TOOLS/module-cache" \
  doc/pockettopo/helpers/pockettopo_ui.swift \
  -o "$POCKETTOPO_TOOLS/pockettopo-ui"
"$POCKETTOPO_TOOLS/pockettopo-ui" windows "$TARGET_PID"
```

`windows` wypisuje JSON, po jednym widocznym oknie wskazanego procesu w wierszu.
Do zrzutu użyj świeżego `kCGWindowNumber`; `kCGWindowBounds` podaje położenie
i rozmiar okna w układzie współrzędnych ekranu. Ustaw `WINDOW_ID` na odczytany
identyfikator, a `POCKETTOPO_WORK` na katalog roboczy przypadku:

```sh
screencapture -x -o -l "$WINDOW_ID" "$POCKETTOPO_WORK/pockettopo.png"
```

Przechwytuj wyłącznie okna PocketTopo. Menu Wine są osobnymi oknami z nowymi
identyfikatorami, więc po otwarciu menu ponownie wywołaj `windows`. Dialog może
zostać przechwycony razem z oknem rodzica: jego obraz nie musi mieć początku
w lewym górnym rogu samego dialogu. Przy ekranie Retina uwzględnij też różnicę
między pikselami obrazu a jednostkami `CGWindowBounds`. Nie używaj współrzędnych
ze starego obrazu po przesunięciu lub zmianie rozmiaru okna.

## Aktywacja, kliknięcia i tekst

Aktywuj proces przez bezpośredni warunek `unix id`. Nie przechowuj obiektu
`application process` w zmiennej AppleScript: kilka procesów nazywa się `wine`
i ponowne rozpoznanie po nazwie może wybrać inny proces.

```sh
osascript - "$TARGET_PID" <<'APPLESCRIPT'
on run argv
  set targetPID to (item 1 of argv) as integer
  tell application "System Events"
    set frontmost of (first application process whose unix id is targetPID) to true
    delay 0.5
    if (unix id of first application process whose frontmost is true) is not targetPID then error "PocketTopo is not active"
  end tell
end run
APPLESCRIPT
```

Odczytaj świeży obraz i przelicz miejsce kontrolki na współrzędne ekranu `X`, `Y`.
Następnie wykonaj jedno kliknięcie i sprawdź jego skutek:

```sh
"$POCKETTOPO_TOOLS/pockettopo-ui" click "$TARGET_PID" "$X" "$Y"
```

Helper wymaga aktywnego wskazanego PID, dostępu do zdarzeń wejściowych i punktu
wewnątrz widocznego okna tego procesu. Nie aktywuje aplikacji samodzielnie.
Wysyła fizyczne kliknięcie ekranu; podczas operacji nie zmieniaj fokusu ani
położenia okien. Przed kliknięciem potwierdź wizualnie, że punktu nie zasłania
Dock, powiadomienie ani inne pływające okno. Helper sprawdza prostokąt okna,
nie ustala, które okno leży na wierzchu w danym punkcie. Kontrola PID nie
oznacza rozpoznania konkretnego pola.

Do wpisywania użyj System Events dopiero po wizualnym potwierdzeniu aktywnego
pola. W dialogu zapisu sprawdź, że dotychczasowa nazwa jest zaznaczona.
`POCKETTOPO_TEXT` zawiera tekst przeznaczony do tego pola; poniższy przykład
zatwierdza go Return:

```sh
osascript - "$TARGET_PID" "$POCKETTOPO_TEXT" <<'APPLESCRIPT'
on run argv
  set targetPID to (item 1 of argv) as integer
  set enteredText to item 2 of argv
  tell application "System Events"
    if (unix id of first application process whose frontmost is true) is not targetPID then error "PocketTopo is not active"
    keystroke enteredText
    if (unix id of first application process whose frontmost is true) is not targetPID then error "PocketTopo lost focus"
    key code 36
  end tell
end run
APPLESCRIPT
```

Nie wykonuj globalnego przeglądu drzewa Accessibility. Wine nie udostępniał
w tej próbie kontrolek formularza; do pracy wystarczały obrazy własnych okien,
lista okien filtrowana przez PID i pojedyncze działania z kontrolą wyniku.

## Eksport porównawczy

1. Otwórz kopię przez `Menu → File → Open` i sprawdź widoczne pomiary.
2. Wykonaj `Menu → Export → Text`, zapisując wynik w katalogu przypadku.
3. Wykonaj `Menu → Export → Graphics`. PocketTopo 1.372 ma wspólny dialog
   Graphics, podczas gdy starsza instrukcja opisuje osobne Outline/Side View.
4. Dla porównania z próbą `shadow.top` ustaw: **Write Plan**, **Write Side**,
   suffixy **P/S**, skala **1:500**, **Shots** i **Xsections** wraz z ich
   **Separate Layers**. Wyłącz **Labels**, **Grid**, **All Data**, **All Colors**.
5. Zachowaj obraz opcji, obraz szkicu, TXT i oba DXF oraz sumy kontrolne.
   Sprawdź, że kopia `.top` pozostała identyczna bajtowo.

Walidację liczb, geometrii i ograniczenia tej próby opisuje
[README dowodu](evidence/shadow/README.md). Eksport aplikacji jest niezależnym
materiałem porównawczym; zgodność liczności obiektów nie zastępuje porównania
ich współrzędnych.

## Uzupełnienie z P01

[Wzorce P01](evidence/p01/README.md) zawierają także nowe pliki utworzone
w GUI i przez [natywny model aplikacji](evidence/p01/NATIVE_API.md).
Helper C# nie jest własnym writerem ani docelowym konwerterem.

W widoku szkicu ponowne kliknięcie aktywnej ikony szkicu na dolnym pasku
przełącza plan/sideview. Przed otwarciem menu po rysowaniu wybierz wskaźnik
(strzałka przed paletą); aktywne narzędzie rysowania może przechwycić kliknięcia.
Po Undo sprawdź zapisany plik i eksport: samo zniknięcie punktu z widoku nie
stanowi dowodu zmiany trwałego źródła. Zrzuty są dowodem widocznego fragmentu;
pełny audyt używa natywnych plików i jawnych oczekiwań.
