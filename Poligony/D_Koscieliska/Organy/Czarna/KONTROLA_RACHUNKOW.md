# Czarna — kontrola rachunkowa każdego wiersza i ranking odczytów

Wynik odtwarzalny; wartości odczytane ze skanów pozostają oddzielone od obliczeń.

## Metoda i ograniczenia

Zakres: 76 odcinków 0–76 oraz 6–a–b; 78 unikalnych wierszy × 5 pól = 390. Fotografie 123052 i 123533 przedstawiają te same strony. 123630 obejmuje 19–60.

Źródłem odniesienia jest ponowny odczyt fotografii przez czytelnika stron zewnętrznych i czytelnika środka oraz kontrola głównego czytelnika na powiększeniach. Czytelnicy znali wcześniejsze raporty; nie był to test całkowicie zaślepiony. Surowe wyniki obu czytelników zachowano osobno.

Wszystkie 78 wierszy obejrzano i przeliczono; nie oznacza to potwierdzenia wszystkich cyfr. Lista uncertain_fields wyłącza identyczne pola referencji z ocen wszystkich modeli. Pytajnik modelu nie wyłącza jego pierwszej propozycji z oceny. Rozstrzygnięte pola nie są wybrane głosowaniem modeli ani dopasowaniem do geometrii.

Długość zredukowana Lh = D cos(V), Δh = D sin(V), D_aux = hypot(Lh,Δh), V_aux = atan2(Δh,Lh). Kąty w stopniach. A pozostaje poza tym sprawdzeniem; żadna z tych kolumn ani sum wysokości nie potwierdza azymutu.

Kolumny pomocnicze i sumy są rachunkami tego samego autora, nie niezależnym pomiarem. Mogą wspierać odczyt cyfry/znaku, ale mogą też powielać błąd. Nie zastąpiono D/A/V wynikiem odwrotnego rachunku. Nie wykorzystano GNSS ani poligonu Borowca do wyboru cyfr.

Dla pól nierozstrzygniętych obliczenia używają jawnie preferowanej wartości; lista alternatyw i zakresy sum zachowują wpływ niepewności. Próg 0,05 m jest tylko przeglądowym progiem rozbieżności, nie oszacowaniem błędu instrumentu; ścisłe zaokrąglenie do centymetra sprawdzono osobno (0,005 m).

Dopiski wysokości zinterpretowano względem stacji 0; przy 26,66,73,76,a,b przypisanie wynika z położenia zapisu. Suma przy 57 jest nadpisana i niepewna. Suma +20,79 nie ma ustalonego zakresu, więc nie wymuszano jej zgodności.


## Wnioski z krzyżowej kontroli

Sprawdzono 78/78 wierszy. Dla preferowanych odczytów 12 wierszy ma obie kolumny zgodne z zaokrągleniem do centymetra, kolejne 50 mieści się w różnicy 0,05 m, a 16 ma co najmniej jedną większą rozbieżność. Nie oznacza to 16 błędnych D/V: część zapisów pomocniczych w źródle jest niespójna, np. 2→3, 10→11 i 44→45. Przeliczenie nie jest automatyczną korektą obserwacji.

a→b: wszystkie trzy modele podały Δh=−3,05, podczas gdy obie fotografie wskazują −3,25. Różnica marginesów −61,95−(−58,70)=−3,25 i 5,40·sin(−37°)=−3,249801 m potwierdzają ten odczyt. Lh=4,21 to osobna niespójność źródła (cos daje 4,312632), której nie poprawiono w transkrypcji. Wizualna słaba alternatywa V=−32 pozostaje wyłączona z rankingu; rachunek silnie wspiera −37.

Nie każda matematycznie spójna transkrypcja jest poprawna: dla 73→74 Gemini Pro i Opus mają D=Lh=12,00 przy V=0, czyli ich rachunek się zgadza, lecz obie fotografie mają 17,00. Dla 2→3 Gemini mają Δh=−2,97 bliskie sin(V), lecz na fotografii jest −4,97. Ranking ocenia wierność zapisowi, a nie wygładzanie błędów źródła.

