---
name: validate-cave
description: Audit a cave's source provenance and every survey record against _RAW, recover missing originals from Git/PR archives and contributor-provided local, cloud or email sources, and repair confirmed source or metadata errors. Use for a cave source audit, not compilation alone or conversion alone.
---

Przeprowadź audyt jaskini od najwcześniejszego dostępnego materiału do aktywnych
pomiarów i modelu. Wynik ma wyjaśniać, co potwierdzono, co poprawiono i czego
nadal nie można rozstrzygnąć. Pracuj według [AGENTS.md](../../../AGENTS.md).

## Zakres zlecenia

Przykłady:

- „Zwaliduj Kalacką, używając mojego Gmaila” — szukaj źródeł także przez
  plugin Gmail w trybie odczytu; pobierz potrzebne materiały.
- „Zwaliduj Śpiących Rycerzy z dostępnych materiałów w _RAW” — ogranicz
  dowody do wskazanych materiałów; luki wypisz bez rozszerzania poszukiwań.
- „Zwaliduj Hardą” — rozpoznaj obiekt, sprawdź repozytorium, jego historię,
  PIG i publiczne źródła oraz inne materiały wskazane do tego audytu.

Źródła zależą od kontrybutora: może wskazać własny katalog, ZIP, pocztę,
folder na OneDrive, Google Drive lub inną usługę. Gmail jest jednym
z przykładów, nie wymaganiem skilla. Korzystaj z narzędzi dostępnych dla
wybranej usługi; nie zakładaj dostępu do konta autora skilla ani dostępności
konkretnego pluginu u innych osób.

Zwykły audyt obejmuje uzupełnienie odzyskanych źródeł, metadanych oraz
poprawki jednoznacznie potwierdzonych błędów. „Tylko analiza”, „bez zmian”
lub „tylko tutaj” ogranicza wynik do raportu w zamówionym miejscu. Nie
uruchamiaj audytu konkretnej jaskini na podstawie samego przykładu użycia.
Wskazany do audytu folder, plik, link lub konto określa zakres odczytu.
Respektuj zgodę już udzieloną w rozmowie; nie pytaj ponownie. Jeśli do dalszego
szukania potrzebne jest prywatne źródło poza tym zakresem, zapytaj o dostęp
do konkretnego źródła i w tym czasie kontynuuj niezależną część audytu.

## Rozpoznanie i odzyskanie źródeł

1. Ustal jednoznacznie nazwę/aliasy, numer inwentarzowy i katalog jaskini.
   Korzystaj z dokładnych pól JSONL PIG według `AGENTS.md`. Gdy nazwa wskazuje
   kilka obiektów, wyjaśnij to przed zmianą ich danych.
2. Sprawdź stan Git, bazowy commit, drzewo `KATASTER.wpj`, wszystkie pomiary
   jaskini, `SOURCE_REF`, paczki `_RAW` i istniejące raporty. Rozróżnij
   aktywne pomiary, historyczne warianty i pliki niepodłączone do projektu.
   Zapisz stan wejściowy oraz hashe materiałów przed zmianami.
3. Odtwórz łańcuch: oryginalny plik/załącznik/archiwum → `_RAW` →
   transkrypcja lub konwersja → aktywny SRV. README, PR i dawna rozmowa są
   tropami oraz zapisami wcześniejszych decyzji, a ich twierdzenia sprawdza się
   w materiałach. Brak pliku na bieżącej gałęzi nie dowodzi braku w historii.
4. Przy poszukiwaniu poprzedników `_RAW`, dyskach, mailach, ZIP-ach i literaturze
   przeczytaj [pozyskiwanie źródeł](references/source-recovery.md).
   Porównuj bajty i zawartość; jednakowe nazwy nie potwierdzają identyczności.
5. Odzyskane oryginały umieść w odpowiedniej paczce `_RAW/NN` bez zmiany
   nazw, struktury i bajtów. Nowy niezależny przekaz lub inna wersja zasługuje
   na osobną paczkę; nie nadpisuj istniejącego materiału. OCR, kadry, poprawione
   obrazy i wyniki konwersji trzymaj poza `_RAW`. Brakujące źródło opisuj jako
   `częściowy` lub `niedostępny`, zgodnie z kontraktem metadanych; kopia
   aktywnego SRV nie staje się przez to odnalezionym oryginałem.

