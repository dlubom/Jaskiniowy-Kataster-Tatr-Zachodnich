# J01 — mapowanie aktywnych plików SRV

[**MAPPING.csv**](MAPPING.csv) obejmuje **208 źródeł i 212 wierszy docelowych**
(207 `underground`, 5 `surface`). Statusy wierszy to 198 `confirmed`,
13 `needs_decision` i 1 `missing_gps`. Czternaście wierszy obejmuje
**11 odrębnych rozstrzygnięć** z tabeli poniżej. Audyt J01 jest domknięty.
Otwarte pozycje blokują użycie mapowania w J04.

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

## Pokrycie i podstawy przypisań

- Inwentarz to śledzone pliki spełniające `is_active_srv_path`. 204 mają
  wpis w [KATASTER.wpj](../../../KATASTER.wpj), w tym trzy wpisy o statusie
  odłączenia 10 (`BK-W`, `CZ_B_DAV`, `LITWOR`). Cztery pliki poza WPJ to
  `CZ_B_S`, `DNZ_ROB`, `DPZ_ROB` i `DZX_ROB`. Ich treści pomiarowe są
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
  źródłowym. `[]` oznacza brak potwierdzonej pary w danym wyniku.
  Referencje zachowują pozycje i tryb dowiązania otworów.
- `confirmed` oznacza przypisanie oparte na wskazanych źródłach.
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
| Ptasia Studnia, 14 SRV → `C-1049` | Oryginalny projekt Walls w `_RAW/01/Ptasia calosc popr/`, księga `RMUL`, `MTZ-0015` → `C-0167` i `MTW-0023` → `C-0273`. `a22` i `A7` mają wyłącznie wpisy punktowe w OTWORY, bez czynnej nogi w SRV z inwentarza. Historyczne `OTW_POW.SRV` zawierało te stacje i zostało usunięte w `5021fd9`. |
| Wysoka–Za Siedmiu Progami–Pośrednia, 7 SRV → `C-1053` | Księga `WYS-7PR`, `W7-0=KSW-0189` i `C-0665` z `system_cave_id: C-1053`. `C-0412` oraz `C-0499` należą do tego systemu. Otwarte przypisania poszczególnych otworów opisano w J01-07–10. |
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

### Bloki do rozstrzygnięcia

Proponowane nazwy plików są też osobnymi `SURVEY_ID`. Tabela wskazuje
kontekst obowiązujący w wejściowym SRV, który należy zachować przy samym
wydzieleniu. Rozstrzygnięcie źródłowe może zmienić wskazaną granicę.

| Źródło i planowany cel | Blok i kontekst |
| --- | --- |
| `PSIA_1987.SRV → PSIA_POW.SRV` (J01-04) | Linia 95, `p87_0–p87_01`, wraz z opisem linii 94. `#prefix Psia`, `meters order=AVD`, `A=D V=D`, `#date 1987-08-17` (Kardaś i Paterek), bez dyrektywy segmentu. `SOURCE_REF "_RAW/01"`. `Psia:p87_0=KSW-0002` występuje także w pozostałej części. Od linii 96 zaczyna się sekcja A3b źródła, z osobną serią podziemną. |
| `KOPRSTUD.SRV → KOPR_POW.SRV` (J01-05) | Linie 45–55. Dziewięć nóg od `ks0` do `ks9` (część wpisana wstecz), LRUD i zerowe `ks9–Swistacza:24`. Pozostałe 17 pomiarów to linie 28–44. `#prefix KoprowaStudnia`, `#UNITS D=M A=D V=D Order=DAV`, obecnie `#DATE 2011-09-09` i brak dyrektywy segmentu. `SOURCE_REF "_RAW/01"` o statusie niedostępny. Końce to `KoprowaStudnia:ks0=MLW-0020` i `Swistacza:24=MLW-0028`, z efektywnymi ID odpowiednio `C-0508` i `C-0657`. |
| `MSW1.SRV → MSW1_POW.SRV` (J01-06) | Kandydat obejmuje 4 nogi w liniach 43–47, `0–B–11–12–13`. Linie 30–41 zawierają 10 pozostałych nóg. W całym wejściu `#prefix MnichStudniaWyz`, `meters order=DAV`, `A=D V=D`, `#DATE 2002-02-03`, brak dyrektywy segmentu. Zachować odniesienia do `_RAW/01` (nowszy CSP), `_RAW/02` (wcześniejszy XLS) i `_RAW/03` (PDF). Potwierdzona para `MnichStudniaWyz:0=MLW-0009` występuje po obu stronach przewidywanej granicy. |

