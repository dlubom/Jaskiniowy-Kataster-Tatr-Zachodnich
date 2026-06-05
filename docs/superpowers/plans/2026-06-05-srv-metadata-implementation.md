# SRV Metadata Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add enforced metadata for active cave-survey `.SRV` files, normalize `_RAW` source packages, update repo skills, and prove that survey data and geometry are preserved.

**Architecture:** Put the reusable metadata parser/formatter in `src/jktz/metadata_contract.py`, keep validation reporting in `src/jktz/validation/metadata.py`, and expose migration/update operations through `scripts/srv_metadata.py`. The validator is a normal `jktz-validate` step; the script is used by skills and by the one-time atomic migration.

**Tech Stack:** Python 3.9, stdlib only for metadata tooling, existing `jktz.reporting.CheckFailed`, existing `uv run pytest` / `uv run ruff`, existing Survex/GDAL validation path.

---

## File Structure

- Create `src/jktz/metadata_contract.py`: field constants, SRV metadata parser/formatter, RAW README parser, source-reference resolver, active-shot scanner.
- Create `src/jktz/validation/metadata.py`: user-facing validation check that aggregates errors and raises `CheckFailed`.
- Create `scripts/srv_metadata.py`: CLI/helper for creating canonical RAW README files, inserting/updating SRV metadata blocks, appending `PROCESSING`, and computing RAW material hashes.
- Create `tests/test_metadata_contract.py`: parser, formatter, resolver, README parser, and active-shot scanner tests.
- Create `tests/test_validation_metadata.py`: validation behavior and error aggregation tests.
- Create `tests/test_srv_metadata_script.py`: script/helper idempotence tests.
- Modify `src/jktz/cli/validate.py`: add metadata as an early validation step and update step count.
- Modify `.claude/skills/add-cave/SKILL.md`: require `_RAW/01`, canonical RAW README, complete SRV metadata block, and `SOURCE_REF`.
- Modify `.claude/skills/svx-to-srv/SKILL.md`: map `*team`, `*instrument`, `*date`, and conversion actions into the new metadata contract.
- Modify `.claude/skills/average-shots/SKILL.md`: require helper-driven `UPDATE_DATE` and `PROCESSING` updates.
- Modify `CLAUDE.md`: replace the old metadata template and `_RAW` description with the new contract.
- Modify active data under `Poligony/`: normalize `_RAW`, add package README files, and insert metadata blocks.

## Task 1: Metadata Contract Module

**Files:**
- Create: `src/jktz/metadata_contract.py`
- Test: `tests/test_metadata_contract.py`

- [ ] **Step 1: Write parser tests for valid SRV metadata**

Add this test file:

```python
from __future__ import annotations

from pathlib import Path

import pytest

from jktz.metadata_contract import (
    MetadataError,
    RawReadme,
    SrvMetadata,
    format_srv_metadata,
    has_dated_or_declared_active_shots,
    is_active_srv_path,
    parse_raw_readme,
    parse_srv_metadata,
    resolve_source_ref,
)


VALID_BLOCK = """#[
CAVE_ID         "T.D-04.01"
CAVE_NAME       "Zbojecka Dziura"
SURVEY_ID       "ZBDZIU"
SURVEY_NAME     "Zbojecka Dziura"
UPDATE_DATE     "2026-06-05"
PROJECT_NAME    "Kataster jaskin tatrzanskich"
COORDINATOR     "Dariusz Lubomski"
COORDINATOR_EMAIL "darek.lubomski@gmail.com"
SOURCE_REF      "_RAW/01"
SOURCE_REF      "../_RAW/02"
LICENSE         "http://creativecommons.org/licenses/by-sa/4.0/"

TEAM            "J. Nowak"
TEAM            "J. Slusarczyk"
INSTRUMENT      "nieznane"
SURVEY_DATE     "2004-06-19"
SURVEY_GRADE    "BCRA:5D"
PROCESSING      "konwersja z arkusza"
#]

#prefix ZbojeckaDziura
0\t1\t13.30\t297\t-19
"""


def test_parse_srv_metadata_with_repeated_fields() -> None:
    parsed = parse_srv_metadata(Path("Poligony/Cave/CAVE.SRV"), VALID_BLOCK)

    assert parsed.single["CAVE_ID"] == "T.D-04.01"
    assert parsed.single["SURVEY_NAME"] == "Zbojecka Dziura"
    assert parsed.repeated["SOURCE_REF"] == ["_RAW/01", "../_RAW/02"]
    assert parsed.repeated["TEAM"] == ["J. Nowak", "J. Slusarczyk"]
    assert parsed.body.startswith("#prefix ZbojeckaDziura")


def test_format_srv_metadata_is_canonical_and_parseable() -> None:
    metadata = SrvMetadata(
        single={
            "CAVE_ID": "T.D-04.01",
            "CAVE_NAME": "Zbojecka Dziura",
            "SURVEY_ID": "ZBDZIU",
            "SURVEY_NAME": "Zbojecka Dziura",
            "UPDATE_DATE": "2026-06-05",
            "PROJECT_NAME": "Kataster jaskin tatrzanskich",
            "COORDINATOR": "Dariusz Lubomski",
            "COORDINATOR_EMAIL": "darek.lubomski@gmail.com",
            "LICENSE": "http://creativecommons.org/licenses/by-sa/4.0/",
        },
        repeated={
            "SOURCE_REF": ["_RAW/01"],
            "TEAM": ["J. Nowak"],
            "INSTRUMENT": ["nieznane"],
            "SURVEY_DATE": ["2004-06-19"],
            "SURVEY_GRADE": ["BCRA:5D"],
            "PROCESSING": ["konwersja z arkusza"],
        },
        body="",
    )

    text = format_srv_metadata(metadata)

    assert text.startswith("#[\n")
    assert 'CAVE_ID         "T.D-04.01"' in text
    assert 'SOURCE_REF      "_RAW/01"' in text
    assert text.endswith("#]\n\n")
    assert parse_srv_metadata(Path("Poligony/Cave/CAVE.SRV"), text).single["CAVE_ID"] == "T.D-04.01"
```