## Weryfikacja pomiarów i informacji

Utrzymuj odrębne dowody: bezpośredni odczyt źródła, jego pochodzenie,
obliczenia autora, konwersję, informacje z publikacji/PIG i wynik modelowania.
Zgodność źródeł pochodnych od tej samej transkrypcji nie jest niezależnym
potwierdzeniem. Użyj [schematu raportu](references/audit-evidence.md) do
zapisywania postępu i pokrycia bez ponownego czytania sprawdzonych materiałów.

- **Sprawdź każdy rekord w obie strony.** Powiąż każdy aktywny wiersz z
  plikiem i miejscem źródłowym; każdemu rekordowi źródła przypisz los: użyty,
  przekształcony, niezależny wariant, świadomie wyłączony, nierozstrzygnięty
  lub bez odpowiednika. Rozlicz także splaje, LRUD, domiary, dowiązania,
  komentarze wpływające na interpretację i szkice bez liczb. Sama zgodność
  sumy długości lub liczby wierszy nie wystarcza.
- **Odczytuj semantykę.** Sprawdź FROM/TO, prefiksy, kolejność D/A/V,
  jednostki, stopnie/grady, zenit/inklinację, znaki, pomiary wsteczne,
  kalibracje, deklinację, daty i aktywność segmentów. Zachowaj dosłowne
  wartości źródła obok jawnych przeliczeń, precyzji i mapowania stacji.
  Dla niepewnej składni czytaj lokalne manuale podlinkowane w `AGENTS.md`.
- **Skany oglądaj.** OCR służy do wyszukiwania i roboczej transkrypcji;
  zweryfikuj wzrokowo każdy wiersz, nagłówki, daty, podpisy i numerację stron.
  Przy niepewności obejrzyj pełną stronę oraz powiększenia/obrót kopii.
  Jeśli dostępny jest niezależny agent, zleć mu odczyt trudnych miejsc bez
  sugerowania oczekiwanej cyfry. Zachowaj oba odczyty, jeżeli nadal są możliwe.
  Nie wybieraj cyfry dlatego, że lepiej zamyka pętlę albo pasuje do PIG.
- **Nie utożsamiaj podobieństwa z tożsamością.** Ta sama numeracja, równe
  wektory i podobny przebieg nie uprawniają do łączenia stacji, uśredniania
  ani usuwania niezależnego pomiaru. Potwierdzenie powtórzenia wymaga dowodu
  źródłowego; udokumentuj osobno każdą zmianę aktywności/statystyki.
- **Metadane wiąż z konkretnym pomiarem.** Rozróżniaj mierniczych, autora
  opracowania, nadawcę i redaktora inwentarza. Zachowuj precyzję daty
  źródłowej; data maila, skanu, modyfikacji czy publikacji nie jest datą
  pomiaru. Zegar PocketTopo mógł się wyzerować: data tripu i nazwa pliku
  wymagają niezależnego potwierdzenia przed użyciem do deklinacji. Opisz
  osobno ewentualną datę obliczeniową i jej podstawę, bez dorabiania dnia.
- **PIG i literatura uzupełniają kontekst.** Przypisuj twierdzenie do
  konkretnego fragmentu publikacji i odróżniaj datę eksploracji od pomiaru.
  Rozbieżności długości, autorstwa i położenia odnotuj. Aktywne współrzędne
  pochodzą z projektu GPS; audyt PIG sam nie uzasadnia zmiany otworu.

## Uzupełnienia i istniejące narzędzia

Poprawiaj potwierdzone błędy z zachowaniem źródła, wcześniejszej wartości
i uzasadnienia w raporcie. Sprzeczność pozostaw jawną; kontynuuj pozostałe
rekordy. Nie rozwiązuj jej arbitralną zmianą danych tylko po to, by walidator
przeszedł. Zachowuj kodowanie i zakończenia linii istniejących SRV.

