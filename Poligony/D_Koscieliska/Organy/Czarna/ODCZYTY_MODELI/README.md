# Niezależne wyniki odczytu modeli

Otrzymano od użytkownika i porównano 2026-09-13. Pliki skopiowano bez zmian
z `/Users/dariuszlubomski/Downloads`. To transkrypcje modeli do kontroli,
nie oryginalne pomiary; dlatego znajdują się poza `_RAW`.
Zachowano także końcową pustą linię Flasha, zgłaszaną przez `git diff --check`;
jej usunięcie zmieniłoby kopię i hash otrzymanego pliku.

| Plik | Oznaczenie podane przez użytkownika / nazwę pliku | SHA-256 |
| --- | --- | --- |
| [gemini_flash_3.8.md](gemini_flash_3.8.md) | Gemini Flash; `3.8` występuje w nazwie pliku | `833a1ce314c7ac98e563486e5b0e8b15a7399368dae249d6c7423e70fa844672` |
| [gemini_pro.md](gemini_pro.md) | Gemini Pro; dokładna wersja nie została podana | `f425823de05cb431400014dc31141f9604bd4f8fbd8cd121eae3af5f34f86e63` |

Nie mamy logów wykonania, konfiguracji modeli ani potwierdzenia dokładnego
promptu faktycznie użytego w obu sesjach. Użytkownik opisał je jako dwa
niezależne odczyty. Przekazany wcześniej prompt prosił o przepisanie tabel
do Markdown, zachowanie znaków i dopisków, oznaczenie niepewności oraz
powstrzymanie się od poprawiania rachunków i obliczania braków.

Oba wyniki numerują zdjęcia 1/2/3, bez oryginalnych nazw. Z zawartości wynika,
że 1 i 2 dotyczą rozkładówki 0–19, 60–76 i 6–a–b (`123052`/`123533`),
a 3 — rozkładówki 19–60 (`123630`). Dokładnej kolejności dwóch pierwszych
fotografii nie można potwierdzić z samych Markdownów. Pro wprost deklaruje
identyczność transkrypcji 1 i 2; nie są to dodatkowe niezależne odczyty.

[POROWNANIE.json](POROWNANIE.json) zachowuje różnice pierwszych wartości
D/A/V względem `CZ_GL_R.SRV` z commitu
`b36d312a9b551116ce983aff976815df8320e59f`, numery linii i literalne pola
z alternatywami. To zamrożony punkt odniesienia sprzed ponownego odczytu,
nie porównanie z każdą przyszłą wersją SRV. Plik bazowy odtworzysz przez:

```sh
git show b36d312:Poligony/D_Koscieliska/Organy/Czarna/CZ_GL_R.SRV
```

Metoda: wykryto wiersze z dwiema nazwami punktów, odczytano pierwsze liczby
w kolumnach A/V/D i zachowano niepewne pola. Kreskę azymutu pionu
znormalizowano do braku wartości. Powtórki z dwóch fotografii złożono dopiero
po sprawdzeniu zgodności ich głównych D/A/V. Rozbieżność z wersją bazową
nie oznacza automatycznie błędu modelu. Rozstrzygnięcia ze skanów i ograniczenia
zawiera [raport porównania](../POROWNANIE_GEMINI.md).