- [ ] **Step 2: Write parser tests for invalid SRV metadata**

Append:

```python
def test_rejects_missing_opening_metadata_block() -> None:
    with pytest.raises(MetadataError, match="must start with #\\["):
        parse_srv_metadata(Path("Poligony/Cave/CAVE.SRV"), "#prefix Cave\n")


def test_rejects_unknown_field_inside_block() -> None:
    text = VALID_BLOCK.replace('LICENSE         "http://creativecommons.org/licenses/by-sa/4.0/"', 'BOGUS           "x"')

    with pytest.raises(MetadataError, match="unknown field BOGUS"):
        parse_srv_metadata(Path("Poligony/Cave/CAVE.SRV"), text)


def test_rejects_duplicate_single_field() -> None:
    text = VALID_BLOCK.replace('CAVE_ID         "T.D-04.01"', 'CAVE_ID         "T.D-04.01"\nCAVE_ID         "T.D-04.02"')

    with pytest.raises(MetadataError, match="duplicate single field CAVE_ID"):
        parse_srv_metadata(Path("Poligony/Cave/CAVE.SRV"), text)


def test_rejects_unknown_structural_field_value() -> None:
    text = VALID_BLOCK.replace('SURVEY_ID       "ZBDZIU"', 'SURVEY_ID       "nieznane"')

    with pytest.raises(MetadataError, match="SURVEY_ID cannot be nieznane"):
        parse_srv_metadata(Path("Poligony/Cave/CAVE.SRV"), text)


def test_rejects_bad_date_and_grade_formats() -> None:
    bad_date = VALID_BLOCK.replace('SURVEY_DATE     "2004-06-19"', 'SURVEY_DATE     "19-06-2004"')
    with pytest.raises(MetadataError, match="SURVEY_DATE"):
        parse_srv_metadata(Path("Poligony/Cave/CAVE.SRV"), bad_date)

    bad_grade = VALID_BLOCK.replace('SURVEY_GRADE    "BCRA:5D"', 'SURVEY_GRADE    "BCRA 5D"')
    with pytest.raises(MetadataError, match="SURVEY_GRADE"):
        parse_srv_metadata(Path("Poligony/Cave/CAVE.SRV"), bad_grade)
```

- [ ] **Step 3: Write source-ref, README, and active-shot tests**

Append:

```python
RAW_README = """# Cave - source package

- **Status materiału:** dostępny
- **Pochodzenie danych:** J. Nowak
- **Autorzy pomiarów:** J. Nowak
- **Daty pomiarów:** 2004-06-19
- **Data pozyskania:** 2013-11-26
- **Dodał do _RAW:** Dariusz Lubomski
- **Licencja źródłowa:** nieznane
- **Kompletność:** pełny pomiar

## Zawartość

- `source.xlsx` - arkusz z pomiarami
"""


def test_resolve_source_ref_allows_sibling_and_parent_raw(tmp_path: Path) -> None:
    root = tmp_path / "Poligony"
    srv_dir = root / "System" / "Section"
    (srv_dir / "_RAW" / "01").mkdir(parents=True)
    (root / "System" / "_RAW" / "02").mkdir(parents=True)

    assert resolve_source_ref(srv_dir / "A.SRV", "_RAW/01", root) == srv_dir / "_RAW" / "01"
    assert resolve_source_ref(srv_dir / "A.SRV", "../_RAW/02", root) == root / "System" / "_RAW" / "02"


def test_resolve_source_ref_rejects_escape_and_non_raw_suffix(tmp_path: Path) -> None:
    root = tmp_path / "Poligony"
    srv = root / "Cave" / "A.SRV"
    srv.parent.mkdir(parents=True)

    with pytest.raises(MetadataError, match="outside Poligony"):
        resolve_source_ref(srv, "../../outside/_RAW/01", root)

    with pytest.raises(MetadataError, match="must end with _RAW/NN"):
        resolve_source_ref(srv, "sources/01", root)


def test_parse_raw_readme_contract() -> None:
    parsed = parse_raw_readme(Path("_RAW/01/README.md"), RAW_README)

    assert isinstance(parsed, RawReadme)
    assert parsed.fields["Status materiału"] == "dostępny"
    assert parsed.content_items == ["`source.xlsx` - arkusz z pomiarami"]


def test_parse_raw_readme_rejects_missing_field() -> None:
    with pytest.raises(MetadataError, match="Licencja źródłowa"):
        parse_raw_readme(Path("_RAW/01/README.md"), RAW_README.replace("- **Licencja źródłowa:** nieznane\n", ""))


def test_active_srv_scope() -> None:
    assert is_active_srv_path(Path("Poligony/Cave/CAVE.SRV"))
    assert not is_active_srv_path(Path("Poligony/OTWORY.SRV"))
    assert not is_active_srv_path(Path("Poligony/Cave/_RAW/01/source.SRV"))
    assert not is_active_srv_path(Path("Powierzchnia/Teren_10x10/POZIOM.SRV"))


def test_active_shot_scanner_requires_date_or_decl_for_nonzero_shots() -> None:
    assert has_dated_or_declared_active_shots("#date 2004-06-19\n0\t1\t1.0\t90\t0\n")
    assert has_dated_or_declared_active_shots("#Units DECL=0.819D\n0\t1\t1.0\t90\t0\n")
    assert has_dated_or_declared_active_shots("0\t1\t0\t0\t0\n")
    assert has_dated_or_declared_active_shots(";0\t1\t1.0\t90\t0\n")
    assert not has_dated_or_declared_active_shots("0\t1\t1.0\t90\t0\n")
```

- [ ] **Step 4: Run failing tests**

Run:

```bash
uv run pytest tests/test_metadata_contract.py -q
```

Expected: collection fails with `ModuleNotFoundError: No module named 'jktz.metadata_contract'`.

- [ ] **Step 5: Implement `src/jktz/metadata_contract.py`**

Create `src/jktz/metadata_contract.py` with:

```python
from __future__ import annotations

import posixpath
import re
from dataclasses import dataclass
from pathlib import Path

SINGLE_FIELDS = (
    "CAVE_ID",
    "CAVE_NAME",
    "SURVEY_ID",
    "SURVEY_NAME",
    "UPDATE_DATE",
    "PROJECT_NAME",
    "COORDINATOR",
    "COORDINATOR_EMAIL",
    "LICENSE",
)
REPEATED_FIELDS = ("SOURCE_REF", "TEAM", "INSTRUMENT", "SURVEY_DATE", "SURVEY_GRADE", "PROCESSING")
STRUCTURAL_FIELDS = {"CAVE_ID", "CAVE_NAME", "SURVEY_ID", "SURVEY_NAME", "SOURCE_REF", "LICENSE"}
ALL_FIELDS = set(SINGLE_FIELDS) | set(REPEATED_FIELDS)

RAW_FIELDS = (
    "Status materiału",
    "Pochodzenie danych",
    "Autorzy pomiarów",
    "Daty pomiarów",
    "Data pozyskania",
    "Dodał do _RAW",
    "Licencja źródłowa",
    "Kompletność",
)
RAW_STATUSES = {"dostępny", "częściowy", "niedostępny"}

_FIELD_RE = re.compile(r'^([A-Z][A-Z0-9_]*)\s+"([^"]*)"$')
_DATE_RE = re.compile(r"^\d{4}(-\d{2})?(-\d{2})?$")
_UPDATE_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_GRADE_RE = re.compile(r"^(nieznane|BCRA:([1-6X][A-D]?|nieznane)|[A-Z][A-Z0-9_-]*:[A-Za-z0-9._-]+)$")
_RAW_ITEM_RE = re.compile(r"^- \*\*([^*]+)\*\*:\s*(.*)$")
_SHOT_RE = re.compile(r"^\s*\S+\s+\S+\s+(-?\d+(?:\.\d+)?)\s+\S+\s+\S+")
_DATE_DIRECTIVE_RE = re.compile(r"^\s*#date\b", re.IGNORECASE)
_DECL_DIRECTIVE_RE = re.compile(r"^\s*#units\b.*\bDECL\s*=", re.IGNORECASE)


class MetadataError(ValueError):
    """Raised when SRV or RAW metadata violates the repository contract."""


@dataclass(frozen=True)
class SrvMetadata:
    single: dict[str, str]
    repeated: dict[str, list[str]]
    body: str


@dataclass(frozen=True)
class RawReadme:
    fields: dict[str, str]
    content_items: list[str]


def is_active_srv_path(path: Path) -> bool:
    parts = path.parts
    return path.suffix == ".SRV" and "_RAW" not in parts and parts[:1] == ("Poligony",) and path.as_posix() != "Poligony/OTWORY.SRV"


def _validate_date(name: str, value: str) -> None:
    if value == "nieznane":
        return
    if "/" in value:
        left, sep, right = value.partition("/")
        if not sep or not _DATE_RE.fullmatch(left) or not _DATE_RE.fullmatch(right):
            raise MetadataError(f"{name} has invalid date range {value!r}")
        return
    if not _DATE_RE.fullmatch(value):
        raise MetadataError(f"{name} has invalid date {value!r}")


def _validate_field(name: str, value: str) -> None:
    if name in STRUCTURAL_FIELDS and value == "nieznane":
        raise MetadataError(f"{name} cannot be nieznane")
    if name == "UPDATE_DATE" and value != "nieznane" and not _UPDATE_DATE_RE.fullmatch(value):
        raise MetadataError(f"UPDATE_DATE has invalid date {value!r}")
    if name == "SURVEY_DATE":
        _validate_date(name, value)
    if name == "SURVEY_GRADE" and not _GRADE_RE.fullmatch(value):
        raise MetadataError(f"SURVEY_GRADE has invalid value {value!r}")


def parse_srv_metadata(path: Path, text: str) -> SrvMetadata:
    if not text.startswith("#[\n"):
        raise MetadataError(f"{path.as_posix()} must start with #[")
    end = text.find("#]\n")
    if end == -1:
        raise MetadataError(f"{path.as_posix()} metadata block is not closed with #]")

    block = text[3:end]
    body = text[end + 3 :]
    single: dict[str, str] = {}
    repeated: dict[str, list[str]] = {name: [] for name in REPEATED_FIELDS}

    for line_num, line in enumerate(block.splitlines(), start=2):
        if not line.strip():
            continue
        match = _FIELD_RE.fullmatch(line)
        if not match:
            raise MetadataError(f"{path.as_posix()}:{line_num}: invalid metadata line {line!r}")
        name, value = match.groups()
        if name not in ALL_FIELDS:
            raise MetadataError(f"{path.as_posix()}:{line_num}: unknown field {name}")
        _validate_field(name, value)
        if name in SINGLE_FIELDS:
            if name in single:
                raise MetadataError(f"{path.as_posix()}:{line_num}: duplicate single field {name}")
            single[name] = value
        else:
            repeated[name].append(value)

    missing = [name for name in SINGLE_FIELDS if name not in single]
    missing.extend(name for name in REPEATED_FIELDS if not repeated[name])
    if missing:
        raise MetadataError(f"{path.as_posix()} missing metadata field(s): {', '.join(missing)}")

    return SrvMetadata(single=single, repeated=repeated, body=body.lstrip("\r\n"))


def format_srv_metadata(metadata: SrvMetadata) -> str:
    lines = ["#["]
    for name in SINGLE_FIELDS:
        if name == "LICENSE":
            for value in metadata.repeated["SOURCE_REF"]:
                lines.append(f'{ "SOURCE_REF":<16}"{value}"')
        lines.append(f'{name:<16}"{metadata.single[name]}"')
    lines.append("")
    for name in ("TEAM", "INSTRUMENT", "SURVEY_DATE", "SURVEY_GRADE", "PROCESSING"):
        for value in metadata.repeated[name]:
            lines.append(f'{name:<16}"{value}"')
    lines.append("#]")
    lines.append("")
    return "\n".join(lines) + "\n"


def resolve_source_ref(srv_path: Path, value: str, poligony_root: Path) -> Path:
    normalized = posixpath.normpath(value)
    parts = normalized.split("/")
    if len(parts) < 2 or parts[-2] != "_RAW" or not re.fullmatch(r"\d{2}", parts[-1]):
        raise MetadataError(f"SOURCE_REF {value!r} must end with _RAW/NN")
    if normalized.startswith("/"):
        raise MetadataError(f"SOURCE_REF {value!r} must be relative")

    resolved = (srv_path.parent / Path(normalized)).resolve()
    root = poligony_root.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise MetadataError(f"SOURCE_REF {value!r} resolves outside Poligony") from exc
    return resolved


def parse_raw_readme(path: Path, text: str) -> RawReadme:
    fields: dict[str, str] = {}
    in_contents = False
    content_items: list[str] = []
    for line in text.splitlines():
        if line == "## Zawartość":
            in_contents = True
            continue
        if in_contents:
            if line.startswith("- "):
                content_items.append(line[2:])
            continue
        match = _RAW_ITEM_RE.fullmatch(line)
        if match:
            fields[match.group(1)] = match.group(2).strip()

    missing = [name for name in RAW_FIELDS if name not in fields]
    if missing:
        raise MetadataError(f"{path.as_posix()} missing RAW field(s): {', '.join(missing)}")
    if fields["Status materiału"] not in RAW_STATUSES:
        raise MetadataError(f"{path.as_posix()} invalid Status materiału {fields['Status materiału']!r}")
    if not content_items:
        raise MetadataError(f"{path.as_posix()} missing ## Zawartość items")
    if fields["Status materiału"] != "niedostępny" and content_items == ["Brak materiałów źródłowych."]:
        raise MetadataError(f"{path.as_posix()} available package cannot have empty source inventory")
    return RawReadme(fields=fields, content_items=content_items)


def has_dated_or_declared_active_shots(text: str) -> bool:
    has_orientation_state = False
    for raw_line in text.splitlines():
        line = raw_line.split(";", 1)[0].strip()
        if not line:
            continue
        if _DATE_DIRECTIVE_RE.match(line) or _DECL_DIRECTIVE_RE.match(line):
            has_orientation_state = True
            continue
        if line.startswith("#"):
            continue
        match = _SHOT_RE.match(line)
        if not match:
            continue
        distance = float(match.group(1))
        if distance == 0:
            continue
        if not has_orientation_state:
            return False
    return True
```

