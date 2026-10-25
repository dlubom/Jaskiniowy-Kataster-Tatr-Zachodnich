# System Jaskiń Pawlikowskiego - paczka źródłowa 01

- **Status materiału:** częściowy
- **Pochodzenie danych:** Filip Filar; SJP.zip z wiadomości 2017-04-04, POW ORM.SRV z wiadomości 2020-06-17; SJP_P.zip jest opakowaniem pliku SRV
- **Autorzy pomiarów:** F. Filar, M. Parczewski; B. Chlipała (Obłazkowa i powierzchnia); K. Zaczyński, M. Rajczak (wsparcie Mylnej wg PIG)
- **Daty pomiarów:** Mylna: 2009-03/2009-06; Obłazkowa: 2013-11-30, 2013-12-01; Raptawicka: 2013-12-22, 2014-01-04, 2014-01-18, 2014-01-19; połączenia: 2015-06; powierzchnia: nieznane; brak dat poszczególnych odczytów
- **Data pozyskania:** 2017-04-04 (SJP.zip); 2020-06-17 (POW ORM.SRV)
- **Dodał do _RAW:** nieznane
- **Licencja źródłowa:** nieznane
- **Kompletność:** 13 opracowanych plików SRV systemu i 66 odczytów powierzchniowych Obłazkowa–Raptawicka; brak powierzchni Mylna–Obłazkowa i pierwotnych odczytów już uśrednionych pomiarów

## Zawartość

- `SJP.zip` — oryginalne archiwum pomiarów jaskiń
- `SJP/` — projekt Walls i 13 plików SRV; rozpakowane teksty mają końce linii LF
- `SJP_P.zip` — archiwum zawierające oryginalny `POW ORM.SRV`
- `SJP_P/` — rozpakowany `POW ORM.SRV` z końcami linii LF

## Źródła i datowanie

Archiwum `SJP.zip` i plik w `SJP_P.zip` są bajtowo zgodne z załącznikami
Filara z podanych wyżej wiadomości. Rozpakowane teksty mają LF, archiwa
zachowują oryginalne CRLF. Materiałów źródłowych nie zmieniono.

Kampanię Mylnej (marzec–czerwiec 2009) opisuje Filar w „Jaskiniach”
3(56)/2009, s.22–23. Daty sesji Obłazkowej i Raptawickiej pochodzą z jego
tabeli przesłanej 20.07.2015. Nie znamy przypisania sesji do wektorów;
historyczne `#date` głównych kampanii pozostają przybliżeniami.
Dla Mylnej PIG podaje topofil Marbacha i Leica DistoX; dla kampanii
2013–2014 autor podaje DistoX i palmtop, bez potwierdzenia modelu X2.

PIG datuje pomiary obu połączeń na czerwiec 2015 (F. Filar, DistoX2),
a zestawienie planu na 15.06.2015. Daty pierwszych przejść
(Obłazkowa: 15.06.2014; Raptawicka: 7.02.2015) nie są datami pomiarów.
`OBL_MYL.SRV` i `RAPT_MYL.SRV` zachowują 13 źródłowych rekordów
(`OBLAZK.SRV:91–98`, `RAPTAW.SRV:147–151`) oraz miesięczną datę, bez `#date`.
Datowanie Raptawickiej `1.48–1.150–1.151` pozostaje nieustalone.
Odcinek Mylnej `638–639` pozostaje wyłączony jak w źródle; przyczyna nieznana.

## Powierzchnia, dowiązanie i deklinacja

`POW_ORM.SRV` przywraca wszystkie 66 odczytów (po trzy w obie strony)
i historyczne dowiązania `p1.0 = Oblazkowa:0.0`, `p1.11 = Raptawicka:1.0`,
obecne przed usunięciem aktywnego pliku w `5021fd9`. Lokalnego źródłowego
`#fix` nie przeniesiono. Jedynym zewnętrznym fixem systemu jest Raptawicka
z GPS Katastra; pozostałe otwory są wynikami tej samej sieci.

Data pomiaru powierzchniowego nie jest potwierdzona. Czerwiec 2015 jest
**założeniem obliczeniowym**, opartym na wzmiance PIG o dowiązaniu otworów,
a nie przypisaną datą tego pliku. Dlatego `SURVEY_DATE` pozostaje nieznane,
bez `#date` i bez deklarowania niepotwierdzonego modelu instrumentu.

