# Odzyskiwanie i pochodzenie źródeł

Czytaj przy poszukiwaniu materiałów sprzed `_RAW`, brakujących załączników
lub historycznych informacji. Dobieraj poszukiwania do konkretnej luki;
zapisuj zapytania, zakres, wynik i ograniczenia, żeby można było je wznowić.

## Historia repozytorium, PR i rozmowy

- Zacznij od historii katalogu, nazw plików, aliasów jaskini i `SOURCE_REF`.
  `git log --all -- <ścieżka>` oraz `git log --follow -- <plik>` pomagają
  znaleźć migracje i usunięcia. Sprawdź stare położenie sprzed numerowanych
  paczek, pliki ZIP, branch dodający jaskinię oraz wskazane w commitach PR/issue.
- Korzystaj z `git show <commit>:<ścieżka>`; pliki binarne wyciągaj do
  katalogu tymczasowego bez dekodowania tekstowego. Nie trzeba przełączać
  bieżącego drzewa, żeby przeczytać historyczny plik.
- Przez dostępny plugin GitHub lub `gh` odczytaj opis PR, komentarze,
  zmienione pliki i odnośniki do źródeł. Paczka wydania JKTZ nie zawiera
  `_RAW`; artefakt CI z samym eksportem nie zastępuje oryginału.
- Jeżeli przydatna jest historia Codex, użyj narzędzi listowania/odczytu
  rozmów. Traktuj zapisaną odpowiedź jako trop do pliku, commita lub maila;
  dawne „zweryfikowano” nie zastępuje weryfikacji bieżącego wejścia.

## Źródła wskazane przez kontrybutora

Dobierz dostęp do miejsca, które wskazała osoba zlecająca audyt. Nie ma
wymaganego dostawcy ani wspólnego prywatnego konta projektu.

- **Pliki lokalne lub dostarczony ZIP:** czytaj wskazane ścieżki, zachowaj
  pochodzenie przekazania i hashe. Katalog synchronizowany z chmurą traktuj
  jako lokalną kopię; nie twierdź, że sprawdzono wersję serwerową bez odczytu
  jej metadanych lub historii.
- **OneDrive, Google Drive i inne dyski:** odkryj dostępny plugin/connector
  i jego skill, jeśli występuje. Szukaj w uzgodnionym folderze lub zbiorze,
  sprawdź paginację i pobierz oryginalny plik binarny. Zapisz usługę, ID/URL,
  ścieżkę, rewizję, jeśli jest dostępna, oraz hash pobranych bajtów. Historia
  wersji może zawierać wcześniejszy materiał niż bieżący plik.
- **Dokument natywny usługi:** eksport arkusza/dokumentu jest reprezentacją
  źródła, nie kopią bajtową obiektu w chmurze. Zachowaj ID i dostępną rewizję,
  sposób eksportu i jego hash; sprawdź wszystkie istotne zakładki, formuły
  oraz ukryte wiersze. Zmiany formatu i precyzji podczas eksportu rozlicz jawnie.
- **Poczta:** użyj pluginu właściwego dla wskazanego konta, np. Gmaila lub
  innego dostępnego dostawcy. Szczegóły odczytu poniżej zależą od jego API.

W każdym przypadku czytaj aktualne schematy narzędzi. Dostęp do jednego
folderu, konta lub udostępnionego linku nie rozszerza zakresu na inne konta.
Audyt obejmuje odczyt i pobranie materiałów, bez zmiany plików źródłowych
w usłudze, udostępnień czy stanu wiadomości. Brak pluginu lub uprawnień nie
oznacza braku źródła: opisz ograniczenie i kontynuuj dostępną część pracy.
Można wykorzystać dostarczony przez kontrybutora plik/eksport lub dostępny
dozwolony interfejs, jawnie zachowując ograniczenia pochodzenia. Nie obchodź
braku dostępu przez szukanie tokenów w profilach aplikacji.

## Poczta i załączniki

Używaj wyszukiwania, odczytu wiadomości/wątku i pobierania załączników.
Zgoda na źródła nie upoważnia do wysyłania, tworzenia szkiców, zmiany etykiet
lub stanu wiadomości.

1. Szukaj po nazwie i aliasach jaskini, nazwach źródłowych plików, autorach
   i temacie przekazania. Filtr załączników (np. `has:attachment` w Gmailu)
   pomaga, lecz nie obejmuje tabel w treści maila. Poszerzaj daty na podstawie
   dowodów; data wysłania może
   być wiele lat późniejsza niż pomiar. Sprawdź paginację wyników.
2. Odczytaj pełne istotne wiadomości, nie tylko snippet. Prześledź odwołania
   do wcześniejszego maila, brakujących części, korekt i list załączników.
   Zachowaj różne przesłane wersje jako odrębne źródła, dopóki nie ustalisz
   ich relacji. Nadawca/forwarder nie musi być autorem pomiarów.
