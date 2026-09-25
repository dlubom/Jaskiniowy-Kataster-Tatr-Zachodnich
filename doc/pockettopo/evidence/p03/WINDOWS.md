# P03 — poprawki przenośności testów na Windows

Kontrola CI po publikacji wykazała dwa błędy w testach P02/P03. Kod parsera,
grupowania, matematyki i raportowania oraz wzorce źródłowe pozostały bez zmian.

## Identyfikatory parametrów pytest

[Log zadania Windows dla `3a81b19`](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/actions/runs/36138766046/job/108083140878)
pokazał błąd ustawiania `PYTEST_CURRENT_TEST` w teście granic varint:

```text
test_string_length_counts_utf8_bytes_across_varint_boundaries[...]
os.environ[var_name] = value
ValueError: the environment variable is longer than 32767 characters
```

Pytest umieszczał całą wartość tekstową parametru w nazwie testu. Sześć nazw
miało długości 96, 223, 480, 16 479, 49 248 i 2 097 248 znaków. Długie nazwy
powodowały błędy obsługi testu i ogromne logi zamiast krótkiego przebiegu.

Dodano jawne identyfikatory opisujące kodowanie i liczbę bajtów. Najdłuższa
nazwa tej grupy ma teraz 109 znaków. Zachowano wszystkie sześć wejść, w tym
tekst długości 2 MiB; nie zmniejszono zakresu ani limitów parsera.
Ponowna kolekcja całego zestawu nie zawiera nazw przekraczających limit Windows.

## Kodowanie wzorców JSON

Trzy odczyty `read_text()` w `test_pockettopo_report.py` korzystały z domyślnego
kodowania systemowego. Odczyt wzorców UTF-8 jako cp1252 zmieniał komentarz
`Unicode trip: Zażółć gęślą jaźń`, podczas gdy parser poprawnie zwracał Unicode.
Każdy z tych odczytów ma teraz jawne `encoding="utf-8"`.

Regresja `test_native_oracle_keeps_unicode_with_a_cp1252_default` wymusza
cp1252 tylko dla odczytów bez podanego kodowania. Przed poprawką zawiodła
na treści komentarza, po poprawce przechodzi. Nie zależy od lokalnego UTF-8 mode.
To osobno odtworzony błąd przenośności, nie wniosek z samego czasu trwania CI.

## Walidacja i postęp

Wyniki i hashe: [windows-portability.json](windows-portability.json).
Testy P03: 190 zaliczonych; cały projekt: 786 zaliczonych. Bramka jakości
zachowuje 96,89% linii / 94,60% gałęzi i maksymalny CRAP 21,54.
Nie zmieniono progów ani zakresu bramek.
Świeża kampania mutacji: 1860/2090 (89,00%), każdy z dziewięciu modułów ≥81%,
bez wyników niepełnych. Dokumenty quality/mutation są identyczne z poprzednimi
raportami; nowy wynik przypięto do aktualnych hashy testów.

Nieaktualne przebiegi `36138146777` i `36138766046` przerwano po odczytaniu
błędu Windows; ich poprawne joby Linux nie stanowią dowodu przejścia całego CI.
Końcowy przebieg poprawionej rewizji należy sprawdzić po pushu w PR #129.
P03 pozostaje zakończone; następny etap to P04.
