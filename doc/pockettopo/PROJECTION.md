# PocketTopo: polityka projekcji

[projection.py](../../src/jktz/pockettopo/projection.py) wylicza podkład
wyłącznie z aktywnych grup eksportu, przed zaokrągleniem SRV/SVX.
`project_geometry(model, report)` zwraca plan i przekrój w milimetrach
źródłowego szkicu: X w prawo, Y w dół. Nie zmienia kresek ani modelu źródła,
nie zakłada CRS referencji i nie potwierdza powtórzeń.

## Osnowa i przekrój rozwinięty

Pierwsza dostępna stacja każdej części spójnej otrzymuje lokalne zero.
Dostępne odcinki dołączane są w kolejności źródłowej; kolejka umożliwia
dołączenie także pomiaru zapisanego przed połączeniem z już znaną stacją.
Dołączenie następuje przez FROM, a gdy znane jest tylko TO — przez TO.
Tożsamości stacji pochodzą z identyfikatorów źródła.

Dla `H = D cos(V)` plan używa `E = H sin(A + DECL)` oraz
`N = H cos(A + DECL)`, a wysokość `Z = D sin(V)`.
Rozwinięcie używa `±H` zależnie od własnego Flip odcinka, bez dziedziczenia
Flip poprzednika. Przy odwrotnym dołączeniu zmienia się znak E/N/Z,
lecz nie znak `±H`: lewo/prawo nadal odnosi się do stacji dołączenia.

Pętle nie są wyrównywane. Każdy odcinek ma własny obliczony koniec, a pierwsze
położenie nazwanej stacji pozostaje odniesieniem dla dalszych pomiarów.
Różnicę opisują `unadjusted_closure`, `closure_residual_mm` i
`target_station_position`. Rozłączne części mają własne lokalne zera;
`disconnected_components_local_origins` i widoczne ostrzeżenie oznaczają,
że ich wzajemne położenie oraz powiązanie ze szkicem pozostają nieustalone.

Niepotwierdzone powtórzenia pozostają osobnymi odcinkami. Potwierdzone grupy
używają średniej kołowej azymutu i arytmetycznej długości oraz pochylenia.
Pierwszy rekord grupy określa Flip. Przy mieszanych Flip polityka
`first_source_reading_unconfirmed_side_direction`, diagnostyka
`mixed_flip_first_source_reading` i napis `CHECK OVERLAY` wskazują
niepotwierdzony kierunek rozwinięcia. Potwierdzenie powtórzeń D/A/V nie
rozstrzyga Flip. Nie odtwarzamy automatycznego natywnego uśredniania
składowych; dla serii nie należy zakładać identycznego podkładu PocketTopo.

## Domiary i XSection

W planie domiar wychodzi ze stacji osnowy zgodnie ze skorygowanym azymutem.
W rozwinięciu jego składowa pozioma wynosi `H cos(A_splay − A_incoming)`
ze znakiem Flip odcinka, który zdefiniował stację. Używa surowych azymutów
bez deklinacji; odwrotne dołączenie dodaje do incoming 180°. Kolejny odcinek
wychodzący nie zmienia tej osi. Korzeń oraz stacja zdefiniowana zerowym
powiązaniem nie mają osi: pozioma składowa domiaru wynosi zero.

XSection zachowuje indeks elementu, pozycję, identyfikator stacji i surowy
`direction`. Powstaje osobny łącznik do stacji oraz projekcje jej domiarów:

- `direction == -1`: przekrój poziomy `(E, −N)` ze skorygowanych składowych;
- inne kierunki: przekrój pionowy `(H sin(A_raw − direction), −Z)`.

Korekta deklinacji nie obraca domiarów wewnątrz pionowego XSection.
Brak stacji w aktywnym podkładzie daje `station_not_in_active_overlay`:
znacznik i ostrzeżenie pozostają, bez wymyślonego łącznika.

Łączna liczba linii domiarów rozwiniętych przez XSection obu widoków nie może
przekroczyć `MAX_SECTION_SPLAY_LINES = 100000`. Kontrola poprzedza tworzenie
geometrii; przekroczenie daje `ValueError` z
`xsection_projection_limit_exceeded`, bez częściowego wyniku.

## Wzorce i granice porównania

[Testy projekcji](../../tests/test_pockettopo_projection.py) porównują
multizbiory linii z niezależnie odczytanymi natywnymi DXF. Zachowane wzorce
to [p01/cases](../../tests/fixtures/pockettopo/p01/cases),
[p05/native](../../tests/fixtures/pockettopo/p05/native) oraz
[shadow](../../tests/fixtures/pockettopo/shadow).
Osobne próby analityczne sprawdzają znaki, deklinację, Flip i wektory.

Konwerter zachowuje wynik zmiennoprzecinkowy do serializacji SVG.
PocketTopo 1.372 zaokrągla składowe do całkowitych milimetrów i dodatkowo
obcina poziomą projekcję domiaru w rozwinięciu. Różnice kumulują się z długością
osnowy. Tolerancja 3 mm w testach wybranych wzorców jest progiem regresji
tych danych, nie gwarancją błędu dowolnego pomiaru.

[Archiwalna analiza kodu natywnego i pochodzenie wzorców](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/blob/3e3daa4156c6e6e79dce5203d8bb8e36122d571f/doc/pockettopo/evidence/p05/NATIVE.md)
oraz [porównania współrzędnych](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/blob/3e3daa4156c6e6e79dce5203d8bb8e36122d571f/doc/pockettopo/evidence/p05/projection-validation.json)
opisują historyczną próbę, niezależnie od bieżącego wyniku testów.
