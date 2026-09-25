# Odtworzenie dowodów P03

Uruchomić poniższy kod przez `uv run --python 3.12 python` z katalogu głównego
repozytorium. Potrzebne są dziewięć wersjonowanych wzorców oraz lokalna kopia
korpusu z [P02](../p02/CORPUS.md); brak korpusu lub niezgodne bajty przerywają
próbę. Skrypt nie pobiera ani nie zmienia oryginałów. Wyniki zapisuje wyłącznie
w `doc/pockettopo/evidence/p03/`. Testy CI nie wymagają korpusu ani sieci.

Potwierdzenie A1–A3 pochodzi z jawnych danych syntetycznych helpera P01,
a nie z podobieństwa odczytów. Dla rzeczywistych materiałów nie przekazujemy
potwierdzeń. Indeksy P03 liczone są **od zera**; starszy raport doboru używał
numerów rekordów od jedynki.

```python
import hashlib
import json
import os
import platform
import subprocess
from collections import Counter
from pathlib import Path

from jktz.pockettopo import ProcessingPlan, RepeatConfirmation, prepare_conversion

out = Path('doc/pockettopo/evidence/p03')
evidence = out.parent
code_hashes = {
    str(path): hashlib.sha256(path.read_bytes()).hexdigest()
    for path in sorted(Path('src/jktz/pockettopo').glob('*.py'))
}

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2)
                    + '\n', encoding='utf-8')

def check(data, plan=None):
    source, report = prepare_conversion(data, plan=plan)
    # Strict JSON roundtrip retains large integer ticks and coordinates.
    decoded = json.loads(json.dumps(source, ensure_ascii=False, allow_nan=False))
    assert decoded['records']['trips'] == list(source['records']['trips'])
    json.dumps(report, ensure_ascii=False, allow_nan=False)
    count = len(source['records']['shots'])
    assert [row['source_index'] for row in report['record_trace']] == list(range(count))
    assert [i for group in report['groups'] for i in group['source_indices']] == list(range(count))
    assert report['completeness']['source_shots'] == report['completeness']['traced_shots']
    assert report['completeness']['conversion_complete'] is False
    return source, report

fixtures = []
paths = sorted((evidence / 'p01/cases').glob('*/*.top'))
paths += sorted((evidence / 'repeat-candidates').glob('*/*.top'))
assert len(paths) == 9
assert len({path.parent.name for path in paths}) == 9
for path in paths:
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    plan = None
    if path.stem == 'api-cardinal':
        plan = ProcessingPlan(digest, (RepeatConfirmation(
            (4, 5, 6),
            'P01 synthetic confirmed repeat A1/A2/A3; '
            'doc/pockettopo/helpers/pockettopo_fixtures.cs:167-169 '
            'and p01/cases/api-cardinal/expected.json',
        ),))
    source, report = check(data, plan)
    if plan:
        mean = report['groups'][4]['average']
        assert mean['count'] == 3
        assert mean['distance_m'] == 5.0 and mean['azimuth_deg'] == 0.0
        assert mean['inclination_deg'] == 9.99755859375
        assert report['groups'][4]['normalized_readings'][2]['reversed'] is True
        save(out / 'api-cardinal/source.json', source)
    else:
        assert all(len(group['source_indices']) == 1 for group in report['groups'])
    report_path = out / path.parent.name / 'conversion-report.json'
    save(report_path, report)
    assert path.read_bytes() == data
    fixtures.append({'path': str(path), 'report_path': str(report_path), 'sha256': digest,
                     'completeness': report['completeness'],
                     'confirmed_groups': sum(len(g['source_indices']) > 1 for g in report['groups'])})
save(out / 'fixture-checks.json', {'schema_version': 1, 'code_sha256': code_hashes,
                                 'fixtures': fixtures})

revision = '4c00c008a8dd441d70f9c62aa376c20b5914c7e0'
root = Path(os.environ.get('POCKETTOPO_CORPUS_ROOT', '/private/tmp/pockettopo-repeat-search/sources'))
tree_path = Path(os.environ.get('POCKETTOPO_CORPUS_TREE', '/private/tmp/pockettopo-test2-tree.json'))
tree_bytes = tree_path.read_bytes()
tree = json.loads(tree_bytes)
assert tree['sha'] == revision and tree['truncated'] is False
entries = sorted((row for row in tree['tree'] if row['path'].lower().endswith('.top')),
                 key=lambda row: row['path'])
assert len(entries) == 262 and len({row['sha'] for row in entries}) == 258
contents = {}
for entry in entries:
    data = (root / entry['path']).read_bytes()
    blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    assert blob == entry['sha'], entry['path']
    digest = hashlib.sha256(data).hexdigest()
    if digest not in contents:
        source, report = check(data)
        assert all(len(group['source_indices']) == 1 for group in report['groups'])
        contents[digest] = {
            'sha256': digest, 'bytes': len(data), 'aliases': [],
            'completeness': report['completeness'],
            'dispositions': dict(Counter(row['disposition'] for row in report['record_trace'])),
            'held_records': [row for row in report['record_trace']
                             if row['disposition'] != 'retained_single'],
            'group_warning_counts': dict(Counter(w for g in report['groups'] for w in g['warnings'])),
        }
    contents[digest]['aliases'].append({'path': entry['path'], 'verified_git_blob_sha1': blob})
rows = list(contents.values())
summary = {
    'unique_sources': len(rows), 'verified_paths': len(entries),
    'source_shots': sum(row['completeness']['source_shots'] for row in rows),
    'traced_shots': sum(row['completeness']['traced_shots'] for row in rows),
    'ready_measurements': sum(row['completeness']['ready_measurements'] for row in rows),
    'held_shots': sum(row['completeness']['held_shots'] for row in rows),
    'confirmed_groups': 0,
    'held_reasons': dict(Counter(item['reason'] for row in rows for item in row['held_records'])),
}
assert code_hashes == {path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
                       for path in code_hashes}, 'Code changed during run'
save(out / 'corpus.json', {
    'schema_version': 1, 'scope': 'P03 record accounting without repeat confirmations or exports',
    'date': '2026-09-25', 'source_revision': revision,
    'tree_sha256': hashlib.sha256(tree_bytes).hexdigest(),
    'jktz_base_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
    'python_version': platform.python_version(), 'code_sha256': code_hashes,
    'summary': summary, 'files': rows,
})
print(json.dumps(summary, ensure_ascii=False, indent=2))
```

Bramki repozytorium i kontrola oryginałów:

```sh
uv run --python 3.12 jktz-quality
uv run --python 3.12 jktz-mutation
uv run --python 3.12 jktz-render-otwory --check
(cd doc/pockettopo/evidence/p01 && shasum -a 256 -c SHA256SUMS)
(cd doc/pockettopo/evidence/repeat-candidates && shasum -a 256 -c SHA256SUMS)
```

`quality.json` i `mutation.json` skopiowano z `logs/quality/` po pełnym przebiegu.
Zbiorczy `repository-checks.json` zawiera polecenia, wyniki i kontekst przeglądu.