D 59→60: skan preferuje 17,60, ale grafia dopuszcza słabsze 12,60; pole wyłączono z rankingu. Dla 17,60 obliczenia Lh=17,077205 i Δh=−4,257825 m są bliskie zapisom 17,07/−4,24. Dla 12,60 otrzymuje się 12,225726/−3,048216 m. Kolumny silnie wspierają 17,60. Samo Lh>12,60 wyklucza 12,60 jako długość zgodną z tą kolumną.

V 71→72: zapisane Δh=−0,35 oraz różnica dopisków 66→73 wspierają −1°. Dla +1° różnica względem Δh wynosi około −0,699 m. Zachowano wizualną niepewność znaku; A 39→40 i A 49→50 nie da się potwierdzić Lh, Δh ani ich sumami.

Przy stacjach 6,11,19,26 suma zapisanej kolumny Δh jest o 0,10 m większa niż margines. Przyrosty 6→11,11→19,19→26 zgadzają się dokładnie. Nie znaleziono cyfry uzasadniającej poprawienie tej różnicy. Również przyrosty 38→45,45→52,52→57 oraz 64→66,66→73,73→76,6→a,a→b zgadzają się dla preferowanych odczytów. Suma przy 57 jest nadpisana; zgodność rachunkowa wspiera jej odczyt +74,23.

Dwie nowe wątpliwości pomocnicze są jawne: Δh27→28 (preferowane 11,63, alternatywa 11,68 w bieżącym SRV) oraz Lh/Δh58→59. Nie zastąpiono komentarzy SRV niepewną preferencją nowego czytelnika. W sumach i rankingu ujawniono także pozostałe miękkie cyfry; łącznie wyłączono 14 pól referencji w 11 wierszach.

Dopisek ΣΔh +20,79 jest czytelny, ale nie ma ustalonego zakresu. Przy założeniu pełnego ciągu suma zapisanych Δh wynosi 16,47 m (16,52 m z niezmienionych komentarzy SRV), a z D,V wynosi 17,454431 m. Żadna z tych wartości nie jest 20,79; to nierozstrzygnięta suma, nie dowód wyboru innego pomiaru. Osobny dopisek +16,42 jest zgodny z ostatnim przyrostem od +35,39, choć całkowite sumowanie kolumny daje resztę. Zakresy wszystkich niepewnych sum są w JSON.

Surowe transkrypcje: Flash 370/376 poprawnych pierwszych pól (373 z alternatywami), Pro 348/376, Opus 337/376 (343 z alternatywami). Pro ma 23 różne wartości oraz brak pięciu pól pary 19→20 z powodu zapisania 18→20. Ranking pozostaje Flash→Pro→Opus także dla samych D/A/V (227/228,216/228,212/228) i samych Lh/Δh (143/148,132/148,125/148).

Pierwotny Codex z 7472374 uzyskał 375/376: błąd Lh20→21=10,23, który wszystkie trzy modele miały poprawnie jako 10,73. To punkt odniesienia po ówczesnej kontroli czytelników, nie uczciwy benchmark pojedynczego wywołania modelu. Pierwotne A39=25 i jego alternatywa 75 pozostają w zamrożonym wejściu; pole jest nierozstrzygnięte wizualnie i nie uczestniczy w punktacji. Nie przyznano nam punktu za późniejszą korektę opartą na modelach.

Nie zmieniono D/A/V, oryginalnych plików _RAW ani trzech surowych transkrypcji modeli. Wynik umacnia część preferencji i ujawnia ograniczenia; nie ustala daty, deklinacji ani fizycznych dowiązań i nie włącza pliku do WPJ.


## Ranking pierwszych odpowiedzi

