# P05 — osnowa, rozwinięcie i XSection

`src/jktz/pockettopo/projection.py` wylicza podkład z **aktywnych grup P04**.
Nie odczytuje ponownie zaokrąglonego SRV, nie zmienia szkicu, nie zakłada CRS
referencji i nie potwierdza powtórzeń. `project_geometry(model, report)` zwraca
geometrię planu i boku w milimetrach źródłowego szkicu: X w prawo, Y w dół.
Raport P04 i niezmienny model pozostają nienaruszone.

## Osnowa i rozwinięcie

Pierwsza dostępna stacja części spójnej otrzymuje lokalne `(0,0,0,0)`.
Dołączamy dostępne odcinki w kolejności źródłowej; kolejka indeksów pozwala
przejść także przez odcinki zapisane przed połączeniem z już znaną stacją.
Odcinek dołącza się przez FROM, a gdy znane jest tylko TO — przez TO.
Nazwy stacji pozostają dosłownymi tożsamościami źródłowymi.

Dla `H=D cos(V)` plan używa `(E,N)=(H sin(A+DECL), H cos(A+DECL))`;
wysokość wynosi `D sin(V)`. Rozwinięcie używa `±H` zależnie od **własnego
Flip odcinka**, bez dziedziczenia Flip rodzica. Podczas odwrotnego dołączenia
zmieniamy znak E/N/Z, lecz nie znak `±H`: lewo/prawo nadal odnosi się do
stacji dołączenia. Natywny wzorzec `branch` sprawdza tę różnicę.

Pętla **nie jest wyrównywana**. Każdy pomiar otrzymuje własny obliczony koniec;
pierwsze położenie nazwanej stacji pozostaje odniesieniem dla dalszych
odcinków. Przy różnicy raportujemy `unadjusted_closure`, wartość niedomknięcia
i `target_station_position`. To odpowiada natywnemu wzorcowi `loop`, który
rysuje zamknięcie do kolejnego wystąpienia stacji `0`, oddalonego od początku.
Różne części spójne mają własne lokalne zera; relacja przestrzenna między
nimi pozostaje nieustalona (`disconnected_components_local_origins`). Renderer
pokazuje widoczne ostrzeżenie — nakładanie lokalnych początków nie stanowi
ustalonego powiązania z inną częścią ani ze szkicem.

Niepotwierdzone powtórzenia pozostają osobnymi odcinkami i mogą dawać kilka
obliczonych końców jednej nazwanej pary. Potwierdzone grupy używają średniej
kołowej A oraz arytmetycznej D/V z P03. Pierwszy rekord grupy określa Flip;
wszystkie flagi pozostają w śladzie źródłowym. Dla mieszanych Flip jawna
polityka `first_source_reading_unconfirmed_side_direction` oznacza kierunek
boku jako **niepotwierdzony** i dodaje diagnostykę
`mixed_flip_first_source_reading` z indeksami rekordów, oryginalnymi flagami
i indeksem przedstawiciela. Renderer pokazuje widoczne `CHECK OVERLAY`;
potwierdzenie powtórzeń D/A/V nie rozstrzyga kierunku rozwinięcia.
**Nie odtwarzamy automatycznego natywnego uśredniania.** Wzorzec
`api-cardinal` celowo odróżnia planowane `H=4924,075756… mm` od natywnego
`4922 mm` po uśrednieniu składowych. Zgodność prostych prób nie oznacza
zgodności z natywnym podkładem dowolnej niepotwierdzonej serii.

## Domiary i XSection

Domiary w planie używają skorygowanego azymutu i biegną od stacji znanej
z osnowy. W rozwinięciu ich składowa pozioma wynosi
`H cos(A_splay − A_incoming)` ze znakiem Flip **odcinka definiującego stację**.
Azymuty są surowymi azymutami kierunkowymi bez deklinacji; przy odwrotnym
dołączeniu incoming otrzymuje `+180°`. Następny wychodzący odcinek nie zmienia
osi. Korzeń i stacja zdefiniowana zerowym powiązaniem nie mają osi:
pozioma składowa domiaru wynosi zero. Natywna aplikacja stosuje te same reguły.

