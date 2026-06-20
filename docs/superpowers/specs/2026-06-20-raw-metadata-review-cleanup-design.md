# Uporządkowanie komunikatów i testów metadanych RAW

## Cel

Domknąć dwie uwagi z review PR #119 bez zmiany kontraktu README ani zachowania
parsera metadanych RAW.

## Komunikaty błędów

Diagnostyka pozostaje po angielsku, zgodnie z pozostałymi komunikatami pakietu.
Polskie nazwy pól i sekcji są identyfikatorami kontraktu, dlatego będą ujmowane
w pojedyncze cudzysłowy. Komunikaty mają jednoznacznie rozróżniać nazwę pola,
wartość oraz wymaganie sekcji.

Docelowe formy:

- `duplicate RAW field 'Status materiału'`;
- `missing RAW field(s): 'Licencja źródłowa'`;
- `invalid value for RAW field 'Status materiału': 'wartość'`;
- `section '## Zawartość' must contain at least one item`.

## Testy parsera

Obecny test granicy sekcji pośrednio polega na błędzie pustej sekcji. Zostanie
rozdzielony na dwa niezależne przypadki:

1. test granicy umieszcza prawidłowy element przed `## Uwagi` i element podobny
   do wpisu inwentarza po nagłówku, a następnie sprawdza, że parser zwrócił tylko
   pierwszy element;
2. test pustej sekcji osobno sprawdza wymaganie co najmniej jednego elementu.

## Zakres

Zmiany obejmują `src/jktz/metadata/raw.py`, `tests/test_raw_metadata.py` oraz
asercję komunikatu CLI w `tests/test_srv_metadata_cli.py`. Parser, format README
i reguły walidacji pozostają bez zmian.