Jednakowy zestaw rozstrzygniętych pól D/A/V/Lh/Δh; niepewne pola referencji wyłączono. Powtórna fotografia nie zwiększa liczby głosów. Brak pary jest brakiem pięciu pól. Wynik ocenia te transkrypcje, nie ogólną jakość modeli ani poprawność pomiaru terenowego.

| Odczyt | Poprawne / oceniane | D/A/V poprawne | Lh/Δh poprawne | Z alternatywami |
| --- | ---: | ---: | ---: | ---: |
| Codex_initial_7472374 | 375/376 | 228 | 147 | 375 |
| gemini_flash_3.8 | 370/376 | 227 | 143 | 373 |
| gemini_pro | 348/376 | 216 | 132 | 348 |
| claude_opus_5 | 337/376 | 212 | 125 | 343 |

Codex_initial to pierwotny SRV z 7472374, już po ówczesnej kontroli czytelników; nie jest surową odpowiedzią z odtworzonym promptem. Obecny SRV po wykorzystaniu wyników innych modeli nie uczestniczy w rankingu. Nazwy Gemini/Opus są etykietami dostarczonymi przez użytkownika.

## Kontrola 78 wierszy

ε = zapis − wynik trygonometrii. R oznacza oba |ε| ≤ 0,005 m (zaokrąglenie do cm), P oba |ε| ≤ 0,05 m, X co najmniej jedno > 0,05 m. P to wyłącznie próg diagnostyczny, nie dowód poprawności. ? wymienia pola bez rozstrzygnięcia wizualnego. A nie uczestniczy w żadnym z tych testów.

