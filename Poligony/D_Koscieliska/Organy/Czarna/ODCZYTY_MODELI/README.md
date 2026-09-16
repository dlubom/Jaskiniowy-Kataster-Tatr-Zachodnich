# Niezależne wyniki odczytu modeli

Wyniki Gemini porównano 2026-09-13, a wynik Claude Opus 5 — 2026-09-16.
Pliki otrzymano od użytkownika i skopiowano bez zmian
z `/Users/dariuszlubomski/Downloads`. To transkrypcje modeli do kontroli,
nie oryginalne pomiary; dlatego znajdują się poza `_RAW`.
Zachowano także końcową pustą linię Flasha, zgłaszaną przez `git diff --check`;
jej usunięcie zmieniłoby kopię i hash otrzymanego pliku.

| Plik | Oznaczenie podane przez użytkownika / nazwę pliku | SHA-256 |
| --- | --- | --- |
| [gemini_flash_3.8.md](gemini_flash_3.8.md) | Gemini Flash; `3.8` występuje w nazwie pliku | `833a1ce314c7ac98e563486e5b0e8b15a7399368dae249d6c7423e70fa844672` |
| [gemini_pro.md](gemini_pro.md) | Gemini Pro; dokładna wersja nie została podana | `f425823de05cb431400014dc31141f9604bd4f8fbd8cd121eae3af5f34f86e63` |
| [claude_opus_5.md](claude_opus_5.md) | Claude Opus 5 — oznaczenie podane przez użytkownika | `493f7a5548f52aa8b1e9fd5edc4105b15136a5bcf9ba8f121c76df0d03b15897` |

W przypadku obu wyników Gemini nie mamy logów wykonania, konfiguracji modeli
ani potwierdzenia dokładnego promptu faktycznie użytego w obu sesjach. Użytkownik opisał je jako dwa
niezależne odczyty. Przekazany wcześniej prompt prosił o przepisanie tabel
do Markdown, zachowanie znaków i dopisków, oznaczenie niepewności oraz
powstrzymanie się od poprawiania rachunków i obliczania braków.

Oba wyniki Gemini numerują zdjęcia 1/2/3, bez oryginalnych nazw. Z zawartości wynika,
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

## Claude Opus 5

Oryginalny plik w Downloads: `transkrypcja_dziennik_Czarna.md`. Nazwa kopii
w tym katalogu służy identyfikacji; treść zachowano bajt w bajt. Nie otrzymano
logu sesji, identyfikatora modelu ani faktycznie użytego promptu. Etykieta
modelu pochodzi wyłącznie od użytkownika.

[POROWNANIE_OPUS.json](POROWNANIE_OPUS.json) zawiera zamrożone porównanie
D/A/V oraz Lh/Δh do `CZ_GL_R.SRV` z `fc33499bc127d784e8e0638ad3e45af9a3d85834`,
przed korektą komentarza Lh20→21. Zapisano SHA-256 źródeł, numery linii,
literalne pola D/A/V, alternatywy i porównanie z wcześniejszymi wynikami.
Ścieżki wejściowe są względem katalogu Czarnej. Bazę odtworzysz przez:

```sh
git show fc33499:Poligony/D_Koscieliska/Organy/Czarna/CZ_GL_R.SRV
```

Wynik ma 115 wierszy, 78 unikalnych par i 37 powtórek z drugiego zdjęcia;
pierwsze wartości powtórek są zgodne. W porównaniu pominięto sumy i uwagi
marginesowe; kreskę azymutu pionu znormalizowano do braku wartości.
Liczby po `[?]` zachowano jako alternatywne odczyty danej kolumny.
[Raport Opusa](../POROWNANIE_OPUS.md) oddziela rozbieżności od kontroli źródła
i opisuje jedyną przyjętą korektę: komentarz Lh, bez zmiany D/A/V.
