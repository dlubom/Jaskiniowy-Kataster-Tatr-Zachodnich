# Odtworzenie geometrii i rozliczenia P04

Z katalogu głównego repozytorium:

```sh
JKTZ_REQUIRE_CAVERN=1 uv run --python 3.12 pytest -q tests/test_pockettopo_compilation.py
```

Testy wymagają `cavern` i `dump3d` na `PATH`. Bez zmiennej
`JKTZ_REQUIRE_CAVERN=1` brak narzędzi oznacza jawne pominięcie; CI ustawia ją
po instalacji Survex na Linux i Windows. Dowody lokalne używają Survex 1.4.22.
Źródła wzorcowe pochodzą z natywnego PocketTopo 1.372, zamrożonego w P01.
Test długich ID zmienia tylko identyfikatory dwóch stacji we wzorcu
`api-trips-ids`; test odwróconego domiaru zamienia tylko jego dwa końce.
Te pochodne nie są nowymi natywnymi wzorcami aplikacji.

Współrzędne oczekiwane obliczamy niezależnie od eksportera: `E = D sin(A)
cos(V)`, `N = D cos(A) cos(V)`, `Z = D sin(V)`, z literalnych wejść P01.
Dla A1/A2/A3 stosujemy ustalony w P03 wynik 5 m / 0° / 1820×360/65536°.
`dump3d` wypisuje centymetry, więc po odjęciu pozycji stacji początkowej
stosujemy tolerancję 0,010001 m (dwa zaokrąglenia do 0,01 m). Porównanie
SRV/SVX obejmuje każdą stację nazwaną i wektor domiaru. Zerowe powiązanie
musi dać współrzędne identyczne dla obu nazw. Survex może łączyć powtarzające
się krawędzie podczas kompilacji; kontrola zachowania niepotwierdzonych
rekordów dotyczy osobnych wierszy eksportu i pełnego śladu źródłowego.

Poniższy kod uruchomić przez `uv run --python 3.12 python` z katalogu głównego.
Odtwarza wersjonowane eksporty wzorców, zapisuje wyniki kompilacji i wykonuje
pełne rozliczenie korpusu. Korzysta z lokalnej kopii przypiętego `test2`
opisanej w [P02](../p02/CORPUS.md); nie pobiera ani nie zmienia oryginałów.
Brak korpusu, inna rewizja lub niezgodny Git blob przerywa próbę.

