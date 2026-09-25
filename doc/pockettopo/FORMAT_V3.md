# PocketTopo `.top` v3 — kontrakt wejścia

Opracowanie specyfikacji **„PocketTopo File Formats”, 17.3.2010 bh (Beat Heeb)**,
dostarczonej przez użytkownika w zadaniu z 2026-09-25. Publiczna kopia:
[SexyTopo, przypięta rewizja](https://github.com/richsmith/sexytopo/blob/d918be049252cda972f78c94761ca3c65b583a7f/docs/PocketTopoFileFormat.txt).
To opis wejścia, nie dowód zgodności przyszłego parsera. `.cal` v1 jest poza
zakresem [PRD](PRD.md).

Wszystkie liczby są **little endian**. Zachowywać surowe wartości całkowite;
przeliczenia i normalizacje wykonywać w osobnej warstwie.

| Struktura | Pola w kolejności zapisu |
| --- | --- |
| File | bajty ASCII `T`, `o`, `p` i liczbowy bajt wersji `0x03` (nagłówek hex `54 6f 70 03`); Int32 tripCount; Trip[tripCount]; Int32 shotCount; Shot[shotCount]; Int32 refCount; Reference[refCount]; Mapping overview; Drawing outline; Drawing sideview |
| Trip | Int64 time; String comment; Int16 declination |
| Shot | Id from; Id to; Int32 dist; Int16 azimuth; Int16 inclination; Byte flags; Byte roll; Int16 tripIndex; jeżeli `flags & 2`: String comment |
| Reference | Id station; Int64 east; Int64 north; Int32 altitude; String comment |
| Mapping | Point origin; Int32 scale |
| Drawing | Mapping mapping; kolejne Element; kończący Byte `0` |
| PolygonElement | Byte `1`; Int32 pointCount; Point[pointCount]; Byte color |
| XSectionElement | Byte `3`; Point pos; Id station; Int32 direction |
| Point | Int32 x; Int32 y |
| Id | Int32 value |
| String | długość bajtowa zakodowana grupami 7-bit; wskazana liczba bajtów UTF-8 |

## Jednostki i znaczenie

- `time`: ticks po 100 ns od 0001-01-01; nie przechodzić przez float.
  Zegar urządzenia może być zresetowany — reguła wiarygodności dat jest w PRD.
- `dist`, współrzędne referencji i Point: milimetry. `altitude` to wysokość
  nad poziomem morza według źródła, bez informacji o CRS/datum.
- Kąty 16-bit: pełny obrót **65536** jednostek. Azymut interpretuje wzorzec
  bitowy modulo 65536: północ `0`, wschód `0x4000`. Pochylenie:
  góra `0x4000`, dół `0xC000` (−16384 jako signed Int16).
- Roll: pełny obrót **256** jednostek; wyświetlacz w górę `0`, lewo `64`, dół `128`.
- `tripIndex=-1`: bez tripu; nie używać jako pythonowego indeksu ostatniego tripu.
  Nieujemny indeks musi wskazywać istniejący rekord.
- `flags & 1`: flipped. Instrukcja aplikacji wiąże Flip z lewo/prawo na
  przekroju rozwiniętym. Nie traktować jako flagi pomiaru wstecznego.
- Reference E/N/Z są signed. Format nie podaje CRS.
- Mapping: zapamiętany środek widoku i skala 10…50000; zachować osobno od geometrii.
- Point opisuje pozycję w świecie względem pierwszej stacji. Polygon jest
  **otwarty**. Zachować też kreski jednopunktowe.
- Kolory 1…7: black, gray, brown, blue, red, green, orange.
- XSection direction: `-1` dla poziomego, nieujemne wartości oznaczają azymut
  projekcji w wewnętrznych jednostkach kąta. Zachować stację oraz pozycję.

## ID i ciągi znaków

`0x80000000` oznacza niezdefiniowane ID. Dla pozostałych ujemnych Int32 zwykły
numer wynosi `value - (-2147483647)`. Dla nieujemnych wartości identyfikator to
`major.minor`, gdzie `major=value >> 16`, `minor=value & 0xffff`.
Nie utożsamiać zwykłego `0` z `0.0`; zachować rodzaj ID i wartość binarną.

Długość String jest liczbą **bajtów**, nie znaków Unicode. Kolejne bajty długości
wnoszą po 7 bitów od najmniej znaczącej grupy; ustawiony bit 7 zapowiada następną
grupę. To nie jest stałe pole jedno- lub dwubajtowe. Tekst nie jest zakończony NUL.
Parser ma sprawdzać przepełnienie, ucięcie, limit długości i poprawność UTF-8.

## Różnica między specyfikacją i zaobserwowanymi plikami

Oba lokalne `.top` i sześć próbek `test2`, w tym zapisany przykład Shadow,
mają po obu rysunkach jeszcze **cztery bajty zerowe**. Specyfikacja ich nie opisuje.
W P01 sprawdzić pliki zapisane na nowo przez aplikację i ustalić dozwolone
zakończenia. Nie pomijać dowolnych dodatkowych bajtów ani nie utożsamiać
zachowania jednego istniejącego parsera ze specyfikacją.