| Potrzeba | Narzędzie i zakres |
| --- | --- |
| PocketTopo `.top` | [pockettopo-convert](../pockettopo-convert/SKILL.md): istniejący CLI, ślad każdego rekordu, decyzje powiązane z SHA i jawna niekompletność |
| Survex → Walls | [svx-to-srv](../svx-to-srv/SKILL.md): konwersja z kontrolą semantyki dyrektyw |
| Potwierdzone odczyty powtórne | [average-shots](../average-shots/SKILL.md), wyłącznie na kopii roboczej po potwierdzeniu konkretnej grupy |
| Statystyki i wpływ korekty | [survex-stats](../survex-stats/SKILL.md), [verify-cave-refactor](../verify-cave-refactor/SKILL.md) dla porównania przed/po |
| Nowe włączenie do projektu | Odpowiednie kroki [add-cave](../add-cave/SKILL.md), tylko jeśli obejmuje je zlecenie |

Inne formaty (np. Therion, arkusz, tabela w mailu) rozpoznaj przed konwersją;
użyj dostępnego parsera/eksportera lub jawnej transkrypcji. Nie zakładaj
obsługi formatu przez konwerter tylko dlatego, że da się otworzyć plik.

Metadane zapisuj przez `uv run jktz-srv-metadata`:

- `raw-set` tworzy/zastępuje README paczki. Dla rozbudowanego README zapisz
  wynik `--dry-run` do pliku tymczasowego, połącz z zachowanymi dodatkowymi
  sekcjami i sprawdź komplet. Do walidacji i atomowego zapisu użyj istniejących
  API `parse_raw_metadata` z `jktz.metadata.raw` i `atomic_write` z
  `jktz.metadata.io`. Sam późniejszy `raw-set` usunąłby dodatkowe sekcje.
- `srv-update` obsługuje datę aktualizacji i dopisanie `PROCESSING`.
  Zmiana autorów, daty pomiaru czy `SOURCE_REF` wymaga `srv-set` z pełnymi
  zachowanymi metadanymi; wartości domyślne nie mogą wymazać znanej informacji.
- `hash-raw` pomaga sprawdzić integralność, ale pomija pliki o nazwie
  `README.md`. Jeśli oryginalna paczka zawiera taki plik, uwzględnij go osobno.

Sprawdź również składnię metadanych przez `parse_raw_metadata` oraz
`parse_srv_metadata` z `jktz.metadata.srv`. To odczyt możliwy także w audycie
bez zmian i bez kompilacji. Sama obecność nazw pól w tekście nie potwierdza,
że parser je rozpoznaje; rozróżnij brak informacji od błędnego formatu zapisu.

## Walidacja i zakończenie

Po zmianach danych porównaj pomiary i model przed/po na jawnych wejściach
i tych samych ustawieniach. Uruchom `uv run jktz-validate` oraz
`git diff --check`; wymagane bramki dla zmienianego kodu opisuje `AGENTS.md`.
Przy braku lokalnych zależności użyj [docker-validate](../docker-validate/SKILL.md).
Błąd środowiska zgłoś oddzielnie od błędu danych; nie obchodź hooków.

Gdy GUI pomaga ocenić zgodność lub użytkownik tego oczekuje, użyj dostępnych
narzędzi obsługi komputera: Walls (także pod Wine) do natywnej kompilacji,
PocketTopo do oryginału, Aven do modelu, QGIS do eksportów/CRS. Pracuj na
kopiach w katalogu tymczasowym i zapisz program, wersję, wejście, ustawienia
oraz faktycznie obejrzany wynik. Sam start procesu nie jest testem.
Nie nazywaj kompilacji SRV przez Survex walidacją w Walls. Brak GUI pozostawia
ten etap niesprawdzony, ale nie zatrzymuje pozostałej weryfikacji.

Zaktualizuj istniejący raport lub zapisz `WERYFIKACJA_ZRODEL.md` obok jaskini
zgodnie z zakresem zapisu; dowody i transkrypcje umieszczaj poza `_RAW`.
Sprawdź końcowe hashe oryginałów i przeglądnij diff. Zmiany do repozytorium
opisz zwięźle w `Unreleased`. Commit/push/PR wykonuj w uzgodnionym zakresie;
sam audyt nie oznacza publikacji ani wydania. Przy PR raportuj CI dla jego
dokładnego commita. Nie zmieniaj rozstrzygniętego zakresu na audyt innych jaskiń.

W podsumowaniu podaj pokrycie, poprawki, nierozstrzygnięte miejsca, wykonane
testy i ścieżki dowodów. „Brak znalezionych błędów” dotyczy tylko sprawdzonych
rekordów; brak źródeł nie pozwala uznać pomiarów za potwierdzone.