```python
import hashlib
import json
import os
import platform
import re
import runpy
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

h = runpy.run_path('tests/test_pockettopo_compilation.py')
export_surveys = h['export_surveys']
out = Path('doc/pockettopo/evidence/p04')
evidence = out.parent
code_hashes = {
    str(path): hashlib.sha256(path.read_bytes()).hexdigest()
    for path in sorted(Path('src/jktz/pockettopo').glob('*.py'))
}
code_hashes['tests/test_pockettopo_compilation.py'] = hashlib.sha256(
    Path('tests/test_pockettopo_compilation.py').read_bytes()).hexdigest()
cavern, dump3d = h['compiler_tools']()
env = {**os.environ, 'LC_ALL': 'C', 'LANG': 'C'}
version = subprocess.check_output([cavern, '--version'], text=True, env=env).strip()

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2)
                    + '\n', encoding='utf-8')

def checked_export(data, **kwargs):
    result = export_surveys(data, **kwargs)
    count = len(result.source_document['records']['shots'])
    assert [row['source_index'] for row in result.report['record_trace']] == list(range(count))
    assert [i for group in result.report['groups'] for i in group['source_indices']] == list(range(count))
    totals = result.report['completeness']
    assert totals['source_shots'] == totals['traced_shots'] == count
    assert totals['exported_source_shots'] + totals['held_shots'] == count
    assert totals['conversion_complete'] is False
    json.dumps((result.source_document, result.report), allow_nan=False)
    return result

def compile_any(text, suffix, folder, active):
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / ('survey.' + suffix)
    path.write_text(text, encoding='ascii')
    result = {'text_sha256': hashlib.sha256(text.encode('ascii')).hexdigest()}
    if not active:
        return {**result, 'status': 'no_active_measurements'}, {}, ''
    proc = subprocess.run([cavern, '-o', str(folder / 'survey.3d'), str(path)],
                          text=True, encoding='utf-8', errors='replace',
                          capture_output=True, env=env, timeout=30, check=False)
    output = (proc.stdout + proc.stderr).replace(str(folder), '<scratch>')
    diagnostics = [line for line in output.splitlines()
                   if re.search(r'\b(?:warning|error):', line, re.I)]
    warnings = [line for line in diagnostics if 'warning:' in line.lower()]
    result.update(returncode=proc.returncode, diagnostics=diagnostics,
                  status='compiler_error' if proc.returncode else
                         'compiled_with_warnings' if warnings else 'compiled_without_warnings')
    if proc.returncode:
        return result, {}, output
    dump = subprocess.check_output([dump3d, '--legs', str(folder / 'survey.3d')],
                                   text=True, encoding='utf-8', env=env)
    nodes = {}
    for line in dump.splitlines():
        if line.startswith('NODE '):
            coordinates, remaining = line[5:].split(' [', 1)
            nodes[remaining.split(']', 1)[0]] = tuple(map(float, coordinates.split()))
    result['named_nodes'] = sum(bool(name) for name in nodes)
    return result, nodes, output + '\n--- dump3d --legs ---\n' + dump

def compare_geometry(report, compiled):
    names = report['station_map']
    srv = {r['raw']: compiled['srv'].get(r['walls_name']) for r in names
           if r['walls_name'] in compiled['srv']}
    svx = {r['raw']: compiled['svx'].get(r['survex_name']) for r in names
           if r['survex_name'] in compiled['svx']}
    if not srv or not svx:
        return {'status': 'unavailable', 'reason': 'one_or_both_compilers_have_no_named_geometry'}
    if srv.keys() != svx.keys():
        return {'status': 'station_set_mismatch', 'srv_only': sorted(srv.keys() - svx.keys()),
                'svx_only': sorted(svx.keys() - srv.keys())}
    exported_ids = {raw for g in report['groups'] if g['export']['status'] == 'exported'
                    for raw in (g['from_raw'], g['to_raw']) if raw != -2147483648}
    missing = sorted(exported_ids - srv.keys())
    origin = next(iter(srv))
    error = max(abs((srv[key][axis] - srv[origin][axis]) -
                    (svx[key][axis] - svx[origin][axis]))
                for key in srv for axis in range(3))
    return {'status': ('consistent_partial' if missing else 'consistent')
                      if error <= h['COORDINATE_TOLERANCE_M'] else 'difference',
            'named_stations': len(srv), 'expected_exported_named_stations': len(exported_ids),
            'missing_exported_station_raw_ids': missing, 'relative_origin_raw': origin,
            'max_absolute_coordinate_difference_m': error,
            'tolerance_m': h['COORDINATE_TOLERANCE_M']}

cases = []
paths = sorted((evidence / 'p01/cases').glob('*/*.top'))
paths += sorted((evidence / 'repeat-candidates').glob('*/*.top'))
assert len(paths) == 9
for path in paths:
    name = 'cardinal-unconfirmed' if path.stem == 'api-cardinal' else path.parent.name
    cases.append((name, path.read_bytes(), {}, str(path)))
cardinal = h['native_source']('api-cardinal')[0]
trips = h['native_source']('api-trips-ids')[0]
long_ids = h['long_id_source']()
reversed_splay = h['reverse_splay_source']()
cases += [
    ('cardinal-confirmed', cardinal, {'plan': h['confirmed_plan'](cardinal)},
     'P01 api-cardinal plus source-pinned confirmation of records 4/5/6'),
    ('trips-overrides', trips, {'correction_policy': h['explicit_test_policy'](trips)},
     'P01 api-trips-ids plus documented synthetic correction choices'),
    ('long-identifiers', long_ids, {'correction_policy': h['explicit_test_policy'](long_ids)},
     'P01 api-trips-ids with only two station IDs replaced; see test helper'),
    ('reversed-splay', reversed_splay, {'plan': h['confirmed_plan'](reversed_splay)},
     'P01 api-cardinal with only the splay endpoints swapped; see test helper'),
]
fixtures = []
with tempfile.TemporaryDirectory(prefix='p04-fixtures-') as scratch:
    for name, data, kwargs, provenance in cases:
        result = checked_export(data, **kwargs)
        destination = out / name
        save(destination / 'source.json', result.source_document)
        save(destination / 'conversion-report.json', result.report)
        row = {'name': name, 'input_basis': provenance,
               'source_sha256': hashlib.sha256(data).hexdigest(),
               'completeness': result.report['completeness'], 'compilation': {}}
        compiled = {}
        for suffix, attr in [('SRV', 'srv'), ('svx', 'svx')]:
            text = getattr(result, attr)
            (destination / ('survey.' + suffix)).write_text(text, encoding='ascii')
            validation, nodes, log = compile_any(text, suffix, Path(scratch) / name / attr,
                                                result.report['exports']['active_measurements'])
            row['compilation'][attr] = validation
            compiled[attr] = nodes
            if log:
                (destination / (attr + '-compilation.txt')).write_text(log, encoding='utf-8')
        row['cross_format_geometry'] = compare_geometry(result.report, compiled)
        fixtures.append(row)
save(out / 'fixture-checks.json', {'schema_version': 1, 'date': '2026-09-25',
                                 'compiler': version, 'code_sha256': code_hashes,
                                 'fixtures': fixtures})

# Independent analytical oracles, separate from source/report arithmetic.
analytical = []
with tempfile.TemporaryDirectory(prefix='p04-oracles-') as scratch:
    for name, data, kwargs, basis in cases[-4:]:
        result = checked_export(data, **kwargs)
        cardinal_case = name in ('cardinal-confirmed', 'reversed-splay')
        expected = h['cardinal_expected']() if cardinal_case else h['trips_expected'](
            long_names=name == 'long-identifiers')
        actual = {}
        for suffix, target in [('SRV', 'walls'), ('svx', 'survex')]:
            compiled = h['compile_export'](getattr(result, suffix.lower()), suffix,
                                          Path(scratch) / name / suffix)
            actual[target] = h['mapped_nodes'](result, compiled, target)
            h['assert_geometry'](actual[target], expected)
            if cardinal_case:
                reversed_direction = name == 'reversed-splay'
                expected_splay = h['vector'](1.234, 225 if reversed_direction else 45,
                    (1 if reversed_direction else -1) * 3641 * 360 / 65536)
            else:
                expected_splay = h['vector'](3, 188, -1820 * 360 / 65536)
            h['assert_splay'](compiled, expected_splay)
        assert actual['walls'] == actual['survex']
        analytical.append({'case': name, 'expected_relative_coordinates_m': expected,
                           'compiled_named_coordinates_m': actual,
                           'expected_splay_vector_m': expected_splay,
                           'tolerance_m': h['COORDINATE_TOLERANCE_M'], 'passed': True})
save(out / 'geometry.json', {'schema_version': 1, 'compiler': version,
                            'code_sha256': code_hashes, 'cases': analytical})

revision = '4c00c008a8dd441d70f9c62aa376c20b5914c7e0'
root = Path(os.environ.get('POCKETTOPO_CORPUS_ROOT', '/private/tmp/pockettopo-repeat-search/sources'))
tree_path = Path(os.environ.get('POCKETTOPO_CORPUS_TREE', '/private/tmp/pockettopo-test2-tree.json'))
tree_bytes = tree_path.read_bytes()
tree = json.loads(tree_bytes)
assert tree['sha'] == revision and tree['truncated'] is False
entries = sorted((r for r in tree['tree'] if r['path'].lower().endswith('.top')),
                 key=lambda r: r['path'])
assert len(entries) == 262 and len({r['sha'] for r in entries}) == 258
contents = {}
with tempfile.TemporaryDirectory(prefix='p04-corpus-') as scratch:
    for entry in entries:
        data = (root / entry['path']).read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        assert blob == entry['sha'], entry['path']
        digest = hashlib.sha256(data).hexdigest()
        if digest not in contents:
            result = checked_export(data)
            assert all(len(group['source_indices']) == 1 for group in result.report['groups'])
            row = {'sha256': digest, 'bytes': len(data), 'aliases': [],
                   'completeness': result.report['completeness'],
                   'held_records': [{'source_index': t['source_index'],
                                     'reason': t['export']['reason']}
                                    for t in result.report['record_trace']
                                    if t['export']['status'] == 'held'], 'compilation': {}}
            compiled = {}
            for suffix, attr in [('SRV', 'srv'), ('svx', 'svx')]:
                validation, nodes, _ = compile_any(getattr(result, attr), suffix,
                    Path(scratch) / digest / attr, result.report['exports']['active_measurements'])
                row['compilation'][attr] = validation
                compiled[attr] = nodes
            row['cross_format_geometry'] = compare_geometry(result.report, compiled)
            contents[digest] = row
        contents[digest]['aliases'].append({'path': entry['path'], 'verified_git_blob_sha1': blob})
rows = list(contents.values())
summary = {
    'unique_sources': len(rows), 'verified_paths': len(entries),
    'source_shots': sum(r['completeness']['source_shots'] for r in rows),
    'traced_shots': sum(r['completeness']['traced_shots'] for r in rows),
    'exported_measurements': sum(r['completeness']['exported_measurements'] for r in rows),
    'exported_source_shots': sum(r['completeness']['exported_source_shots'] for r in rows),
    'held_shots': sum(r['completeness']['held_shots'] for r in rows),
    'confirmed_groups': 0,
    'held_reasons': dict(Counter(t['reason'] for r in rows for t in r['held_records'])),
    'compilation': {name: dict(Counter(r['compilation'][name]['status'] for r in rows))
                    for name in ('srv', 'svx')},
    'cross_format_geometry': dict(Counter(r['cross_format_geometry']['status'] for r in rows)),
    'omitted_exported_named_stations': sum(len(r['cross_format_geometry'].get(
        'missing_exported_station_raw_ids', [])) for r in rows),
}
assert code_hashes == {path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
                       for path in code_hashes}, 'Code changed during run; rerun against final source'
save(out / 'corpus.json', {
    'schema_version': 1, 'date': '2026-09-25', 'source_revision': revision,
    'scope': 'P04 exports without repeat confirmations, correction overrides or inferred fixes',
    'tree_sha256': hashlib.sha256(tree_bytes).hexdigest(),
    'jktz_base_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
    'python_version': platform.python_version(), 'compiler': version,
    'code_sha256': code_hashes, 'summary': summary, 'files': rows,
})
print(json.dumps(summary, ensure_ascii=False, indent=2))
```

Żaden test nie tworzy aktywnych fixów z referencji `.top`. Kompilator może
przyjąć umowny początek układu dla jednej sieci i zgłosić odłączone składowe;
wyniki korpusu zapisują te komunikaty i statusy. Brak aktywnych odcinków
nie jest przedstawiany jako udana kompilacja. Nie dodajemy powiązań ani
współrzędnych w celu usunięcia ostrzeżeń źródła.