3. Pobieraj oryginalny załącznik, a nie wygenerowany podgląd/OCR. Stosuj
   identyfikator z odpowiedzi narzędzia, respektuj obsługiwane typy oraz
   ograniczenia pobierania. SHA-256 i rozmiar licz z pełnych lokalnych bajtów.
   Ten sam obraz po rekompresji może być wizualnie równy, ale nie identyczny.
4. Jeśli bezpośredni załącznik nie jest obsługiwany, sprawdź, czy plugin
   udostępnia pełny raw/MIME. W takim przypadku można wyodrębnić część MIME
   bez utraty bajtów. Nie rekonstruuj oryginału z uciętego base64, HTML
   ani OCR; gdy narzędzie nie daje pełnego pliku, zapisz brak weryfikacji.
5. W raporcie zachowaj minimalne potrzebne pochodzenie: data przekazania,
   nadawca w roli źródła, nazwa pliku, hash i odnośnik/identyfikator wiadomości.
   Pełnych prywatnych wątków, nagłówków dostępowych i niezwiązanej korespondencji
   nie dodawaj automatycznie do repozytorium. Gdy pomiary są wyłącznie w treści
   maila, zachowaj w `_RAW` dostępną oryginalną część MIME lub wierny eksport
   źródłowej treści, w zakresie potrzebnym do audytu. Opisz sposób i zakres
   ekstrakcji, kodowanie i hash; odróżnij bajty MIME, zdekodowaną treść
   i wyciąg tekstowy pluginu. Wyciągu nie nazywaj kopią bajtową wiadomości.
   Roboczą transkrypcję tabeli zapisuj osobno poza `_RAW`.

## ZIP i inne archiwa

- Zachowaj oryginalne archiwum i jego hash. Przed rozpakowaniem sprawdź
  spis, rozmiar i ścieżki; wyklucz wyjście poza katalog docelowy, nadpisanie
  oraz dowiązania prowadzące na zewnątrz. Rozpakowuj do nowego katalogu.
- Zachowaj nazwy i strukturę członków; w manifeście zapisz hash archiwum
  i członka oraz relację do `_RAW`. To pozwala sprawdzić identyczność
  rozpakowanego pliku niezależnie od daty pliku w ZIP-ie.
- Rozlicz brakujące strony/części i duplikaty. Jeśli archiwum zawiera już
  SRV, ustal, czy jest to pomiar autora, czy późniejsza konwersja; rozszerzenie
  i wiek pliku nie określają jego roli w łańcuchu.
- Przy kolizji nazwy zachowaj oryginały w osobnych paczkach. Nie naprawiaj
  źródłowych błędów ani nazwy pliku wewnątrz `_RAW`.

## PIG, czasopisma i publikacje

Najpierw rozpoznaj rekord w lokalnym JSONL po `inventory_number`, zachowując
odrębny `cave_id`. Następnie szukaj konkretnej luki: nazwiska mierniczego,
terminu akcji, autorstwa planu lub historii danego ciągu. Uwzględniaj
pisownię polską i aliasy, tytuły wskazane przez użytkownika (np. „Jaskinie”,
„Wiercica”, „Wierchy”, „Taternik”), biblioteki cyfrowe, archiwa klubowe
i publikacje naukowe. Sprawdzaj tytuł, wydanie, rok i stronę w samym materiale.

Wyszukiwarka, OCR i bibliografia służą do odnalezienia publikacji. Dowodem
twierdzenia jest przeczytany fragment, podpis planu lub skan strony.
Zapisuj pełny opis bibliograficzny, URL, stronę, twierdzenie i jego zakres.
Zespół eksploracyjny nie musi być zespołem pomiarowym; wymienienie nazwiska
w historii jaskini nie przypisuje mu wszystkich pomiarów. Nie podnoś
precyzji daty ponad to, co zapisano w źródle. Nie przyjmuj licencji projektu
za licencję odnalezionej publikacji lub załącznika.

Nie kopiuj całej publikacji do repozytorium tylko po to, żeby poprzeć jedno
twierdzenie; wystarczy sprawdzalny odnośnik i zwięzłe przytoczenie/parafraza.
W publicznych zapytaniach nie umieszczaj prywatnej treści maili.

## Kiedy zakończyć poszukiwania

Zakończ, gdy porównano odnalezione źródła i sprawdzono konkretne tropy
w zamówionym zakresie. Brak dostępu, wygasły artefakt lub nierozstrzygająca
publikacja to ograniczenie dowodowe. Po bezowocnym sprawdzeniu sensownych
aliasów, historii i wskazanych odnośników opisz, czego brakuje i jaki nowy
materiał mógłby to rozstrzygnąć; nie ponawiaj tych samych zapytań bez nowego
tropu. Dalsze niezależne części audytu nadal można ukończyć.