`11A.SRV` Ptasiej Studni ma 15 pomiarów w liniach 25–39 oraz notę przy
`n13` w linii 40. Kontekst to `#prefix PtasiaStudnia`,
`meters order=DAV`, `A=D V=D`, `#DATE 2004-07-01`, bez dyrektywy
segmentu, `SOURCE_REF "_RAW/01"` i `PtasiaStudnia:a14=MTW-0023`.
W CSV wskazano tę samą ścieżkę i robocze `underground` ze statusem
`needs_decision`. Granicę i ewentualny cel wydzielenia wyznaczy J01-11.

Kontrola historii objęła usunięte w `5021fd9` `POW_POM1.SRV`,
`MIET_PW.SRV`, `LITW_TER.SRV` i `OTW_POW.SRV`. Żaden nie należy
do inwentarza. `MWYZN_OT.SRV:27` opisuje usunięty strzał `gps→ot_0`.
Archiwalna tabela powierzchniowa z Rzędów Tomanowych jest materiałem
`_RAW`; trzy robocze transkrypcje zawierają wyłącznie komentowane pomiary
podziemne, a numeracja jej otworów pozostaje hipotezą.

## Otwarte rozstrzygnięcia

| Sprawa | Źródła i decyzja potrzebna przed użyciem |
| --- | --- |
| J01-01 · `DNZ_ROB` | `SRV:22–33`, `_RAW/02/README.md` i DOC, kandydat `T.F-10.18 → C-0216` (`KSW-0063`). Opis kierunku wejścia przeczy planowi i DAV. Ustalić tożsamość tabeli i otworu, bez rozstrzygania na podstawie wspólnych współrzędnych z `KSW-0103`. |
| J01-02 · `DPZ_ROB` | `SRV:22–31`, `_RAW/02/README.md` i DOC, kandydat `T.F-10.19 → C-0335` (`KSW-0103`). Plan i opis wspierają hipotezę; brak przypisania numeru otworu z tabeli powierzchniowej do stacji `0`. Potwierdzić tożsamość źródłową. |
| J01-03 · `DZX_ROB` | `SRV:20–31`, `_RAW/01/README.md` i DOC. Robocza nazwa i hipoteza „Otwór 3” nie pozwalają wskazać kanonicznego rekordu. Ustalić tożsamość, a jeśli potrzebny jest nowy rekord, nadać go w GPS. |
| J01-04 · Psia | Skan `_RAW/01/source/Pomiary od Izy Luty/Psia pomiary x.jpg` wydziela `0–01` jako A3a, z dopiskiem „ciąg nad otworem”. Plan autora pokazuje `01`, lecz bez oznaczenia granicy jaskini. Opis PIG wspomina też wstępny korytarzyk wznoszący się ponad głównym. Potwierdzić z materiału oznaczającego granicę lub z autorem, czy `0–01` jest na zewnątrz. [PIG 1652](https://jaskiniepolski.pgi.gov.pl/Details/Information/1652) |
| J01-05 · Koprowa–Świstacza | Linia 45 SRV jest hipotezą. Autorzy potwierdzają pomiar między otworami w sesji 2012-12-01. Rysunek s. 31 pokazuje rozstaw otworów około 32 m w osi planu, a cały blok SRV ma 26,94 m długości po nogach i stosuje datę 2011-09-09. Rysunek nie podaje stacji pośrednich domiaru. Potwierdzić, które odczyty należą do tego ciągu oraz datę, zanim zostanie wydzielony. [E. Soja i J. Szczygieł, Jaskinie 1(70), s. 31–32](https://pza.org.pl/wp-content/uploads/2016/06/Koprowa-Studnia-i-Jaskinia-%C5%9Awistacza-Tatry-E.-Soja-i-J.-Szczygie%C5%82.pdf#page=2) |
| J01-06 · Mnichowa Studnia Wyżnia | `_RAW/02` XLS, Arkusz1!A3:J3, ma datę 2002-06-12 dla wspólnie zatytułowanej sekcji powierzchni i dolnego otworu. Nowszy CSP odpowiada 14 rekordom SRV. PDF s. 13 potwierdza 2002-02-03 dla pomiarów górnego otworu. Ustalić granicę, datę i stacje ewentualnych pozostałych końców z materiału autora. [#151](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/issues/151) |
| J01-07 · `7PROGOW.SRV` | `W7-200` to dolny otwór Za7 według SRV:32–33 i OTWORY:416–418. Zakomentowany kandydat `KSW-0153` należy do Pośredniej (`C-0499`). Potwierdzić właściwy obiekt z planu lub źródłowej identyfikacji otworu. |
| J01-08 · `III.SRV` | `W7-500` to górny otwór Za7 (SRV:45–46, OTWORY:420–422). `KSW-0123` należy do Za7, ale OTWORY:402–404 oznacza powiązanie jako niepewne. Potwierdzić fizyczny otwór, także w relacji do `W7-200`. |
| J01-09 · `IV.SRV` | `W-300` to górny otwór Wysokiej (SRV:64–65, OTWORY:405–407). Jedyny obiekt przypisany w GPS do Wysokiej `C-0665` to `KSW-0189`, już użyty dla innej stacji `W7-0`. Potrzebny osobny, źródłowo potwierdzony obiekt. |
| J01-10 · `III.SRV` i `PIONY.SRV` | OTWORY:424–434 i `_RAW/01/README.md` rozróżniają dolny `W7-PD` (alias `W7-505/1`), środkowy `W7-P500` i górny `W7-P507`. GPS ma jeden obiekt Pośredniej `KSW-0153 → C-0499`. Ustalić jego otwór oraz brakujące rekordy na podstawie źródeł, bez ponownego użycia ID przy różnych otworach. |
| J01-11 · Ptasia Studnia, `11A.SRV` | Oryginalna nota przy `n13` w `_RAW/01/Ptasia calosc popr/11A.SRV:20` mówi o ścianie przy otworze. Oryginalny projekt (linie 8–10 i 38–40) ujmuje `11A` jako osobną część obok zestawienia `OTW POW`. W kompilacji od `a14` do `n13` jest +58,60 m, a karta Lodowej Litworowej podaje przewyższenie 0 m. Te informacje nie wyznaczają granicy. Potwierdzić z opisanym planem lub źródłem autora, czy i gdzie 15 nóg wychodzi na powierzchnię. [PIG 1475](https://jaskiniepolski.pgi.gov.pl/Details/Information/1475) |

## Kontrole J01

- Zbiór `source_path` jest równy inwentarzowi `is_active_srv_path`.
  Każdy `target_path` jest unikalny, wszystkie hashe odpowiadają bajtom
  wejściowym. Dodatkowe ścieżki dotyczą wyłącznie czterech opisanych
  podziałów. Każdy wiersz `confirmed` ma dowód przypisania.
- Wszystkie użyte GPS ID istnieją, ścieżki systemowe prowadzą do
  istniejących rekordów i są acykliczne. Kontrola par stacji i obiektów
  obejmuje 103 wystąpienia (90 różnych par), w tym powtórzenia zgodnych
  powiązań na granicy plików. Wszystkie potwierdzone stacje odczytano
  w kompilacji, z uwzględnieniem ich wystąpień także w odłączonych SRV.
- Lokalna kompilacja wejścia Survex na wersjonowanym OTWORY zakończyła
  się bez ostrzeżeń, z 18 541 stacjami i 18 651 nogami. Zmiana J01
  dotyczy trzech plików dokumentacji. Powtórny manifest RAW jest identyczny.