Każdy XSection zachowuje indeks elementu, pozycję, identyfikator stacji
i surowy `direction`. Ma osobny łącznik do stacji oraz projekcje jej domiarów:

- `direction == -1`: poziomy przekrój `(E,-N)` ze skorygowanych składowych;
- inne kierunki: pionowy przekrój `(H sin(A_raw − direction), -Z)`.

Kierunek pionowego XSection jest zapisany względem surowych kierunków,
więc korekta deklinacji nie obraca domiarów wewnątrz takiego przekroju.
Wzorzec z jawnymi +5° sprawdza tę różnicę. Brak stacji w aktywnym podkładzie
pozostawia pozycję XSection i status `station_not_in_active_overlay`, bez
wymyślonego łącznika. Renderer zachowuje znacznik i ostrzeżenie.

Domiary są indeksowane po stacji raz dla obu widoków; kolejne XSection nie
skanują całej osnowy. Przed konstruowaniem geometrii sprawdzamy łączną liczbę
rozwiniętych linii domiarów wszystkich XSection w obu widokach. Stała
`MAX_SECTION_SPLAY_LINES = 100000` ogranicza zwielokrotnienie małego wejścia;
przekroczenie daje `ValueError("xsection_projection_limit_exceeded: N")` bez
częściowego wyniku. To limit projekcji, odrębny od limitów parsera.

## Niezależne sprawdzenie współrzędnych

[projection-validation.json](projection-validation.json) zapisuje każdy
porównany odcinek: indeks grupy/źródła, oba końce konwertera i natywnego DXF,
różnicę każdej pary przez maksimum współrzędnych oraz hashe źródeł/DXF.
Parser DXF jest niezależny od kodu projekcji. Porównuje całe multizbiory,
więc żadna brakująca lub nadmiarowa linia nie przechodzi kontroli.

| Wzorzec | Plan: maks. różnica współrzędnej | Bok: maks. różnica współrzędnej |
| --- | ---: | ---: |
| `api-drawings` | < 1e-8 mm | < 1e-8 mm |
| `loop` | 0,455205 mm | 0,124147 mm |
| `branch` | 0,232532 mm | 0,767468 mm |
| `xsection` | 0,831153 mm | 0,686140 mm |
| `shadow` | 1,797289 mm | 2,449857 mm |

Konwerter zachowuje zmiennoprzecinkowy wynik do serializacji SVG. PocketTopo
zaokrągla składowe odcinków do całkowitych mm oraz dodatkowo obcina poziomą
projekcję domiaru w rozwinięciu. Na dłuższej osnowie zaokrąglenia kumulują się.
Granica regresji **3 mm dotyczy tych zamrożonych wzorców**, nie deklaracji
ogólnego błędu dowolnej jaskini. Próby analityczne mają znacznie ciaśniejsze
oczekiwania i osobno sprawdzają znaki, deklinację, Flip oraz wektory.

Shadow: oba natywne DXF mają po 30 odcinków osnowy i jednym domiarze;
sprawdzono każdy z nich. Jedyny zatrzymany rekord to niepoprawne zerowe
powiązanie stacji z nią samą, wcześniej oznaczone przez P03/P04. Nie było
automatycznego potwierdzenia ani usunięcia żadnej serii powtórzeń.

```sh
uv run pytest tests/test_pockettopo_projection.py
```

W tej kontroli: **29 testów**, 100% wykonanych linii i gałęzi modułu projekcji
(156 instrukcji, 60 gałęzi). Pełne bramki repozytorium są raportowane osobno.
Wzorce i badanie natywnego kodu opisuje [NATIVE.md](NATIVE.md).
