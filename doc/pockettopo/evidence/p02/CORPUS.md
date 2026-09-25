# P02 — pełny przebieg korpusu `test2`

Źródło: `dlubom/test2`, przypięty commit
`4c00c008a8dd441d70f9c62aa376c20b5914c7e0`. Przebieg używa publicznego
`jktz.pockettopo.parse_bytes` z domyślnymi limitami parsera.
Oryginały pozostają poza repozytorium; nie przypisujemy im licencji JKTZ.

Wyniki dla wszystkich 258 unikalnych zawartości i ich 262 ścieżek zapisuje
[corpus.json](corpus.json). Każdy alias ma oczekiwany i obliczony Git blob SHA-1;
każda zawartość ma SHA-256, status, liczności obu rysunków i rodzaj zakończenia
albo jawny błąd parsera z kodem, offsetem i kontekstem. Niepowodzenie nie
tworzy częściowego modelu. Data, bazowy commit JKTZ, SHA-256 kodu parsera/modelu
i parametry limitów wiążą raport z konkretnym uruchomieniem.

## Wynik

Przebieg z **2026-09-25** odczytał **258/258 unikalnych zawartości** bez błędu;
bajty wszystkich **262/262 ścieżek** odpowiadały obiektom przypiętego drzewa Git.
Nie było pustych plików, brakujących źródeł ani niezgodności hashy.
Łącznie model zachował 287 tripów, 37 801 pomiarów, 25 referencji,
106 687 elementów rysunku, w tym 106 677 polilinii, 952 211 wierzchołków
i 10 XSection. Sumy obejmują unikalne zawartości; aliasy nie są liczone ponownie.

**256** plików ma końcowe cztery zera, a **2** kończą się dokładnie po
terminatorze sideview, zgodnie z opublikowanym schematem:

- `495-Interessante/20160802-Za_Owsikami/Old/ows.top`
- `508-Schacht_unter_dem_Stein/20160807-schacht_1/schacht_1.top`

To rozszerza obserwację P01, w której wszystkie sześć małych wzorców miało
cztery zera. Oba warianty pozostają rozróżnione w modelu i raporcie.

## Powtórzenie

Wykonać z katalogu głównego JKTZ. Potrzebne są lokalny korpus oraz zapisane
drzewo Git tej samej rewizji. `POCKETTOPO_CORPUS_ROOT` i `POCKETTOPO_CORPUS_TREE`
pozwalają wskazać inne lokalne kopie; skrypt niczego nie pobiera i nie modyfikuje
źródeł. Kopia drzewa musi zawierać 262 ścieżki `.top` oraz 258 identyfikatorów
obiektów Git. Weryfikacja bajtów poprzedza parsowanie każdego pliku.

