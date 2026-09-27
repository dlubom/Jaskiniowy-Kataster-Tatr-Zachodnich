# Jaskinia Marmurowa — weryfikacja źródeł

## Materiał pierwotny

Tomasz Pryjma przesłał 2014-05-20 trzy wiadomości z załącznikami
`img182.jpg`–`img193.jpg` w odpowiedzi na prośbę o tabelę pomiarową.
Każdy z 12 plików w `_RAW/01` ma ten sam SHA-256 co odpowiedni załącznik;
wykaz i zakres arkuszy są w [README paczki](_RAW/01/README.md).
Maile nie podają odrębnych wartości pomiarowych, dokładnych dni wykonania
pomiarów ani warunków licencji skanów.

| SRV | Skan | Wiersze D/A/V przed zmianą | Wynik porównania |
| --- | --- | ---: | --- |
| `MARMUR_KK.SRV` | img182 | 14 | wartości zgodne |
| `MARMUR_DU.SRV` | img183 | 15 | wartości zgodne |
| `MARMUR_ME.SRV` | img184 | 8 | wartości zgodne |
| `MARMUR_OK.SRV` | img185 | 6 | wartości zgodne |
| `MARMUR_S2.SRV` | img186 | 8 | wartości zgodne |
| `MARMUR_ST.SRV` | img187 | 12 | wartości zgodne |
| `MARMUR_OT.SRV` | img188–img191 | 63 | jedna rozbieżność azymutu |
| `MARMUR_P.SRV` | img193 | 8 | wartości zgodne; ten sam zestaw co część OT |

`img192` jest szkicem bez tabeli D/A/V. Skany podają miesiąc i rok:
V/1986 (OT), IV/1987 (KK, DU, ME, OK, S2), IV/1990 (ST).
`img193` nie ma daty. Metadane `SURVEY_DATE` odzwierciedlają tę
precyzję; dzień 01 w pozostałych dyrektywach `#date` jest technicznym
przybliżeniem do obliczenia deklinacji, nie datą potwierdzoną przez źródło.

## Rozstrzygnięcia w modelu

- **OT 57→58.** W kolumnie `AZYM` skanu img188 zapisano 216°, podczas gdy
  wcześniejszy SRV miał 210°. Pochodne kolumny skanu ΔY = −1,059 i
  ΔX = −1,835 odpowiadają 210° przy D = 2,4 m i V = −28°.
  Aktywne 216° przenosi bezpośredni zapis pomiaru; 210° pozostaje
  jawną alternatywą wynikającą z rachunku. Bez kolejnego źródła nie można
  stwierdzić, która liczba odpowiada odczytowi przyrządu.
- **Wspólny początek od stacji 8.** img182–img184 mają tę samą bazę
  współrzędnych oraz identyczne strzały 3,00 m / 31° / +58° i
  4,95 m / 345° / +24°. Aktywną kopię pozostawiono w KK; dalsze
  strzały DU i ME odchodzą od wspólnej stacji `kk_2`.
  Powtórzenia w DU i ME pozostały w komentarzach.
- **Przeliczenie Piaskownicy II.** Osiem strzałów img193, opisanych jako
  18→19S→…→25S→18, ma dokładnie te same D/A/V co OT 23→31
  w img190 (33,90 m). Wysokość H bazy img193 (−96,702 m) odpowiada
  stacji 23 w OT, a nie stacji 18. To mocny dowód powtórnego przeliczenia,
  ale nie upoważnia do automatycznego utożsamienia numerów.
  Na img193 azymuty 222° i 340° skreślono, zastępując je 190° i 280°;
  SRV zachowuje wartości po korekcie. Zapisane tam 32,445 m to suma
  rzutów poziomych, a 33,90 m to suma długości strzałów.
  `MARMUR_P.SRV` zachowuje arkusz jako nieaktywny wariant, a projekt
  `KATASTER.wpj` go nie włącza.

Przed usunięciem aktywnych powtórzeń suma 134 strzałów w ośmiu SRV
wynosiła 714,79 m. Po wyłączeniu ośmiu strzałów P (33,90 m) oraz
czterech powtórzeń wspólnego początku DU/ME (15,90 m) pozostają
122 aktywne strzały o sumie 664,99 m. To suma odcinków pomiarowych,
nie długość inwentarzowa jaskini.

## Porównanie z PIG i lokalizacją otworu

[Rekord PIG 1472](https://jaskiniepolski.pgi.gov.pl/Details/Information/1472)
odpowiada `T.E-11.05` w `doc/jaskinie_polski_pig_dump.jsonl`.
Zrzut opisuje stan na 2013 r.: długość 681 m, głębokość −126 m,
przewyższenie +24,5 m i deniwelację 150,5 m. Pozostałe po usunięciu
powtórzeń 664,99 m jest o 16,01 m mniejsze od długości PIG, lecz
te wielkości nie muszą mieć tej samej definicji. Zgodność 680,89 m
(suma bez P, ale nadal z powtórzonym początkiem DU/ME) po zaokrągleniu
z 681 m nie dowodzi metody obliczenia PIG i nie wybiera numeracji stacji.
Zasięg wysokościowy wynikający z aktywnych strzałów wynosi około
−124,36 do +24,50 m; brakujące 1,64 m do głębokości PIG nie jest
podstawą do zmiany odczytów.

PIG podaje otwór 49,23969444° N, 19,89911111° E, 1770,6 m.
`Poligony/OTWORY.SRV` korzysta z punktu 49,23937210° N,
19,90080063° E, 1767,70 m, pochodzącego z obiektu GPS
`MTZ-0018` i eksportu TPN. Różnica położenia wynosi około 128 m.
W wiadomości z 2014-06-21 Krzysztof Dudziński podał z fotomapy
49°14′21,81″ N, 19°54′2,93″ E, około 2,4 m od punktu TPN.
To dodatkowy odczyt z obrazu, nie niezależny terenowy pomiar otworu.
Obie współrzędne w rejestrze GPS pozostają nieweryfikowane; tutaj
nie zmieniono generowanego `OTWORY.SRV`.

PIG podaje też 1–3 maja 1986 r. jako okres eksploracji nowego dna,
nie jako dokładny dzień wykonania każdego pomiaru z tabel.
