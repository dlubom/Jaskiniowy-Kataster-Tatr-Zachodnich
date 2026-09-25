# P03 — potwierdzone średnie i ślad każdego rekordu

**Zakończone 2026-09-25 na `codex/pockettopo-convert`. Następny etap: P04.**

[Ponowna weryfikacja i publikacja](REVALIDATION.md) dokumentuje świeże bramki,
odtworzenie dowodów oraz push istniejących commitów P02/P03 podczas wznowienia.
[Poprawki testów Windows](WINDOWS.md) opisują późniejszy błąd długich nazw
pytest, jawne UTF-8 oraz aktualny zestaw 786 testów (190 P03).

Biblioteka przygotowuje w pamięci dwa dokumenty zgodne z JSON: pełne dane
źródłowe oraz raport przetwarzania. Nie zapisuje plików. Zapis atomowego pakietu
oraz CLI należą do P06; SRV/SVX, mapowanie nazw i polityka użytych korekt do P04;
rysunki do P05. Raport zawsze ma `conversion_complete=false`.

## Użycie

```python
import hashlib
import json
from pathlib import Path

from jktz.pockettopo import ProcessingPlan, RepeatConfirmation, prepare_conversion

path = Path('doc/pockettopo/evidence/p01/cases/api-cardinal/api-cardinal.top')
data = path.read_bytes()
plan = ProcessingPlan(
    source_sha256=hashlib.sha256(data).hexdigest(),
    confirmations=(RepeatConfirmation(
        indices=(4, 5, 6),  # indeksy od zera, wyłącznie ten wzorzec P01
        evidence='P01 helper pockettopo_fixtures.cs:167-169: jawne A1/A2/A3',
    ),),
)
source, report = prepare_conversion(data, plan=plan)
print(json.dumps(report['groups'][4], ensure_ascii=False, allow_nan=False, indent=2))
```

Bez `plan` żaden rekord nie jest uśredniany z innym. `ProcessingPlan` jest
niezmienną dataclass; obejmuje SHA-256 wejścia, `confirmations` i `exclusions`.
`Exclusion(index, reason)` jawnie wyłącza rekord z przygotowanych pomiarów,
lecz zachowuje go w źródle i raporcie. Biblioteka weryfikuje komplet decyzji
przed zwróceniem wyniku. Błędny SHA, indeks, puste uzasadnienie, powtórzone
wyłączenie lub nakładające się grupy kończą się `ValueError`; wadliwy `.top`
pozostaje błędem parsera P02. Nie ma częściowego zapisu.

Treść `evidence` jest twierdzeniem osoby przygotowującej plan; biblioteka
wymaga uzasadnienia, ale nie potrafi poświadczyć jego prawdziwości. Nazwy stacji,
komentarz zawierający słowo „repeat”, kolejność ani podobieństwo D/A/V nie
uruchamiają grupowania. Potwierdzenia są związane z bajtami źródła, więc plan
nie może przypadkiem zadziałać na innym pliku o podobnych nazwach stacji.

## Kontrakt grupowania i klasyfikacji

Każda grupa obejmuje co najmniej dwa kolejne indeksy, znaną identyczną sesję
oraz tę samą parę dwóch nazwanych, różnych stacji. Kolejność FROM/TO może być
odwrotna; pierwszy rekord ustala kierunek. Plain `0` i major.minor `0.0`
pozostają różnymi stacjami dzięki porównaniu surowych identyfikatorów.
Sesja `-1` nie jest potwierdzoną wspólną sesją. Rozdzielona seria, domiar,
zerowe powiązanie, inna para, zmiana sesji lub jawne wyłączenie uniemożliwiają
połączenie przez tę granicę. Plan może jawnie wskazać osobne podgrupy; automat
nie dzieli ani nie rozszerza serii.

- `leg`: dodatni odcinek między różnymi nazwanymi stacjami.
- `splay`: dodatni odcinek z dokładnie jednym niezdefiniowanym końcem;
  jeśli to FROM, normalizacja odwraca go do kierunku od znanej stacji.
- `zero_link`: zerowa długość między różnymi nazwanymi stacjami; kąty zachowane,
  lecz bez wpływu geometrycznego. Nie bierze udziału w grupie średnich.
- `invalid`: ujemna długość, pochylenie poza ±90°, oba końce niezdefiniowane,
  odcinek do tej samej stacji albo zerowy odcinek bez obu nazwanych końców.
  Surowe dane pozostają w `source`, raport podaje przyczynę. Zerowe powiązanie
  stacji z samą sobą nie łączy dwóch punktów i jest jawnie zatrzymane.

Flip nie odwraca D/A/V. Różne wartości Flip wewnątrz grupy pozostają w śladzie
każdego rekordu i wywołują ostrzeżenie do rozstrzygnięcia w P05.

## Matematyka i granice

`averaging.py` przelicza całkowite mm i kąty dopiero w oddzielnej warstwie.
Pełen obrót ma 65536 jednostek; kierunek wsteczny zmienia A o 180° modulo 360
i znak V. D i V to średnie arytmetyczne, A to `atan2(fsum(sin), fsum(cos))`.
Długości nie ważą azymutu. Nie stosujemy średniej wektorów 3D, usuwania
odstających odczytów ani zaokrągleń do precyzji przyszłego pliku tekstowego.

Raport zawiera liczność, długość wypadkowej kołowej `R` w [0,1], największe
odchylenie kołowe od średniej oraz rozstęp D i V (`max-min`). Nieokreślone A
oraz jego odchylenie mają JSON `null`, nigdy NaN. Cała grupa ma wówczas status
`unresolved`; oryginały i odczyty znormalizowane pozostają dostępne.

