# Meander w Małołąckim Siodle - paczka źródłowa 01

- **Status materiału:** dostępny
- **Pochodzenie danych:** Oryginalne załączniki wiadomości Zbigniewa Tabaczyńskiego z 2014-05-12, temat „pomiary meander w malolackim siodle”; odzyskane z archiwum poczty bez zmiany bajtów.
- **Autorzy pomiarów:** Zbigniew Tabaczyński (wpis *team w SVX; autor planu i przekroju w podpisach PDF).
- **Daty pomiarów:** 2014-04-30
- **Data pozyskania:** 2014-05-12
- **Dodał do _RAW:** Dariusz Lubomski
- **Licencja źródłowa:** nieznane
- **Kompletność:** Zachowany przekaz z 2014-05-12: 1 plik SVX zawierający 28 wektorów i 2 rysunki PDF. Brak surowego pliku urządzenia, dziennika terenowego i dokumentu kalibracji.

## Zawartość

- `meander_w_malolackim_siodle.svx` — źródłowe pomiary i dyrektywy; 1080 bajtów.
- `MEANDER_W_MALOLACKIM_SIODLE_1_100.pdf` — plan; 59118 bajtów.
- `przekroj_N_S MEANDER_W_MALOLACKIM_SIODLE_1_100.pdf` — przekrój; 35511 bajtów.

## Uwagi o źródle i konwersji

Źródłowy SVX podaje `*date 2014.04.30`, zespół/instrument w jednym wpisie `*team` oraz `*calibrate compass 2.37`. Odpowiednikiem tej korekty w Walls jest `INCA=-2.37`; jest ona odrębna od deklinacji wynikającej z daty. Tekst `KALIBR 047` zachowuje się jako informację źródłową, nie jako współczynnik korekty.

Współrzędne i wysokość źródłowego `*fix` zachowano w oryginale. Późniejsza wiadomość autora wyjaśnia, że lokalizację GPS określano na grani około 3–4 m powyżej otworu. Aktywne fixy otworów są utrzymywane przez projekt GPS; przy archiwizacji nie zastępuje się ich tym wpisem.

Wewnętrzny podpis rysunku przekroju brzmi E–W, chociaż oryginalna nazwa pliku zawiera `N_S`. Nazwy i bajty oryginału pozostają bez zmian. Nie odzyskano osobnego oświadczenia o licencji źródłowej.

## Sumy kontrolne oryginałów

SHA-256 obliczone z plików paczki i porównane 2026-11-09 z manifestem oryginalnych załączników odzyskanych podczas audytu. Wszystkie trzy sumy są zgodne.

| Plik | SHA-256 |
| --- | --- |
| `MEANDER_W_MALOLACKIM_SIODLE_1_100.pdf` | `6980cc797fd0014fa52b8427a2af691973e626aa7f4181d3d511476da0636901` |
| `meander_w_malolackim_siodle.svx` | `e651008af47611e362088502673c1c64dd4c1ca401d3b94c45b4d164de71a083` |
| `przekroj_N_S MEANDER_W_MALOLACKIM_SIODLE_1_100.pdf` | `000132685a9a32bcd5b3da4f4a75c368f06f2288071c9052d8e9973ee83bfc81` |

## Natywna próba znaku INCA — #148

2026-11-09 sprawdzono rzeczywisty Walls v2.3.0-beta.1, build 2025-09-13,
uruchomiony przez Wine w osobnej sesji. SHA-256 `Walls32.exe`:
`ee11c4cf908d200176c96528e702846ef3e2caba7e356fc0e4c03bde17ae782f`.

Minimalne wejście do odtworzenia próby (lokalny układ, bez `#date` i IGRF):

```text
#units meters order=DAV
#units A=D V=D DECL=0
#fix a 0 0 0
#units INCA=0
a zero 10 90 0
#units INCA=-2.37
a minus 10 90 0
#units INCA=2.37
a plus 10 90 0
```

Po rekompilacji wygenerowano w Walls raport **Station and Vector Reports**,
alfabetycznie według nazw stacji, z sześcioma miejscami po przecinku:

| Stacja | INCA [°] | East [m] | North [m] | Up [m] | Azymut wynikowy [°] |
| --- | ---: | ---: | ---: | ---: | ---: |
| zero | 0 | 10.000000 | 0.000000 | 0.000000 | 90.00 |
| minus | −2.37 | 9.991446 | 0.413525 | 0.000000 | 87.63 |
| plus | +2.37 | 9.991446 | −0.413525 | 0.000000 | 92.37 |

Współrzędne zgadzają się z `E=10·sin(90°+INCA)`, `N=10·cos(90°+INCA)`
do dokładności zapisu raportu. Potwierdza to dodawanie INCA przez natywny Walls
i właściwy znak `INCA=-2.37` dla źródłowego `*calibrate compass 2.37`,
które odejmuje błąd zera. Zgodność konwersji SVX/SRV potwierdziła osobna
próba Survex 1.4.24; nie zastępuje ona powyższego testu Walls.

Pełne wejścia, raport LST, logi i porównanie analityczne zachowano w lokalnym
pakiecie `.verification/2026-11-09-pr154-followup/` (poza Git i ZIP wydania).
Pomiary, daty operacyjne i fixy Meandra pozostają bez zmian.