| Odcinek | D / A / V | Lh zapis → oblicz. | Δh zapis → oblicz. | ε Lh / ε Δh | Kontrola / niepewne |
| --- | --- | --- | --- | --- | --- |
| 0→1 | 15.80 / 92 / -43 | 11.80 → 11.555 | -10.84 → -10.776 | 0.245 / -0.064 | X; — |
| 1→2 | 20.00 / 93 / -58 | 10.59 → 10.598 | -16.96 → -16.961 | -0.008 / 0.001 | P; — |
| 2→3 | 5.20 / 107 / -35 | 4.25 → 4.260 | -4.97 → -2.983 | -0.010 / -1.987 | X; — |
| 3→4 | 20.00 / 48 / -25 | 18.12 → 18.126 | -8.45 → -8.452 | -0.006 / 0.002 | P; — |
| 4→5 | 20.00 / 114 / -37 | 15.97 → 15.973 | -12.03 → -12.036 | -0.003 / 0.006 | P; — |
| 5→6 | 17.00 / 89 / -22 | 15.76 → 15.762 | -6.38 → -6.368 | -0.002 / -0.012 | P; — |
| 6→7 | 14.00 / 23 / 20 | 13.14 → 13.156 | 4.78 → 4.788 | -0.016 / -0.008 | P; — |
| 7→8 | 18.70 / 71 / 42 | 14.08 → 13.897 | 12.50 → 12.513 | 0.183 / -0.013 | X; — |
| 8→9 | 13.50 / 24 / 34 | 11.19 → 11.192 | 7.53 → 7.549 | -0.002 / -0.019 | P; — |
| 9→10 | 11.60 / 57 / 39 | 9.00 → 9.015 | 7.28 → 7.300 | -0.015 / -0.020 | P; — |
| 10→11 | 5.40 / 32 / 36 | 3.28 → 4.369 | 3.16 → 3.174 | -1.089 / -0.014 | X; — |
| 11→12 | 20.20 / 65 / -31 | 17.31 → 17.315 | -10.40 → -10.404 | -0.005 / 0.004 | R; — |
| 12→13 | 15.10 / 29 / 1 | 15.10 → 15.098 | 0.25 → 0.264 | 0.002 / -0.014 | P; — |
| 13→14 | 20.20 / 80 / -12 | 19.75 → 19.759 | -4.19 → -4.200 | -0.009 / 0.010 | P; — |
| 14→15 | 20.20 / 75 / 10 | 19.88 → 19.893 | 3.50 → 3.508 | -0.013 / -0.008 | P; — |
| 15→16 | 10.30 / 40 / 4 | 10.30 → 10.275 | 0.71 → 0.718 | 0.025 / -0.008 | P; — |
| 16→17 | 20.20 / 85 / -18 | 19.21 → 19.211 | -6.24 → -6.242 | -0.001 / 0.002 | R; — |
| 17→18 | 20.20 / 105 / 25 | 18.30 → 18.307 | 8.53 → 8.537 | -0.007 / -0.007 | P; — |
| 18→19 | 20.60 / 55 / -31 | 17.65 → 17.658 | -10.55 → -10.610 | -0.008 / 0.060 | X; — |
| 19→20 | 17.50 / 85 / -13 | 17.04 → 17.051 | -3.93 → -3.937 | -0.011 / 0.007 | P; — |
| 20→21 | 12.40 / 115 / 30 | 10.73 → 10.739 | 6.20 → 6.200 | -0.009 / 0.000 | P; — |
| 21→22 | 20.20 / 60 / -36 | 16.34 → 16.342 | -11.86 → -11.873 | -0.002 / 0.013 | P; — |
| 22→23 | 5.40 / 78 / -3 | 5.40 → 5.393 | -0.28 → -0.283 | 0.007 / 0.003 | P; — |
| 23→24 | 9.20 / 108 / 23 | 8.46 → 8.469 | 3.58 → 3.595 | -0.009 / -0.015 | P; — |
| 24→25 | 11.10 / 117 / 43 | 8.11 → 8.118 | 7.56 → 7.570 | -0.008 / -0.010 | P; — |
| 25→26 | 20.60 / 94 / 14 | 19.98 → 19.988 | 4.97 → 4.984 | -0.008 / -0.014 | P; — |
| 26→27 | 20.30 / 204 / 45 | 14.35 → 14.354 | 14.35 → 14.354 | -0.004 / -0.004 | R; — |
| 27→28 | 13.20 / 180 / 62 | 6.18 → 6.197 | 11.63 → 11.655 | -0.017 / -0.025 | P; dh |
| 28→29 | 20.50 / 132 / 45 | 14.49 → 14.496 | 14.49 → 14.496 | -0.006 / -0.006 | P; — |
| 29→30 | 13.80 / 77 / -3 | 13.80 → 13.781 | -0.71 → -0.722 | 0.019 / 0.012 | P; D, Lh |
| 30→31 | 20.50 / 93 / 23 | 18.87 → 18.870 | 8.00 → 8.010 | -0.000 / -0.010 | P; — |
| 31→32 | 9.30 / 132 / 40 | 7.11 → 7.124 | 5.97 → 5.978 | -0.014 / -0.008 | P; dh |
| 32→33 | 10.50 / 160 / 46 | 7.28 → 7.294 | 7.54 → 7.553 | -0.014 / -0.013 | P; — |
| 33→34 | 10.50 / 82 / 3 | 10.50 → 10.486 | 0.54 → 0.550 | 0.014 / -0.010 | P; — |
| 34→35 | 6.50 / 97 / -22 | 6.02 → 6.027 | -2.42 → -2.435 | -0.007 / 0.015 | P; — |
| 35→36 | 5.60 / 37 / 0 | 5.60 → 5.600 | 0.00 → 0.000 | 0.000 / 0.000 | R; — |
| 36→37 | 20.70 / 63 / 3 | 20.70 → 20.672 | 1.07 → 1.083 | 0.028 / -0.013 | P; — |
| 37→38 | 10.50 / 74 / 24 | 9.59 → 9.592 | 4.26 → 4.271 | -0.002 / -0.011 | P; — |
| 38→39 | 17.50 / 75 / -62 | 8.20 → 8.216 | -15.44 → -15.452 | -0.016 / 0.012 | P; — |
| 39→40 | 12.20 / 75 / -17 | 11.66 → 11.667 | -3.55 → -3.567 | -0.007 / 0.017 | P; A, dh |
| 40→41 | 20.30 / 87 / 16 | 19.50 → 19.514 | 5.59 → 5.595 | -0.014 / -0.005 | P; dh |
| 41→42 | 20.10 / 79 / -3 | 20.10 → 20.072 | -1.04 → -1.052 | 0.028 / 0.012 | P; — |
| 42→43 | 15.00 / 95 / 43 | 10.96 → 10.970 | 10.23 → 10.230 | -0.010 / 0.000 | P; — |
| 43→44 | 20.70 / 85 / 5 | 20.70 → 20.621 | 1.75 → 1.804 | 0.079 / -0.054 | X; — |
| 44→45 | 6.70 / 91 / 35 | 6.46 → 5.488 | 3.84 → 3.843 | 0.972 / -0.003 | X; — |
| 45→46 | 20.40 / 78 / -3 | 20.40 → 20.372 | -1.06 → -1.068 | 0.028 / 0.008 | P; — |
| 46→47 | 20.10 / 58 / -19 | 19.00 → 19.005 | -6.54 → -6.544 | -0.005 / 0.004 | R; — |
| 47→48 | 17.50 / 85 / 18 | 16.63 → 16.643 | 5.40 → 5.408 | -0.013 / -0.008 | P; — |
| 48→49 | 14.20 / 74 / 23 | 13.06 → 13.071 | 5.53 → 5.548 | -0.011 / -0.018 | P; — |
| 49→50 | 14.20 / 68 / 61 | 6.86 → 6.884 | 12.40 → 12.420 | -0.024 / -0.020 | P; A |
| 50→51 | 9.90 / 62 / 42 | 7.34 → 7.357 | 6.62 → 6.624 | -0.017 / -0.004 | P; — |
| 51→52 | 10.30 / 57 / 33 | 8.63 → 8.638 | 5.60 → 5.610 | -0.008 / -0.010 | P; — |
| 52→53 | 8.40 / 12 / -3 | 8.40 → 8.388 | -0.43 → -0.440 | 0.012 / 0.010 | P; — |
| 53→54 | 19.30 / 45 / 46 | 13.39 → 13.407 | 13.87 → 13.883 | -0.017 / -0.013 | P; — |
| 54→55 | 9.10 / 43 / 45 | 6.43 → 6.435 | 6.43 → 6.435 | -0.005 / -0.005 | R; dh |
| 55→56 | 5.90 / 60 / -24 | 5.38 → 5.390 | -2.39 → -2.400 | -0.010 / 0.010 | P; — |
| 56→57 | 3.00 / 97 / -13 | 2.92 → 2.923 | -0.67 → -0.675 | -0.003 / 0.005 | R; — |
| 57→58 | 10.00 / — / -90 | 0.00 → 0.000 | -10.00 → -10.000 | -0.000 / 0.000 | R; — |
| 58→59 | 9.10 / 270 / -45 | 6.45 → 6.435 | -6.44 → -6.435 | 0.015 / -0.005 | P; Lh, dh |
| 59→60 | 17.60 / 35 / -14 | 17.07 → 17.077 | -4.24 → -4.258 | -0.007 / 0.018 | P; D |
| 60→61 | 11.00 / 47 / -12 | 10.75 → 10.760 | -2.27 → -2.287 | -0.010 / 0.017 | P; — |
| 61→62 | 9.20 / 50 / 9 | 9.20 → 9.087 | 1.43 → 1.439 | 0.113 / -0.009 | X; — |
| 62→63 | 3.50 / 55 / -25 | 3.07 → 3.172 | -1.37 → -1.479 | -0.102 / 0.109 | X; — |
| 63→64 | 14.50 / 49 / 0 | 14.50 → 14.500 | 0.00 → 0.000 | 0.000 / 0.000 | R; — |
| 64→65 | 8.00 / 85 / -33 | 6.70 → 6.709 | -3.64 → -4.357 | -0.009 / 0.717 | X; — |
| 65→66 | 19.80 / 110 / -75 | 5.10 → 5.125 | -18.72 → -19.125 | -0.025 / 0.405 | X; — |
| 66→67 | 16.00 / 15 / 22 | 14.83 → 14.835 | 5.98 → 5.994 | -0.005 / -0.014 | P; — |
| 67→68 | 13.50 / 40 / -6 | 13.50 → 13.426 | -1.40 → -1.411 | 0.074 / 0.011 | X; — |
| 68→69 | 14.60 / 33 / -3 | 14.60 → 14.580 | -0.75 → -0.764 | 0.020 / 0.014 | P; — |
| 69→70 | 16.60 / 83 / 8 | 16.60 → 16.438 | 2.30 → 2.310 | 0.162 / -0.010 | X; — |
| 70→71 | 17.00 / 50 / 2 | 17.00 → 16.990 | 0.58 → 0.593 | 0.010 / -0.013 | P; — |
| 71→72 | 20.00 / 58 / -1 | 20.00 → 19.997 | -0.35 → -0.349 | 0.003 / -0.001 | R; V |
| 72→73 | 18.00 / 49 / 0 | 18.00 → 18.000 | 0.00 → 0.000 | 0.000 / 0.000 | R; — |
| 73→74 | 17.00 / 40 / 0 | 17.00 → 17.000 | 0.00 → 0.000 | 0.000 / 0.000 | R; — |
| 74→75 | 17.00 / 60 / -25 | 14.40 → 15.407 | -7.17 → -7.185 | -1.007 / 0.015 | X; — |
| 75→76 | 26.00 / 77 / -27 | 23.16 → 23.166 | -11.80 → -11.804 | -0.006 / 0.004 | P; — |
| 6→a | 7.40 / 302 / 8 | 7.40 → 7.328 | 1.03 → 1.030 | 0.072 / 0.000 | X; — |
| a→b | 5.40 / 270 / -37 | 4.21 → 4.313 | -3.25 → -3.250 | -0.103 / -0.000 | X; V |