```bash
UV_CACHE_DIR=/tmp/jktz-p02-uv-cache uv run --offline --python 3.12 python - <<'PY'
import hashlib
import json
import os
import platform
import subprocess
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from jktz.pockettopo import parse_bytes
from jktz.pockettopo.model import Polygon, XSection
from jktz.pockettopo.parser import DEFAULT_LIMITS, ParseError

revision = "4c00c008a8dd441d70f9c62aa376c20b5914c7e0"
root = Path(os.environ.get(
    "POCKETTOPO_CORPUS_ROOT", "/private/tmp/pockettopo-repeat-search/sources"
))
tree_path = Path(os.environ.get(
    "POCKETTOPO_CORPUS_TREE", "/private/tmp/pockettopo-test2-tree.json"
))
tree_bytes = tree_path.read_bytes()
tree = json.loads(tree_bytes)
assert tree["sha"] == revision and tree["truncated"] is False
entries = [row for row in tree["tree"] if row["path"].lower().endswith(".top")]
assert len(entries) == 262 and len({row["sha"] for row in entries}) == 258
code_paths = ["src/jktz/pockettopo/parser.py", "src/jktz/pockettopo/model.py"]
code_hashes = {path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
               for path in code_paths}
groups = {}
source_failures = []
for entry in sorted(entries, key=lambda row: row["path"]):
    path = root / entry["path"]
    try:
        data = path.read_bytes()
    except OSError as error:
        source_failures.append({"path": entry["path"], "error": str(error)})
        continue
    sha256 = hashlib.sha256(data).hexdigest()
    blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    alias = {"path": entry["path"], "expected_git_blob_sha1": entry["sha"],
             "actual_git_blob_sha1": blob, "git_blob_match": blob == entry["sha"]}
    group = groups.setdefault(sha256, {"sha256": sha256, "bytes": len(data),
                                       "aliases": [], "data": data})
    group["aliases"].append(alias)

def drawing_counts(drawing):
    return {"elements": len(drawing.elements),
            "polygons": sum(isinstance(item, Polygon) for item in drawing.elements),
            "vertices": sum(len(item.points) for item in drawing.elements
                            if isinstance(item, Polygon)),
            "xsections": sum(isinstance(item, XSection) for item in drawing.elements)}

rows = []
for row in groups.values():
    data = row.pop("data")
    row.update({"counts": None, "ending": None, "error": None})
    if not all(alias["git_blob_match"] for alias in row["aliases"]):
        row.update({"status": "source_mismatch", "error": {
            "code": "git_blob_mismatch", "offset": None, "context": "source"}})
    else:
        try:
            parsed = parse_bytes(data)
        except ParseError as error:
            row.update({"status": "parse_error", "error": {
                "code": error.code, "offset": error.offset, "context": error.context}})
        else:
            outline = drawing_counts(parsed.outline)
            sideview = drawing_counts(parsed.sideview)
            counts = {"trips": len(parsed.trips), "shots": len(parsed.shots),
                      "references": len(parsed.references),
                      "outline": outline, "sideview": sideview}
            counts.update({name: outline[name] + sideview[name]
                           for name in ("elements", "polygons", "vertices", "xsections")})
            row.update({"status": "parsed", "counts": counts, "ending": parsed.ending})
    rows.append(row)

assert code_hashes == {path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
                       for path in code_paths}, "Parser/model changed during the run"
statuses = Counter(row["status"] for row in rows)
summary = {
    "expected_paths": len(entries), "expected_unique_git_blobs": 258,
    "read_paths": sum(len(row["aliases"]) for row in rows),
    "unique_contents": len(rows), "parsed_unique": statuses["parsed"],
    "parse_errors_unique": statuses["parse_error"],
    "source_mismatches_unique": statuses["source_mismatch"],
    "source_read_errors": len(source_failures),
    "git_blob_matches": sum(alias["git_blob_match"] for row in rows for alias in row["aliases"]),
    "zero_byte_unique": sum(row["bytes"] == 0 for row in rows),
    "endings": dict(Counter(row["ending"] for row in rows if row["status"] == "parsed")),
    "parse_error_codes": dict(Counter(row["error"]["code"] for row in rows
                                      if row["status"] == "parse_error")),
}
summary["parsed_record_totals"] = {
    name: sum(row["counts"][name] for row in rows if row["status"] == "parsed")
    for name in ("trips", "shots", "references", "elements", "polygons", "vertices", "xsections")
}
report = {
    "schema_version": 1,
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "scope": "P02 strict source parsing only; not export or geometry validation",
    "repository": "https://github.com/dlubom/test2", "source_revision": revision,
    "source_root": str(root), "tree_file": str(tree_path),
    "tree_file_sha256": hashlib.sha256(tree_bytes).hexdigest(),
    "jktz_base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
    "code_sha256": code_hashes, "python_version": platform.python_version(),
    "parse_limits": asdict(DEFAULT_LIMITS), "summary": summary,
    "source_read_errors": source_failures, "files": rows,
}
output = Path("doc/pockettopo/evidence/p02/corpus.json")
output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
PY
```

## Granice dowodu

Pełny przebieg obejmuje również puste i uszkodzone źródła; ich odrzucenie jest
wynikiem do udokumentowania, nie powodem do poluzowania parsera. Raport nie
potwierdza dat terenowych, CRS, poprawności pomiarów, powtórzeń, geometrii
osnowy ani przyszłego eksportu. CI używa niezależnych małych wzorców P01 i
testów błędów, bez zależności od tego zewnętrznego korpusu lub sieci.
