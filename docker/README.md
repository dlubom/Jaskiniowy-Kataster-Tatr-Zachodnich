# Docker — lokalne generowanie eksportow

Buduje Survex ze źródeł i uruchamia ten sam proces eksportu co GitHub Actions,
generując lokalnie pliki `.3d`, `.dxf`, `.shp` i `.err`.

## Pliki

Dwa warianty obrazu Survex — wybierz jeden:

**`Dockerfile.survexImage-release`** — buduje Survex z oficjalnego archiwum wydania (tarball z `survex.com`). Wariant **stabilny**, zalecany do generowania oficjalnych eksportów wydania.

**`Dockerfile.survexImage-commit`** — buduje Survex z konkretnego commita w repozytorium `ojwb/survex` (zmienna `SURVEX_COMMIT`). Wariant do testowania niewydanych jeszcze poprawek lub funkcji rozwojowych.

Oba pliki tworzą obraz pod tym samym tagiem `jktz-survex` i zawierają komplet bibliotek uruchomieniowych (`libproj`, `libgdal`, `ogr2ogr`). Obraz jest jednoetapowy (~1 GB) — `survexport` linkuje się do GTK3/wxWidgets, więc lean multi-stage nie jest możliwy.

**`exports.sh`** — uruchamiany wewnątrz kontenera; odwzorowuje proces eksportu z `release.yml`. Wyniki trafiają do `exports/JKTZ-<WERSJA>/` w katalogu glownym repozytorium.

## Uzycie

Wszystkie polecenia wykonuj z **katalogu glownego repozytorium**.

### 1. Zbuduj obraz (jednorazowo)

Wariant stabilny (release tarball) — domyślny:

```bash
docker build -f docker/Dockerfile.survexImage-release -t jktz-survex .
```

Wariant z commita (rozwojowy):

```bash
docker build -f docker/Dockerfile.survexImage-commit -t jktz-survex .
```

Pierwsze budowanie trwa dłużej. Wynik jest cache'owany — kolejne budowania są natychmiastowe, chyba ze zmieni się `SURVEX_VERSION` / `SURVEX_COMMIT`.

### 2. Uruchom eksport

```bash
docker run --rm -v "$(pwd):/project" jktz-survex bash docker/exports.sh v1.2.6
```

Podmień `v1.2.6` na dowolna etykietę wersji.

Wyniki pojawią się w `exports/JKTZ-<WERSJA>/` w folderze repozytorium:

```
exports/
  JKTZ-v1.2.6/
    JKTZ-v1.2.6.3d
    JKTZ-v1.2.6.dxf
    JKTZ-v1.2.6-all.shp
    JKTZ-v1.2.6-cavern-log.txt
    JKTZ-v1.2.6.err
    caves/
      tc1601.shp
      ...
  JKTZ-v1.2.6-exports.zip
```

### 3. Jednorazowe polecenia Survex

Obrazu można tez uzyć do uruchamiania pojedyńczych narzędzi Survex:

```bash
docker run --rm -v "$(pwd):/project" jktz-survex cavern KATASTER.wpj
docker run --rm -v "$(pwd):/project" jktz-survex survexport --legs --dxf KATASTER.3d out.dxf
```
