# Nova Kresanica — model Survex z 2009 r.

- **Status materiału:** częściowy
- **Pochodzenie danych:** Juraj Szunyog przesłał plik 30 października 2013 r.
- **Autorzy pomiarów:** nieustaleni
- **Daty pomiarów:** nieustalone
- **Data pozyskania:** 2026-09-25
- **Dodał do _RAW:** Codex na zlecenie Dariusza Lubomskiego
- **Licencja źródłowa:** nieustalona
- **Kompletność:** Skompilowany poligon. Brakuje pliku pomiarowego Therion i dziennika terenowego.

## Zawartość

- `cave.3d` — model Survex v4 z 21 października 2009 r., 5237 bajtów, SHA-256 `24a17df9a260fbedc9eb48666d4fb48bc5bbcb8786003ede425d374fda5fad8b`.

## Porównanie z pomiarami katastru

Po przypisaniu końcówek nazw stacji (np. `NK_03.28` do `nvk28`) wszystkie
155 odcinków modelu ma odpowiednik w siedmiu SRV. W pętli
`nvk111–112–113–114–115–116–111` współrzędne modelu uwzględniają wyrównanie.
Format v4 nie przechowuje przekrojów LRUD. W 2011 r. przekazano też projekt On Station ze wszystkimi 142 przekrojami. Kolejność kierunków w SRV skorygowano po sprawdzeniu pól CDI i opublikowanych rysunków z numerami stacji. [Porównanie z CDI](../01/README.md)

Plan z 1990 r. i profil partii odkrytych w 2002 r. dokumentują daty prac,
ale nie pozwalają przypisać dnia pomiaru poszczególnym wierszom SRV.
Wpis `#date 2007-01-03` pochodzi z dawnych plików Walls i służy do obliczenia
deklinacji. [Peter Holúbek, *Jaskyniar* 1991, s. 11–12](https://sss.sk/wp-content/uploads/2022/10/Jaskyniar_SSS_1991.pdf)
i [Juraj Szunyog, *Spravodaj SSS* 3/2003, s. 27–29](https://sss.sk/wp-content/uploads/2022/01/Spravodaj_SSS_2003_3.pdf).

Współrzędne geograficzne otworu przekazała w styczniu 2015 r. redakcja
„Jaskiń”. Korespondencja nie podaje metody pomiaru ani wysokości otworu.
W Katastrze stacja `NovaKresanica:nvk0` odpowiada obiektowi GPS `SK-0001`.