- [ ] **Step 6: Run contract tests**

Run:

```bash
uv run pytest tests/test_metadata_contract.py -q
```

Expected: all tests pass.

- [ ] **Step 7: Commit contract module**

Run:

```bash
git add src/jktz/metadata_contract.py tests/test_metadata_contract.py
git commit -m "[codex] Dodaj kontrakt metadanych SRV"
```

## Task 2: Metadata Validation Module

**Files:**
- Create: `src/jktz/validation/metadata.py`
- Test: `tests/test_validation_metadata.py`

- [ ] **Step 1: Write validation tests**

Create `tests/test_validation_metadata.py`:

```python
from __future__ import annotations

from pathlib import Path

import pytest

from jktz.reporting import CheckFailed
from jktz.validation import metadata


def _raw_readme(status: str = "dostępny") -> str:
    item = "`source.xlsx` - arkusz" if status != "niedostępny" else "Brak materiałów źródłowych."
    return (
        "# Cave - source package\n\n"
        f"- **Status materiału:** {status}\n"
        "- **Pochodzenie danych:** J. Nowak\n"
        "- **Autorzy pomiarów:** J. Nowak\n"
        "- **Daty pomiarów:** 2004-06-19\n"
        "- **Data pozyskania:** 2013-11-26\n"
        "- **Dodał do _RAW:** Dariusz Lubomski\n"
        "- **Licencja źródłowa:** nieznane\n"
        "- **Kompletność:** pełny pomiar\n\n"
        "## Zawartość\n\n"
        f"- {item}\n"
    )


def _srv(source_ref: str = "_RAW/01", body: str = "#date 2004-06-19\n0\t1\t1.0\t90\t0\n") -> str:
    return (
        "#[\n"
        'CAVE_ID         "T.D-04.01"\n'
        'CAVE_NAME       "Zbojecka Dziura"\n'
        'SURVEY_ID       "ZBDZIU"\n'
        'SURVEY_NAME     "Zbojecka Dziura"\n'
        'UPDATE_DATE     "2026-06-05"\n'
        'PROJECT_NAME    "Kataster jaskin tatrzanskich"\n'
        'COORDINATOR     "Dariusz Lubomski"\n'
        'COORDINATOR_EMAIL "darek.lubomski@gmail.com"\n'
        f'SOURCE_REF      "{source_ref}"\n'
        'LICENSE         "http://creativecommons.org/licenses/by-sa/4.0/"\n'
        "\n"
        'TEAM            "J. Nowak"\n'
        'INSTRUMENT      "nieznane"\n'
        'SURVEY_DATE     "2004-06-19"\n'
        'SURVEY_GRADE    "BCRA:5D"\n'
        'PROCESSING      "konwersja z arkusza"\n'
        "#]\n\n"
        + body
    )


def test_metadata_check_passes_for_valid_srv_and_raw(tmp_path: Path) -> None:
    cave = tmp_path / "Poligony" / "Cave"
    raw = cave / "_RAW" / "01"
    raw.mkdir(parents=True)
    (raw / "README.md").write_text(_raw_readme())
    (raw / "source.xlsx").write_text("raw")
    (cave / "CAVE.SRV").write_text(_srv())

    metadata.check(root=tmp_path / "Poligony")


def test_metadata_check_reports_all_errors(tmp_path: Path) -> None:
    cave = tmp_path / "Poligony" / "Cave"
    raw = cave / "_RAW" / "01"
    raw.mkdir(parents=True)
    (raw / "README.md").write_text(_raw_readme().replace("- **Licencja źródłowa:** nieznane\n", ""))
    (raw / "loose.txt").write_text("raw")
    (cave / "BAD.SRV").write_text("#prefix Cave\n0\t1\t1.0\t90\t0\n")
    (cave / "CAVE.SRV").write_text(_srv(body="0\t1\t1.0\t90\t0\n"))

    with pytest.raises(CheckFailed) as excinfo:
        metadata.check(root=tmp_path / "Poligony")

    msg = str(excinfo.value)
    assert "BAD.SRV" in msg
    assert "must start with #[" in msg
    assert "Licencja źródłowa" in msg
    assert "active shot without #date or DECL" in msg


def test_metadata_check_allows_parent_source_ref(tmp_path: Path) -> None:
    system = tmp_path / "Poligony" / "System"
    section = system / "Section"
    raw = system / "_RAW" / "02"
    raw.mkdir(parents=True)
    section.mkdir(parents=True)
    (raw / "README.md").write_text(_raw_readme())
    (raw / "source.svx").write_text("raw")
    (section / "SECTION.SRV").write_text(_srv(source_ref="../_RAW/02"))

    metadata.check(root=tmp_path / "Poligony")


def test_metadata_check_ignores_raw_and_otwory(tmp_path: Path) -> None:
    root = tmp_path / "Poligony"
    raw = root / "Cave" / "_RAW"
    raw.mkdir(parents=True)
    (raw / "ORIG.SRV").write_text("0\t1\t1.0\t90\t0\n")
    (root / "OTWORY.SRV").write_text("#fix Cave:0 E19.9 N49.2 1000m\n")

    metadata.check(root=root)
```

