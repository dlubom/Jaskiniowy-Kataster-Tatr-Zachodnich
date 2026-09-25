# Odtworzenie P06

Z katalogu głównego repozytorium, po `uv sync --locked --python 3.12`.
Renderer resvg 0.48.1 i jego SHA-256 opisuje [manifest P01](../p01/renderer/manifest.json).
Potrzebne są również `cavern` i `dump3d`. Korpus 258 źródeł / 262 ścieżek
Git pochodzi z przypiętej rewizji opisanej w [P02](../p02/CORPUS.md).
`POCKETTOPO_CORPUS_ROOT` i `POCKETTOPO_CORPUS_TREE` wskazują lokalną kopię;
każdy obiekt musi odpowiadać przypiętemu SHA-1 Git. Brak pliku nie zmniejsza
zakresu próby: zatrzymuje ją.

```sh
RESVG=/path/to/resvg JKTZ_REQUIRE_RESVG=1 JKTZ_REQUIRE_CAVERN=1 uv run --python 3.12 jktz-quality
uv run --python 3.12 jktz-mutation
uv run --python 3.12 jktz-validate
uv run --python 3.12 python /path/to/skill-creator/scripts/quick_validate.py .agents/skills/pockettopo-convert
```

Skopiuj poniższy blok do pliku tymczasowego i uruchom przez
`RESVG=/path/to/resvg uv run --python 3.12 python /path/to/reproduce.py`.
Używa rzeczywistego entrypointu CLI, renderera i obu kompilacji dla każdego
wejścia. Weryfikuje 12 plików, manifest, statusy i niezmienność źródeł.
Wszystkie cztery SVG/PNG 13 wzorców muszą być identyczne bajtowo z P05.
Pełne pakiety trzech małych wzorców zostają w `examples/`; pakiety korpusu
są sprawdzane i usuwane z katalogów tymczasowych, a wyniki każdego źródła
oraz hashe pozostają w `corpus.json`.

Ten blok nadpisuje wyłącznie pochodne dowody P06 (`examples/`,
`fixture-checks.json`, `corpus.json`); nie dotyka źródeł. Nie powtarza
natywnych eksperymentów P01–P05 ani nie uznaje obserwacji powtórzeń za
potwierdzenia. Bramka nie obniża istniejącego zakresu ani progów mutacji.

