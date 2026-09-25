# PocketTopo: resvg 0.48.1

Konwerter wymaga **resvg CLI dokładnie 0.48.1**. Program nie jest częścią
repozytorium. Pobierz archiwum dla swojego systemu z
[przypiętego wydania](https://github.com/linebender/resvg/releases/tag/v0.48.1).
Sumę archiwum sprawdź przed rozpakowaniem, a sumę programu przed jego
uruchomieniem. Poniższe SHA-256 pochodzą z
[archiwalnego manifestu weryfikacji](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/blob/3e3daa4156c6e6e79dce5203d8bb8e36122d571f/doc/pockettopo/evidence/p01/renderer/manifest.json).

| Platforma i pobranie | SHA-256 archiwum | SHA-256 rozpakowanego `resvg` |
| --- | --- | --- |
| [macOS arm64 ZIP](https://github.com/linebender/resvg/releases/download/v0.48.1/resvg-macos-aarch64.zip) | `06440eb5aa14a28cbfc7e40ae39e1ffa71adc051b89fbaa913b4f1d9b905d09f` | `50e57a945189f74ee89766a2d5b8e1a8e5254416880f9e57b36d1307e71e94ce` |
| [Linux x86_64 tar.gz](https://github.com/linebender/resvg/releases/download/v0.48.1/resvg-linux-x86_64.tar.gz) | `fa8c26495a187e592c501db15bf9e8a9fdc051d4b2b336b39703d5b59f912b9d` | `8d1dbe4d8e56d3d052668afc69d9d93fba7b723b06f1d3425f29418da9a816af` |

Na macOS oblicz hash poleceniem `shasum -a 256 /path/to/file`, a na Linux
`sha256sum /path/to/file`, i porównaj cały wynik z odpowiednią kolumną.
Rozpakuj ZIP przez `unzip`, a tar.gz przez `tar -xzf`, do osobnego katalogu.
Po sprawdzeniu obu sum:

```sh
export RESVG=/path/to/resvg
"$RESVG" --version
```

Oczekiwana wersja to `0.48.1`. CLI przyjmuje też ścieżkę w `--resvg`;
bez niej używa `RESVG`, a następnie programu `resvg` z `PATH`.
[Akcja CI](../../.github/actions/install-resvg/action.yml) pobiera program
Linux i automatycznie sprawdza obie powyższe sumy. Inne platformy nie mają
w tym dokumencie zweryfikowanych archiwów.

## Sprawdzenie wzorca PNG

Po ustawieniu `RESVG` uruchom z katalogu głównego repozytorium:

```sh
pockettopo_probe=tests/fixtures/pockettopo/p01/renderer
pockettopo_render=$(mktemp -d "${TMPDIR:-/tmp}/jktz-resvg-probe.XXXXXX")
"$RESVG" --skip-system-fonts --dpi 96 --width 480 --height 320 \
  --background '#ffffff' "$pockettopo_probe/renderer-probe.svg" "$pockettopo_render/1x.png"
"$RESVG" --skip-system-fonts --dpi 96 --width 960 --height 640 \
  --background '#ffffff' "$pockettopo_probe/renderer-probe.svg" "$pockettopo_render/2x.png"
cmp "$pockettopo_probe/renderer-probe-macos.png" "$pockettopo_render/1x.png"
cmp "$pockettopo_probe/renderer-probe-2x-macos.png" "$pockettopo_render/2x.png"
```

Oba `cmp` powinny zakończyć się kodem 0. Wzorzec bada otwarte polilinie,
kolory, osie, skalę, pojedynczy punkt i marginesy, bez fontów systemowych.
To syntetyczna próba renderera; nie potwierdza geometrii PocketTopo ani
historycznej poprawności danych. Przy zmianie wersji najpierw sprawdź
oczekiwania, zamiast automatycznie podmieniać PNG.

Bieżące testy renderingu są w
[test_pockettopo_drawings.py](../../tests/test_pockettopo_drawings.py).
Szczegóły historycznej próby macOS/Linux pozostają w
[archiwum renderera](https://github.com/dlubom/Jaskiniowy-Kataster-Tatr-Zachodnich/blob/3e3daa4156c6e6e79dce5203d8bb8e36122d571f/doc/pockettopo/evidence/p01/renderer/README.md).
