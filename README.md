🇵🇱 **Polski** | [🇬🇧 English](README.en.md) | [🇸🇰 Slovenčina](README.sk.md)

# Jaskiniowy Kataster Tatr

![Walls 2D screen](doc/walls_2d_screen.png)
![Walls 2D screen](doc/walls_3d_screen.png)
![Survex Aven](doc/Survex.jpeg)

[![Latest Release](https://img.shields.io/github/v/release/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich)](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/releases/latest)

[Pobierz najnowsze wydanie](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/releases/latest)

[Model 3D online](https://dlubom.github.io/Jaskiniowy-Kataster-Tatr-Zachodnich/)

### Opis projektu
Projekt ma na celu zgromadzenie w jednym miejscu wszystkich danych kartograficznych dotyczących tatrzańskich jaskiń. Wykorzystując oprogramowanie Walls, głównym celem jest stworzenie zestawienia przestrzennego ciągów pomiarowych, współrzędnych wejść do jaskiń oraz modelu terenu. Projekt jest otwarty dla wszystkich zainteresowanych, by ułatwić działania eksploracyjne, edukacyjne oraz wspierać badania naukowe. Zebranie kompleksowych i dokładnych danych stanowi wyzwanie ze względu na różnorodność metod i czasu ich wykonania.

### Uzupełniające zbiory danych

Kataster obejmuje obiekty, dla których dostępne są dane pomiarowe. Uzupełniają go dwa powiązane zbiory obejmujące także obiekty, których nie ma jeszcze w tym repozytorium:

- [GPS Kataster Obiektów Tatr](https://github.com/dlubom/gps-kataster-obiektow-tatr) — baza lokalizacji GPS otworów jaskiń i innych obiektów terenowych. Ten projekt korzysta z publikowanych w niej najlepszych pomiarów GPS do wyznaczania współrzędnych wejść. Gotowe dane GIS i terenowe można pobrać z [najnowszego wydania](https://github.com/dlubom/gps-kataster-obiektow-tatr/releases/latest).
- [Georeferencer](https://github.com/dlubom/Georeferencer) — georeferencjonowane skany planów jaskiń w formacie GeoTIFF, obejmujące również obiekty bez danych pomiarowych w tym katastrze. Gotową paczkę GeoTIFF można pobrać z [najnowszego wydania](https://github.com/dlubom/Georeferencer/releases/latest).

Projekt oparty jest o oprogramowanie Walls – tutaj znajdziesz [najnowszą wersję programu](https://github.com/wallscavesurvey/walls/releases)  oraz [instrukcję obsługi](http://texasspeleologicalsurvey.org/Walls/tsswalls.htm).

Projekt działa również w [Survex](https://survex.com/) — wystarczy zainstalować najnowszą wersję i wczytać plik `KATASTER.wpj` w programie Aven lub skompilować z linii poleceń: `cavern KATASTER.wpj`. W Aven można też wczytać model terenu `Powierzchnia/Survex/N49E019_VF1.hgt`.

### Jak można pomóc?
Zachęcamy do współpracy przy projekcie oraz do udostępniania własnych pomiarów. Kontakt: [darek.lubomski@gmail.com](mailto:darek.lubomski@gmail.com).

Instrukcje przygotowania środowiska dla nowych developerów i agentów znajdują
się w [CONTRIBUTING.md](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/blob/master/CONTRIBUTING.md). Po sklonowaniu repozytorium rozpocznij
od `python scripts/initial-setup.py`.

### Licencja
[Creative Commons Attribution-ShareAlike 4.0](http://creativecommons.org/licenses/by-sa/4.0/).

### Zawartość projektu
Aktualna lista jaskiń zawartych w projekcie znajduje się w pliku [Lista Jaskiń](LISTA_JASKIN.md).

### Pokrewne projekty
Warto wspomnieć o projekcie [Caves of the Tatra Mountains](https://github.com/RadostW/jaskinie) prowadzonym przez Speleoklub Warszawski. Stosują oni odmienną filozofię — bazują na własnych pomiarach terenowych wykonywanych współcześnie, a nie na pozyskiwaniu danych z historycznych źródeł. Wykorzystują również wtórną digitalizację planów jaskiń, bez informacji o głębokości. To ciekawe podejście, choć pomierzenie w ten sposób wszystkich tatrzańskich jaskiń będzie dużym wyzwaniem. Projekt korzysta z formatu Survex i jest udostępniany na licencji CC BY-SA 4.0.

### Historia zmian
Wszystkie zmiany w projekcie są dokumentowane w pliku [CHANGELOG.md](CHANGELOG.md).

### Pliki źródłowe `_RAW/`
Paczka ZIP z wydania nie zawiera katalogów `_RAW/` z oryginalnymi plikami źródłowymi pomiarów. Służą one do weryfikacji i archiwizacji danych. Aby je uzyskać, sklonuj repozytorium lub pobierz [branch master](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/archive/refs/heads/master.zip).
