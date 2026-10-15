# PocketTopo Exporter

Do odczytu i eksportu TOP używaj gotowego
[`pockettopo-exporter`](https://github.com/dlubom/pockettopo-exporter).

Pobierz [ZIP v1.0.1](https://github.com/dlubom/pockettopo-exporter/releases/tag/v1.0.1)
dla swojego systemu i architektury. Sprawdź `SHA256SUMS`, rozpakuj pakiet
poza `_RAW` i przeczytaj dołączone `QUICKSTART.md`. Program działa bez Go,
Pythona, Wine i PocketTopo. Na macOS/Linux uruchamiaj `./pockettopo-exporter`,
a w Windows `./pockettopo-exporter.exe`; można też dodać program do PATH.

Inspekcja, eksporty SRV/SVX i rysunki są opisane w
[pockettopo-convert](../../.agents/skills/pockettopo-convert/SKILL.md).
Opcje używanej wersji pokazuje `pockettopo-exporter --help`.

CI pobiera binaria v1.0.1 z przypiętymi SHA-256 przez
[install-pockettopo-exporter](../../.github/actions/install-pockettopo-exporter/action.yml).
Do testów lokalnych ustaw `POCKETTOPO_EXPORTER` na ścieżkę programu
lub dodaj go do PATH, następnie uruchom:

```sh
uv run pytest -q tests/test_pockettopo_binary.py
```

`JKTZ_REQUIRE_POCKETTOPO_EXPORTER=1` wymusza obecność binarium, tak jak w CI.
