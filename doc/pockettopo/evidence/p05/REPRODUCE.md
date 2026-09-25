# Odtworzenie P05

Z katalogu głównego repozytorium, Python 3.12. Kod poniżej używa publicznego
API i niezależnego czytnika XML/DXF z testów. Nie modyfikuje źródeł.
Potrzebny jest lokalny przypięty korpus `test2` i drzewo Git opisane w
[P02](../p02/CORPUS.md); zmienne `POCKETTOPO_CORPUS_ROOT` oraz
`POCKETTOPO_CORPUS_TREE` pozwalają podać inne lokalizacje. Każdy obiekt Git
jest weryfikowany przed konwersją. Brak źródła lub niezgodny hash przerywa
próbę, zamiast zmniejszać badany zakres.

Renderer to resvg **0.48.1**, z [manifestu P01](../p01/renderer/manifest.json).
`RESVG` musi wskazywać właściwy program. W CI Linux lokalna akcja
`.github/actions/install-resvg` sprawdza sumę archiwum i programu oraz ustawia
`JKTZ_REQUIRE_RESVG=1`. Testy wszystkich 52 zachowanych PNG wymagają zgodności
bajtowej z macOS, więc wykonanie w Linux CI jest także porównaniem platform.
Testy jednostkowe procesu nie zastępują tego uruchomienia.

```sh
uv sync --locked --python 3.12
RESVG=/path/to/resvg JKTZ_REQUIRE_RESVG=1 uv run --python 3.12 pytest -q tests/test_pockettopo_drawings.py tests/test_pockettopo_projection.py tests/test_pockettopo_dxf.py
RESVG=/path/to/resvg JKTZ_REQUIRE_RESVG=1 JKTZ_REQUIRE_CAVERN=1 uv run --python 3.12 jktz-quality
uv run --python 3.12 jktz-mutation
uv run --python 3.12 jktz-validate
```

Poniższy kod uruchomić przez `uv run --python 3.12 python`. Nadpisuje wyłącznie
pochodne dowody P05: `examples/`, `fixture-checks.json`, `corpus.json`.
Nie aktualizować referencyjnych PNG bez ponownej kontroli pikseli i wizualnej.
Dla 13 lokalnych wzorców zapisuje pełne cztery SVG/PNG oraz raport. Dla korpusu
renderuje wszystkie wyniki i porównuje każdy wierzchołek, a zapisuje hashe,
rozmiary, statusy i ograniczenia każdego pliku, bez powielania całego korpusu.
Wierzchołki są liczone raz na widok, mimo dwóch wariantów tego samego szkicu.
Korpus nie ma własnych natywnych DXF dla każdego źródła: niezależna zgodność
DXF dotyczy 13 wskazanych wzorców, nie wszystkich 258 wejść.

