# Historyczne mapowanie migracji CAVE_ID

[MAPPING.csv](MAPPING.csv) rozlicza migrację z 2026-11-12: **207 źródeł →
210 plików** (205 `underground`, 5 `surface`), wszystkie `confirmed`.
To zamknięty zapis migracji; bieżące ID i referencje utrzymujemy w nagłówkach
SRV według [SPEC.md](SPEC.md). CSV pozostaje niezmieniony.

## Jak odczytywać zapis

- `source_path`, `source_sha256` i numery linii w `evidence` dotyczą wejść
  sprzed migracji, dostępnych w rewizji
  [`77963f9`](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/tree/77963f9ea8268556197a16e9b391cb0539b5a4ee).
  Nie są sumami ani numerami linii dzisiejszych plików docelowych.
- `target_path`, `survey_kind`, `cave_id` i `object_refs` opisują wynik
  migracji [`9f0a36d`](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/commit/9f0a36db763d3694d31e42d4f4a065c632b3e478).
  Podział ma kilka wierszy z tym samym źródłem. `object_refs` to tablica JSON
  par `stacja=object_id`; `[]` oznacza brak potwierdzonej pary w danej części.
- `evidence` zachowuje chronologię ustaleń. Dawne wzmianki o brakujących
  obiektach lub oczekiwaniu na wydanie rozliczają końcowe pola i status.
  Referencje `MAPPING.md J01-…` wskazują trwałe oznaczenia decyzji poniżej;
  „sprawdzenie v2.1.1” dotyczy rozliczenia Mnichowej w J01-06.
- Podstawą są paczki `SOURCE_REF`, jawne oznaczenia otworów, dokładne
  `external_refs`/`NR_INWENT` w GPS i decyzje koordynatora. Podobieństwo
  nazwy, prefiksu, katalogu lub geometrii samo nie potwierdza tożsamości.
