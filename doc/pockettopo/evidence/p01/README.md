# P01 — małe wzorce PocketTopo

**Zakończone 2026-09-25 na `codex/pockettopo-convert`.** Pakiet zawiera sześć
małych źródeł `.top` zapisanych przez PocketTopo 1.372, ich natywne TXT/DXF,
oczekiwania każdego rekordu oraz dowody weryfikacji. Następny etap to **P02**
zgodnie z [PRD](../../PRD.md).

## Pochodzenie i zawartość

Wszystkie pomiary, daty i szkice są syntetycznymi danymi testowymi utworzonymi
na potrzeby JKTZ w tej sesji, na warunkach licencji repozytorium CC BY-SA 4.0.
Nie pochodzą z pomiarów jaskiń ani z korpusu `test2`. Nie zawierają aplikacji
PocketTopo, jej bibliotek ani zdekompilowanego kodu. Wersję i SHA-256 użytego
programu zapisuje [native-api-evidence.json](native-api-evidence.json).

| Katalog | Sposób utworzenia | Przypadek |
| --- | --- | --- |
| [gui-cardinal](cases/gui-cardinal/expected.json) | Ręczne wpisanie w GUI, File → Save As | Jeden odcinek plain `0 → 1`, 10 m na północ, poziomo, bez tripu, puste szkice |
| [gui-colors](cases/gui-colors/expected.json) | Kliknięcia palety i szkicu w GUI, File → Save | 9 pojedynczych punktów planu, wszystkie 7 kolorów, w tym dwa punkty nakładające się; pusty bok |
| [api-cardinal](cases/api-cardinal/expected.json) | Natywny model i serializer aplikacji | N/E/S/W, 358°/2° i odczyt wsteczny, piony, splay, zero, roll |
| [api-trips-ids](cases/api-trips-ids/expected.json) | Natywny model i serializer aplikacji | 3 tripy, ±deklinacja i Auto, ticks z częścią 100 ns, plain/major.minor, UTF-8 i długi prefiks długości, Flip, trip −1 |
| [api-references](cases/api-references/expected.json) | Natywny model i serializer aplikacji | Signed E/N Int64 poza zakresem Int32, ujemne Z; bez założenia CRS |
| [api-drawings](cases/api-drawings/expected.json) | Natywny model i serializer aplikacji | W obu widokach otwarte kreski 7 kolorów, singleton, 2 XSection, Flip, różne Mapping |