JSON zawiera także test Pitagorasa (D z Lh i Δh), kąt atan2(Δh,Lh), wartości literalne, numery linii, alternatywy modeli oraz rachunki dla każdego ich wiersza.

## Sumy i punkty kontrolne

Suma Δh to suma zapisanej kolumny. Wynik z D,V jest niezależnym przeliczeniem tych samych obserwacji, a nie niezależnym pomiarem terenowym. Przypisania dopisków do stacji są jawne w JSON.

| Dopisek | Stacja | Zapis | Suma Δh | Różnica | Suma D sin V | Różnica przyrostu od poprzedniego dopisku |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| wysokość przy stacji 6 | 6 | -59.73 | -59.630 | 0.100 | -57.576 | — |
| wysokość przy stacji 11 | 11 | -24.48 | -24.380 | 0.100 | -22.252 | 0.000 |
| wysokość przy stacji 19 | 19 | -42.87 | -42.770 | 0.100 | -40.681 | 0.000 |
| Margines przy 25→26 | 26 | -36.63 | -36.530 | 0.100 | -34.425 | 0.000 |
| Margines stacji 29 | 29 | 3.86 | 3.940 | 0.080 | 6.080 | -0.020 |
| Margines stacji 38 | 38 | 28.09 | 28.190 | 0.100 | 30.368 | 0.020 |
| Margines stacji 45 | 45 | 29.47 | 29.570 | 0.100 | 31.770 | 0.000 |
| Margines stacji 52 | 52 | 57.42 | 57.520 | 0.100 | 59.768 | 0.000 |
| Suma przed pionem 57→58 | 57 | 74.23 | 74.330 | 0.100 | 76.572 | 0.000 |
| krawędź Studni Imieninowej | 64 | 51.39 | 51.440 | 0.050 | 53.552 | -0.050 |
| Studnia Imieninowa | 66 | 29.03 | 29.080 | 0.050 | 30.070 | 0.000 |
| wysokość przy 72→73 | 73 | 35.39 | 35.440 | 0.050 | 36.443 | 0.000 |
| osobny wynik obok podsumowania | 76 | 16.42 | 16.470 | 0.050 | 17.454 | -0.000 |
| wysokość stacji a | a | -58.70 | -58.600 | 0.100 | -56.546 | 0.000 |
| wysokość stacji b | b | -61.95 | -61.850 | 0.100 | -59.796 | 0.000 |

