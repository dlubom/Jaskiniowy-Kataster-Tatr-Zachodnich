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
Historyczne `#date` pozostają przybliżeniami, bez zmiany obliczeń.

W relacji o kampanii 2013–2014 Filar podaje zestaw DistoX i palmtop, bez
oznaczenia modelu X2. DistoX2 jest potwierdzony przez PIG dla połączeń
z czerwca 2015 r. Dla głównego pomiaru Mylnej PIG podaje topofil Marbacha
i Leica DistoX, bez przypisania instrumentu do odcinków.

W dostarczonym `Dane/Mylna/CPBUL.SRV` odcinek `638–639` jest komentarzem.
Aktywny plik przywraca to wyłączenie; nie znamy jego terenowego powodu.
Autor w 2020 r. nie odnalazł pomiaru powierzchniowego Mylna–Obłazkowa.

## Źródła datowania i instrumentów

- F. Filar, [„Nowy plan Jaskini Mylnej”](https://nowe.pza.org.pl/jaskinie/kwartalnik/jaskinie__56_2009.pdf), „Jaskinie” 3(56)/2009, s.22–23 — okres kampanii; dzienne daty odczytów nieustalone.
- F. Filar, [„Powtórne pomiary jaskiń udostępnionych turystycznie w TPN”](https://tatry365.pl/powtorne-pomiary-jaskin-udostepnionych-turystycznie-w-tpn/), 1.07.2014 — kampania listopad 2013–marzec 2014, DistoX i palmtop.
- F. Filar, [„System Jaskini Mylnej i Obłazkowej”](https://pza.org.pl/wp-content/uploads/2016/06/System-Jaskini-Mylnej-i-Ob%C5%82azkowej-po%C5%82%C4%85czenie-Filip-Filar.pdf), „Jaskinie” 3(76)/2014, s.35 — przejście 15.06.2014; sprzeczny rok 2015 w zbiorczej karcie PIG nie jest podstawą datowania przejścia.
- F. Filar, [„System jaskiń Pawlikowskiego”](https://pza.org.pl/wp-content/uploads/2016/06/System-jaski%C5%84-Pawlikowskiego.pdf), „Jaskinie” 2–3(79–80)/2015, s.44–45 — przejście 7.02.2015.
- PIG, historia dokumentacji: [Mylna](https://jaskiniepolski.pgi.gov.pl/Details/Information/1349), [Obłazkowa](https://jaskiniepolski.pgi.gov.pl/Details/Information/1351), [Raptawicka](https://jaskiniepolski.pgi.gov.pl/Details/Information/1387), [system 010935](https://jaskiniepolski.pgi.gov.pl/Details/Information/10935).
