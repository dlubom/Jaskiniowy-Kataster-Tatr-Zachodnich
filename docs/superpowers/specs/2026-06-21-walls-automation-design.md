# Automatyczna walidacja projektu w Walls

**Data:** 2026-06-21

**Status:** zaakceptowany projekt

**Zakres:** lokalny test pod Wine oraz nieblokujacy test GitHub Actions na Windows

## Cel

Projekt ma uruchamiac natywny Walls na `KATASTER.wpj`, wymuszac pelna
rekompilacje korzenia projektu i publikowac jednoznaczny raport. Pierwsze
wdrozenie ma charakter diagnostyczny: wykryte problemy beda widoczne jako
ostrzezenia i artefakty, ale nie zablokuja pull requestu ani galezi `master`.

Istniejaca walidacja Survex pozostaje niezaleznym, obowiazkowym gate'em.
Test Walls ma wykrywac roznice zachowania oryginalnego programu, ktorych
Cavern nie musi raportowac.

## Ustalenia z rozpoznania

- `Walls32.exe` przyjmuje sciezke projektu `.wpj` jako argument i otwiera go
  poprawnie pod Wine.
- Dostarczany z Walls `runwalls.exe` jest launcherem przekazujacym argumenty
  do `Walls32.exe`; nie udostepnia interfejsu kompilacji w trybie CLI.
- Polecenie `Recompile item` ma skrot `F5` i identyfikator Win32
  `ID_RECOMPILE` (`32825`) w przypietej wersji kodu Walls.
- Computer Use rozpoznaje aplikacje `Wine Staging`, ale nie potrafi pobrac
  drzewa dostepnosci okna programu Windows. Test cykliczny nie moze zalezec od
  klikania, rozpoznawania obrazu ani macOS Accessibility.
- Testy widocznego desktopowego GUI nie sa wspierane na hostowanych agentach
  Microsoft. Dlatego `windows-latest` jest najpierw srodowiskiem proof of
  concept, a nie zalozona gwarancja dzialania. W razie braku dostepu do okien
  Win32 test zostanie przeniesiony na interaktywny self-hosted Windows.

Zrodla:

- [Oficjalne zrodla Walls](https://github.com/wallscavesurvey/walls)
- [Microsoft: UI testing considerations](https://learn.microsoft.com/en-us/azure/devops/pipelines/test/ui-testing-considerations)
- [GitHub: GitHub-hosted runners](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)

## Zakres pierwszej wersji

Pierwsza wersja obejmuje:

1. natywny sterownik Win32 uruchamiajacy Walls;
2. pelna rekompilacje korzenia `KATASTER.wpj`;
3. klasyfikacje wyniku i raport maszynowy;
4. uruchomienie lokalne pod Wine;
5. osobny workflow Windows uruchamiany recznie i codziennie;
6. publikacje raportu i plikow diagnostycznych jako GitHub Artifact oraz Job
   Summary;
7. zawsze nieblokujacy wynik workflow w pierwszej fazie.

Poza zakresem sa eksporty map, testowanie widokow 2D/3D, porownywanie
geometrii Walls z Survex, obsluga wielu wersji Walls oraz automatyczne
uruchamianie na kazdym pull requescie.

## Architektura

### Sterownik Win32

Maly program konsolowy `walls-driver.exe` bedzie jedynym komponentem
sterujacym GUI. Zostanie zbudowany ze zrodel w repozytorium i nie bedzie
wymagal Python, .NET, AutoHotkey, pywinauto ani aktywnego fokusu klawiatury.

Sterownik przyjmuje:

- sciezke do `Walls32.exe`;
- sciezke do `KATASTER.wpj`;
- katalog raportu;
- limit czasu;
- opcjonalny tryb zachowania wygenerowanych plikow roboczych.

Sterownik:

1. uruchamia `Walls32.exe <project>` w osobnej grupie procesow;
2. odnajduje glowne okno nalezace do uruchomionego procesu;
3. odnajduje kontrolke `SysTreeView32` projektu;
4. zaznacza pierwszy element drzewa, czyli korzen projektu;
5. wysyla polecenie `ID_RECOMPILE` przez Win32 `WM_COMMAND`;
6. monitoruje okna dialogowe, proces i pliki wynikowe;
7. zapisuje raport;
8. zamyka Walls przez `WM_CLOSE`, a po przekroczeniu okresu ochronnego konczy
   pozostale procesy potomne.

Bezposrednie komunikaty Win32 sa preferowane nad `F5`, poniewaz nie zaleza od
fokusu, ukladu klawiatury ani widocznosci pulpitu. Identyfikator polecenia jest
bezpieczny tylko przy przypietej wersji Walls; zmiana wersji wymaga ponownej
weryfikacji identyfikatorow i fixture'ow integracyjnych.

### Uruchomienie lokalne

Lokalnie ten sam `walls-driver.exe` dziala wewnatrz istniejacego prefixu Wine.
Codex lub uzytkownik uruchamia test z terminala i odczytuje raport JSON. Nie
jest wymagane sterowanie oknem przez Computer Use.

Sterownik nie uznaje zastanych plikow za wynik biezacego testu. Rejestruje
czas startu, wymusza `Recompile item` i akceptuje tylko niepuste artefakty o
czasie modyfikacji pozniejszym niz start rekompilacji.

### GitHub Actions

Powstanie osobny workflow Windows z wyzwalaczami:

- `workflow_dispatch`;
- harmonogram `17 2 * * *`.

Workflow:

1. pobiera kod z zaufanej galezi;
2. pobiera oficjalny asset
   `WallsInstaller-2.3.0-beta.1.2025-09-13.msi`;
3. weryfikuje SHA-256
   `11445a522760ef98876c3d025e90b734c2073d8a033717c7313a8da130168ce0`;
4. instaluje MSI przez `msiexec /i <asset> /qn /norestart`;
5. buduje sterownik narzedziami MSVC dostepnymi na runnerze;
6. uruchamia test z limitem czasu;
7. zawsze publikuje raport, logi i manifest plikow jako artifact;
8. zapisuje czytelne podsumowanie i adnotacje GitHub;
9. konczy job powodzeniem niezaleznie od klasy wyniku diagnostycznego.

Sterownik zachowuje znaczenie kodow wyjscia. Workflow stosuje
`continue-on-error` tylko na kroku uruchomienia i na podstawie raportu tworzy
podsumowanie. Dzieki temu lokalne wywolanie moze rozroznic problem danych od
problemu infrastruktury, a workflow pozostaje nieblokujacy.

Workflow nie jest uruchamiany automatycznie dla kodu z pull requestow. Chroni
to self-hosted fallback i instalator GUI przed wykonywaniem niezaufanych zmian.

## Przeplyw danych

```text
KATASTER.wpj + pliki SRV
        |
        v
walls-driver.exe -> Walls32.exe -> pelna rekompilacja korzenia
        |                 |
        |                 +-> dialogi i KATASTER.LOG
        |                 +-> KATASTER.NTA/NTN/NTP/NTS/NTV
        v
walls-report.json + walls-dialogs.jsonl + walls-artifacts.txt
        |
        +-> terminal lokalny
        +-> GitHub Job Summary i artifact
```

Raport JSON zawiera co najmniej:

- wersje schematu raportu;
- klase wyniku;
- wersje Walls i systemu;
- sciezke projektu;
- czasy startu, kompilacji i zakonczenia;
- status kazdego etapu;
- tytuly i tresc przechwyconych dialogow;
- liste wymaganych artefaktow z rozmiarem, czasem modyfikacji i SHA-256;
- sciezke do logu Walls;
- powod klasyfikacji i kod wyjscia sterownika.

## Klasy wynikow

| Klasa | Kod sterownika | Znaczenie |
|---|---:|---|
| `PASS` | 0 | Kompilacja zakonczyla sie, wymagane artefakty sa swieze i brak niepustego logu problemow. |
| `WALLS_WARNING` | 10 | Kompilacja utworzyla komplet swiezych artefaktow, ale Walls utworzyl niepusty `.LOG` lub pokazal niekrytyczny dialog. |
| `WALLS_ERROR` | 20 | Walls raportuje blad krytyczny albo po zakonczeniu kompilacji brakuje wymaganego artefaktu. |
| `INFRA_ERROR` | 30 | Nie mozna zainstalowac lub uruchomic Walls, odnalezc okna/kontrolki, albo test przekroczyl limit czasu. |

Wymagany komplet sukcesu to niepuste, swieze pliki `KATASTER.NTA`,
`KATASTER.NTN`, `KATASTER.NTP`, `KATASTER.NTS` i `KATASTER.NTV`.

## Dialogi i bledy

Sterownik enumeruje okna dialogowe `#32770` nalezace do procesu Walls. Dla
kazdego zapisuje tytul, tekst kontrolek i czas pojawienia sie. Znane dialogi
koncowe sa zamykane programowo dopiero po zapisaniu tresci.

Zasady klasyfikacji:

- niepusty `.LOG` przy komplecie wynikow daje `WALLS_WARNING`;
- dialog bledu krytycznego lub brak kompletu wynikow daje `WALLS_ERROR`;
- brak mozliwosci rozpoznania dialogu nie jest zgadywany jako blad danych;
  daje `INFRA_ERROR`;
- timeout zawsze daje `INFRA_ERROR` i wymusza sprzatanie procesow;
- zastane artefakty nigdy nie moga podniesc wyniku do `PASS`;
- raport i dostepne logi sa zapisywane nawet po awarii.

## Strategia testow

### Testy jednostkowe

Logika klasyfikacji, sprawdzanie swiezosci artefaktow, serializacja raportu i
mapowanie kodow wyjscia beda testowane bez uruchamiania Walls.

### Fixture'y integracyjne Walls

Repozytorium bedzie zawieralo trzy minimalne projekty:

1. poprawny projekt generujacy komplet artefaktow i `PASS`;
2. projekt z kontrolowanym niekrytycznym problemem generujacy
   `WALLS_WARNING`;
3. projekt z bledem skladni generujacy `WALLS_ERROR`.

Fixture'y sa uruchamiane przed pelnym `KATASTER.wpj`. Chroni to przed
sytuacja, w ktorej sam sterownik przestal dzialac, a wynik rzeczywistego
projektu zostal blednie zinterpretowany.

### Proof of concept runnera

Pierwszy workflow ma osobno raportowac:

1. czy `Walls32.exe` uruchomil sie;
2. czy sterownik odnalazl glowne okno;
3. czy odnalazl drzewo projektu;
4. czy fixture `PASS` utworzyl swieze artefakty;
5. czy fixture'y negatywne otrzymaly oczekiwane klasy;
6. jaki wynik otrzymal pelny `KATASTER.wpj`.

Jesli `windows-latest` nie udostepni okien Win32, nie upraszczamy testu do
klikania po wspolrzednych. Workflow pozostawia `INFRA_ERROR`, a jego runner
zostaje zmieniony na oznaczony interaktywny self-hosted Windows. Sterownik,
fixture'y i format raportu pozostaja bez zmian.

## Kryteria akceptacji

Prototyp jest uznany za wykonalny, gdy:

1. ten sam sterownik uruchamia fixture `PASS` pod lokalnym Wine i na wybranym
   runnerze Windows;
2. kazda rekompilacja tworzy nowy komplet wymaganych plikow;
3. fixture ostrzegawczy daje `WALLS_WARNING`;
4. fixture bledny daje `WALLS_ERROR`;
5. brak Walls i kontrolowany timeout daja `INFRA_ERROR`;
6. wszystkie wyniki tworza poprawny raport i artifact diagnostyczny;
7. workflow reczny i nocny pozostaje zielony, ale wynik inny niz `PASS` jest
   widoczny w Job Summary;
8. test nie modyfikuje sledzonych plikow projektu.

## Dalsze decyzje po prototypie

Po zebraniu wynikow z co najmniej siedmiu nocnych uruchomien nalezy osobno
zdecydowac, czy:

- dodac wyzwalanie na pull requestach;
- zmienic `WALLS_ERROR` w wymagany gate;
- utrzymywac self-hosted runner;
- rozszerzyc test o porownanie statystyk lub geometrii z Survex.

Zadna z tych zmian nie nalezy do pierwszej implementacji.