- +26,3?: Ołówek bardzo blady, możliwe przekreślenie/korekta. Wizualnie +26,3, słabsze +2,63; nie traktować jako pewnej wysokości ani wyniku. Druga fotografia nie rozstrzyga.

- ΣΔh +20,79: Obie fotografie jednoznacznie pokazują +20,79. Zakres sumy nie jest zapisany; nie utożsamiać automatycznie z sumą wierszy 60–76 ani wynikiem całego ciągu.

- po [nieczytelne] 2 m: Liczba 2 m w uwagach, nie suma długości ani kolumna pomiarowa. Nie używać do rachunku bez ustalenia znaczenia.

- Stanowisko nad Błotnym Progiem [odczyt częściowy]: Po ponownym powiększeniu marginesu preferuję Błotnym zamiast pierwszego odczytu Białym. Tekst w czterech wierszach przy podsumowaniu przed pionem. Nazwa częściowo słaba; nie wpływa na wartości tabeli.

## Rozbieżności ocenianych pól

To rozbieżności względem ponownie obejrzanych, rozstrzygniętych pól skanu. Pola niepewne są wyłączone, a nie zaliczone żadnemu modelowi.

### gemini_flash_3.8

| Odcinek | Pole | Pierwszy wynik | Odczyt skanu | Poprawne w alternatywach |
| --- | --- | --- | --- | --- |
| 1→2 | Lh | 10.73 | 10.59 | tak |
| 2→3 | dh | -2.97 | -4.97 | tak |
| 24→25 | D | 21.10 | 11.10 | tak |
| 28→29 | Lh | 14.45 | 14.49 | nie |
| 28→29 | dh | 14.45 | 14.49 | nie |
| a→b | dh | -3.05 | -3.25 | nie |
### gemini_pro