- [ ] **Step 2: Run failing validation tests**

Run:

```bash
uv run pytest tests/test_validation_metadata.py -q
```

Expected: fails with `ImportError: cannot import name 'metadata'`.

- [ ] **Step 3: Implement validation module**

Create `src/jktz/validation/metadata.py`:

```python
from __future__ import annotations

from pathlib import Path

from jktz.metadata_contract import (
    MetadataError,
    is_active_srv_path,
    parse_raw_readme,
    parse_srv_metadata,
    resolve_source_ref,
    has_dated_or_declared_active_shots,
)
from jktz.reporting import CheckFailed


def _root_for(path: Path) -> Path:
    try:
        idx = path.parts.index("Poligony")
    except ValueError:
        return path
    return Path(*path.parts[: idx + 1])


def _check_raw_root(raw_dir: Path, errors: list[str]) -> None:
    for child in raw_dir.iterdir():
        if child.name == "README.md":
            continue
        if child.is_dir() and len(child.name) == 2 and child.name.isdigit():
            continue
        errors.append(f"  {child.as_posix()}: material left directly under _RAW")


def _check_raw_package(package: Path, errors: list[str]) -> None:
    readme = package / "README.md"
    if not readme.exists():
        errors.append(f"  {readme.as_posix()}: missing RAW package README.md")
        return
    try:
        parsed = parse_raw_readme(readme, readme.read_text(encoding="utf-8"))
    except MetadataError as exc:
        errors.append(f"  {exc}")
        return
    material_children = [p for p in package.iterdir() if p.name != "README.md"]
    if not material_children and parsed.fields["Status materiału"] != "niedostępny":
        errors.append(f"  {package.as_posix()}: empty RAW package must have status niedostępny")


def check(root: Path = Path("Poligony")) -> None:
    errors: list[str] = []
    root = root.resolve()

    for raw_dir in sorted(root.rglob("_RAW")):
        if not raw_dir.is_dir():
            continue
        _check_raw_root(raw_dir, errors)
        for package in sorted(raw_dir.iterdir()):
            if package.is_dir() and len(package.name) == 2 and package.name.isdigit():
                _check_raw_package(package, errors)

    for path in sorted(root.rglob("*.SRV")):
        rel = path.relative_to(root.parent)
        if not is_active_srv_path(rel):
            continue
        text = path.read_text(encoding="latin-1")
        try:
            parsed = parse_srv_metadata(rel, text)
        except MetadataError as exc:
            errors.append(f"  {exc}")
            continue
        if not has_dated_or_declared_active_shots(parsed.body):
            errors.append(f"  {rel.as_posix()}: active shot without #date or DECL")
        for source_ref in parsed.repeated["SOURCE_REF"]:
            try:
                package = resolve_source_ref(path, source_ref, root)
            except MetadataError as exc:
                errors.append(f"  {rel.as_posix()}: {exc}")
                continue
            readme = package / "README.md"
            if not package.exists():
                errors.append(f"  {rel.as_posix()}: SOURCE_REF {source_ref!r} does not exist")
            elif not readme.exists():
                errors.append(f"  {rel.as_posix()}: SOURCE_REF {source_ref!r} missing README.md")

    if errors:
        raise CheckFailed("ERROR: SRV metadata contract violation:\n" + "\n".join(errors))
```

- [ ] **Step 4: Run validation tests**

Run:

```bash
uv run pytest tests/test_metadata_contract.py tests/test_validation_metadata.py -q
```

Expected: all tests pass.

- [ ] **Step 5: Commit validation module**

Run:

```bash
git add src/jktz/validation/metadata.py tests/test_validation_metadata.py
git commit -m "[codex] Dodaj walidacje metadanych SRV"
```

## Task 3: Integrate Metadata Validation into `jktz-validate`

**Files:**
- Modify: `src/jktz/cli/validate.py`
- Test: existing validation tests through `uv run pytest`

- [ ] **Step 1: Modify imports and step count**

In `src/jktz/cli/validate.py`, add `metadata` to the validation import list and change `_TOTAL_STEPS = 11` to `_TOTAL_STEPS = 12`.

Expected import block shape:

```python
from jktz.validation import (
    cavern_warnings,
    coordinates,
    decimal_format,
    directives,
    empty_shapefiles,
    filenames,
    metadata,
    non_ascii,
    prefixes,
    shapefiles_count,
    shapefiles_extent,
    unattached,
)

_TOTAL_STEPS = 12
```

- [ ] **Step 2: Add metadata as step 2 and renumber later steps**

In `main()`, run metadata immediately after filename validation and before legacy directive/content checks:

```python
_run(1, "Checking SRV filenames format", "SRV filenames format", filenames.check)
_run(2, "Checking SRV metadata contract", "SRV metadata contract", metadata.check)
_run(3, "Checking for invalid directives", "Invalid directives", directives.check)
```

