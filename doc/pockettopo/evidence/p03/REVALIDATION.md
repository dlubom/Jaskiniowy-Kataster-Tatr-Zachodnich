# Ponowna weryfikacja i publikacja P03 — 2026-09-25

Przy wznowieniu `codex/pockettopo-convert` drzewo robocze było czyste.
P02 (`62047ee3e53a6fbca6ebce488c5d4e446059b0da`) oraz P03
(`f86a9e3e2563efe794fa99a2a1086b2dd1872e9e`) były już zatwierdzone lokalnie,
lecz nieobecne na `origin`. Pierwszy push opublikował oba commity po poprawnym
przejściu hooka `jktz-validate`, obejmującego kompilację cavern i eksporty GDAL.

Zakres wznowienia to sprawdzenie ukończonego P03 i zapis świeżych dowodów.
Nie było potrzeby ponownej implementacji. Następnym etapem pozostaje P04;
daty, korekty, CRS i ograniczenia eksportu mają status opisany w [README](README.md).

## Kontrole lokalne

Python 3.12.13. Polecenia wykonano ponownie na kodzie commita `f86a9e3`:

| Kontrola | Wynik |
| --- | --- |
| `uv run --python 3.12 jktz-quality` | 785 testów; 96,89% linii, 94,60% gałęzi; maks. CRAP 21,54 |
| `uv run --python 3.12 jktz-mutation` | 1860/2090 (89,00%); każdy z dziewięciu modułów ≥81%; brak błędów i wyników niepełnych |
| `uv run --python 3.12 jktz-render-otwory --check` | 87 fixów zgodnych z wydaniem GPS v1.0.2 |
| Hash kodu, testów i konfiguracji P03 | Wszystkie 13 zgodne z `repository-checks.json` |
| Świeże `quality.json` i `mutation.json` | Dokładnie te same dokumenty JSON co zapisane dowody P03 |

Pierwsza próba uruchomienia mutacji zatrzymała się przed testami na blokadzie
cache uv przez sandbox. Ponowienie z dostępem do cache wykonało całą świeżą
kampanię; nie użyto wyniku z cache mutmut i nie zmieniono progów bramek.

## Odtworzenie i przegląd

Szczegółowy wynik odtworzenia zapisano w [revalidation.json](revalidation.json).
Procedurę z [REPRODUCE.md](REPRODUCE.md) uruchomiono z katalogiem wynikowym
w `/private/tmp`, a wyniki porównano z wersjonowanymi dowodami. W raporcie
korpusu pominięto wyłącznie `jktz_base_commit`, który rejestruje rewizję
uruchomienia, a nie treść danych. Oryginałów ani poprzednich raportów nie
nadpisano.

Zgodne są wszystkie 12 dokumentów: 11 bajtowo, korpus po pominięciu wyłącznie
wspomnianej rewizji. Dziewięć wzorców rozlicza 70 rekordów; korpus 258 źródeł
i 262 ścieżek rozlicza 37 801 rekordów (37 426 gotowych, 375 zatrzymanych
z przyczyną). Sumy SHA-256 wzorców pozostają zgodne: 55/55 oraz 21/21.

Niezależny przegląd kodu i 189 testów P03 nie wykazały usterek wymagających
poprawki. Dodatkowe próby objęły wszystkie 65 536 surowych azymutów (pojedyncze
odczyty i pary przeciwstawne) oraz 5000 deterministycznie losowanych grup:
zgodność D/V ze wzorcem wymiernym i niezmienniki odwrócenia kierunku.
Największa różnica D wynosiła 1 ULP, zgodnie z precyzją float.

Wyniki lokalne odnoszą się do wskazanego commita. Wyniki GitHub Actions są
dostępne przy [PR #129](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/pull/129);
kontrola końcowego SHA po kolejnym pushu jest osobnym krokiem dostarczenia.
