# Metadane aktywnych pomiarow SRV i paczek zrodlowych RAW

Data projektu: 2026-06-04

## Cel

Kazdy aktywny plik pomiarowy `.SRV` ma zawierac na poczatku kompletny,
walidowalny blok metadanych. Metadane maja opisywac pomiar, jego jakosc,
przetworzenie oraz wskazywac konkretne paczki materialow zrodlowych.

Oryginalne materialy wewnatrz `_RAW` pozostaja bitowo nietkniete. Metadane
kazdej dostawy zrodlowej sa przechowywane w pliku `README.md` numerowanej paczki
`_RAW/01`, `_RAW/02` itd.

Zmiana ma zapewnic:

- lokalna identyfikowalnosc pochodzenia kazdego aktywnego pomiaru;
- jawne oznaczanie nieznanych lub niedostepnych informacji;
- odroznienie danych terenowych od konwersji, korekt i rekonstrukcji;
- automatyczna walidacje kompletnego kontraktu;
- jednolity sposob tworzenia metadanych przez repozytoryjne skills.

## Zakres

Kontrakt metadanych dotyczy wszystkich aktywnych plikow `.SRV` pod
`Poligony/`, z nastepujacymi wyjatkami:

- generowany `Poligony/OTWORY.SRV`;
- modele terenu i inne pliki `.SRV` pod `Powierzchnia/`;
- wszystkie pliki znajdujace sie wewnatrz katalogow `_RAW/`.

Kontrakt paczek zrodlowych dotyczy kazdego katalogu `_RAW/` nalezacego do
jaskini lub aktywnego pomiaru.

## Wybrane podejscie

Metadane aktywnego pomiaru sa przechowywane w bloku komentarza Walls
`#[ ... #]` na poczatku tego samego pliku `.SRV`. Metadane zrodel sa
przechowywane w `README.md` numerowanych paczek `_RAW/NN/`.

To podejscie:

- utrzymuje opis aktywnego pomiaru razem z pomiarem;
- jest ignorowane przez Walls jako komentarz blokowy;
- nie wymaga osobnych plikow sidecar dla kazdego `.SRV`;
- zachowuje niezmiennosc oryginalnych materialow;
- pozwala walidowac powiazania przez `SOURCE_REF`.

Odrzucono osobne pliki YAML przy kazdym `.SRV` oraz centralny manifest. Oba
rozwiazania latwiej oddzielic od pomiarow podczas przenoszenia plikow, a
centralny manifest dodatkowo zwiekszalby konflikty edycyjne.

## Kontrakt aktywnego SRV

Kazdy aktywny plik pomiarowy `.SRV` musi zaczynac sie dokladnie jednym blokiem
metadanych:

```text
#[
CAVE_ID         "T.X-00.00"
CAVE_NAME       "Nazwa jaskini"
SURVEY_ID       "IDENTYFIKATOR"
SURVEY_NAME     "Nazwa lub opis ciagu"
UPDATE_DATE     "YYYY-MM-DD"
PROJECT_NAME    "Kataster jaskin tatrzanskich"
COORDINATOR     "Imie i nazwisko"
COORDINATOR_EMAIL "adres@example.org"
SOURCE_REF      "_RAW/01"
SOURCE_REF      "../_RAW/02"
LICENSE         "http://creativecommons.org/licenses/by-sa/4.0/"

TEAM            "osoby lub nieznane"
INSTRUMENT      "instrument lub nieznane"
SURVEY_DATE     "YYYY-MM-DD"
SURVEY_GRADE    "BCRA:5D"
PROCESSING      "opis przetworzenia"
#]
```

Wartosci tekstowe sa zapisywane w podwojnych cudzyslowach. Wszystkie metadane
aktywnych `.SRV` musza pozostac ASCII, zgodnie z ograniczeniami repozytorium.
Kazde pole zajmuje jeden wiersz w postaci `NAZWA_POLA "wartosc"`. Puste
wiersze wewnatrz bloku sa dozwolone wylacznie jako wizualne oddzielenie grup
pol. Komentarze oraz dowolne inne wiersze wewnatrz bloku nie sa dozwolone.

### Pola strukturalne

Nastepujace pola sa wymagane i nie moga miec wartosci `nieznane`:

- `CAVE_ID`;
- `CAVE_NAME`;
- `SURVEY_ID`;
- `SURVEY_NAME`;
- `SOURCE_REF`;
- `LICENSE`.

`SOURCE_REF` moze wystapic wielokrotnie. Jest wzgledna sciezka POSIX liczona od
katalogu aktywnego `.SRV`; musi konczyc sie segmentami `_RAW/NN` i po
normalizacji pozostawac wewnatrz `Poligony/`. Dzieki temu pliki w podkatalogach
systemu jaskiniowego moga wskazywac wspolna paczke nadrzedna bez duplikowania
materialow. Bezwzgledne sciezki i wyjscie poza `Poligony/` sa zabronione. Kazda
wskazana paczka musi zawierac poprawny `README.md`.