`api-*` powstały przez wywołanie rzeczywistych obiektów i metod PocketTopo,
nie przez własny writer `.top`. [Helper C#](../../helpers/pockettopo_fixtures.cs)
ma jawne wejścia; [NATIVE_API.md](NATIVE_API.md) opisuje reprodukcję i granice
tej metody. Dwa `gui-*` stanowią dodatkowe źródło niezależne od helpera.

Każdy katalog zawiera oryginał `.top`, `native.txt`, oba natywne DXF oraz
`expected.json`. `.top`, TXT i DXF są chronione przez `.gitattributes` przed
normalizacją końców linii. W API `native.txt` wywołuje `Survey.WriteText`,
w GUI eksport Text dodaje jeszcze nagłówek nazwy pliku.

## Sprawdzenie w rzeczywistym GUI

Użyto działającej instalacji PocketTopo 1.372 przez Wine Staging 11.7.
Procedura bazowa: [POCKETTOPO_MACOS.md](../../POCKETTOPO_MACOS.md).

1. `gui-cardinal`: New Cave, tabela `0 / 1 / 10 / 0 / 0`, Save As. Nowy
   projekt pokazywał początkowo zerowy rekord; zastąpiono go tym jednym odcinkiem.
   Zapis ma 78 bajtów, zero tripów i `tripIndex=-1`.
2. `gui-colors`: osobny Save As tego odcinka, następnie pojedyncze kliknięcia
   kolorów. Finalny zapis ma 9 punktów, nie siedem polilinii. Próby wyboru
   koloru/Undo zostawiły dwa gray i dwa green; zachowano końcowy stan źródła,
   łącznie z green/orange w tym samym miejscu. Dokładny wynik i kolejność są
   w oczekiwaniach. Precyzyjne punkty ustalone przed zapisem ma `api-drawings`.
3. Dla obu GUI przypadków wykonano Menu → Export → Text oraz Graphics.
   Zachowano zrzuty tabeli/planu i ustawień Graphics. Finalne źródła po
   eksporcie mają niezmienione SHA-256.
4. Każdy `api-*` otwarto również w GUI z izolowanej kopii w osobnym katalogu.
   Wszystkie cztery aplikacja przyjęła. `api-cardinal`, `api-trips-ids`
   i `api-references` mają dodatkowy `native-ui.txt` oraz `ui-table.png`.
   Zrzuty pokazują widoczny fragment tabeli, nie zastępują pełnego odczytu.
5. Dla `api-drawings` zachowano `ui-plan.png`, `ui-side.png`, opcje Graphics
   i `native-uiP.dxf`/`native-uiS.dxf`. Oba DXF z GUI są **identyczne bajtowo**
   z `native-plan.dxf`/`native-side.dxf` wywołanymi przez API. Po kontroli
   wszystkie cztery kopie `.top` były nadal identyczne z oryginałami.

Eksport Graphics: Write Plan/Side, suffix P/S, 1:500, Shots/Xsections oraz
Separate Layers włączone; Labels/Grid/All Data/All Colors wyłączone.
Katalogów nie łączono: aplikacja wczytuje sąsiednie pliki `.top`.
Automatyczne kopie robocze `backup/` nie należą do zamrożonych wzorców.

## Wyniki i decyzje

- [Oczekiwania i audyt](EXPECTATIONS.md): 6 tripów, 20 pomiarów, 2 referencje,
  53 wierzchołki i 4 XSection. Sprawdzono każde pole źródła oraz wszystkie
  157 encji w 12 głównych DXF, z pełnymi współrzędnymi, kolorami i kolejnością.
  Dane maszynowe: [validation.json](validation.json).
- [Koniec pliku i Auto](NATIVE_API.md): 1.372 zapisuje dodatkowe Int32 `0`;
  natywny reader ignoruje dowolny sufiks. P02 dopuszcza tylko dokładne EOF
  po schemacie albo cztery zera. Deklinacja `-32768` jest trybem Auto.
- [Renderer PNG](renderer/README.md): resvg 0.48.1, rzeczywiste próby macOS
  arm64 i Linux amd64/Ubuntu 24.04, PNG identyczne bajtowo w obu skalach.
  To sprawdzenie działania na Linux, nie uruchomienie GitHub Actions.
- [Bramki repozytorium](repository-checks.json): Python 3.12, 385 testów,
  linie 96,08%, gałęzie 93,40%, maksymalny CRAP 21,54;
  mutacje 832/985 (84,47%), każdy objęty moduł powyżej 81%.

P01 dostarcza wzorce dla kolejnych etapów. Ogólna projekcja XSection z domiarami,
pętle/rozgałęzienia, implementacja parsera i średnich, integracja renderera oraz
CLI/skill pozostają w P02–P06. Natywny algorytm uśredniania DXF różni się od
kontraktu PRD i nie staje się jego zamiennikiem. Korpus 258 plików i pełny
audyt Shadow pozostają osobnymi zadaniami dalszych etapów.

## Kontrola integralności i wznowienie

[manifest.json](manifest.json) zawiera rozmiary, SHA-256, role i pochodzenie
plików dowodowych. Lista obejmuje binaria, eksporty, oczekiwania i wyniki JSON;
pomija Markdown oraz siebie i `SHA256SUMS`. Nie normalizować oryginałów.

Z katalogu tego pakietu:

```sh
shasum -a 256 -c SHA256SUMS
```

W P02 traktować `.top` i `expected.json` jako zamrożone pary wejście/oczekiwanie.
Parser ma czytać wartości surowe, w tym ticks bez float i rozróżnione rodzaje
ID. Uszkodzenia tworzyć z kopii z opisem zmienionych bajtów; nie modyfikować
oryginałów, aby dopasować je do implementacji. Odtworzenie natywnych wzorców
i renderera jest opisane lokalnie w linkowanych dokumentach i nie wymaga
zachowania plików roboczych z `/tmp`.
