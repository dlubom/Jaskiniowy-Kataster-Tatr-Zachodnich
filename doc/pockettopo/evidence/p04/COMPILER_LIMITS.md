# Granice kompilacji: ostrzeżenia, niepełna geometria i błędna sieć

Eksporter P04 zachowuje rekordy i jawnie zwraca `validation=not_run_by_library`.
Nie sprawdza spójności całej sieci i nie naprawia topologii. Wynik API to tekst
pomiarów oraz raport; powodzenie eksportu nie gwarantuje udanej ani kompletnej
kompilacji w zewnętrznym programie.

Próby poniżej wykonano w **cavern 1.4.22** na macOS. Są to celowo syntetyczne
wejścia utworzone helperem testowym, nie źródła terenowe ani nowe wzorce natywnego
PocketTopo. Każdy katalog w `compiler-limits/` zawiera dokładne `input.top`,
`source.json`, `conversion-report.json`, `survey.SRV`, `survey.svx` i pełne
wyjście procesów. [compiler-limits.json](compiler-limits.json) podaje skróty
wejść i tekstów, wersję oraz status każdego procesu.

- **Dwie odłączone składowe**: `0→1` oraz `2→3`, po 1,234 m na północ.
  Oba formaty kończą się kodem 0 i ostrzeżeniem
  `Survey not all connected to fixed stations`. `dump3d` zawiera tylko stacje
  0/1 i jeden wektor; składowa 2/3 nie trafia do geometrii `.3d`.
- **Zatrzymany łącznik Auto**: `0→1`, `1→2` z trybem Auto bez rozstrzygnięcia,
  `2→3`. Eksporter prawidłowo zatrzymuje środkowy rekord, co pozostawia dwie
  składowe. W obu formatach występuje to samo ostrzeżenie i pominięcie 2/3.
- **Dwa niezależne początki domiarów**: po jednym domiarze ze stacji 0 i 2.
  Kompilator zgłasza odłączenie i pomija drugą składową.
- **Sprzeczność bezpośrednia**: `0→1` o długości 1,234 m i zerowe powiązanie
  `0=1`. Oba teksty kończą proces sygnałem SIGSEGV (kod procesu −11).
- **Sprzeczność przez trzeci punkt**: `0→1` o długości 1,234 m oraz zerowe
  powiązania `0=2` i `2=1`. Oba teksty również kończą proces SIGSEGV.

To zaobserwowane ograniczenia konkretnej wersji Survex, nie deklaracja
zachowania przyszłych wersji ani rzeczywistego Walls. Nie zmieniono pomiarów,
aby obejść te przypadki; źródła i sprzeczności pozostają możliwe do odtworzenia.
Nie dodano testu CI wymagającego awarii: poprawiony kompilator może bezpiecznie
odrzucić sprzeczną sieć. Test integracyjny zachowuje natomiast regresję dla
odłączonego źródła: wszystkie rekordy pozostają w eksporcie, a ostrzeżenie
kompilatora jest widoczne przy kodzie zakończenia 0.

**Konsekwencja dla P06:** kod zakończenia procesu równy 0 nie wystarcza do
uznania walidacji za poprawną. CLI musi wychwycić ostrzeżenia, sygnały/błędy
procesu i porównać obecność oczekiwanych nazwanych stacji w wyniku. Nie może
przedstawiać `.3d` z pominiętymi składowymi jako pełnej geometrii ani przerabiać
źródła w celu jej wymuszenia. Siedem ostrzeżeń pełnego korpusu P04 oznacza
właśnie wyniki częściowe. Zgodność SRV/SVX na stacjach obecnych w obu wynikach
nie usuwa tego ograniczenia; `corpus.json` osobno podaje brakujące surowe ID.

Odtworzenie prób z katalogu głównego repozytorium:

```python
import hashlib
import json
import os
import platform
import runpy
import subprocess
import tempfile
from pathlib import Path

h = runpy.run_path('tests/test_pockettopo_export.py')
F, S, z = h['_file'], h['_shot'], h['PLAIN_ZERO']
cases = {
    'disconnected': F((S(z, z+1), S(z+2, z+3))),
    'held-auto-bridge': F((S(z, z+1), S(z+1, z+2, trip=1), S(z+2, z+3)),
                          declinations=(0, -32768)),
    'independent-splays': F((S(z, h['UNDEFINED']), S(z+2, h['UNDEFINED']))),
    'direct-contradiction': F((S(z, z+1), S(z, z+1, distance=0))),
    'transitive-contradiction': F((S(z, z+1), S(z, z+2, distance=0), S(z+2, z+1, distance=0))),
}
env = {**os.environ, 'LC_ALL': 'C', 'LANG': 'C'}
out = Path('doc/pockettopo/evidence/p04')
rows = []
def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2)+'\n',
                    encoding='utf-8')
with tempfile.TemporaryDirectory(prefix='p04-limits-') as scratch:
    for name, data in cases.items():
        destination = out / 'compiler-limits' / name
        destination.mkdir(parents=True, exist_ok=True)
        (destination / 'input.top').write_bytes(data)
        result = h['export_surveys'](data)
        save(destination / 'source.json', result.source_document)
        save(destination / 'conversion-report.json', result.report)
        row = {'case': name, 'source_sha256': hashlib.sha256(data).hexdigest(),
               'completeness': result.report['completeness'], 'compilation': {}}
        for suffix in ('SRV', 'svx'):
            text = getattr(result, suffix.lower())
            (destination / ('survey.' + suffix)).write_text(text, encoding='ascii')
            work = Path(scratch) / name / suffix
            work.mkdir(parents=True)
            path = work / ('survey.' + suffix)
            path.write_text(text, encoding='ascii')
            proc = subprocess.run(['cavern', '-o', str(work / 'survey.3d'), str(path)],
                                  capture_output=True, text=True, encoding='utf-8', errors='replace',
                                  env=env, timeout=30, check=False)
            output = (proc.stdout + proc.stderr).replace(str(work), '<scratch>')
            node_names = []
            if proc.returncode == 0:
                dump = subprocess.check_output(['dump3d', '--legs', str(work / 'survey.3d')],
                                               text=True, encoding='utf-8', env=env)
                node_names = [line.split('[', 1)[1].split(']', 1)[0]
                              for line in dump.splitlines() if line.startswith('NODE ')]
                node_names = [name for name in node_names if name]
                output += '\n--- dump3d --legs ---\n' + dump
            (destination / (suffix.lower() + '-compilation.txt')).write_text(output, encoding='utf-8')
            row['compilation'][suffix.lower()] = {
                'text_sha256': hashlib.sha256(text.encode('ascii')).hexdigest(),
                'returncode': proc.returncode, 'signal': -proc.returncode if proc.returncode < 0 else None,
                'compiled_named_stations': node_names,
            }
        rows.append(row)
save(out / 'compiler-limits.json', {
    'schema_version': 1, 'date': '2026-09-25', 'platform': platform.platform(),
    'compiler': subprocess.check_output(['cavern', '--version'], text=True, env=env).strip(),
    'input_basis': 'Synthetic P04 test helper; exact bytes stored with each case',
    'code_sha256': {str(path): hashlib.sha256(path.read_bytes()).hexdigest()
                   for path in sorted(Path('src/jktz/pockettopo').glob('*.py'))},
    'cases': rows,
})
print(json.dumps(rows, ensure_ascii=False, indent=2))
```