Dla połączeń i powierzchni przyjęto `DECL=4.83`: średnią 30 dziennych
wartości IGRF14 z czerwca 2015, z jednakową wagą dni. Survex 1.4.24,
`.REF` projektu (WGS84 / UTM 34N: E=420990,593, N=5444258,858, H=1800 m),
średnia +4,827861°, zakres +4,822168°–+4,833555°, zaokrąglenie do 0,01°.
Różnica azymutów wektora kontrolnego dla dziennej daty i `DECL=0` usuwa
zbieżność siatki; kompilator stosuje ją osobno.

Nie uśredniano odczytów powierzchniowych w pliku. Survex 1.4.24 uśrednia
kolejne trójki tego samego kierunku; kierunki przeciwne pozostają osobno
([`netbits.c:341–365`](https://github.com/ojwb/survex/blob/878202413cac5cbf41b88ee82c0cab72b97725ce/src/netbits.c#L341-L365)).
`#segment P` oznacza powierzchnię w Survex i grupę w Walls.
Niezależne rozwiązania powierzchnią i podziemiami różnią się przy Obłazkowej
o około 4,20 m (4,13 m poziomo, 0,77 m pionowo). Wyrównanie rozdziela tę
rozbieżność; dokładność bezwzględna i pionowy układ odniesienia są nieznane.
Brakującego pomiaru powierzchniowego Mylna–Obłazkowa autor nie odnalazł w 2020 r.

Dla tego systemu referencją współrzędnych Best w GPS Katastrze i eksportów
JKTZ jest Survex 1.4.24. Natywny Walls daje różnice do około 0,70 m,
wynikające z innych wag i obsługi powtórzeń. Kontrolna emulacja modelu
Walls w Survex odtworzyła jego wynik z maksymalną różnicą 3D poniżej 8 mm;
był to test diagnostyczny, bez przyjmowania tych wag w danych produkcyjnych.

## Stacje otworów

Źródłowy `SJP/Dane/Mylna/CG.SRV:43–50` oznacza osiem stacji flagami.
Nazwy okien potwierdzają komentarze `BOKI_CG.SRV:27–31` i `BCDCHCG.SRV:27–32`
oraz plan PIG. Położenie znaków względem progów nie jest ustalone.

| Stacja w prefiksie `Pawlikowskiego` | Otwór |
| --- | --- |
| `Mylna:0` | Mylna, główny |
| `Mylna:39` | Mylna, północny |
| `Mylna:52` | I Okno Pawlikowskiego |
| `Mylna:53` | II Okno Pawlikowskiego |
| `Mylna:333` | III Okno Pawlikowskiego |
| `Oblazkowa:0.0` | Obłazkowa |
| `Raptawicka:1.0` | Raptawicka, główny |
| `Raptawicka:5.1` | Raptawicka, górny |

## Źródła publiczne

- F. Filar, [„Nowy plan Jaskini Mylnej”](https://nowe.pza.org.pl/jaskinie/kwartalnik/jaskinie__56_2009.pdf), „Jaskinie” 3(56)/2009, s.22–23.
- F. Filar, [„Powtórne pomiary jaskiń udostępnionych turystycznie w TPN”](https://tatry365.pl/powtorne-pomiary-jaskin-udostepnionych-turystycznie-w-tpn/), 1.07.2014.
- F. Filar, [„System Jaskini Mylnej i Obłazkowej”](https://pza.org.pl/wp-content/uploads/2016/06/System-Jaskini-Mylnej-i-Ob%C5%82azkowej-po%C5%82%C4%85czenie-Filip-Filar.pdf), „Jaskinie” 3(76)/2014, s.35; [„System jaskiń Pawlikowskiego”](https://pza.org.pl/wp-content/uploads/2016/06/System-jaski%C5%84-Pawlikowskiego.pdf), „Jaskinie” 2–3(79–80)/2015, s.44–45.
- PIG: [Mylna](https://jaskiniepolski.pgi.gov.pl/Details/Information/1349), [Obłazkowa](https://jaskiniepolski.pgi.gov.pl/Details/Information/1351), [Raptawicka](https://jaskiniepolski.pgi.gov.pl/Details/Information/1387), [system 010935](https://jaskiniepolski.pgi.gov.pl/Details/Information/10935), [plan systemu](https://jaskiniepolski.pgi.gov.pl/Details/RenderImage?id=11826&zoom=10&ifGet=false).
