# System Jaskiń Pawlikowskiego - paczka źródłowa 01

- **Status materiału:** częściowy
- **Pochodzenie danych:** Filip Filar; SJP.zip z wiadomości 2017-04-04, POW ORM.SRV z wiadomości 2020-06-17; archiwum SJP_P.zip jest opakowaniem pliku SRV; datowanie i instrumenty uzupełniono publikacjami autora oraz PIG
- **Autorzy pomiarów:** F. Filar, M. Parczewski; B. Chlipała (Obłazkowa i pomiary powierzchniowe); K. Zaczyński, M. Rajczak (wsparcie pomiarów Mylnej wg PIG)
- **Daty pomiarów:** 2009-03/2009-06 (kampania Mylnej); 2013-11-30 i 2013-12-01 (Obłazkowa); 2013-12-22, 2014-01-04, 2014-01-18 i 2014-01-19 (Raptawicka); 2015-06 (pomiary połączeń wg PIG); brak przypisania dat do poszczególnych odczytów
- **Data pozyskania:** 2017-04-04 (SJP.zip); 2020-06-17 (POW ORM.SRV)
- **Dodał do _RAW:** nieznane
- **Licencja źródłowa:** nieznane
- **Kompletność:** 13 opracowanych plików SRV systemu i 66 odczytów powierzchniowych Obłazkowa–Raptawicka; brak odcinka powierzchniowego Mylna–Obłazkowa i pierwotnych odczytów dla pomiarów już uśrednionych

## Zawartość

- `SJP.zip` — archiwum ZIP z pomiarami jaskiń
- `SJP/` — rozpakowana zawartość:
- `SJP_P.zip` — archiwum ZIP z pomiarami powierzchniowymi
- `SJP_P/` — rozpakowana zawartość:

## Pochodzenie i ograniczenia

`SJP.zip` jest bajtowo zgodny z załącznikiem Filipa Filara z 4 kwietnia 2017 r.
Plik `POW ORM.SRV` w `SJP_P.zip` jest bajtowo zgodny z jego załącznikiem
z 17 czerwca 2020 r. Rozpakowane kopie tekstowe w tej paczce mają końce
linii LF; archiwa zachowują oryginalne bajty CRLF.

Zakres kampanii pomiarowej Mylnej to marzec–czerwiec 2009 r., według
indeksowanej treści artykułu Filipa Filara „Nowy plan Jaskini Mylnej”,
„Jaskinie” 3(56)/2009, s.22–23. Daty sesji Obłazkowej i Raptawickiej pochodzą
z tabeli autora przesłanej 20 lipca 2015 r.; PIG potwierdza 1.12.2013 dla
Obłazkowej i zakres 22.12.2013–19.01.2014 dla Raptawickiej. Nie znamy
przypisania tych dat do poszczególnych wektorów.

Pierwsze przejście Mylna–Obłazkowa nastąpiło 15.06.2014, a Mylna–Raptawicka
7.02.2015, co potwierdzają relacje Filara. Są to daty przejść. PIG osobno
podaje czerwiec 2015 jako miesiąc pomiarów obu połączeń i dowiązania otworów,
a 15.06.2015 jako datę zestawienia planu i przekroju systemu. Dat przejść
i opracowania planu nie wpisano jako dat pomiarów w `SURVEY_DATE` ani `#date`.
Historyczne `#date` głównych kampanii pozostają przybliżeniami. Pomiary
połączeń z `2015-06` wydzielono do `Oblazkowa/OBL_MYL.SRV` i
`Raptawicka/RAPT_MYL.SRV`, bez fikcyjnej daty dziennej; metoda poniżej.

W relacji o kampanii 2013–2014 Filar podaje zestaw DistoX i palmtop, bez
oznaczenia modelu X2. DistoX2 jest potwierdzony przez PIG dla połączeń
z czerwca 2015 r. Dla głównego pomiaru Mylnej PIG podaje topofil Marbacha
i Leica DistoX, bez przypisania instrumentu do odcinków.

W dostarczonym `Dane/Mylna/CPBUL.SRV` odcinek `638–639` jest komentarzem.
Aktywny plik przywraca to wyłączenie; nie znamy jego terenowego powodu.
Autor w 2020 r. nie odnalazł pomiaru powierzchniowego Mylna–Obłazkowa.

## Datowanie wydzielonych połączeń i deklinacja