Renumber every later hard-coded progress line so rendered entrances becomes `[7/12]`, cavern compile `[9/12]`, unattached `[10/12]`, warnings `[11/12]`, and exports `[12/12]`.

- [ ] **Step 3: Run formatting and tests**

Run:

```bash
uv run ruff format --check src tests
uv run ruff check src tests
uv run pytest
```

Expected: pass, except `uv run pytest` may fail if repository fixtures depend on current data before migration. If it fails only because metadata validation is now active against unmigrated real data, do not weaken the validator; continue to Task 4 and Task 5 before the full gate.

- [ ] **Step 4: Commit validation integration**

Run:

```bash
git add src/jktz/cli/validate.py
git commit -m "[codex] Podlacz walidacje metadanych do jktz-validate"
```

## Task 4: Metadata Helper Script

**Files:**
- Create: `scripts/srv_metadata.py`
- Test: `tests/test_srv_metadata_script.py`

- [ ] **Step 1: Write helper tests**

Create `tests/test_srv_metadata_script.py`:

```python
from __future__ import annotations

from pathlib import Path

from scripts import srv_metadata


def test_replace_or_insert_metadata_preserves_body() -> None:
    original = "#prefix Cave\n#date 2004-06-19\n0\t1\t1.0\t90\t0\n"
    metadata = srv_metadata.default_metadata(
        cave_id="T.X-00.00",
        cave_name="Cave",
        survey_id="CAVE",
        survey_name="Cave",
        source_refs=["_RAW/01"],
        update_date="2026-06-05",
    )

    updated = srv_metadata.replace_or_insert_metadata(original, metadata)

    assert updated.startswith("#[\n")
    assert updated.endswith("#date 2004-06-19\n0\t1\t1.0\t90\t0\n")
    assert srv_metadata.replace_or_insert_metadata(updated, metadata) == updated


def test_append_processing_is_idempotent() -> None:
    metadata = srv_metadata.default_metadata(
        cave_id="T.X-00.00",
        cave_name="Cave",
        survey_id="CAVE",
        survey_name="Cave",
        source_refs=["_RAW/01"],
        update_date="2026-06-05",
    )

    updated = srv_metadata.append_processing(metadata, "usredniono pomiary przod/tyl")
    updated_again = srv_metadata.append_processing(updated, "usredniono pomiary przod/tyl")

    assert updated.repeated["PROCESSING"].count("usredniono pomiary przod/tyl") == 1
    assert updated_again == updated


def test_canonical_raw_readme_for_missing_materials() -> None:
    text = srv_metadata.canonical_raw_readme(
        title="Cave - missing source package",
        status="niedostępny",
        origin="nieznane",
        authors="nieznane",
        dates="nieznane",
        acquired="nieznane",
        added_by="nieznane",
        license_value="nieznane",
        completeness="brak materiałów źródłowych",
        contents=["Brak materiałów źródłowych."],
    )

    assert "- **Status materiału:** niedostępny" in text
    assert "## Zawartość" in text
    assert "- Brak materiałów źródłowych." in text


def test_material_hashes_skip_readmes(tmp_path: Path) -> None:
    raw = tmp_path / "_RAW" / "01"
    raw.mkdir(parents=True)
    (raw / "README.md").write_text("metadata")
    (raw / "source.srv").write_text("raw")

    hashes = srv_metadata.material_hashes(tmp_path)

    assert len(hashes) == 1
    assert hashes[0].path.as_posix().endswith("source.srv")
```

- [ ] **Step 2: Run failing helper tests**

Run:

```bash
uv run pytest tests/test_srv_metadata_script.py -q
```

Expected: import failure for `scripts.srv_metadata`.

- [ ] **Step 3: Make `scripts` importable for tests**

If `tests/test_srv_metadata_script.py` cannot import `scripts.srv_metadata` because `scripts/` lacks `__init__.py`, create an empty `scripts/__init__.py`. Commit it with the helper script in this task.

- [ ] **Step 4: Implement helper script functions**

Create `scripts/srv_metadata.py`:

```python
from __future__ import annotations

import argparse
import hashlib
from dataclasses import dataclass
from pathlib import Path

from jktz.metadata_contract import SrvMetadata, format_srv_metadata, parse_srv_metadata


@dataclass(frozen=True)
class MaterialHash:
    path: Path
    sha256: str


def default_metadata(
    *,
    cave_id: str,
    cave_name: str,
    survey_id: str,
    survey_name: str,
    source_refs: list[str],
    update_date: str,
    project_name: str = "Kataster jaskin tatrzanskich",
    coordinator: str = "nieznane",
    coordinator_email: str = "nieznane",
    license_value: str = "http://creativecommons.org/licenses/by-sa/4.0/",
    team: list[str] | None = None,
    instruments: list[str] | None = None,
    survey_dates: list[str] | None = None,
    survey_grade: str = "nieznane",
    processing: list[str] | None = None,
) -> SrvMetadata:
    return SrvMetadata(
        single={
            "CAVE_ID": cave_id,
            "CAVE_NAME": cave_name,
            "SURVEY_ID": survey_id,
            "SURVEY_NAME": survey_name,
            "UPDATE_DATE": update_date,
            "PROJECT_NAME": project_name,
            "COORDINATOR": coordinator,
            "COORDINATOR_EMAIL": coordinator_email,
            "LICENSE": license_value,
        },
        repeated={
            "SOURCE_REF": source_refs,
            "TEAM": team or ["nieznane"],
            "INSTRUMENT": instruments or ["nieznane"],
            "SURVEY_DATE": survey_dates or ["nieznane"],
            "SURVEY_GRADE": [survey_grade],
            "PROCESSING": processing or ["nieznane"],
        },
        body="",
    )


def replace_or_insert_metadata(text: str, metadata: SrvMetadata) -> str:
    try:
        existing = parse_srv_metadata(Path("Poligony/MEMORY.SRV"), text)
        body = existing.body
    except Exception:
        body = text.lstrip("\r\n")
    return format_srv_metadata(metadata) + body


def append_processing(metadata: SrvMetadata, note: str) -> SrvMetadata:
    values = [value for value in metadata.repeated["PROCESSING"] if value != "nieznane"]
    if note not in values:
        values.append(note)
    repeated = dict(metadata.repeated)
    repeated["PROCESSING"] = values or ["nieznane"]
    return SrvMetadata(single=dict(metadata.single), repeated=repeated, body=metadata.body)


def canonical_raw_readme(
    *,
    title: str,
    status: str,
    origin: str,
    authors: str,
    dates: str,
    acquired: str,
    added_by: str,
    license_value: str,
    completeness: str,
    contents: list[str],
) -> str:
    lines = [
        f"# {title}",
        "",
        f"- **Status materiału:** {status}",
        f"- **Pochodzenie danych:** {origin}",
        f"- **Autorzy pomiarów:** {authors}",
        f"- **Daty pomiarów:** {dates}",
        f"- **Data pozyskania:** {acquired}",
        f"- **Dodał do _RAW:** {added_by}",
        f"- **Licencja źródłowa:** {license_value}",
        f"- **Kompletność:** {completeness}",
        "",
        "## Zawartość",
        "",
    ]
    lines.extend(f"- {item}" for item in contents)
    return "\n".join(lines) + "\n"


def material_hashes(root: Path) -> list[MaterialHash]:
    hashes: list[MaterialHash] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name == "README.md":
            continue
        if "_RAW" not in path.parts:
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        hashes.append(MaterialHash(path=path, sha256=digest))
    return hashes


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage JKTZ SRV metadata helpers.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    hash_cmd = sub.add_parser("hash-raw")
    hash_cmd.add_argument("root", type=Path, nargs="?", default=Path("Poligony"))
    args = parser.parse_args()
    if args.cmd == "hash-raw":
        for item in material_hashes(args.root):
            print(f"{item.sha256}  {item.path.as_posix()}")
        return 0
    raise AssertionError(args.cmd)


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Run helper tests**

Run:

```bash
uv run pytest tests/test_srv_metadata_script.py tests/test_metadata_contract.py -q
```

Expected: pass.

- [ ] **Step 6: Commit helper script**

Run:

```bash
git add scripts/srv_metadata.py scripts/__init__.py tests/test_srv_metadata_script.py
git commit -m "[codex] Dodaj helper metadanych SRV"
```

If `scripts/__init__.py` was not needed, omit it from `git add`.

## Task 5: Atomic Data Migration

**Files:**
- Modify: many `Poligony/**/*.SRV` outside `_RAW`
- Move/Create: many `Poligony/**/_RAW/NN/**`
- Create/Modify: `Poligony/**/_RAW/NN/README.md`

- [ ] **Step 1: Capture pre-migration RAW material hashes**

Run:

```bash
uv run python scripts/srv_metadata.py hash-raw Poligony > /private/tmp/jktz-raw-before.sha256
wc -l /private/tmp/jktz-raw-before.sha256
```

Expected: nonzero line count. The exact count is file-state-dependent.

- [ ] **Step 2: Capture pre-migration compiled geometry baseline**

Run:

```bash
env UV_CACHE_DIR=/private/tmp/uv-cache uv run jktz-validate
cp KATASTER.3d /private/tmp/jktz-metadata-before.3d
```

Expected: validation passes before the migration begins. If this fails for an existing known environmental dependency such as missing Survex/GDAL, stop and fix the environment rather than continuing without a baseline.

- [ ] **Step 3: Normalize `_RAW` directories**

Use `git mv` for tracked material moves so history remains readable. Apply these deterministic rules:

- If `_RAW/` already contains numbered packages, keep them.
- If `_RAW/` is flat, create `_RAW/01/`, move every non-README material file/directory into `_RAW/01/`, and convert the old `_RAW/README.md` into `_RAW/01/README.md`.
- If `_RAW/` has no README, create `_RAW/01/README.md` with known values from neighboring active `.SRV` metadata or `nieznane`.
- If an active survey directory has no `_RAW`, create `_RAW/01/README.md` with status `niedostępny`.

Run these discovery commands while migrating:

```bash
find Poligony -type d -name _RAW | sort > /private/tmp/jktz-raw-dirs.txt
find Poligony -type f -name '*.SRV' ! -path '*/_RAW/*' ! -path 'Poligony/OTWORY.SRV' | sort > /private/tmp/jktz-active-srv.txt
```

Expected: every active `.SRV` in `/private/tmp/jktz-active-srv.txt` has a reachable `_RAW/NN` package after migration.

- [ ] **Step 4: Insert active SRV metadata headers**

For each active `.SRV`, insert or replace the leading `#[ ... #]` block using the helper contract. Fill values from current file headers and `_RAW/NN/README.md` when available. Use these defaults when unknown:

```text
UPDATE_DATE "2026-06-05"
PROJECT_NAME "Kataster jaskin tatrzanskich"
COORDINATOR "nieznane"
COORDINATOR_EMAIL "nieznane"
TEAM "nieznane"
INSTRUMENT "nieznane"
SURVEY_DATE "nieznane"
SURVEY_GRADE "nieznane"
PROCESSING "nieznane"
```

Do not keep `DATA_SOURCE` in active `.SRV`. Preserve its value in the referenced RAW package README under `Pochodzenie danych`.

- [ ] **Step 5: Run metadata validation and fix reported data-contract errors**

Run:

```bash
uv run pytest tests/test_validation_metadata.py -q
env UV_CACHE_DIR=/private/tmp/uv-cache uv run jktz-validate
```

Expected: metadata step passes. If later steps fail, investigate normally; do not weaken metadata validation to pass unrelated failures.

- [ ] **Step 6: Compare RAW material hashes**

Run:

```bash
uv run python scripts/srv_metadata.py hash-raw Poligony > /private/tmp/jktz-raw-after.sha256
cut -d' ' -f1 /private/tmp/jktz-raw-before.sha256 | sort > /private/tmp/jktz-raw-before-hashes.txt
cut -d' ' -f1 /private/tmp/jktz-raw-after.sha256 | sort > /private/tmp/jktz-raw-after-hashes.txt
diff -u /private/tmp/jktz-raw-before-hashes.txt /private/tmp/jktz-raw-after-hashes.txt
```