```python
import contextlib
import hashlib
import io
import json
import os
import platform
import runpy
import shutil
import tempfile
from collections import Counter
from pathlib import Path

from jktz.cli.pockettopo import main
from jktz.pockettopo.package import json_bytes

out = Path('doc/pockettopo/evidence/p06')
out.mkdir(parents=True, exist_ok=True)
renderer = Path(os.environ.get('RESVG', '/private/tmp/p01-resvg/macos/resvg'))
code_paths = sorted(Path('src/jktz/pockettopo').glob('*.py')) + [Path('src/jktz/cli/pockettopo.py')]
def sha(data):
    return hashlib.sha256(data).hexdigest()
def save(path, value):
    path.write_bytes(json_bytes(value))
code_hashes = {str(p): sha(p.read_bytes()) for p in code_paths}
h = runpy.run_path('tests/test_pockettopo_dxf.py')
p05 = json.loads(Path('doc/pockettopo/evidence/p05/fixture-checks.json').read_bytes())
prior = {r['source_sha256']: r for r in p05['fixtures']}

def audit(path, destination):
    data = path.read_bytes()
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        exit_code = main(['convert', str(path), '--output', str(destination), '--resvg', str(renderer)])
    assert exit_code in (0, 2), (path, exit_code, stderr.getvalue())
    report = json.loads((destination / 'conversion-report.json').read_bytes())
    assert report['completeness']['conversion_complete'] == (exit_code == 0)
    assert json.loads(stdout.getvalue())['completeness'] == report['completeness']
    source = json.loads((destination / 'source.json').read_bytes())
    assert source['provenance']['sha256'] == sha(data)
    assert data == path.read_bytes()
    assert len(list(destination.iterdir())) == 12
    manifest = report['package']['artifacts']
    for name, value in manifest.items():
        content = (destination / name).read_bytes()
        assert value == {'bytes': len(content), 'sha256': sha(content)}
    if sha(data) in prior:
        for name, values in prior[sha(data)]['views'].items():
            for suffix in ('svg','png'):
                assert manifest[name+'.'+suffix]['sha256'] == values[suffix+'_sha256']
    validation = report['exports']['validation']
    return {
        'source_sha256':sha(data), 'source_bytes':len(data), 'exit_code':exit_code,
        'completeness':report['completeness'], 'drawing_notices':report['package']['drawing_notices'],
        'compilation': {'complete':validation['complete'], 'geometry_status': validation['geometry_status'],
            'comparison':validation['comparison'],
            'formats':{kind:{'complete':value['complete'], 'compile_status':value['compile']['status'],
                'returncode':value['compile']['returncode'], 'warnings':value['compile']['warnings'],
                'checks':value['checks']} for kind,value in validation['formats'].items()}},
        'artifact_manifest':manifest, 'report_sha256':sha((destination / 'conversion-report.json').read_bytes()),
        'source_unchanged':True, 'artifact_manifest_verified':True,
    }

with tempfile.TemporaryDirectory(prefix='p06-fixtures-') as temporary:
    rows=[]
    for index,path in enumerate(h['SOURCES']):
        destination=Path(temporary)/str(index)
        row=audit(path,destination)
        row['source']=str(path)
        row['drawings_byte_identical_to_p05']=True
        rows.append(row)
        if path.parent.name in ('api-drawings','api-trips-ids','api-cardinal'):
            example=out/'examples'/path.parent.name
            example.parent.mkdir(exist_ok=True)
            if example.exists():
                shutil.rmtree(example)
            shutil.copytree(destination,example)
        print('fixture',path.parent.name,row['exit_code'],flush=True)
    save(out/'fixture-checks.json',{'code_sha256':code_hashes,'fixtures':rows})

revision='4c00c008a8dd441d70f9c62aa376c20b5914c7e0'
root=Path(os.environ.get('POCKETTOPO_CORPUS_ROOT','/private/tmp/pockettopo-repeat-search/sources'))
tree_path=Path(os.environ.get('POCKETTOPO_CORPUS_TREE','/private/tmp/pockettopo-test2-tree.json'))
tree=json.loads(tree_path.read_bytes())
assert tree['sha']==revision and tree['truncated'] is False
entries=[r for r in tree['tree'] if r['path'].lower().endswith('.top')]
assert len(entries)==262 and len({r['sha'] for r in entries})==258
groups={}
for entry in sorted(entries,key=lambda r:r['path']):
    path=root/entry['path']
    data=path.read_bytes()
    assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==entry['sha']
    row=groups.setdefault(sha(data),{'path':path,'aliases':[]})
    row['aliases'].append({'path':entry['path'],'git_blob_sha1':entry['sha']})
rows=[]
for index,node in enumerate(groups.values()):
    with tempfile.TemporaryDirectory(prefix='p06-corpus-') as temporary:
        row=audit(node['path'],Path(temporary)/'package')
    row['aliases']=node['aliases']
    rows.append(row)
    if index%25==0:
        print('corpus',index+1,len(groups),flush=True)
assert code_hashes=={str(p):sha(p.read_bytes()) for p in code_paths}, 'Code changed: rerun'
summary={
    'unique_sources':len(rows),'git_paths_verified':len(entries),'packages':len(rows),
    'svg_artifacts':4*len(rows),'png_artifacts':4*len(rows),'artifacts':12*len(rows),
    'source_shots':sum(r['completeness']['source_shots'] for r in rows),
    'held_shots':sum(r['completeness']['held_shots'] for r in rows),
    'compilation_complete':sum(r['compilation']['complete'] for r in rows),
    'conversion_complete':sum(r['completeness']['conversion_complete'] for r in rows),
    'exit_codes':dict(Counter(r['exit_code'] for r in rows)),
    'drawing_notices':dict(sum((Counter(r['drawing_notices']) for r in rows),Counter())),
}
save(out/'corpus.json',{'schema_version':1,'source_revision':revision,'tree_sha256':sha(tree_path.read_bytes()),
    'code_sha256':code_hashes,'renderer_sha256':sha(renderer.read_bytes()),'python':platform.python_version(),
    'summary':summary,'files':rows})
print(json.dumps(summary,indent=2))
```