```python
import hashlib
import json
import os
import platform
import runpy
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree

from jktz.pockettopo import export_drawings, parse_bytes
from jktz.pockettopo.model import Polygon

out = Path('doc/pockettopo/evidence/p05')
renderer = Path(os.environ['RESVG'])
h = runpy.run_path('tests/test_pockettopo_dxf.py')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2)+'\n', encoding='utf-8')

def audit(data, result):
    model = parse_bytes(data)
    ns = {'s': 'http://www.w3.org/2000/svg'}
    views = {}
    for name, svg in result.svgs.items():
        view = model.outline if name.startswith('plan') else model.sideview
        expected = [(h['ACI'][e.color], [(h['Decimal'](p.x)/500, -h['Decimal'](p.y)/500) for p in e.points]) for e in view.elements if isinstance(e, Polygon)]
        assert h['svg_sketch'](svg) == expected
        root = ElementTree.fromstring(svg)
        meta = result.report['drawings']['artifacts'][name]
        assert int(root.attrib['width']) == meta['viewport']['width_px']
        assert int(root.attrib['height']) == meta['viewport']['height_px']
        # Exact same source vertices in both variants, no geometric transform.
        views[name] = {
            'svg_sha256': sha(svg.encode()), 'png_sha256': sha(result.pngs[name]),
            'svg_bytes': len(svg.encode()), 'png_bytes': len(result.pngs[name]),
            'sketch_status': meta['sketch_status'], 'sketch_vertices': sum(len(p) for _, p in expected),
            'viewport': meta['viewport'],
        }
    assert len(result.svgs) == len(result.pngs) == 4
    return views

code_paths = sorted(Path('src/jktz/pockettopo').glob('*.py'))
code_hashes = {str(p): sha(p.read_bytes()) for p in code_paths}
fixtures = []
for path in h['SOURCES']:
    data = path.read_bytes()
    result = export_drawings(data, resvg_path=renderer)
    views = audit(data, result)
    name = path.parent.name
    if '/p05/native/' in str(path):
        name = 'native-' + name
    destination = out / 'examples' / name
    destination.mkdir(parents=True, exist_ok=True)
    for artifact, svg in result.svgs.items():
        (destination / (artifact+'.svg')).write_text(svg, encoding='utf-8')
        (destination / (artifact+'.png')).write_bytes(result.pngs[artifact])
    save(destination / 'conversion-report.json', result.report)
    dxfs = {}
    for view, source_view in [('plan','outline'),('side','sideview')]:
        native = h['native_path'](path, source_view)
        assert h['native_sketch'](native) == h['svg_sketch'](result.svgs[view+'-sketch'])
        dxfs[str(native)] = sha(native.read_bytes())
    fixtures.append({'source': str(path), 'source_sha256': sha(data), 'native_dxf_sha256': dxfs,
                     'views': views, 'geometry_diagnostics': result.report['drawings']['geometry']['diagnostics'],
                     'completeness': result.report['completeness']})
    print('fixture', name, flush=True)
save(out / 'fixture-checks.json', {'code_sha256':code_hashes, 'fixtures':fixtures})

revision='4c00c008a8dd441d70f9c62aa376c20b5914c7e0'
root=Path(os.environ.get('POCKETTOPO_CORPUS_ROOT','/private/tmp/pockettopo-repeat-search/sources'))
tree_path=Path(os.environ.get('POCKETTOPO_CORPUS_TREE','/private/tmp/pockettopo-test2-tree.json'))
tree=json.loads(tree_path.read_bytes())
assert tree['sha']==revision and tree['truncated'] is False
entries=[r for r in tree['tree'] if r['path'].lower().endswith('.top')]
assert len(entries)==262 and len({r['sha'] for r in entries})==258
groups={}
for e in sorted(entries,key=lambda r:r['path']):
    data=(root/e['path']).read_bytes()
    blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    assert blob==e['sha']
    node=groups.setdefault(sha(data),{'source_sha256':sha(data),'bytes':len(data),'aliases':[],'data':data})
    node['aliases'].append({'path':e['path'],'git_blob_sha1':blob})
rows=[]
for index,row in enumerate(groups.values()):
    data=row.pop('data')
    result=export_drawings(data,resvg_path=renderer)
    row['views']=audit(data,result)
    row['completeness']=result.report['completeness']
    geometry=result.report['drawings']['geometry']
    row['components']=geometry['components']
    row['diagnostic_counts']=dict(Counter(d['code'] for d in geometry['diagnostics']))
    row['xsection_statuses']=dict(Counter(s['status'] for v in geometry['views'].values() for s in v['xsections']))
    row['status']='exported_and_vertices_verified'
    rows.append(row)
    if index%25==0: print('corpus',index+1,len(groups),flush=True)
assert code_hashes=={str(p):sha(p.read_bytes()) for p in code_paths}, 'Code changed; rerun evidence'
summary={'unique_sources':len(rows),'git_paths_verified':len(entries),'svg_artifacts':4*len(rows),'png_artifacts':4*len(rows),
         'vertices_both_views':sum(r['views'][n]['sketch_vertices'] for r in rows for n in ('plan-sketch','side-sketch')),
         'source_shots':sum(r['completeness']['source_shots'] for r in rows),
         'held_shots':sum(r['completeness']['held_shots'] for r in rows),
         'diagnostics':dict(sum((Counter(r['diagnostic_counts']) for r in rows),Counter())),
         'xsection_statuses':dict(sum((Counter(r['xsection_statuses']) for r in rows),Counter()))}
save(out/'corpus.json',{'schema_version':1,'source_revision':revision,'tree_sha256':sha(tree_path.read_bytes()),
                     'code_sha256':code_hashes,'renderer_sha256':sha(renderer.read_bytes()),
                     'python':platform.python_version(),'summary':summary,'files':rows})
print(json.dumps(summary,indent=2))
```
