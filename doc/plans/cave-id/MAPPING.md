# J01 — mapowanie aktywnych plików SRV

[**MAPPING.csv**](MAPPING.csv) rozlicza **207 źródeł i 210 plików docelowych**
(205 `underground`, 5 `surface`). Po wydaniu GPS v2.1.2 i kontroli J02
wszystkie **210 wierszy ma status `confirmed`**; brak `needs_decision`
i `missing_gps`. Zapisane hashe dotyczą wejść migracji, zachowanych w audycie;
nowe nagłówki i trzy podziały celowo zmieniają hashe wynikowych SRV.
Mnichowa ma zatwierdzone `0=MLW-0054`, `11=MLW-0009`; zmieniono wyłącznie
ID istniejącego fixa `0`, bez zmiany jego współrzędnych i bez fixa `11`.
Poniższe sekcje zachowują źródła, decyzje i chronologię rozliczania braków.

## Stan odniesienia

| Wejście | Sprawdzony stan |
| --- | --- |
| JKTZ | [Draft PR #163](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/pull/163), `codex/cave-id-gps`. Zdalny HEAD i czysty lokalny checkout przed rozpoczęciem wskazywały `dfc403a2c08632297a275a5f08087416ff5c1ce0`. Właściwy audyt w czystym, osobnym worktree z odłączonym HEAD tego commita. |
| Baza PR | Lokalny `origin/master`, żywy `refs/heads/master` i baza raportowana przez PR wskazywały `1e994ddc11071a0c7e8a48c16d304edb2a059596`. |
| GPS | [Kanoniczny katalog YAML](https://github.com/dlubom/gps-kataster-obiektow-tatr/tree/2f3fb1c324b7792a0333e8c7e40020f51d6e724a/data), zdalny `main` i commit tagu `v2.0.2` wskazywały `2f3fb1c324b7792a0333e8c7e40020f51d6e724a`. Drzewo `data` ma SHA `f9a26da1c5eab12ce12148046d36dbede80a8d5b`. Wcześniejszy commit przygotowania wydania podany w SPEC ma identyczne drzewo. |
| Wydanie GPS | [v2.0.2](https://github.com/dlubom/gps-kataster-obiektow-tatr/releases/tag/v2.0.2), release ID `438390757`. `best-measurements.csv` służy istniejącej kontroli renderu. SHA-256 artefaktu według GitHub `c69c858f024a368852eb149bc4031db9f9e29d7cbfef121dcd35812c69d41568`. |
| RAW | 658 śledzonych plików pod `_RAW/` (łącznie z README). SHA-256 manifestu `d176f3b61e2038a0b672cac6127e5131c3977d2e60f4f66084bf7617efcbe193`. Każda linia manifestu to SHA-256 bajtów, dwie spacje, ścieżka względem repo i LF. Linie uporządkowano po ścieżce, kodowanie UTF-8. |
| Narzędzia | Survex **1.4.24** (`cavern`, `dump3d`), GDAL **3.13.3**. Walls **v2.3.0-beta.1**, build **2025-09-13**. Suma lokalnego `Walls32.exe` odpowiada sumie przypiętej w [instalatorze CI](../../../.github/actions/install-walls/action.yml). Job `walls-windows` przeszedł w [CI wejściowego HEAD](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/actions/runs/43087872283). |

Katalog GPS obejmuje 1026 jaskiń i systemów oraz 1029 obiektów. Dziesięć
rekordów jaskiń lub systemów nie ma własnego obiektu. Należy do nich
`C-0295`, więc identyfikatory w CSV pochodzą z YAML, przez `cave_id` obiektu
lub dokładny zewnętrzny numer inwentarzowy jaskini oraz jawne
`system_cave_id` do rekordu końcowego.

### Sprawdzenie wejść do J04, 2026-11-12

Sprawdzono HEAD PR `77963f9ea8268556197a16e9b391cb0539b5a4ee` względem
`origin/master` `1e994ddc11071a0c7e8a48c16d304edb2a059596`. Wszystkie 208
hashy SRV oraz manifest 658 śledzonych plików pod `_RAW/` odpowiadają J01.
Katalog `data/` GPS ma to samo drzewo co w v2.0.2.

Z jednego [wydania GPS v2.1.0](https://github.com/dlubom/gps-kataster-obiektow-tatr/releases/tag/v2.1.0)
(ID `442653463`, commit `9cc09122a5403808cdcc662cfc98636c2aaff3ad`) pobrano:

| Artefakt | ID | SHA-256 |
| --- | --- | --- |
| `katalog.gpkg` | `738636801` | `b86be342a0ac98564e717812317bae8b3ae857bb00051235e578d7e2e9fc4e4d` |
| `best-measurements.csv` | `738636804` | `c69c858f024a368852eb149bc4031db9f9e29d7cbfef121dcd35812c69d41568` |

Czytnik J02 zweryfikował 1026 jaskiń, 1029 obiektów i relacje wszystkich
1029 wierszy Best. Render z tego samego CSV odpowiada wersjonowanemu
`OTWORY.SRV`. Stacja `LodowaMalolacka:31` pozostaje bez aktywnego fixu.

Po decyzji J01-03 pozostało 207 źródeł SRV, wszystkie z niezmienionymi
hashami. Przeniesiona transkrypcja Dziury X ma identyczne bajty. W `_RAW/`
zmieniono jedynie odnośniki w dwóch README Dziury X, a wszystkie materiały
źródłowe pozostały bez zmian. Kontrola mapowania czytnikiem J02 nie wykazała
błędów w potwierdzonych tożsamościach i referencjach.

### Rozstrzygnięcia źródłowe i decyzje koordynatora

- **J01-01, Dziura nad Zawaliskiem.** Koordynator 2026-11-12 zatwierdził
  przypisanie tabeli „Szczelina nad Zawaliskiem” w `DNZ_ROB.SRV` do
  `C-0216` (T.F-10.18). Podstawą decyzji jest wspólny przekaz Tabaczyńskiego
  i porównanie z planem autora opisane w `_RAW/02/README.md`. Zatwierdzenie
  dotyczy tożsamości w nagłówku roboczej transkrypcji. Data i odniesienie
  azymutów, numery otworów domiaru oraz zakotwiczenie GPS wymagają
  rozstrzygnięcia przy przyszłym włączaniu tych pomiarów do modelu.
- **J01-02, Dziura pod Zawaliskiem.** Koordynator 2026-11-12 zatwierdził
  przypisanie tabeli „Dziura w Zawalisku” w `DPZ_ROB.SRV` do `C-0335`
  (T.F-10.19), na podstawie wspólnego przekazu Tabaczyńskiego, planu
  i opisu. Zatwierdzenie dotyczy tożsamości w nagłówku roboczej
  transkrypcji. Numeracja domiaru, data i zakotwiczenie GPS wymagają
  rozstrzygnięcia przy przyszłym włączaniu pomiarów do modelu.
- **J01-03, Dziura X.** Koordynator 2026-11-12 zdecydował o zachowaniu
  transkrypcji w dokumentacji roboczej. Plik przeniesiono z
  `Poligony/D_Tomanowa/Rzedy_Tomanowe/Dziura_X/DZX_ROB.SRV` do
  [doc/robocze/DZX_ROB.SRV.txt](../../robocze/DZX_ROB.SRV.txt).
  Wszystkie bajty zachowano, SHA-256 przed i po wynosi
  `6efd875fe136d23bb48a3f9d36ac2aa611b7fd20fbd97c110c0b1cf67540dfb5`.
  Cała treść pomiarowa jest wykomentowana i nie ma wpisu WPJ ani fixa.
  Plik usunięto z inwentarza aktywnych SRV. Tożsamość Dziury X pozostaje
  nieustalona. Literalne `SOURCE_REF "_RAW/01"` w zachowanym nagłówku
  odnosi się do dawnej lokalizacji, czyli
  [pakietu źródłowego Dziury X](../../../Poligony/D_Tomanowa/Rzedy_Tomanowe/Dziura_X/_RAW/01/README.md).
- **J01-04, Psia.** W arkuszu `Psia pomiary x.jpg` autorzy oznaczyli jedyny
  rekord sekcji A3a (`0–01`, 5,20 m, `+38°`) jako ciąg nad otworem. Ręczny
  plan pokazuje punkt `01` na tej odnodze. Opublikowany plan i przekrój
  Kardasia i Luty z pomiarów 1987 r. oznaczają ją jako korytarz nad otworem,
  a opis PIG współautorstwa Kardasia i Luty umieszcza ten korytarzyk we
  wstępnej części jaskini nad głównym korytarzem. Wiersz 95 zostaje w
  `PSIA_1987.SRV`. [PIG 1652, plan 12927 i przekrój 12928](https://jaskiniepolski.pgi.gov.pl/Details/Information/1652)
- **J01-05, Koprowa–Świstacza.** Koordynator 2026-11-12 zatwierdził
  cały blok `ks0–ks9` (9 nóg) i zerowe dowiązanie `ks9–Swistacza:24`
  jako domiar powierzchniowy do wydzielenia do `KOPR_POW.SRV`.
  Blok dodano w `8a300f95` (2013-12-08) z komentarzem o prawdopodobnej
  powierzchni. Publikacja autorów potwierdza pomiar między otworami,
  ale nie identyfikuje stacji tego bloku. Klasyfikacja wynika z decyzji
  koordynatora. J04 zachowuje bajty pomiarów, LRUD, dowiązanie i skuteczne
  `#DATE 2011-09-09`. Publikacja wskazuje sesję 2012-12-01, więc wyjaśnienie
  daty pozostaje do osobnej korekty. [E. Soja i J. Szczygieł, Jaskinie 1(70),
  s. 31–32](https://pza.org.pl/wp-content/uploads/2016/06/Koprowa-Studnia-i-Jaskinia-%C5%9Awistacza-Tatry-E.-Soja-i-J.-Szczygie%C5%82.pdf#page=2)
- **J01-06, Mnichowa Studnia Wyżnia — podział.** Koordynator 2026-11-12
  zatwierdził powierzchnię `0–B–11` (2 nogi, 29,70 m), stację `11` jako
  dolny otwór i podziemie `11–12–13` (2 nogi, 9,27 m). Decyzję poprzedziło
  porównanie poligonu na parametrach Georeferencera z autorskim planem
  Z. Tabaczyńskiego, „Jaskinie” 3(28)/2002, s. 20. Autor narysował domiar
  powierzchniowy z jednym załamaniem i oznaczył dolny otwór jako odkryty
  w 1959 r. Na rysunku brak numerów stacji, dlatego numerowane przypisanie
  zapisano jako decyzję koordynatora. Podpis „GÓRNY OTWÓR” przy północnym
  wejściu w planie PIG 1125 jest sprzeczny z autorską publikacją.
  J04 zachowuje skuteczne `#DATE 2002-02-03` i pomiary. Koordynator
  następnie zatwierdził `MnichStudniaWyz:11=MLW-0009` dla dolnego otworu
  oraz osobny nowy obiekt GPS dla górnego `0`. Kolejna decyzja tego samego
  dnia przypisała obecny punkt TPN górnemu `0`, a dolny `11` nakazała
  wyliczyć z domiaru bez przesunięcia modelu. Przygotowano w GPS górny
  `MLW-0054` z dokładnym dotychczasowym XY/Z i dolny `MLW-0009/m-003`
  z sieci. Oba rekordy opublikowano w v2.1.1 i sprawdzono czytnikiem J02.
  Obecny szablon pozostaje bez zmian; przed użyciem nowego Best fix stacji
  `0` ma wskazywać `MLW-0054`. Kopia z tą zmianą daje identyczne bajty OTWORY.
- **J01-07, Za Siedmiu Progami.** `7PROGOW.SRV:33` nazywa `W7-200`
  dolnym otworem. Karta PIG 1667 wymienia górny otwór (04) osobno w polu
  „Pozostałe otwory”, a legenda Napierały przypisuje otwór podstawowy
  tej karty do dolnego (03). `KSW-0123` nadano z pomiaru `m-001` z PIG
  1667. W mapowaniu `W7-200=KSW-0123` jest referencją tożsamości.
  Wybrany w Best pomiar TPN `m-002` pozostaje nieweryfikowany terenowo.
  Oba fixy Za7 w szablonie są zakomentowane. [PIG 1667](https://jaskiniepolski.pgi.gov.pl/Details/Information/1667),
  [legenda planu PIG 1665](https://jaskiniepolski.pgi.gov.pl/Details/Information/1665),
  [GPS KSW-0123](https://github.com/dlubom/gps-kataster-obiektow-tatr/blob/v2.1.0/data/objects/KSW/KSW-0123.yml)

- **J01-11, Ptasia Studnia.** Koordynator 2026-11-12 przyjął wszystkie
  15 nóg `11A.SRV` jako powierzchnię po obejrzeniu przebiegu na planie
  i kontroli oryginalnych archiwów. Zachować ścieżkę pliku, `SURVEY_ID 11A`,
  stacje, odczyty, notę przy `n13`, `#DATE 2004-07-01`, jednostki i prefiks.
  Referencją jest `PtasiaStudnia:a14=MTW-0023`. Całość ma 230,24 m,
  a `n13` leży 58,61 m ponad początkiem. To pomocnicze dane geometryczne.
  Źródłowe archiwa Marka Lorczyka i Jacka Szczygła zawierają te same
  16 plików Ptasiej bajt w bajt, bez szkicu lub objaśnienia `11A`.
  Wzmianka o domiarach między otworami odpowiada osobnemu `OTW POW.SRV`.
  Klasyfikacja `11A` jest decyzją koordynatora, nie potwierdzeniem autora.
  `n13` i `n10c` pozostają nierozpoznanymi końcami ciągu, bez nowych
  referencji GPS i fixów. Skrótu `pr` w źródłowej nocie nie rozwinięto.

## Pokrycie i podstawy przypisań

- Inwentarz to śledzone pliki spełniające `is_active_srv_path`. 204 mają
  wpis w [KATASTER.wpj](../../../KATASTER.wpj), w tym trzy wpisy o statusie
  odłączenia 10 (`BK-W`, `CZ_B_DAV`, `LITWOR`). Trzy pliki poza WPJ to
  `CZ_B_S`, `DNZ_ROB` i `DPZ_ROB`. Ich treści pomiarowe są
  wykomentowane. W inwentarzu pozostają także bezczynne `LIT99` i `10A`.
  Definicja pomija `Poligony/OTWORY.SRV`, model terenu i archiwum.
- `source_sha256` liczy surowe bajty SRV. Wiersze tego samego źródła mają
  identyczny hash. `source_path` i `target_path` są względne wobec repo.
  Pliki z zaplanowanym podziałem mają osobne wiersze podziemne i powierzchniowe.
  Warunkowe nazwy docelowe ułatwiają przegląd. Oba wiersze mają status
  `needs_decision`, gdy ustalenie granicy wpływa na oba pliki.
- W `evidence` zapisano obecny `CAVE_ID`, wpis WPJ, paczki `SOURCE_REF`
  względem katalogu SRV i konkretne rekordy GPS. `SRV:n` oznacza linię
  wskazanego źródła. `GPS NR_INWENT` oznacza dokładny wpis
  `external_refs` w pierwszym wymienionym YAML. Przy częściach z ID
  `WPJ:…` podstawą jest wspólna księga pomiarowa i kotwica z tej serii
  lub źródło wskazane w wierszu. Podobieństwo nazwy i geometria służą
  do wykrywania kandydatów.
- `object_refs` to tablica JSON z parami `stacja=object_id`. Stacja
  występuje w rekordzie pomiaru danego pliku lub bloku. Źródłem par jest
  [OTWORY.SRV.j2](../../../Poligony/OTWORY.SRV.j2) albo jawne odniesienie
  GPS `source_ref` do stacji JKTZ, potwierdzone flagą i materiałem
  źródłowym, albo jawna, zapisana decyzja koordynatora. `[]` oznacza brak potwierdzonej pary w danym wyniku.
  Referencje zachowują pozycje i tryb dowiązania otworów.
- `confirmed` oznacza przypisanie oparte na wskazanych źródłach lub jawnej,
  zapisanej decyzji koordynatora.
  `needs_decision` pozostawia udokumentowaną decyzję otwartą.
  `missing_gps` wskazuje rozpoznany otwór bez odrębnego rekordu.
  Ustalony identyfikator jaskini może pozostać w niepotwierdzonym wierszu.
  Puste `cave_id` w `underground` oznacza tożsamość do rozstrzygnięcia.
  `surface` ma zawsze puste `cave_id`.

### Przypisania wieloplikowe i otwory

| Pomiary | Uzasadnienie |
| --- | --- |
| Bańdzioch Kominiarski, 27 SRV → `C-0078` | Księga Bańdziocha w WPJ, udokumentowane ciągi pomiarowe, `BK-CG.SRV` z oboma otworami oraz `KSZ-0112` i `LEJ-0002` w GPS. Dwa SRV z `T.E-07.07` mają również bezpośredni odpowiednik `NR_INWENT`. `BK-W` rozliczono w tej samej księdze ze statusem odłączenia. |
| Jaskinie Pawlikowskiego, 15 podziemnych SRV → `C-0095` | `T.E-08.03` → `C-0403`, `T.E-08.04` → `C-0573`, `T.E-08.05` → `C-0759`. Wszystkie mają `system_cave_id: C-0095`. Źródłowe flagi stacji w `_RAW/01/SJP/Dane/Mylna/CG.SRV:43–50` i numeracja okien z `BOKI_CG.SRV` oraz `BCDCHCG.SRV` zgadzają się z jawnymi `source_ref: JKTZ:…` siedmiu niefiksowanych obiektów GPS. |
| Wielka Śnieżna, 20 SRV → `C-0295` | Księgi Wielkiej Śnieżnej i Wielkiej Litworowej, potwierdzone stacje w `MAIN`, `JASNYA`, `LITSTARE` i odłączonym `LITWOR` oraz `C-0331`, `C-0648`, `C-0858`, `C-0120` w GPS. `C-0812` (Wilcza) należy do tego systemu w GPS. W inwentarzu nie ma przypisanej stacji otworu Wilczej. |
| Ptasia Studnia, 13 podziemnych SRV → `C-1049`, osobne powierzchniowe `11A.SRV` | Oryginalny projekt Walls w `_RAW/01/Ptasia calosc popr/`, księga `RMUL`, `MTZ-0015` → `C-0167` i `MTW-0023` → `C-0273`. `a22` i `A7` mają wyłącznie wpisy punktowe w OTWORY, bez czynnej nogi w SRV z inwentarza. Historyczne `OTW_POW.SRV` zawierało te stacje i zostało usunięte w `5021fd9`. |
| Wysoka–Za Siedmiu Progami–Pośrednia, 7 SRV → `C-1053` | Księga `WYS-7PR`, `W7-0=KSW-0189` i `C-0665` z `system_cave_id: C-1053`. `C-0412` oraz `C-0499` należą do tego systemu. Potwierdzone przypisania i brakujące rekordy GPS otworów opisano w J01-07–10. |
| Studnia w Kazalnicy i Lodowa Miętusia → `C-1054` | `MTZ-0011` → `C-0130` oraz `MTZ-0022` → `C-0271`. Oba człony wskazują wspólny system w GPS, także przy osobnych księgach WPJ. |
| Ziobrowa → `C-1052` | `KSW-0075` → `C-0251`; podpisana stacja `5.24` w `JZ_S` i OTWORY odpowiada otworowi `KSW-0177` → `C-0623`. GPS grupuje obie jaskinie. Fix `5.24` jest zakomentowany. |
| Zośka–Zagonna Studnia → `C-1055` | `MLZ-0057` → `C-0567` i `MLZ-0055` → `C-0553`. Źródłowa historia `ZOSKA_S` rozróżnia sesje i wyliczone dowiązanie `31G–32G` wewnątrz systemu. |
| Przy Jędrusiowej → `C-1056`; Śnieżna Studnia i Upłazkowa → `C-0581` | Jawne przejścia w katalogu `C-0013 → C-1056` i `C-0617 → C-0581`. Osobny Schron pod Jędrusiową ma `C-0503` z kotwicy `MLZ-0048`. |
| Słowacja | GPS `C-1003` i `C-1004` wskazują w `morphometry_source_ref` dokładne księgi JKTZ `NK` i `OBVYV`. OTWORY wiąże je z `SK-0001` i `SK-0002`. `OVA2` to syfon przyłączony do `A1:40` w linii 26. |

## Ciągi powierzchniowe i podziały

Przegląd objął dyrektywy i komentarze aktywnych SRV niezależnie od nazwy
pliku, końce dowiązań, sekcje WPJ i wcześniejsze usunięcia domiarów.
Odczyt `dump3d` kompilacji wejściowej z wersjonowanym OTWORY wykazał
15 linii z flagą `SURFACE`, po 4 w LODMAL i 11 w POW_ORM. Dwa zerowe
dowiązania POW_ORM pozostają częścią danych tego pliku. Kandydaci niżej
występują w danych bez flagi `SURFACE`. Sam `#s domiar` oznacza także
pomiary pod ziemią, np. w partiach Hardej i Litworowej.

### LODMAL

[LODMAL.SRV](../../../Poligony/D_Malej_Laki/Mnich_Turnie/Lodowa_Malolacka/LODMAL.SRV#L25)
dzieli się na pozostający `LODMAL.SRV` (72 pomiary podziemne) oraz
`LODMAL_POW.SRV` (4 pomiary). Do powierzchni przechodzi blok linii
31–36 z `0–1p–2p–3p–31` w liniach 33–36. Reszta rekordów z linii 38–115
zostaje pod ziemią. W obu plikach zachować `#prefix LodowaMalolacka`,
`meters order=DAV`, `A=D V=D` oraz [`_RAW/01`](../../../Poligony/D_Malej_Laki/Mnich_Turnie/Lodowa_Malolacka/_RAW/01/README.md).
Powierzchnia ma sesję 2004-09-04 (F. Filar, M. Parczewski według SRV),
`#date 2004-09-04`, cztery zastane `#S P`. Pod ziemią utrzymać sześć
bloków `#date` kolejno 2004-09-04, 2004-10-23, 2004-09-04, 2004-09-25,
2004-10-30 i 2004-11-06. Deklinacja wynika z `#date` w obu plikach.

Arkusze źródłowe identyfikują dolny i górny otwór. Stacja `0` to
`MLW-0011 → C-0332 → C-0588`, stacja `31` to `MLW-0024 → C-0588`.
Obie występują w obu wynikach. `31` pozostaje wyznaczona z poligonu
z wyłączonym fixem. Planowana nazwa pomiaru `SURVEY_ID` dla wydzielenia
to `LODMAL_POW`.

### POW_ORM

[POW_ORM.SRV](../../../Poligony/D_Koscieliska/Kom_Wierch/Rapt_Turnia/Syst_Pawlikowskiego/Powierzchnia/POW_ORM.SRV#L22)
jest już osobnym plikiem powierzchniowym. Docelowa ścieżka i `SURVEY_ID`
pozostają te same. Cały blok 22–45 obejmuje jedną niedatowaną sesję,
11 uśrednionych nóg DAV z 66 odczytów i dwa dowiązania zerowe.
Zachować `#prefix2 Pawlikowskiego`, `#prefix PawlikowskiegoPow`,
`meters order=DAV`, `A=D V=D`, `#segment P`, `DECL=4.83` i
`SOURCE_REF "../_RAW/01"`. Czerwiec 2015 jest założeniem do deklinacji.
Źródłem jest `../_RAW/01/SJP_P/POW ORM.SRV`, a linie 32 i 45 wiążą
`Pawlikowskiego:Oblazkowa:0.0=KSZ-0090` i
`Pawlikowskiego:Raptawicka:1.0=KSZ-0047`. Pierwsze powiązanie potwierdza
wprost `source_ref` w GPS. Aktywny fix dotyczy Raptawickiej.

### Pozostałe zatwierdzone podziały i pliki powierzchniowe

Nazwy plików są też osobnymi `SURVEY_ID`. Podział Koprowej zatwierdzono
w J01-05, a Mnichowej w J01-06. Tabela wskazuje
kontekst obowiązujący w wejściowym SRV, który należy zachować przy samym
wydzieleniu. Granice wynikają z zapisanych decyzji koordynatora.

| Źródło i planowany cel | Blok i kontekst |
| --- | --- |
| `KOPRSTUD.SRV → KOPR_POW.SRV` (J01-05) | Linie 45–55. Dziewięć nóg od `ks0` do `ks9` (część wpisana wstecz), LRUD i zerowe `ks9–Swistacza:24`. Pozostałe 17 pomiarów to linie 28–44. `#prefix KoprowaStudnia`, `#UNITS D=M A=D V=D Order=DAV`, obecnie `#DATE 2011-09-09` i brak dyrektywy segmentu. `SOURCE_REF "_RAW/01"` o statusie niedostępny. Końce to `KoprowaStudnia:ks0=MLW-0020` i `Swistacza:24=MLW-0028`, z efektywnymi ID odpowiednio `C-0508` i `C-0657`. |
| `MSW1.SRV → MSW1_POW.SRV` (J01-06) | Zatwierdzono 2 nogi w liniach 43–44, `0–B–11`. Pozostałe 12 nóg podziemnych obejmuje linie 30–41 i 46–47 (`11–12–13`). Stacja `11` jest dolnym otworem według decyzji koordynatora. W obu wynikach zachować `#prefix MnichStudniaWyz`, `meters order=DAV`, `A=D V=D`, `#DATE 2002-02-03` i odniesienia do `_RAW/01` (CSP), `_RAW/02` (XLS), `_RAW/03` (PDF). Wydanie v2.1.1 potwierdza `0=MLW-0054` i `11=MLW-0009`. Przed użyciem nowego Best zmienić ID istniejącego fixa `0` na `MLW-0054`, zachowując jego XY/Z; nie dodawać aktywnego fixa `11`. |

`11A.SRV` Ptasiej Studni ma 15 pomiarów w liniach 25–39 oraz notę przy
`n13` w linii 40. Kontekst to `#prefix PtasiaStudnia`,
`meters order=DAV`, `A=D V=D`, `#DATE 2004-07-01`, bez dyrektywy
segmentu, `SOURCE_REF "_RAW/01"` i `PtasiaStudnia:a14=MTW-0023`.
W CSV zachowano tę samą ścieżkę i przyjęto `surface` ze statusem
`confirmed`, zgodnie z decyzją koordynatora J01-11.

Kontrola historii objęła usunięte w `5021fd9` `POW_POM1.SRV`,
`MIET_PW.SRV`, `LITW_TER.SRV` i `OTW_POW.SRV`. Żaden nie należy
do inwentarza. `MWYZN_OT.SRV:27` opisuje usunięty strzał `gps→ot_0`.
Archiwalna tabela powierzchniowa z Rzędów Tomanowych jest materiałem
`_RAW`; trzy robocze transkrypcje zawierają wyłącznie komentowane pomiary
podziemne, a numeracja jej otworów pozostaje hipotezą.

## Pozostałe blokady GPS

Mnichowa jest rozliczona w GPS v2.1.1. Przed renderem/CI z nowym Best
trzeba zastosować zatwierdzoną zmianę ID fixa stacji `0` na `MLW-0054`;
nie dodawać drugiego aktywnego fixa `11`. Datowanie pozostaje odrębne
w [#151](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/issues/151).

| Sprawa | Potwierdzone przypisanie i brakujący warunek |
| --- | --- |
| J01-08 · `III.SRV` | `W7-500` to górny otwór Za7 (SRV:45–46, OTWORY:420–422). Legenda PIG 1665 odróżnia go jako 04 od dolnego 03. Jedyny rekord Za7 w GPS, `KSW-0123`, pochodzi z karty otworu dolnego. Potrzebny odrębny, źródłowo potwierdzony rekord GPS dla 04. |
| J01-09 · `IV.SRV` | `W-300` to górny otwór Wysokiej (SRV:64–65, OTWORY:405–407). Jedyny obiekt przypisany w GPS do Wysokiej `C-0665` to `KSW-0189`, już użyty dla innej stacji `W7-0`. Potrzebny osobny, źródłowo potwierdzony obiekt. |
| J01-10 · `III.SRV` i `PIONY.SRV` | Przyjęta w PR #146 rekonstrukcja (`106507e`, alias `d1253aa`, squash `4b5d15d`) już rozróżnia otwory dolny `W7-PD=W7-505/1`, środkowy `W7-P500` i górny `W7-P507`. Opis wnętrza PIG przypisuje im odpowiednio 05/06/07. Zachowano status rekonstrukcji bez protokołu; ponowne zatwierdzenie tych samych stacji nie jest warunkiem migracji. `KSW-0153` pochodzi z karty PIG 1668 dla dolnego 05 i można go użyć dla `W7-PD`. Potrzebne osobne rekordy GPS dla 06 i 07, bez wymogu nowych fixów. [Przyjęta rekonstrukcja](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/commit/106507ebab8470241cf113bba610dfcc552d19c9), [PIG 1668](https://jaskiniepolski.pgi.gov.pl/Details/Information/1668) |

### Rekordy GPS potrzebne przed J04

Identyfikatory nowych obiektów musi nadać katalog GPS. Nie używać
placeholderów ani istniejących ID dolnych otworów dla górnych.

| Nowy obiekt | cave_id | Stacja JKTZ | Podstawa |
| --- | --- | --- | --- |
| Za Siedmiu Progami — otwór górny 04 | `C-0412` | `Wysoka7Progow:W7-500` | Jawny opis w `III.SRV`, legenda planu PIG 1665. Dolny 03 to `W7-200=KSW-0123`. |
| Wysoka — otwór górny | `C-0665` | `Wysoka7Progow:W-300` | Jawny opis w `IV.SRV` i OTWORY. `KSW-0189` pozostaje powiązany z `W7-0`. |
| Pośrednia — otwór środkowy 06 | `C-0499` | `Wysoka7Progow:W7-P500` | Przyjęta rekonstrukcja PR #146 i opis wnętrza PIG. |
| Pośrednia — otwór górny 07 | `C-0499` | `Wysoka7Progow:W7-P507` | Przyjęta rekonstrukcja PR #146 i opis wnętrza PIG. Dolny 05 to `W7-PD=KSW-0153`. |

Sprawdzenie rzeczywistego kontraktu GPS wykazało, że obecnie każdy obiekt
musi mieć co najmniej jeden pomiar z geometrią i politykę Best. Pełne tabele
G04 nie wprowadziły możliwości wydania obiektu bez pomiarów. Wcześniejsze
założenie o samych pustych rekordach było błędne.

Obsługiwana metoda `siec_pomiarowa` pozwala zapisać pozycje wyznaczone
z udokumentowanej sieci. Dla już rozpoznanych otworów można przygotować
wyniki z konkretną rewizją JKTZ, stacją, kotwicą i jej pomiarem GPS,
zachowując status nieweryfikowany oraz nieznane dokładności. Wyliczenie
pozycji nie ustanawia tożsamości otworu ani nie upoważnia do nowego fixa.
Alternatywą jest osobna zmiana kontraktu GPS obsługująca obiekty bez pomiaru.

W przypadku Mnichowej koordynator wybrał dotychczasowy punkt TPN jako
kotwicę górnego `0`, a dolny `11` jako wynik domiaru. Wymagana jest
skoordynowana zmiana ID już czynnego fixa, bez zmiany jego XY/Z.
Pozostałe cztery rekordy nie wymagają aktywowania fixów. Po uzupełnieniu GPS trzeba pobrać nowy,
wspólny snapshot GPKG/Best i odnotować jego wydanie, artefakty oraz sumy.
Wydanie v2.1.0 zachowuje rolę pierwotnego wejścia tego audytu.
Wydanie v2.1.1 uzupełnia Mnichową, ale nie pozostałe cztery otwory.

Sprawdzenie publicznego API TPN 2026-11-12 nie wykazało nowszego wpisu
Mnichowej: zapytania po numerze `T.E-13.03` i GLOBALID
`{29508047-79F7-4739-BAD5-FC2D7E4CAD8B}` zwracają jeden rekord,
`OBJECTID=601`, z datą edycji `2022-05-25T12:02:40Z`. Współrzędne
różnią się od importu o mniej niż 0,1 mm; `WERYF=1`, ale `OTWÓR`,
`WER_LOK` i `UWAGI` pozostają puste. Flaga weryfikacji nie identyfikuje
otworu ani metody pomiaru. [Bieżący rekord TPN](https://gis.tpn.pl/server/rest/services/Topografia___wektor_MIL1/MapServer/6/query?f=pjson&objectIds=601&outFields=*&outSR=4326&returnGeometry=true)

Warstwa otworów nie udostępnia wysokości. Osobna usługa NMT TPN
`nmt_05m_mggp_2019` zwróciła w tym punkcie `1699.619995 m` wysokości
gruntu; stary eksport zawiera `Z=1699.893361 m`. Nie ustalono pochodzenia
kolumny Z starego eksportu. Odczyt NMT nie potwierdza wysokości konkretnego
otworu ani nowego pomiaru terenowego. Nie ma podstaw do automatycznej
zamiany Best na PIG `m-001` tylko dlatego, że jego `1685 m` pasuje do
opisu dolnego wejścia. Wcześniejsza rekomendacja takiego wyboru została
wycofana; w zbadanym wydaniu v2.1.0 Best wskazuje TPN `m-002`. Surowe odpowiedzi,
adresy zapytań i SHA-256 zapisano w dowodach audytu
`.verification/2026-11-12-cave-id-j04/tpn-live/`.

Na zlecenie koordynatora wykonano też analizę NMT pochodzącego z LiDAR TPN
i inspekcję wizualną Geoportalu TATRY/ObliView w Chrome. Nie uzyskano
surowej chmury punktów. Próbkowanie objęło 865 odczytów dla 847 różnych
XY: otoczenie 48 × 48 m, oś otworów, łamaną `0–B–11` i sąsiedztwo stacji.
Przy hipotezie punkt TPN = dolny `11` różnica wysokości gruntu między
otworami wynosi 9,81 m; przy hipotezie punkt TPN = górny `0` — 7,43 m,
wobec 19,57 m z pomiarów. W drugim wariancie przewidywany dolny otwór
wypada przy gwałtownym progu: próbki w kwadracie ±2 m obejmują
1683,70–1701,99 m. To zmienność terenu, nie przedział błędu pomiaru.
Rzeźba wspiera badanie drugiego wariantu, lecz żadnego nie rozstrzyga:
na obrazach nie rozpoznano jednoznacznie obu fizycznych wejść. NMT nie
oddaje wielu wysokości tej samej pionowej ściany; dokładność i pochodzenie
XY/Z pomiaru TPN pozostają nieustalone. Analiza sama nie ustaliła tożsamości;
późniejszą decyzję koordynatora i sposób zachowania geometrii zapisano niżej.
Parametry, surowe odpowiedzi, profile i zrzuty Chrome znajdują się w
`.verification/2026-11-12-cave-id-j04/tpn-lidar/`.

### Decyzja o kotwicy Mnichowej, 2026-11-12

Koordynator przyjął punkt TPN dla górnego otworu `0` i nakazał wyliczyć
dolny `11=MLW-0009` z domiaru, zachowując geometrię. Zmiany przygotowano
w [draft GPS PR #50](https://github.com/dlubom/gps-kataster-obiektow-tatr/pull/50),
commit `c8f8600622ea34a7b16db803599881ca724163c6`, bez merge ani wydania. Przygotowany w GPS
górny `MLW-0054/m-001` zachowuje dokładne XY/Z historycznego
`MLW-0009/m-002` z v2.1.0. Dolny `m-003` ma lon `19.9295483110`,
lat `49.2433268258`, H `1680.325745 m`; wektor UTM 34N od górnego to
E `−6.24870609`, N `+9.86874755`, H `−19.567616144078105 m`.
Datum i dokładności pozostają nieznane. Historyczny `m-002` pozostaje
w dolnym obiekcie jako odrzucony dla tej tożsamości.

Próbne przełączenie wyłącznie ID fixa `0` na `MLW-0054` zachowuje bajtowo
cały render `OTWORY.SRV` (SHA-256
`ad2516accce935caba83cb6d23fd68e75a3eae2affbec55c180adae0a24038bc`).
Izolowany model Mnichowej przed/po jest identyczny; 15/15 stacji zgadza
się z obecnym modelem JKTZ na poziomie zapisu 0,01 m. Dowody, próby
numeryczne i ograniczenia opisuje
`.verification/2026-11-12-cave-id-j04/gps-mnichowa-decision/RAPORT.md`.
Pełne porównanie projektu i Walls nastąpi przy rzeczywistej integracji.
Rzeczywisty preview GPS PR #50 (run `43198026423`, artifact `13933797401`)
przeszedł czytnik J02: 1026 jaskiń, 1030 obiektów i Best. Wszystkie 1028
pozostałych wierszy Best są identyczne. CSV ma SHA-256
`5db01e2f6651d2673dff4efd3919267d00d282edd2fd92dae7230cb16181a189`,
GPKG `9ed1dd63cf88404f9ee96ac7d70b8c66373631af8b1d16cda59a93aadc1d4f18`.
Render z faktycznego CSV i nowego ID jest bajtowo identyczny z aktywnym
OTWORY (87 fixów). CI walidacji i eksportów commita `c8f8600` zakończyło
się sukcesem. Dowody: `.verification/2026-11-12-cave-id-j04/gps-pr50-preview/`.
Powyższe jest zapisem kontroli preview. Stan wydania i mapowania aktualizuje
następna sekcja.

### Sprawdzenie wydania GPS v2.1.1, 2026-11-12

[GPS PR #50](https://github.com/dlubom/gps-kataster-obiektow-tatr/pull/50)
scalono jako `b7e3cf6cd23300ab0589a2cd997981f7d5526823`. Opublikowano
[v2.1.1](https://github.com/dlubom/gps-kataster-obiektow-tatr/releases/tag/v2.1.1),
release ID `442857930`, commit `d34bcb0868f636af2eaa9ddb702bb11a78c193ab`,
annotowany tag `61907a0d2251203a45716349a6766b7147fd0519`.

| Artefakt | ID | SHA-256 |
| --- | --- | --- |
| `best-measurements.csv` | `739239578` | `44f6f6e678b9255fe7ac7920828e64c05e004c91d06213770ac7e6b841685294` |
| `katalog.gpkg` | `739239579` | `46dc1b1777aeb3835c782931a4e49e0561ac6e7d50d428af9d0110c3f1089b62` |

Pliki pobrano z tego jednego wydania i sprawdzono sumy GitHub. Czytnik J02
potwierdził 1026 jaskiń, 1030 obiektów i 1030 Best oraz zgodność relacji.
Wobec v2.1.0 dodano tylko `MLW-0054`, zmieniono `MLW-0009`, a 1028 innych
wierszy Best pozostało identycznych. Wobec zbadanego preview zmieniło się
tylko pole `tpn_globalid` dolnego: poprawiony eksporter pomija odrzucone
pomiary; źródłowe `source_ref` w historii pozostały zachowane.
Geometrie i XYZ odpowiadają preview. Kopia szablonu ze zmianą ID `0` daje
ten sam cały OTWORY (87 fixów, SHA powyżej). Stary szablon z nowym Best
nie przechodzi `--check` i przeniósłby kotwicę na dolny punkt.

Oba wiersze Mnichowej mają teraz `0=MLW-0054`, `11=MLW-0009`, `confirmed`.
Pozostałe 3 wiersze `missing_gps` reprezentują 4 nadal brakujące otwory.
Aktywne SRV, szablon, WPJ i parser pozostały niezmienione; J04 nie rozpoczęto.

API `releases/latest` sprawdzone niezależnie 2026-11-12 11:48 UTC zwraca
**v2.1.1**, mimo noty wydania i trailera `Make-Latest: false` mówiących
o zachowaniu v2.1.0. Nie polegać na tej nocie; przed renderem ponownie
sprawdzić żywy stan i używać jawnego snapshotu.
CI commita wydania: [validate](https://github.com/dlubom/gps-kataster-obiektow-tatr/actions/runs/43209810053)
(977 passed, 2 skipped; osobny Docker smoke zaliczony) i
[release](https://github.com/dlubom/gps-kataster-obiektow-tatr/actions/runs/43209909262)
zakończone sukcesem. Dowody są w trwałym katalogu projektu
`.verification/2026-11-12-cave-id-j04/gps-v2.1.1/`.

### Przygotowane cztery rekordy GPS, 2026-11-12

W [draft GPS PR #53](https://github.com/dlubom/gps-kataster-obiektow-tatr/pull/53)
przygotowano commit `aa4cf0d55870eb01cc7753e0b0749402e3ccf91a` na bazie
`d34bcb0868f636af2eaa9ddb702bb11a78c193ab` (v2.1.1).

| Sprawa | Stacja Wysoka7Progow | Przygotowany obiekt | cave_id |
| --- | --- | --- | --- |
| J01-08 | W7-500 | KSW-0264 | C-0412 |
| J01-09 | W-300 | KSW-0265 | C-0665 |
| J01-10 | W7-P500 | KSW-0266 | C-0499 |
| J01-10 | W7-P507 | KSW-0267 | C-0499 |

Każdy obiekt ma jeden wynik `siec_pomiarowa` z niezmienionej sieci JKTZ
`77963f9`, zakotwiczonej w `W7-0=KSW-0189/m-003`. Wszystkie 1373 stacje
izolowanego systemu są zgodne z całym projektem przy zapisie 0,01 m.
Nie zmieniono kotwicy, pomiarów ani historii GPS. Status pozostaje
nieweryfikowany, dokładności i datum nieznane; zachowano zastępcze DECL=0
oraz status rekonstrukcji Pośredniej. Źródła tożsamości, sumy wejść
oraz reprodukcja są w `data/sources/jktz/wysoka-entrances-2026-11-12/`
PR GPS. Nowe punkty są zależnymi wynikami sieci, bez nowych aktywnych fixów.

**Trzy wiersze nadal mają `missing_gps`: rekordów nie ma we wspólnym
wydanym snapshotcie.** Nie wpisano jeszcze nowych ID do `object_refs`.
Merge, tag i wydanie GPS wymagają osobnego polecenia. Po wydaniu trzeba
sprawdzić jeden snapshot GPKG/Best czytnikiem J02 i dopiero wtedy rozliczyć
statusy. J04, parser, aktywne SRV i szablon pozostają bez przełączenia.
Dowody lokalne: `.verification/2026-11-12-cave-id-j04/wysoka-four-entrances/`
w głównym checkoutcie JKTZ; ograniczenie lokalnej bramki GPS: Docker I/O
przypiętego obrazu PostGIS. CI dokładnego HEAD aa4cf0d5 zakończyło się
sukcesem: walidacja run 43215277534, eksporty run 43215277536.
Rzeczywisty podgląd (artifact 13943042422) przeszedł J02: 1026 caves,
1034 objects/Best, 1952 measurements. Wszystkie 1030 dotychczasowych
wierszy Best są identyczne z v2.1.1. Kopia szablonu z zatwierdzoną zmianą
ID Mnichowej daje bajtowo identyczne OTWORY (87 fixów). To nadal preview,
nie wydanie; latest na koniec kontroli pozostaje v2.1.1.

## Kontrole pierwotnego J01 na 93c739e

- Zbiór `source_path` jest równy inwentarzowi `is_active_srv_path`.
  Każdy `target_path` jest unikalny, wszystkie hashe odpowiadają bajtom
  wejściowym. Pierwotne cztery planowane podziały obejmowały także Psią,
  której klasyfikację rozstrzygnięto wyżej podczas przygotowania J04. Każdy wiersz `confirmed` ma dowód przypisania.
- Wszystkie użyte GPS ID istnieją, ścieżki systemowe prowadzą do
  istniejących rekordów i są acykliczne. Kontrola par stacji i obiektów
  obejmuje 103 wystąpienia (90 różnych par), w tym powtórzenia zgodnych
  powiązań na granicy plików. Wszystkie potwierdzone stacje odczytano
  w kompilacji, z uwzględnieniem ich wystąpień także w odłączonych SRV.
- Lokalna kompilacja wejścia Survex na wersjonowanym OTWORY zakończyła
  się bez ostrzeżeń, z 18 541 stacjami i 18 651 nogami. Zmiana J01
  dotyczy trzech plików dokumentacji. Powtórny manifest RAW jest identyczny.


## Wydanie GPS v2.1.2 i migracja J04, 2026-11-12

[GPS PR #53](https://github.com/dlubom/gps-kataster-obiektow-tatr/pull/53)
scalono jako `a5c6d0ec7811362f7bd6e51a1c55bbc837b49684` po pomyślnym
CI HEAD `21262b53d6e15bbaf0579464d6bfd988c5d9de1d`.
[Wydanie v2.1.2](https://github.com/dlubom/gps-kataster-obiektow-tatr/releases/tag/v2.1.2)
ma ID `442948071`; workflow publikacji `43222142096` zakończył się sukcesem.
Czytnik J02 odczytał jeden wydany snapshot i sprawdził relacje CSV/GPKG:
1026 jaskiń, 1034 obiekty, 1034 Best, 1952 pomiary; integralność i FK bez błędów.

| Artefakt | ID | SHA-256 |
| --- | --- | --- |
| best-measurements.csv | 739491997 | `61874fca2441cc364c3f09d30a56210e863c595fddad417d1bc7e694d72edcf6` |
| katalog.gpkg | 739491994 | `dcc27f90f741cb8e6d27562a27d4252f0c679769035a36a14c497f7eed3eb7a9` |

Wszystkie 1030 wcześniejszych wierszy Best zachowało wartości z v2.1.1.
Cztery nowe referencje KSW-0264–0267 zamykają trzy wiersze mapowania.
Nie wprowadzono dodatkowych kotwic. Szablon ma 83 czynne fixy oraz cztery
zakomentowane wyrażenia; licznik renderera 87 obejmuje również komentarze.
Bajty OTWORY pozostały identyczne, SHA-256
`ad2516accce935caba83cb6d23fd68e75a3eae2affbec55c180adae0a24038bc`.

W J04 wydzielono LODMAL_POW (4 nogi), MSW1_POW (2 nogi) i KOPR_POW
(9 nóg i dowiązanie zerowe). Zachowano wszystkie odczyty, LRUD, daty,
jednostki, prefixy i SOURCE_REF; 11A Ptasiej ma zatwierdzone 15 nóg surface.
Nowy segment P klasyfikuje te bloki zgodnie z decyzjami koordynatora.
CAVE_NAME opisuje jaskinię/system GPS w ASCII; SURVEY_NAME zachowuje opis sekcji.

Kontrola przed/po Survex 1.4.24: 12112 nazwanych stacji ma identyczne
współrzędne przy precyzji eksportu 0,01 m; multizbiór 18554 skompilowanych
odcinków zachowuje końce i pozostałe flagi. Liczba odcinków surface wzrosła
zgodnie z decyzjami z 15 do 41 (Koprowa +9, Mnichowa +2, Ptasia +15).
Dla podziałów porównano odczyty z krotnością i skutecznym kontekstem
dyrektyw; wszystkie pozostałe treści pomiarowe są bajtowo identyczne.
482 archiwalne materiały RAW i zachowana transkrypcja DZX nie zmieniły bajtów.
Sprawdzenie referencji do katalogu i nazw stacji z kompilacji: PASS.

Dowody lokalne: `.verification/2026-11-12-cave-id-j04/j04-implementation/`
w głównym checkoutcie; podsumowanie bramek i natywnego Walls jest w PR #163.
J05 pozostaje osobnym, niewykonanym etapem włączenia walidacji sieciowej.