- Końcowy katalog to [GPS v2.1.2](https://github.com/dlubom/gps-kataster-obiektow-tatr/releases/tag/v2.1.2),
  release ID `442948071`. Rekordy Mnichowej opublikowano w
  [GPS PR #50](https://github.com/dlubom/gps-kataster-obiektow-tatr/pull/50),
  a cztery dodatkowe otwory systemu Wysokiej w
  [GPS PR #53](https://github.com/dlubom/gps-kataster-obiektow-tatr/pull/53).

## Rozstrzygnięcia źródłowe i decyzje koordynatora

### J01-01 — Dziura nad Zawaliskiem

Koordynator 2026-11-12 przypisał tabelę „Szczelina nad Zawaliskiem”
(`DNZ_ROB.SRV`) do `C-0216` / T.F-10.18. Podstawą jest wspólny przekaz
Tabaczyńskiego i porównanie z planem autora opisane w
[paczce źródłowej](../../../Poligony/D_Koscieliska/Wawoz_Krakow/Dziura_nad_Zawaliskiem/_RAW/02/README.md).
Decyzja dotyczy nagłówka wykomentowanej transkrypcji. Data, odniesienie
azymutów, numery otworów domiaru i kotwica wymagają rozstrzygnięcia przed
włączeniem pomiarów do modelu.

### J01-02 — Dziura pod Zawaliskiem

Koordynator 2026-11-12 przypisał tabelę „Dziura w Zawalisku” (`DPZ_ROB.SRV`)
do `C-0335` / T.F-10.19 na podstawie wspólnego przekazu Tabaczyńskiego,
planu i opisu. Decyzja dotyczy nagłówka wykomentowanej transkrypcji;
numeracja domiaru, data i zakotwiczenie pozostają nierozstrzygnięte.
Materiały zachowano w [archiwum jaskini](../../../Poligony/D_Koscieliska/Wawoz_Krakow/Dziura_pod_Zawaliskiem/_RAW/README.md).

### J01-03 — Dziura X

Koordynator 2026-11-12 zdecydował o zachowaniu nierozpoznanej transkrypcji
jako [doc/robocze/DZX_ROB.SRV.txt](../../robocze/DZX_ROB.SRV.txt), poza
inwentarzem aktywnych SRV. Wszystkie pomiary są wykomentowane; brak wpisu
WPJ i fixa. Bajty zachowano, SHA-256:
`6efd875fe136d23bb48a3f9d36ac2aa611b7fd20fbd97c110c0b1cf67540dfb5`.
Literalne `SOURCE_REF "_RAW/01"` w zachowanym nagłówku odnosi się do
[pierwotnego pakietu Dziury X](../../../Poligony/D_Tomanowa/Rzedy_Tomanowe/Dziura_X/_RAW/01/README.md).

### J01-04 — Psia

Rekord A3a `0–01`, 5,20 m, `+38°` w arkuszu `Psia pomiary x.jpg`
opisano jako ciąg nad otworem. Ręczny plan wskazuje punkt `01` na tej
odnodze. Plan, przekrój i opis Kardasia i Luty identyfikują ją jako
korytarzyk nad głównym korytarzem we wstępnej części jaskini. Rekord
pozostał pod ziemią w `PSIA_1987.SRV`.
[PIG 1652, plan 12927 i przekrój 12928](https://jaskiniepolski.pgi.gov.pl/Details/Information/1652).

### J01-05 — Koprowa–Świstacza

Koordynator 2026-11-12 sklasyfikował cały blok `ks0–ks9` (9 nóg) i zerowe
`ks9–Swistacza:24` jako powierzchnię. Dodany w `8a300f95` blok miał komentarz
o prawdopodobnej powierzchni. Publikacja autorów potwierdza pomiar między
otworami, ale nie identyfikuje stacji tego bloku; klasyfikacja jest decyzją
koordynatora. Wydzielenie do `KOPR_POW.SRV` zachowuje odczyty, LRUD,
dowiązanie i skuteczne `#DATE 2011-09-09`. Publikacja podaje 2012-12-01;
rozbieżność dat pozostaje do osobnego wyjaśnienia.
[E. Soja i J. Szczygieł, Jaskinie 1(70), s. 31–32](https://pza.org.pl/wp-content/uploads/2016/06/Koprowa-Studnia-i-Jaskinia-%C5%9Awistacza-Tatry-E.-Soja-i-J.-Szczygie%C5%82.pdf#page=2).

### J01-06 — Mnichowa Studnia Wyżnia; rozliczenie GPS v2.1.1

Koordynator 2026-11-12 przyjął powierzchnię `0–B–11` (2 nogi, 29,70 m),
dolny otwór na `11` i podziemie `11–12–13` (2 nogi, 9,27 m).
Podstawą było porównanie poligonu z autorskim planem Z. Tabaczyńskiego,
„Jaskinie” 3(28)/2002, s. 20, zachowanym w
[_RAW/03](../../../Poligony/D_Malej_Laki/Prawe_zb/Mnich_Studnia_Wyz/_RAW/03/README.md).
Autor narysował domiar z jednym załamaniem i wskazał dolny otwór odkryty
w 1959 r., ale nie podał numerów stacji. Numerowane przypisanie jest
zatem decyzją koordynatora. Podpis „GÓRNY OTWÓR” przy północnym wejściu
na planie PIG 1125 jest sprzeczny z autorską publikacją.

Koordynator przyjął dotychczasowy punkt TPN dla górnego `0=MLW-0054`,
a dolny `11=MLW-0009` jako wynik domiaru. Górny `MLW-0054/m-001`
zachowuje XY/Z dawnego `MLW-0009/m-002`. Historyczny `m-002` pozostał
w dolnym obiekcie jako odrzucony dla tej tożsamości. Dolny `m-003` ma
lon `19.9295483110`, lat `49.2433268258`, H `1680.325745 m`; wektor
UTM 34N od górnego: E `−6.24870609`, N `+9.86874755`, H `−19.567616144078105 m`.
Datum i dokładności pozostają nieznane. Wydanie GPS v2.1.1 potwierdziło
oba rekordy. Zmieniono wyłącznie ID czynnego fixa `0`, bez zmiany jego
współrzędnych i bez fixa `11`. Datowanie `#DATE 2002-02-03` zachowano;
otwarte wyjaśnienie pozostaje w [#151](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/issues/151).

Kontrola TPN z 2026-11-12 po numerze T.E-13.03 i GLOBALID
`{29508047-79F7-4739-BAD5-FC2D7E4CAD8B}` znalazła tylko
[rekord 601](https://gis.tpn.pl/server/rest/services/Topografia___wektor_MIL1/MapServer/6/query?f=pjson&objectIds=601&outFields=*&outSR=4326&returnGeometry=true)
z 2022-05-25, bez oznaczenia otworu i metody pomiaru. `WERYF=1` nie
rozstrzyga tożsamości. Warstwa nie udostępnia wysokości; pochodzenie Z
starego eksportu pozostaje nieustalone. NMT i inspekcja obrazów nie
pozwoliły jednoznacznie rozpoznać obu wejść. NMT nie odwzorowuje wielu
wysokości pionowej ściany, a zmienność wysokości gruntu nie jest błędem
pomiaru. Nie uzasadnia to automatycznej zamiany Best na PIG `m-001`
na podstawie zgodności wysokości 1685 m. Decyzja o kotwicy pozostaje
jawną decyzją koordynatora, bez potwierdzenia terenowego.

### J01-07 — Za Siedmiu Progami, otwór dolny

`7PROGOW.SRV` nazywa `W7-200` dolnym otworem. Karta PIG 1667 wymienia
górny (04) osobno, a legenda Napierały przypisuje podstawowy otwór karty
do dolnego (03). `KSW-0123` nadano z PIG 1667 (`m-001`), więc
`W7-200=KSW-0123` jest referencją tożsamości. Wybrany pomiar TPN `m-002`
pozostaje nieweryfikowany terenowo; oba fixy Za7 są zakomentowane.
[PIG 1667](https://jaskiniepolski.pgi.gov.pl/Details/Information/1667),
[legenda planu PIG 1665](https://jaskiniepolski.pgi.gov.pl/Details/Information/1665).

### J01-08–10 — dodatkowe otwory systemu Wysokiej

| Decyzja | Stacja → obiekt GPS | Podstawa |
| --- | --- | --- |
| J01-08 | `Wysoka7Progow:W7-500=KSW-0264` (`C-0412`) | Jawny opis w `III.SRV` i OTWORY oraz legenda PIG 1665 wskazują górny otwór Za7 (04). Dolny 03 ma odrębną stację i `KSW-0123`. |
| J01-09 | `Wysoka7Progow:W-300=KSW-0265` (`C-0665`) | Jawny opis w `IV.SRV` i OTWORY wskazuje górny otwór Wysokiej. `KSW-0189` pozostaje przy innej stacji, `W7-0`. |
| J01-10 | `Wysoka7Progow:W7-P500=KSW-0266`, `Wysoka7Progow:W7-P507=KSW-0267` (`C-0499`) | Przyjęta rekonstrukcja Pośredniej i opis wnętrza PIG rozróżniają otwory dolny 05 (`W7-PD=W7-505/1`), środkowy 06 i górny 07. Dolny zachowuje `KSW-0153` z karty PIG 1668. |

Zachowano status rekonstrukcji Pośredniej bez pierwotnego protokołu:
[PR #146](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/pull/146),
[rekonstrukcja 106507e](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/commit/106507ebab8470241cf113bba610dfcc552d19c9)
(alias `d1253aa`, squash `4b5d15d`),
[PIG 1668](https://jaskiniepolski.pgi.gov.pl/Details/Information/1668).

Cztery obiekty opublikowano w GPS v2.1.2. Pozycje są zależnymi wynikami
`siec_pomiarowa` z sieci JKTZ `77963f9`, z kotwicą `W7-0=KSW-0189/m-003`.
Nie są nowymi pomiarami terenowymi: status pozostaje nieweryfikowany,
dokładności i datum nieznane. Zachowano zastępcze `DECL=0` i rekonstrukcję
Pośredniej. Źródła oraz reprodukcja są w
[archiwum GPS](https://github.com/dlubom/gps-kataster-obiektow-tatr/tree/v2.1.2/data/sources/jktz/wysoka-entrances-2026-11-12).
Obiekty występują w `OBJECT_REF`, bez nowych aktywnych fixów. Obliczenie
pozycji nie ustanawia tożsamości otworu ani nie upoważnia do jego fiksowania.

### J01-11 — Ptasia Studnia, 11A

Koordynator 2026-11-12 sklasyfikował wszystkie 15 nóg `11A.SRV` jako
powierzchnię po kontroli oryginalnych archiwów i przebiegu na planie.
Zachowano plik, `SURVEY_ID 11A`, stacje, odczyty, notę przy `n13`,
`#DATE 2004-07-01`, jednostki i prefiks. Referencja to `PtasiaStudnia:a14=MTW-0023`.
Archiwa Marka Lorczyka i Jacka Szczygła zawierają te same 16 plików bajtowo,
bez szkicu lub objaśnienia `11A`; wzmianka o domiarach między otworami
dotyczy osobnego `OTW POW.SRV`. Klasyfikacja jest decyzją koordynatora,
nie potwierdzeniem autora. `n13` i `n10c` pozostają nierozpoznanymi końcami,
bez nowych referencji i fixów; skrótu `pr` w źródłowej nocie nie rozwinięto.

## Przypisania wieloplikowe i systemy

| Pomiary | Uzasadnienie |
| --- | --- |
| Bańdzioch Kominiarski, 27 SRV → `C-0078` | Księga Bańdziocha w WPJ, udokumentowane ciągi pomiarowe, `BK-CG.SRV` z oboma otworami oraz `KSZ-0112` i `LEJ-0002` w GPS. Dwa SRV z `T.E-07.07` mają również bezpośredni odpowiednik `NR_INWENT`. `BK-W` rozliczono w tej samej księdze ze statusem odłączenia. |
| Jaskinie Pawlikowskiego, 15 podziemnych SRV → `C-0095` | `T.E-08.03` → `C-0403`, `T.E-08.04` → `C-0573`, `T.E-08.05` → `C-0759`. Wszystkie mają `system_cave_id: C-0095`. Źródłowe flagi stacji w `_RAW/01/SJP/Dane/Mylna/CG.SRV:43–50` i numeracja okien z `BOKI_CG.SRV` oraz `BCDCHCG.SRV` zgadzają się z jawnymi `source_ref: JKTZ:…` siedmiu niefiksowanych obiektów GPS. |
| Wielka Śnieżna, 20 SRV → `C-0295` | Księgi Wielkiej Śnieżnej i Wielkiej Litworowej, potwierdzone stacje w `MAIN`, `JASNYA`, `LITSTARE` i odłączonym `LITWOR` oraz `C-0331`, `C-0648`, `C-0858`, `C-0120` w GPS. `C-0812` (Wilcza) należy do tego systemu w GPS. W inwentarzu nie ma przypisanej stacji otworu Wilczej. |
| Ptasia Studnia, 13 podziemnych SRV → `C-1049`, osobne powierzchniowe `11A.SRV` | Oryginalny projekt Walls w `_RAW/01/Ptasia calosc popr/`, księga `RMUL`, `MTZ-0015` → `C-0167` i `MTW-0023` → `C-0273`. `a22` i `A7` mają wyłącznie wpisy punktowe w OTWORY, bez czynnej nogi w SRV z inwentarza. Historyczne `OTW_POW.SRV` zawierało te stacje i zostało usunięte w `5021fd9`. |
| Wysoka–Za Siedmiu Progami–Pośrednia, 7 SRV → `C-1053` | Księga `WYS-7PR`, `W7-0=KSW-0189` i `C-0665` z `system_cave_id: C-1053`. `C-0412` oraz `C-0499` należą do tego systemu. Uzasadnienia przypisań otworów zachowano poniżej jako J01-07–10. |
| Studnia w Kazalnicy i Lodowa Miętusia → `C-1054` | `MTZ-0011` → `C-0130` oraz `MTZ-0022` → `C-0271`. Oba człony wskazują wspólny system w GPS, także przy osobnych księgach WPJ. |
| Ziobrowa → `C-1052` | `KSW-0075` → `C-0251`; podpisana stacja `5.24` w `JZ_S` i OTWORY odpowiada otworowi `KSW-0177` → `C-0623`. GPS grupuje obie jaskinie. Fix `5.24` jest zakomentowany. |
| Zośka–Zagonna Studnia → `C-1055` | `MLZ-0057` → `C-0567` i `MLZ-0055` → `C-0553`. Źródłowa historia `ZOSKA_S` rozróżnia sesje i wyliczone dowiązanie `31G–32G` wewnątrz systemu. |
| Przy Jędrusiowej → `C-1056`; Śnieżna Studnia i Upłazkowa → `C-0581` | Jawne przejścia w katalogu `C-0013 → C-1056` i `C-0617 → C-0581`. Osobny Schron pod Jędrusiową ma `C-0503` z kotwicy `MLZ-0048`. |
| Słowacja | GPS `C-1003` i `C-1004` wskazują w `morphometry_source_ref` dokładne księgi JKTZ `NK` i `OBVYV`. OTWORY wiąże je z `SK-0001` i `SK-0002`. `OVA2` to syfon przyłączony do `A1:40` w linii 26. |

## Ciągi powierzchniowe i zachowany kontekst

Wszystkie pliki powierzchniowe mają segment `P`; podziały zachowują
odczyty, LRUD, dowiązania oraz skuteczne jednostki, daty i prefiksy.
Numery linii poniżej dotyczą wejść migracji.

| Plik wynikowy | Zakres, kontekst i źródła |
| --- | --- |
| `LODMAL_POW.SRV` | Cztery nogi `0–1p–2p–3p–31` z linii 33–36; zastane `#S P`, `#date 2004-09-04`, F. Filar i M. Parczewski. Zachowano `#prefix LodowaMalolacka`, `meters order=DAV`, `A=D V=D`, [_RAW/01](../../../Poligony/D_Malej_Laki/Mnich_Turnie/Lodowa_Malolacka/_RAW/01/README.md). Pod ziemią pozostały 72 pomiary i sześć bloków dat: 2004-09-04, 2004-10-23, 2004-09-04, 2004-09-25, 2004-10-30, 2004-11-06. Arkusze identyfikują dolny `0=MLW-0011 → C-0332 → C-0588` i górny `31=MLW-0024 → C-0588`; oba są w referencjach obu plików. Górny pozostaje wyznaczany z poligonu, bez czynnego fixa. |
| `POW_ORM.SRV` | Istniejący domiar: 11 uśrednionych nóg DAV z 66 odczytów i dwa dowiązania zerowe. Zachowano `#prefix2 Pawlikowskiego`, `#prefix PawlikowskiegoPow`, `meters order=DAV`, `A=D V=D`, `DECL=4.83`. Czerwiec 2015 jest założeniem do deklinacji. Źródło: `../_RAW/01/SJP_P/POW ORM.SRV`. Końce: `Pawlikowskiego:Oblazkowa:0.0=KSZ-0090` (potwierdzone także `source_ref` GPS) i `Pawlikowskiego:Raptawicka:1.0=KSZ-0047`; czynny fix tylko Raptawickiej. |
| `KOPR_POW.SRV` | J01-05: 9 nóg `ks0–ks9`, LRUD i zerowe `ks9–Swistacza:24`; linie 46–55. Pod ziemią pozostało 17 pomiarów. `#prefix KoprowaStudnia`, `D=M A=D V=D Order=DAV`, `#DATE 2011-09-09`, `SOURCE_REF "_RAW/01"` o statusie niedostępny. Końce: `KoprowaStudnia:ks0=MLW-0020` (`C-0508`) i `Swistacza:24=MLW-0028` (`C-0657`). Domiar nie tworzy systemu. |
| `MSW1_POW.SRV` | J01-06: 2 nogi `0–B–11`, linie 43–44; pod ziemią pozostało 12 nóg (linie 30–41 i 46–47). `#prefix MnichStudniaWyz`, `meters order=DAV`, `A=D V=D`, `#DATE 2002-02-03`. Zachowano `_RAW/01` (CSP), `_RAW/02` (XLS), `_RAW/03` (PDF). `0=MLW-0054`, `11=MLW-0009`; czynny fix tylko `0`. |
| `11A.SRV` | J01-11: 15 nóg, linie 25–39, oraz nota przy `n13` w linii 40. `#prefix PtasiaStudnia`, `meters order=DAV`, `A=D V=D`, `#DATE 2004-07-01`, `SOURCE_REF "_RAW/01"`. Ścieżka i `SURVEY_ID` bez zmian. |

Inwentarz stosuje `is_active_srv_path`, także dla odłączonych `BK-W`,
`CZ_B_DAV`, `LITWOR` i wykomentowanych `CZ_B_S`, `DNZ_ROB`, `DPZ_ROB`,
`LIT99`, `10A`. Historyczne `POW_POM1`, `MIET_PW`, `LITW_TER` i `OTW_POW`
usunięte w `5021fd9` nie należą do inwentarza. `MWYZN_OT` opisuje usunięty
strzał `gps→ot_0`. Samo `#s domiar` nie dowodzi powierzchni — występuje
też pod ziemią w Hardej i Litworowej. Archiwalna tabela powierzchniowa
Rzędów Tomanowych pozostaje w `_RAW`; numeracja jej otworów jest hipotezą.

Migracja zachowała pomiary, geometrię, materiały RAW i bajty OTWORY.
Zmiana klasyfikacji zwiększyła liczbę skompilowanych odcinków powierzchniowych
z 15 do 41: Koprowa +9, Mnichowa +2, Ptasia +15. Wyniki bramek i paczka
są w [PR #163](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/pull/163).