Expected: empty diff. If non-empty, a material file changed or was lost; stop and repair before committing.

- [ ] **Step 7: Compare compiled geometry**

Run:

```bash
env UV_CACHE_DIR=/private/tmp/uv-cache uv run jktz-validate
cp KATASTER.3d /private/tmp/jktz-metadata-after.3d
diffpos /private/tmp/jktz-metadata-before.3d /private/tmp/jktz-metadata-after.3d 0
```

Expected: no output from `diffpos`. If metadata comments only were changed, compiled geometry must be identical.

- [ ] **Step 8: Commit data migration**

Run:

```bash
git status --short
git add Poligony
git commit -m "[codex] Uzupelnij metadane pomiarow SRV i paczek RAW"
```

## Task 6: Update Repo Skills and Documentation

**Files:**
- Modify: `.claude/skills/add-cave/SKILL.md`
- Modify: `.claude/skills/svx-to-srv/SKILL.md`
- Modify: `.claude/skills/average-shots/SKILL.md`
- Modify: `CLAUDE.md`

- [ ] **Step 1: Update `add-cave` skill**

Replace its `_RAW` README section with the canonical `_RAW/01/README.md` contract and replace the old Step 9 metadata template with one containing `SOURCE_REF`, `SURVEY_DATE`, `SURVEY_GRADE`, and `PROCESSING`. The active SRV template must not contain `DATA_SOURCE`.

Use this SRV header in the skill:

```text
#[
CAVE_ID         "T.X-00.00"
CAVE_NAME       "Cave Name ASCII"
SURVEY_ID       "SURVEY_ID"
SURVEY_NAME     "Survey name"
UPDATE_DATE     "2026-06-05"
PROJECT_NAME    "Kataster jaskin tatrzanskich"
COORDINATOR     "nieznane"
COORDINATOR_EMAIL "nieznane"
SOURCE_REF      "_RAW/01"
LICENSE         "http://creativecommons.org/licenses/by-sa/4.0/"

TEAM            "nieznane"
INSTRUMENT      "nieznane"
SURVEY_DATE     "nieznane"
SURVEY_GRADE    "nieznane"
PROCESSING      "utworzono aktywny plik SRV z materialow zrodlowych"
#]
```

- [ ] **Step 2: Update `svx-to-srv` skill**

Change directive mapping so:

- `*team` maps to repeated `TEAM`;
- `*instrument` maps to repeated `INSTRUMENT`;
- `*date` maps to repeated `SURVEY_DATE` and operative `#date`;
- conversion adds `PROCESSING "konwersja SVX -> SRV"`;
- helper usage is required to create or update metadata blocks.

- [ ] **Step 3: Update `average-shots` skill**

Replace the current instruction that only updates `UPDATE_DATE` with:

```markdown
After averaging, run the repo metadata helper or update the metadata block so:
- `UPDATE_DATE` is today's date (`YYYY-MM-DD`)
- `PROCESSING "usredniono pomiary przod/tyl"` is present exactly once
- all existing `SOURCE_REF`, `TEAM`, `INSTRUMENT`, `SURVEY_DATE`, and `SURVEY_GRADE` lines are preserved
```

- [ ] **Step 4: Update `CLAUDE.md`**

Replace the old survey-file metadata template and `_RAW` rules with a concise summary that points to:

```markdown
docs/superpowers/specs/2026-06-04-srv-metadata-design.md
```

Include the non-negotiable rules:

- active `.SRV` metadata is mandatory;
- `_RAW` material files are never modified;
- `_RAW/NN/README.md` is metadata and may be updated;
- `DATA_SOURCE` is deprecated in active `.SRV`;
- `SOURCE_REF` is the active-to-RAW link.

- [ ] **Step 5: Run doc and code checks**

Run:

```bash
git diff --check
uv run ruff format --check src scripts tests
uv run ruff check src scripts tests
uv run pytest
```

Expected: pass.

- [ ] **Step 6: Commit skills and documentation**

Run:

```bash
git add .claude/skills/add-cave/SKILL.md .claude/skills/svx-to-srv/SKILL.md .claude/skills/average-shots/SKILL.md CLAUDE.md
git commit -m "[codex] Zaktualizuj skills pod kontrakt metadanych"
```

## Task 7: Final Validation and Evidence

**Files:**
- No planned source files; this task records proof in the final response.

- [ ] **Step 1: Run full local gate**

Run:

```bash
git diff --check
uv run ruff format --check src scripts tests
uv run ruff check src scripts tests
uv run pytest
env UV_CACHE_DIR=/private/tmp/uv-cache uv run jktz-validate
```

Expected: all pass. If `jktz-validate` fails because Survex/GDAL is unavailable, rerun only after fixing the environment; do not report success without the full gate.

- [ ] **Step 2: Re-run RAW hash proof**

Run:

```bash
uv run python scripts/srv_metadata.py hash-raw Poligony > /private/tmp/jktz-raw-final.sha256
cut -d' ' -f1 /private/tmp/jktz-raw-before.sha256 | sort > /private/tmp/jktz-raw-before-final-hashes.txt
cut -d' ' -f1 /private/tmp/jktz-raw-final.sha256 | sort > /private/tmp/jktz-raw-final-hashes.txt
diff -u /private/tmp/jktz-raw-before-final-hashes.txt /private/tmp/jktz-raw-final-hashes.txt
```

Expected: empty diff.

- [ ] **Step 3: Re-run geometry proof**

Run:

```bash
diffpos /private/tmp/jktz-metadata-before.3d /private/tmp/jktz-metadata-after.3d 0
```

Expected: no output.

- [ ] **Step 4: Inspect final git status and commit log**

Run:

```bash
git status --short --branch
git log --oneline --decorate -5
```

Expected: branch contains the spec commit plus implementation commits; working tree is clean unless generated validation artifacts are known ignored files.

- [ ] **Step 5: Final response**

Report:

- commits created;
- validation commands and outcomes;
- RAW hash proof path and result;
- geometry proof result;
- any remaining `nieznane` values that deserve follow-up;
- whether the branch is ahead of `origin/master`.
