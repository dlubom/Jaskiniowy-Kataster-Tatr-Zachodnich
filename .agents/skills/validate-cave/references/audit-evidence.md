# Dowody, pokrycie i raport audytu

Rozwijaj istniejący raport jaskini zamiast tworzyć konkurencyjne podsumowania.
Gdy go brak, użyj `WERYFIKACJA_ZRODEL.md` obok plików jaskini. Duże porównanie
wierszy zapisz w osobnym CSV/JSON obok raportu; małe może być tabelą Markdown.
Nie traktuj poniższych tabel jako nakazu zakładania pustych plików.

## Stan audytu i łańcuch pochodzenia

Zapisz obiekt, zakres źródeł wskazanych przez kontrybutora i ograniczenia dostępu, datę audytu,
bazowy commit i stan zmian lokalnych. Dla każdego źródła określ:

| Pole | Zawartość |
| --- | --- |
| Identyfikator | Trwały identyfikator w raporcie, np. S01 |
| Miejsce pozyskania | Usługa lub ścieżka lokalna, plik/rewizja/PR/mail/URL i dokładna strona, członek archiwum lub załącznik |
| Integralność | Oryginalna nazwa, rozmiar i SHA-256 pobranych bajtów |
| Relacja do _RAW | Paczka i plik; identyczny / różny / brak / niezweryfikowany oraz metoda porównania |
| Rola | Pierwotny pomiar, kopia, transkrypcja, konwersja, obliczenia, opis historyczny |
| Kompletność | Strony, pliki i rekordy dostępne/brakujące; granice potwierdzonego pochodzenia |

Najwcześniejszy odnaleziony plik nie musi być pierwotnym pomiarem. Jeśli
łańcuch urywa się na cudzej transkrypcji, powiedz to wprost. Oddziel datę
pomiaru z jej precyzją od daty pliku, publikacji, przekazania i pozyskania.

## Rejestr porównania rekordów

Każdy rekord ma własny wiersz lub element JSON. Zachowaj:

- źródło + strona/wiersz/komórka lub indeks rekordu oraz kontekst dyrektyw;
- dosłowny FROM/TO i D/A/V lub inną treść źródłową, jednostki i niepewne znaki;
- docelowy plik, stabilny identyfikator rekordu i numer linii dla wskazanego
  commita/hasza (linia może się zmienić po dodaniu metadanych);
- wartości aktywne, mapowanie stacji, wykonane przekształcenie i jego podstawę;
- wynik: zgodny, uzasadnione przekształcenie, rozbieżny, nieczytelny,
  brak źródła albo brak odpowiednika; osobno los w projekcie, np. wariant
  historyczny lub wyłączenie z podaniem dowodu i przyczyny.

Uśrednienie wielu odczytów wymaga relacji wiele → jeden z listą wejść
i potwierdzeniem powtórzenia. Pominięty rekord nadal występuje w rejestrze.
Nie zakładaj stałej pozycji pól ani tego, że każdy niekomentarz jest strzałem.
Zachowaj odrębnie rekordy bez liczb, jeśli niosą istotną informację.

Podsumuj obie strony: ile aktywnych rekordów ma źródło i ile źródłowych
rekordów rozliczono. Podaj mianowniki, rozbieżności, nieczytelne miejsca
i braki, z rozdziałem typów pomiarów. Zgodność 100% dostępnych rekordów
nie oznacza kompletności, jeżeli brakuje stron lub całego pomiaru.

## Ustalenia i decyzje

Dla każdej korekty/spornej informacji zapisuj: **źródło → obserwacja →
hipoteza → sprawdzenie → decyzja → ograniczenie**. Podaj wcześniejszą
i przyjętą wartość, jej status oraz dokładną podstawę. „Preferowany odczyt”
nie oznacza „potwierdzony odczyt”. Nierozstrzygnięty znak ma warianty,
a nie wymuszoną jedną liczbę. Tak samo dokumentuj autorstwo, daty,
deklinację, identyfikację stacji i wyłączenia z aktywnego pomiaru.

## Wyniki walidacji

Raportuj odrębnie, ze statusem i dowodem:

| Obszar | Co wynik może potwierdzić |
| --- | --- |
| Pochodzenie i integralność | Zgodność pobranych bajtów z _RAW oraz zakres odzyskanej historii |
| Pomiary | Zgodność rekordów i uzasadnienie przekształceń w zbadanym zakresie |
| Metadane | Zgodność informacji z przypisanymi źródłami oraz kontraktem repozytorium |
| Kompilacja/eksporty | Poprawność przetwarzania konkretnych wejść przez wskazane wersje programów |
| Kontrola GUI | Faktycznie obejrzany model, oryginał lub eksport i zakres tej kontroli |

Używaj stanów `potwierdzone w podanym zakresie`, `rozbieżność`, `częściowe`,
`niesprawdzone` lub `nie dotyczy`, zamiast jednego zbiorczego „OK”. Przy
narzędziach zapisz polecenie/wersję, wejście, ustawienia, kod zakończenia,
ostrzeżenia, istotne statystyki przed/po i lokalizację dowodów.

Podsumowanie zawiera listę zmian, nierozstrzygnięte pytania i konkretny
brakujący dowód, a także ostatni ukończony zakres i następny krok, jeśli
audyt trzeba wznowić. Wynik kompilacji nie potwierdza pochodzenia danych,
tożsamości stacji, odczytu skanu ani historycznej daty.
