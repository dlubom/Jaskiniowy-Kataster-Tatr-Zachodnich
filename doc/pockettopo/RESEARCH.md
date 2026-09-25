# PocketTopo — wyniki researchu

Stan dowodów: **2026-09-25**. Zakres produktu, decyzje i kolejność wdrożenia
opisuje [PRD](PRD.md). Dostęp do aplikacji i odtwarzanie eksportu są osobno
w [POCKETTOPO_MACOS.md](POCKETTOPO_MACOS.md). Ten dokument przechowuje
ustalenia źródłowe i granice dotychczasowego sprawdzenia; nie potwierdza
istnienia gotowego konwertera.

## Źródła i istniejące implementacje

Punktem odniesienia jest specyfikacja „PocketTopo File Formats”, 17.3.2010 bh,
przekazana przez użytkownika: `.top` v3, little endian, milimetry, pełny obrót
65536 jednostek kąta i 256 jednostek roll. Jej
[kopia w przypiętej rewizji SexyTopo](https://github.com/richsmith/sexytopo/blob/d918be049252cda972f78c94761ca3c65b583a7f/docs/PocketTopoFileFormat.txt)
pozwala wrócić do opisu struktur. Instrukcje i program udostępnia
[autor PocketTopo](https://paperless.bheeb.ch/download.html).

| Implementacja i sprawdzona rewizja | Przydatność i potwierdzone ograniczenia |
| --- | --- |
| [inkscape-speleo/topreader](https://github.com/speleo3/inkscape-speleo/blob/64b13a199e7820b2caa620e254ec2a62344f96f7/extensions/topreader.py), commit `64b13a199e7820b2caa620e254ec2a62344f96f7` | Eksportuje m.in. Survex i SVG, stosuje średnią kołową. Używa dzielników 65535/255; grupuje pary stacji globalnie, także między tripami; z grupy zachowuje tylko pierwszy komentarz/trip/extend. Referencje odczytuje jako unsigned, dekoder ID jest niepełny, długość tekstu obsługuje najwyżej w dwóch bajtach. Nie jest wzorcem całkowicie wiernego odczytu. |
| [TopParser 1.3](https://deb.debian.org/debian/pool/main/t/topparser/topparser_1.3.orig.tar.gz), SHA256 archiwum `ca93588813bcb94a2fc20841902a4097ad8e3b43b6deb59f0a8bdc3c63779470` | Ma właściwe dzielniki 65536/256; starszy parser także ogranicza obsługę długości tekstu i identyfikatorów. Nie rozwiązuje całego wymaganego kontraktu zachowania danych i grupowania. |
| [SexyTopo PocketTopoImporter](https://github.com/richsmith/sexytopo/blob/d918be049252cda972f78c94761ca3c65b583a7f/app/src/main/java/org/hwyl/sexytopo/control/io/thirdparty/pockettopo/PocketTopoImporter.java), commit `d918be049252cda972f78c94761ca3c65b583a7f` | Przydatny niezależny odczyt pól. Import do modelu aplikacji nie zachowuje całego modelu `.top`: używa pierwszego tripu, pomija XSection, a z referencji przenosi komentarze, nie pełne dane współrzędnych. |

TopParser i topreader deklarują GPL-3.0-or-later. Własna implementacja według
specyfikacji oraz porównania wyników nie oznaczają kopiowania kodu dostawcy.
Przed ewentualnym włączeniem jego kodu trzeba zachować właściwe warunki licencji.

Wcześniejszy lokalny eksperyment Shadow w repozytorium `caves_paint` używał
niezmienionego topreader z commitu `25e3e7557d4e8611a5568e019718275a9a32df58`
oraz wrappera korygującego dzielniki. Jest dodatkowym materiałem porównawczym,
ale docelowy skill nie może wymagać tamtego checkoutu. Istotne nowe dowody
natywne są już zachowane [w tym repozytorium](evidence/shadow/README.md).

Wniosek projektowy: własny parser i wspólny model źródłowy, a powyższe narzędzia
oraz PocketTopo jako niezależne porównania. Sam round-trip parser/writer może
odtwarzać ten sam błąd i nie dowodzi zgodności z programem.

## Korpus i zakres odczytu

Lokalne pliki odczytano bezpośrednio według specyfikacji, bez ich modyfikowania:

| Źródło JKTZ | Pomiary | Plan / sideview |
| --- | --- | --- |
| [Kalacka](../../Poligony/D_Bystra/Kalacka/_RAW/01/kalacka.top) | 257 rekordów: 216 z dwoma nazwanymi końcami, 41 anonimowych; 70 serii po 3 i 3 serie po 2; 12 rekordów zerowych | 7 polilinii / 68 punktów; 5 polilinii / 59 punktów |
| [Czarna–Zimna](../../Poligony/D_Koscieliska/Organy/Czarna/_RAW/01/source/Czarna-zimna.top) | 756 rekordów: 714 z dwoma nazwanymi końcami, 42 anonimowe; 238 serii po 3; 1 rekord zerowy; 7 komentarzy | oba szkice puste |

„Seria” oznacza tu zaobserwowane kolejne rekordy tej samej pary w tym samym
tripie, a nie samodzielne rozstrzygnięcie ich pochodzenia. Anonimowe rekordy
obejmują także rekordy zerowe. Oba źródła mają jeden trip z deklinacją 0°,
brak referencji, XSection i flagi flipped. Kalacka ma wyłącznie czarne kreski.

SHA256 lokalnych źródeł:

```text
4fbba274872ee511d90fd4021a84a4d80a3ef46489548deefe8a8b9ff4bb8bc0  kalacka.top
c2bf206c803c7755b1e565d2bf2e5c476510ade8e466a2edcf8302cbb22fd5b2  Czarna-zimna.top
```

Kalacka ma obok archiwalne `.srv` i `.the`, a Czarna tekstowy zrzut pomiarów.
Każdy taki eksport trzeba porównać ze źródłem: samo sąsiedztwo plików nie
potwierdza identycznego zakresu, ustawień ani poprawności konwersji.

Inwentaryzacja [dlubom/test2](https://github.com/dlubom/test2/tree/4c00c008a8dd441d70f9c62aa376c20b5914c7e0)
dla commitu `4c00c008a8dd441d70f9c62aa376c20b5914c7e0` wykazała 262 ścieżki
`.top`, 258 różnych obiektów Git, około 9,2 MB. Dla 259 ścieżek w tym samym
katalogu istnieje także `.svx`, `.th`, `.txt` lub `.dxf`. To inwentaryzacja,
**nie walidacja wszystkich 258 zawartości**.

Zbadano sześć wybranych próbek: mały Kitzgraben z pustymi szkicami, wielobarwny
Shadow, Baltazar ze szkicem i bez niego, Poprzeczna oraz RKM2. W próbkach nie
uzyskano pokrycia wielu tripów, flipped ani XSection. Dla
[RKM2 i sąsiedniego TXT](https://github.com/dlubom/test2/tree/4c00c008a8dd441d70f9c62aa376c20b5914c7e0/495-Interessante/20160720-Na_raty2)
odczyt binarny potwierdził zgodność wszystkich 109 polilinii / 621 punktów
po zmianie mm na m i odwróceniu Y. Niektóre dystanse TXT różnią się jednak
od `.top` o 1 mm; przyczyna pozostaje niewyjaśniona. Wzorzec rysunku nie jest
automatycznie wzorcem pomiarów.

W sprawdzonym drzewie `test2` nie znaleziono LICENSE/COPYING, a API nie podało
licencji. Nie przypisujemy oryginałom licencji JKTZ. Zachowana próbka Shadow
jest dowodem researchu wraz z pochodzeniem; status jej licencji pozostaje
nieustalony. Powtarzalne CI należy oprzeć także na własnych minimalnych
przypadkach, bez pobierania całego zewnętrznego korpusu podczas testów.

## Daty z zegara urządzenia

| Źródło | Data zapisana w trip | Data opisana w README źródeł |
| --- | --- | --- |
| Kalacka | 2005-07-01 | 2013-11-09 |
| Czarna–Zimna | 2011-10-02 | 1972-03-15 |

Użytkownik wyjaśnił, że palmtopy Dell miały słabe baterie podtrzymujące zegar,
więc data trip mogła pochodzić z resetu. Jest poszlaką do zestawienia z innymi
źródłami; sama nie potwierdza daty pomiaru i nie uprawnia do wyliczenia IGRF.
Zachowujemy datę zapisaną, a osobno ustaloną datę pomiaru, źródło ustalenia
i status wiarygodności. Podejrzenie resetu nie upoważnia do automatycznej
zamiany daty np. na datę z nazwy pliku.

Także zapisane 0° deklinacji nie stanowi dowodu historycznej poprawności
korekty. Wierny eksport ustawień źródłowych i integracja pomiaru z aktywnym
JKTZ wymagają rozróżnienia opisanego w PRD. `AGENTS.md` zabrania połączenia
operatywnego `#date` z `DECL`; datę źródłową można zachować w metadanych
lub komentarzu przy eksporcie z jawną korektą.

## Dowód z rzeczywistego PocketTopo

2026-09-25 w **PocketTopo 1.372 przez Wine** otwarto odizolowaną kopię
`shadow.top`, wykonano natywny eksport tekstowy i Graphics: plan oraz sideview
DXF. Pliki, opcje eksportu, dwa obrazy okna, sumy SHA256 i wyniki odczytu
są w [evidence/shadow/README.md](evidence/shadow/README.md).

Sprawdzono wszystkie 32 rekordy TXT oraz strukturę i liczności obu DXF:
plan 191 kresek / 4150 punktów, sideview 48 / 1330. Dwie jednopunktowe kreski
planu są w DXF encjami POINT. **Pełnego audytu współrzędnych, kolorów
i geometrii podkładu DXF jeszcze nie wykonano.** To dowód dostępu do aplikacji
i istnienia niezależnego wzorca, nie ukończenia konwersji ani całej macierzy
przypadków szczególnych.

## Otwarte zagadnienia przed implementacją

- W obydwu lokalnych `.top` oraz Shadow występują cztery końcowe bajty zerowe,
  których nie opisuje dostarczona specyfikacja. Nie uznawać dowolnych końcowych
  danych za bezpieczne do pominięcia; potwierdzić kontrakt nowych zapisów aplikacji.
- Utworzyć w PocketTopo minimalne wzorce dla wielu tripów, ±deklinacji, Flip,
  wszystkich kolorów, XSection, referencji i różnych postaci ID; zachować
  ustawienia i natywne eksporty. Przypadki uszkodzeń zbudować osobno z jawnym
  opisem zmienionych bajtów.
- Sprawdzić podkład rozwinięcia dla rozgałęzień i pętli oraz pomiarów pionowych;
  nie przesuwać oryginalnych kresek, aby dopasować je do własnych obliczeń.
- Zachować oddzielność plain ID `0` i `0.0`; uwzględnić limit 8 znaków Walls
  oraz separator nazw Survex. Referencje `.top` nie deklarują CRS.
- Istniejący helper `average-shots` ma kołową średnią azymutu i normalizację
  przód/tył, lecz obsługuje tekst SRV. Nowa konwersja musi grupować i uśredniać
  model źródłowy przed zaokrągleniem; nie uruchamiać średniej dopiero na
  wygenerowanym tekście. Flipped dotyczy rozwinięcia, nie zamiany FROM/TO.
- Wybrać renderer PNG i ustalić tolerancje porównań, wynikające z precyzji
  zapisu. Osobno sprawdzić zgodność z rzeczywistym Walls.

Kalibracja `.cal` pozostaje poza zakresem tego zadania. Następny etap,
kryteria akceptacji i wymagane testy są zapisane w [PRD](PRD.md).