### Pola wymagane dopuszczajace nieznane

Nastepujace pola sa wymagane, ale moga miec wartosc `nieznane`, gdy informacji
nie da sie wiarygodnie ustalic:

- `UPDATE_DATE`;
- `PROJECT_NAME`;
- `COORDINATOR`;
- `COORDINATOR_EMAIL`;
- `TEAM`;
- `INSTRUMENT`;
- `SURVEY_DATE`;
- `SURVEY_GRADE`;
- `PROCESSING`.

`TEAM`, `INSTRUMENT`, `SURVEY_DATE` i `PROCESSING` moga wystapic wielokrotnie.
Pozostale pola musza wystapic dokladnie raz.

### Daty i deklinacja

`SURVEY_DATE` jest metadana opisowa i nie zastepuje operacyjnych dyrektyw
Walls/Survex. Moze wystapic wielokrotnie dla pomiarow wykonanych w roznych
dniach. Nie wolno dopisywac falszywej precyzji. Znane daty moga miec format
`YYYY`, `YYYY-MM`, `YYYY-MM-DD` albo zakres `DATA/DATA`, gdzie obie strony
uzywaja jednego z tych formatow. Dopuszczalna jest wartosc `nieznane`.

Kazdy aktywny strzal pomiarowy o niezerowej dlugosci musi byc poprzedzony
obowiazujaca w jego miejscu operacyjna dyrektywa:

- `#date`, gdy data pomiaru jest wiarygodna; albo
- swiadome `#Units DECL=...`, gdy wiarygodnej daty brak.

Stan dyrektyw jest sledzony w kolejnosci pliku, tak jak podczas przetwarzania
przez Walls/Survex. Zero-shoty oraz pliki bez aktywnych strzalow, na przyklad
calkowicie wykomentowane odlozone pomiary, nie wymagaja `#date` ani `DECL`.

### Jakosc pomiaru

`SURVEY_GRADE` opisuje deklarowana jakosc pomiaru. Preferowany format to
`BCRA:<klasa>`, na przyklad `BCRA:5D`. Dopuszczalne sa:

- znana klasa BCRA;
- `BCRA:nieznane`;
- jawnie nazwany inny standard;
- `nieznane`.

Wartosci innych standardow maja postac `<STANDARD>:<KLASA>`, gdzie oba czlony
sa niepustymi identyfikatorami ASCII bez spacji.

Walidator sprawdza format pola, ale nie wylicza klasy i nie potwierdza jej
prawdziwosci. Klasyfikacja BCRA zalezy od metody, dokladnosci instrumentow,
stabilnosci punktow i sposobu rejestracji szczegolow, dlatego nie moze byc
wnioskowana tylko z nazwy instrumentu.

### Przetworzenie

`PROCESSING` opisuje operacje wykonane podczas tworzenia aktywnego pliku ze
zrodla. Przyklady:

```text
PROCESSING      "konwersja SVX -> SRV"
PROCESSING      "usredniono pomiary przod/tyl"
PROCESSING      "dodano zero-shot laczacy"
```

Gdy historia przetworzenia jest nieznana, wymagane jest:

```text
PROCESSING      "nieznane"
```

Walidator wymaga co najmniej jednego pola `PROCESSING`, ale nie ocenia
prawdziwosci opisu.

### Rola DATA_SOURCE

Dotychczasowe pole `DATA_SOURCE` nie pozostaje czescia docelowego kontraktu
aktywnych `.SRV`. Pochodzenie danych jest opisywane w `README.md` paczki
zrodlowej, a aktywny plik wskazuje ja przez `SOURCE_REF`.

Podczas migracji wartosci z istniejacych `DATA_SOURCE` nalezy zachowac w
metadanych odpowiednich paczek `_RAW/NN`.

## Kontrakt paczki RAW

Kazda niezalezna dostawa materialow zrodlowych jest osobna, numerowana paczka:

```text
<katalog-jaskini>/_RAW/
  01/
    README.md
    source.zip
    source/
      ...
  02/
    README.md
    ...
```

Numer ma zawsze dwie cyfry, zaczynajac od `01`. Nowa niezalezna dostawa
dostaje kolejny wolny numer. Istniejace numerowane paczki zachowuja swoje
numery.

Glowny `_RAW/README.md` jest opcjonalnym indeksem paczek. Nie jest miejscem
docelowego kontraktu dostawy i nie zastepuje `_RAW/NN/README.md`.

### Niezmiennosc materialow