| Odcinek | Pole | Pierwszy wynik | Odczyt skanu | Poprawne w alternatywach |
| --- | --- | --- | --- | --- |
| 1→2 | A | 83.00 | 93.00 | nie |
| 2→3 | dh | -2.97 | -4.97 | nie |
| 19→20 | D | — | 17.50 | nie |
| 19→20 | A | — | 85.00 | nie |
| 19→20 | V | — | -13.00 | nie |
| 19→20 | Lh | — | 17.04 | nie |
| 19→20 | dh | — | -3.93 | nie |
| 20→21 | A | 145.00 | 115.00 | nie |
| 24→25 | D | 21.10 | 11.10 | nie |
| 24→25 | Lh | 15.44 | 8.11 | nie |
| 24→25 | dh | 14.39 | 7.56 | nie |
| 27→28 | Lh | 6.19 | 6.18 | nie |
| 28→29 | D | 20.40 | 20.50 | nie |
| 28→29 | Lh | 14.45 | 14.49 | nie |
| 28→29 | dh | 14.45 | 14.49 | nie |
| 32→33 | D | 10.30 | 10.50 | nie |
| 32→33 | Lh | 7.22 | 7.28 | nie |
| 43→44 | V | 15.00 | 5.00 | nie |
| 43→44 | Lh | 20.00 | 20.70 | nie |
| 43→44 | dh | 5.35 | 1.75 | nie |
| 44→45 | Lh | 5.46 | 6.46 | nie |
| 46→47 | V | -15.00 | -19.00 | nie |
| 46→47 | dh | -6.84 | -6.54 | nie |
| 48→49 | dh | 5.33 | 5.53 | nie |
| 62→63 | D | 3.30 | 3.50 | nie |
| 73→74 | D | 12.00 | 17.00 | nie |
| 73→74 | Lh | 12.00 | 17.00 | nie |
| a→b | dh | -3.05 | -3.25 | nie |
### claude_opus_5