PIG, karta systemu 010935, „Historia dokumentacji”, przypisuje pomiary obu
połączeń F. Filarowi w czerwcu 2015 r. Osobno podaje 15.06.2015 jako datę
zestawienia planu i przekroju. Nie jest to potwierdzony dzień pomiaru.
W nowych plikach zachowano `SURVEY_DATE "2015-06"`, bez `#date`, ponieważ
Walls wymaga pełnej daty dziennej i zapisuje ją także w eksportach.
Odpowiednie źródła to `SJP/Dane/OBLAZK.SRV:91–98` (8 rekordów) i
`SJP/Dane/RAPTAW.SRV:147–151` (5 rekordów). Wartości i stacje zachowano
z dotychczasowymi kwalifikacjami dowiązań do Mylnej.

`#units DECL=4.83` jest jawnym założeniem obliczeniowym: średnią arytmetyczną
30 dziennych wartości IGRF14 dla czerwca 2015, wyznaczonych osobno przez
Survex 1.4.24 na pozycji oryginalnej `.REF` projektu: WGS84 / UTM 34N,
E=420990,593 m, N=5444258,858 m, H=1800 m. Średnia wynosi +4,827861°,
zakres +4,822168° do +4,833555°; wynik zaokrąglono do 0,01°.
Każdy dzień ma jednakową wagę, ponieważ nie znamy dni rzeczywistych odczytów.
Nie jest to terenowy pomiar deklinacji. Zbieżność siatki kompilator stosuje
osobno; nie jest dodana do zapisanej wartości `DECL`.

Model i zasady: [Survex 1.4.24, IGRF14](https://github.com/ojwb/survex/blob/878202413cac5cbf41b88ee82c0cab72b97725ce/doc/datafile.rst),
opis `*declination`; [Walls v2.3.0-beta.1, parser dat](https://github.com/wallscavesurvey/walls/blob/v2.3.0-beta.1/Walls32/wall-srv.cpp#L1492),
oraz lokalny manual Walls §4.9. Wyznaczenie kąta polegało na odjęciu
azymutu kontrolnego wektora z `DECL=0` od azymutu tego samego wektora
z dzienną `#date`; różnica usuwa korektę siatki.

Nie zmieniono przybliżeń `#date` głównych kampanii, ponieważ tabela sesji
nie przypisuje dat do konkretnych wektorów. Dwa końcowe odcinki Raptawickiej
`1.48–1.150–1.151` mają nieustalone datowanie; nie objęto ich czerwcem 2015.
103 splaje Obłazkowej pozostały w podstawowym pliku, poza połączeniem.

## Źródła datowania i instrumentów

- F. Filar, [„Nowy plan Jaskini Mylnej”](https://nowe.pza.org.pl/jaskinie/kwartalnik/jaskinie__56_2009.pdf), „Jaskinie” 3(56)/2009, s.22–23 — okres kampanii; dzienne daty odczytów nieustalone.
- F. Filar, [„Powtórne pomiary jaskiń udostępnionych turystycznie w TPN”](https://tatry365.pl/powtorne-pomiary-jaskin-udostepnionych-turystycznie-w-tpn/), 1.07.2014 — kampania listopad 2013–marzec 2014, DistoX i palmtop.
- F. Filar, [„System Jaskini Mylnej i Obłazkowej”](https://pza.org.pl/wp-content/uploads/2016/06/System-Jaskini-Mylnej-i-Ob%C5%82azkowej-po%C5%82%C4%85czenie-Filip-Filar.pdf), „Jaskinie” 3(76)/2014, s.35 — przejście 15.06.2014; sprzeczny rok 2015 w zbiorczej karcie PIG nie jest podstawą datowania przejścia.
- F. Filar, [„System jaskiń Pawlikowskiego”](https://pza.org.pl/wp-content/uploads/2016/06/System-jaski%C5%84-Pawlikowskiego.pdf), „Jaskinie” 2–3(79–80)/2015, s.44–45 — przejście 7.02.2015.
- PIG, historia dokumentacji: [Mylna](https://jaskiniepolski.pgi.gov.pl/Details/Information/1349), [Obłazkowa](https://jaskiniepolski.pgi.gov.pl/Details/Information/1351), [Raptawicka](https://jaskiniepolski.pgi.gov.pl/Details/Information/1387), [system 010935](https://jaskiniepolski.pgi.gov.pl/Details/Information/10935).