Domyślny próg to `min_resultant=1e-12`, warunek niejednoznaczności `R <= próg`.
To osłona numeryczna przed pozornym kierunkiem pary 0°/180°, a nie terenowy
próg jakości instrumentu. Wyższy próg można jawnie ustawić; dopuszczalny zakres
to skończone [1e-12, 1), bez wartości bool. Ustawienie zapisuje się w raporcie.
Dokładnie jednakowe kąty modulo 360° mają R=1; nie tracą kierunku przez błąd
`hypot` przy progu bliskim 1. Testy obejmują równość i obie strony granicy.

Piony zachowują V=±90° i źródłowy azymut, z ostrzeżeniem o jego braku znaczenia
geometrycznego. Nie dostają wyjątkowej średniej; potwierdzona grupa pionów
z przeciwnymi azymutami pozostaje `unresolved`. To jawny, ostrożny kontrakt P03.

## Dokumenty i ograniczenia

`source` zawiera wszystkie surowe dataclass P02, oba rysunki, typ każdego
elementu, mapowania i rodzaj końca pliku. Zachowuje integer mm, kąty, roll,
flagi, ID, ticks i komentarze (w tym różnicę `null`/pusty napis). To nie jest
zamiennik oryginalnych bajtów `.top`. Odbiorca JSON musi zachować dokładność
64-bitowych liczb całkowitych; np. ticks nie należy odczytywać przez JS Number.

Raport ma SHA-256 i rozmiar wejścia, wersję pakietu/numer algorytmu, ustawienia,
pełny plan, grupy, kierunki normalizacji i `record_trace` w kolejności źródła.
Każdy rekord trafia dokładnie raz do grupy i śladu, z przyczyną uśrednienia,
pozostawienia osobno, wyłączenia albo zatrzymania. `ready` oznacza tylko gotowe
D/A/V na etapie P03; nie upoważnia do aktywnego eksportu.

Mapa stacji obejmuje pomiary, referencje oraz XSection; zachowuje rodzaj i nazwę
źródłową. Docelowe nazwy Walls/Survex są jawnie `null` (P04). Daty pozostają
niezweryfikowanymi ticks zegara; daty ustalone i użyte są `null`. Zapisane
jawne deklinacje są przeliczone na stopnie, lecz nie zastosowane. Auto pozostaje
nierozstrzygnięte. Referencje mają nieznany CRS i nie tworzą aktywnych fixów.
Puste rysunki mają status `empty`, pozostałe `retained_not_exported`.

## Dowody

- [Przykładowe źródło JSON](api-cardinal/source.json) i
  [raport A1–A3](api-cardinal/conversion-report.json): 11 rekordów, 9 grup,
  średnia **5 m / 0° / 9,99755859375°**, indeksy 4/5/6, trzeci kierunek odwrócony.
  R=0,9995940829335641. Ułamkowe V wynika z kwantyzacji źródła, nie z błędu.
- [Dziewięć wzorców](fixture-checks.json): osobny raport każdego pliku;
  70 rekordów łącznie; 50 rzeczywistych pozostaje osobno, bez potwierdzonych
  średnich (47 gotowych, 3 zatrzymane jako `zero_unnamed_shot`).
- [Pełny korpus](corpus.json): kontrola SHA obiektów Git i rozliczenie każdego
  rekordu: 258 źródeł / 262 ścieżki, 37 801 rekordów, 37 426 gotowych i 375
  zatrzymanych (358 zer bez obu nazwanych końców, 5 dodatnich odcinków do siebie,
  11 z oboma końcami niezdefiniowanymi, 1 pochylenie poza zakresem).
  To kontrola P03, nie dowód dat, powtórzeń ani geometrii eksportów.
- [Bramki repozytorium](repository-checks.json), [quality](quality.json),
  [mutacje](mutation.json) oraz [odtworzenie próby](REPRODUCE.md).

Testy: `tests/test_pockettopo_averaging.py`, `test_pockettopo_grouping.py` i
`test_pockettopo_report.py`. Matematyka i grupowanie są jawnie dodane do zakresu
mutacji, bez usunięcia poprzednich modułów i bez zmiany progów.

| Kontrola | Wynik |
| --- | --- |
| Testy P03 / cały projekt | 189 / 785 zaliczone |
| Pokrycie linii / gałęzi całego projektu | 96,89% / 94,60% |
| Maksymalny CRAP | 21,54 przy limicie 25 |
| Mutacje matematyki / grupowania | 173/182 (95,05%) / 183/183 (100%) |
| Mutacje całego zakresu | 1860/2090 (89,00%), każdy z 9 modułów ≥81% |
| Snapshot GPS | 87 fixów, wydanie v1.0.2, zgodny |
| Oryginały P01 / wzorce rzeczywiste | 55/55 i 21/21 zgodne SHA-256 |

Pierwsza kampania mutacji została prawidłowo odrzucona: dwa mutanty zmieniały
postęp pętli grupowania i kończyły się timeoutem. Testy otrzymały kontrolę
zakończenia małych wejść przez POSIX SIGALRM (błąd asercji po sekundzie,
przywrócenie poprzedniego handlera i timera; na Windows te same testy bez
watchdoga). Świeża pełna kampania nie ma błędów ani wyników niepełnych.
Nie zmieniono kodu produkcyjnego ani progów z powodu samych metryk.
Lista ocalałych mutacji jest zachowana; nie uznano ich zbiorczo za równoważne.