| Odcinek | Pole | Pierwszy wynik | Odczyt skanu | Poprawne w alternatywach |
| --- | --- | --- | --- | --- |
| 1→2 | Lh | 10.53 | 10.59 | nie |
| 4→5 | Lh | 15.93 | 15.97 | tak |
| 7→8 | A | 74.00 | 71.00 | nie |
| 16→17 | Lh | 19.20 | 19.21 | tak |
| 21→22 | dh | -11.88 | -11.86 | nie |
| 23→24 | dh | 3.18 | 3.58 | nie |
| 24→25 | V | 13.00 | 43.00 | nie |
| 24→25 | Lh | 11.10 | 8.11 | nie |
| 24→25 | dh | 2.56 | 7.56 | nie |
| 28→29 | V | -45.00 | 45.00 | nie |
| 28→29 | dh | -14.45 | 14.49 | nie |
| 36→37 | V | 5.00 | 3.00 | tak |
| 36→37 | dh | 1.02 | 1.07 | nie |
| 37→38 | V | 29.00 | 24.00 | tak |
| 37→38 | Lh | 9.19 | 9.59 | nie |
| 38→39 | D | 17.10 | 17.50 | nie |
| 38→39 | V | 62.00 | -62.00 | nie |
| 38→39 | dh | 15.44 | -15.44 | tak |
| 39→40 | Lh | 11.60 | 11.66 | nie |
| 41→42 | dh | -1.09 | -1.04 | nie |
| 42→43 | A | 91.00 | 95.00 | nie |
| 44→45 | D | 6.20 | 6.70 | nie |
| 44→45 | dh | 3.54 | 3.84 | nie |
| 48→49 | A | 24.00 | 74.00 | nie |
| 53→54 | D | 15.30 | 19.30 | nie |
| 53→54 | dh | 13.09 | 13.87 | nie |
| 55→56 | D | 5.80 | 5.90 | nie |
| 55→56 | Lh | 5.30 | 5.38 | nie |
| 55→56 | dh | -2.59 | -2.39 | nie |
| 59→60 | Lh | 12.07 | 17.07 | nie |
| 59→60 | dh | -4.04 | -4.24 | nie |
| 60→61 | A | 43.00 | 47.00 | nie |
| 60→61 | dh | -2.37 | -2.27 | nie |
| 62→63 | D | 3.10 | 3.50 | nie |
| 71→72 | dh | 0.35 | -0.35 | nie |
| 73→74 | D | 12.00 | 17.00 | nie |
| 73→74 | Lh | 12.00 | 17.00 | nie |
| 74→75 | D | 12.00 | 17.00 | tak |
| a→b | dh | -3.05 | -3.25 | nie |
### Codex_initial_7472374

| Odcinek | Pole | Pierwszy wynik | Odczyt skanu | Poprawne w alternatywach |
| --- | --- | --- | --- | --- |
| 20→21 | Lh | 10.23 | 10.73 | nie |

## Odtworzenie

```sh
uv run jktz-czarna-kontrola
```

Wejścia: `KONTROLA_RACHUNKOW/odczyt_uzgodniony.json`, trzy fotografie `_RAW/02`, trzy surowe transkrypcje `ODCZYTY_MODELI`, bieżący SRV i SRV z commitu 7472374. SHA-256 w `KONTROLA_RACHUNKOW/wyniki.json`. Skrypt nie modyfikuje źródeł ani SRV.