Plikow i katalogow materialow zrodlowych wewnatrz paczek nie wolno
modyfikowac, poprawiac, przepisywac ani normalizowac. Metadane `README.md` nie
sa materialem zrodlowym i moga byc tworzone lub aktualizowane. Podczas migracji
dopuszczalne jest jedynie przeniesienie materialow do numerowanej paczki z
zachowaniem bajtow i wewnetrznej struktury.

Walidator nie analizuje tresci plikow zrodlowych.

### Wymagane metadane README

Kazdy `_RAW/NN/README.md` musi uzywac nastepujacego kanonicznego formatu:

```markdown
# Nazwa jaskini - opis paczki

- **Status materiału:** dostępny
- **Pochodzenie danych:** opis albo nieznane
- **Autorzy pomiarów:** osoby albo nieznane
- **Daty pomiarów:** daty albo nieznane
- **Data pozyskania:** data albo nieznane
- **Dodał do _RAW:** osoba albo nieznane
- **Licencja źródłowa:** licencja albo nieznane
- **Kompletność:** opis albo nieznane

## Zawartość

- `source.zip` - opis
- `source/` - opis
```

Nazwy osmiu pol oraz naglowek `## Zawartość` sa dokladne i
niepowtarzalne. Kolejnosc pol jest stala jak w szablonie. Naglowek dokumentu
oraz opisy wartosci sa dowolne. Lista pod `## Zawartość` musi miec co najmniej
jeden wpis dla paczki dostepnej lub czesciowej.

Wartosci nieznane sa dozwolone i musza byc jawnie zapisane jako `nieznane`.
README moze uzywac polskich znakow; ograniczenie ASCII dotyczy aktywnych
plikow `.SRV`, a nie dokumentacji `_RAW`.

### Brak materialow zrodlowych

Aktywny `.SRV`, dla ktorego repozytorium nie ma jeszcze materialow
zrodlowych, nadal wskazuje konkretna pusta paczke, na przyklad `_RAW/01`.

Jej `README.md` musi zawierac kompletny kanoniczny szablon, w tym:

```markdown
- **Status materiału:** niedostępny
- **Pochodzenie danych:** nieznane
- **Kompletność:** brak materiałów źródłowych

## Zawartość

- Brak materiałów źródłowych.
```

Pozostale wymagane pola rowniez musza byc obecne. Pusta paczka jest dozwolona
wylacznie ze statusem `niedostępny`.

## Walidacja

Powstanie modul `src/jktz/validation/metadata.py`, uruchamiany jako wczesny
krok `jktz-validate`.

### Walidacja aktywnych SRV

Walidator sprawdza:

- dokladnie jeden blok `#[ ... #]` na poczatku pliku;
- obecnosc wszystkich wymaganych pol;
- brak nieznanych nazw pol;
- pojedynczosc pol niepowtarzalnych;
- format znanych wartosci `UPDATE_DATE` oraz precyzyjnych, czesciowych i
  zakresowych wartosci `SURVEY_DATE`;
- format `SURVEY_GRADE`;
- format `SOURCE_REF` jako wzglednej sciezki konczacej sie `_RAW/NN`;
- bezpieczne rozwiazanie `SOURCE_REF` do sciezki pozostajacej w `Poligony/`;
- istnienie kazdej wskazanej paczki i poprawnego `README.md`;
- obecnosc obowiazujacego `#date` albo swiadomego `#Units DECL=...` dla kazdego
  aktywnego niezerowego strzalu pomiarowego.

### Walidacja RAW

Walidator sprawdza:

- w `_RAW/` wystepuja wylacznie numerowane katalogi paczek oraz opcjonalny
  glowny `README.md`;
- materialy nie pozostaly bezposrednio w glownym `_RAW/`;
- kazda paczka ma poprawny `README.md`;
- README zawiera wszystkie wymagane pola i sekcje `## Zawartość`;
- pusta paczka ma status `niedostępny`;
- wszystkie `SOURCE_REF` wskazuja istniejace paczki.

Pliki zrodlowe nie sa parsowane ani modyfikowane przez walidator.

### Raportowanie bledow

Jeden przebieg walidatora zbiera wszystkie naruszenia i grupuje je wedlug
pliku. Kazdy blad wskazuje sciezke oraz konkretne brakujace, powtorzone albo
niepoprawne pole. Walidacja nie zatrzymuje sie na pierwszym naruszeniu.

## Helper i repozytoryjne skills

Wspolnym repozytoryjnym helperem jest entry point `jktz-srv-metadata`.
Udostepnia `srv-set`, `srv-update`, `raw-set` oraz `hash-raw`. Skills uzywaja
tych komend zamiast recznie skladac bloki.

Helper:

- zachowuje bez zmian wszystkie pomiary i dyrektywy poza blokiem metadanych;
- nigdy nie modyfikuje materialow zrodlowych wewnatrz `_RAW`;
- moze tworzyc lub aktualizowac wylacznie metadane `README.md` w `_RAW`;
- wstawia brakujace wartosci jako `nieznane`;
- tworzy lub uzupelnia `_RAW/NN/README.md`;
- przyjmuje wiele `SOURCE_REF`, dat, zespolow, instrumentow i operacji
  przetwarzania;
- jest idempotentny.

Komendy zapisujace obsluguja `--dry-run`, waliduja kompletny wynik przed
zapisem i podmieniaja plik atomowo. Implementacja CLI znajduje sie w
`src/jktz/cli/srv_metadata.py`, a kod domenowy w `src/jktz/metadata/`.

Aktualizacji wymagaja co najmniej:

- `add-cave`: zawsze tworzy `_RAW/01/`, README paczki i kompletny naglowek;
- `svx-to-srv`: przenosi dostepne daty, zespol, instrument i zapisuje
  `PROCESSING`;
- `average-shots`: dopisuje operacje przetwarzania;
- inne skills zmieniajace aktywne `.SRV`: zachowuja blok i aktualizuja
  `UPDATE_DATE` lub `PROCESSING`, gdy zmieniaja znaczenie danych.

Walidator pozostaje ostatecznym zabezpieczeniem przed pominieciem helpera.

## Migracja atomowa

Twarda walidacja zostanie wlaczona dopiero po migracji calego aktualnego
zbioru. Repozytorium nie powinno miec przejsciowego stanu, w ktorym obecne dane
nie spelniaja aktywnej walidacji.

Migracja:

1. Przenosi materialy z kazdego plaskiego `_RAW/` do `_RAW/01/`, zachowujac
   bajty i wewnetrzna strukture. Istniejacy glowny `_RAW/README.md` staje sie
   podstawa kanonicznego `_RAW/01/README.md`; nie jest traktowany jako
   chroniony material zrodlowy.
2. Zachowuje istniejace numery paczek.
3. Dodaje brakujace README do numerowanych paczek.
4. Tworzy puste paczki ze statusem `niedostępny` dla pomiarow bez materialow
   zrodlowych.
5. Dodaje kompletny naglowek do wszystkich aktywnych pomiarowych `.SRV`.
6. Dodaje jedno lub wiele `SOURCE_REF` do odpowiednich paczek.
7. Przenosi istniejace `DATA_SOURCE` do README paczek.
8. Zachowuje mozliwe do ustalenia metadane, a pozostale wypelnia wartoscia
   `nieznane`.
9. Aktualizuje skills i wlacza twarda walidacje w tym samym zestawie zmian.

## Testowanie i kryteria akceptacji

### Testy automatyczne

Testy jednostkowe obejmuja:

- parser bloku metadanych aktywnego `.SRV`;
- parser kontraktu `_RAW/NN/README.md`;
- wszystkie wymagane pola, formaty i reguly powtarzalnosci;
- rozpoznawanie aktywnych strzalow oraz wymogu `#date` lub `DECL`;
- wyjatki zakresu;
- grupowanie wielu bledow;
- helper, w tym idempotencje i brak zmian poza naglowkiem;
- brak odczytu lub modyfikacji tresci plikow zrodlowych.

### Dowod zachowania danych

Migracja musi wykazac:

- identyczny multizbior sum kontrolnych wszystkich dotychczasowych plikow
  materialowych `_RAW` przed i po migracji, niezaleznie od zmiany sciezki;
  inwentaryzacja pomija metadane `README.md`;
- brak zmian geometrii aktywnych pomiarow przed i po migracji;
- brak zmian pomiarow i dyrektyw aktywnych `.SRV` poza dodanym lub
  zaktualizowanym blokiem metadanych;
- poprawne przejscie pelnego `jktz-validate`.

### Stan koncowy

Zmiana jest zakonczona, gdy:

- kazdy objety zakresem aktywny `.SRV` ma poprawny kompletny naglowek;
- kazdy `SOURCE_REF` wskazuje poprawna paczke `_RAW/NN`;
- kazda paczka ma poprawny `README.md`;
- bezposrednio pod `_RAW/` nie ma materialow zrodlowych;
- wszystkie objete skills tworza lub zachowuja kontrakt;
- testy i pelna walidacja przechodza.

## Zrodla dziedzinowe

- Survex opisuje daty pomiarow jako operacyjna informacje o pomiarze i
  dopuszcza zakresy oraz daty o niepelnej precyzji:
  <https://survex.com/docs/manual/datafile.htm>
- Walls i Survex obliczaja deklinacje magnetyczna na podstawie lokalizacji i
  daty pomiaru:
  <https://survex.com/docs/manual/walls.htm>
- Klasy BCRA opisuja jakosc pomiaru na podstawie metody i dokladnosci, nie
  tylko nazwy instrumentu:
  <https://www.bcra.org.uk/surveying/>
