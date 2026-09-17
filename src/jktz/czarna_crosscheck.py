"""Reproducible, source-separated arithmetic audit of Czarna's 78 journal legs.

A numerical agreement is corroboration, never an instruction to correct a scan.
All ranking exclusions and checkpoint interpretations are explicit reviewed inputs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path

from jktz.czarna_model_readings import read_model

CAVE = Path("Poligony/D_Koscieliska/Organy/Czarna")
FIELDS = ("D", "A", "V", "Lh", "dh")
PAIRS = [(str(i), str(i + 1)) for i in range(76)] + [("6", "a"), ("a", "b")]
INITIAL_COMMIT = "74723744834ee9badf4b5334f9319de651c73c6c"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_srv(text: str) -> list[dict]:
    rows = []
    pending = []
    for lineno, line in enumerate(text.splitlines(), 1):
        if line.startswith("; DO_WERYFIKACJI:"):
            pending.append(line)
        if not re.match(r"^(?:\d+|a)\s+(?:\d+|a|b)\s", line):
            continue
        body, comment = line.split(";", 1)
        start, end, distance, azimuth, inclination = body.split()
        auxiliary = dict(re.findall(r"(Lh|dh)_scan=([+\-\d.]+)", comment))
        values = dict(
            zip(
                FIELDS,
                [
                    float(distance),
                    None if azimuth == "--" else float(azimuth),
                    float(inclination),
                    float(auxiliary["Lh"]),
                    float(auxiliary["dh"]),
                ],
            )
        )
        alternatives = {}
        for note in pending:
            match = re.search(
                r"DO_WERYFIKACJI: ([DAV])=.*?(?:mozliwy odczyt |dawne )([+\-\d.]+)", note
            )
            if match:
                alternatives[match[1]] = [float(match[2].rstrip("."))]
            else:
                raise ValueError(f"Unrecognized uncertainty note: {note}")
        rows.append(
            {
                "from": start,
                "to": end,
                "line": lineno,
                "raw": line,
                "values": values,
                "alternatives": alternatives,
                "uncertain_fields": list(alternatives),
                "uncertainty_notes": pending,
            }
        )
        pending = []
    if [pair(row) for row in rows] != PAIRS:
        raise ValueError("SRV must contain exactly the ordered 78 journal legs")
    return rows


def pair(row: dict) -> tuple[str, str]:
    return row["from"], row["to"]


def arithmetic(values: dict) -> dict:
    """Use displayed degree values exactly; no GNSS, fitting or uncertainty inflation."""
    d, v, h, z = (values.get(field) for field in ("D", "V", "Lh", "dh"))
    if d is None or v is None:
        return {"status": "missing_D_or_V"}
    theta = math.radians(v)
    expected_h, expected_z = d * math.cos(theta), d * math.sin(theta)
    residuals = {
        "Lh": None if h is None else h - expected_h,
        "dh": None if z is None else z - expected_z,
    }
    return {
        "status": "complete" if h is not None and z is not None else "missing_auxiliary",
        "calculated_Lh": expected_h,
        "calculated_dh": expected_z,
        "residual_scan_minus_calculated": residuals,
        "strict_rounding_0_005m": {
            f: None if x is None else abs(x) <= 0.005000001 for f, x in residuals.items()
        },
        "within_0_05m": {
            f: None if x is None else abs(x) <= 0.050000001 for f, x in residuals.items()
        },
        "norm_distance_from_aux": None if h is None or z is None else math.hypot(h, z),
        "norm_residual_m": None if h is None or z is None else math.hypot(h, z) - d,
        "inclination_from_aux_deg": None
        if h is None or z is None
        else math.degrees(math.atan2(z, h)),
        "Lh_equals_D_at_nonzero_V": h == d and v != 0,
        "azimuth_testable": False,
    }


def unique_readings(rows: list[dict]) -> dict:
    """First photo is the primary answer, repeated photos are retained but not re-voted."""
    result = {}
    for row in rows:
        key = pair(row)
        if key not in result:
            result[key] = {**row, "repeat_lines": [], "repeat_conflicts": []}
        else:
            first = result[key]
            first["repeat_lines"].append(row["line"])
            for f in FIELDS:
                if first["values"][f] != row["values"][f]:
                    first["repeat_conflicts"].append(
                        {"field": f, "line": row["line"], "value": row["values"][f]}
                    )
    return result


def compare_model(rows: list[dict], reference: list[dict]) -> dict:
    unique = unique_readings(rows)
    counters = {f: Counter() for f in FIELDS}
    mismatches, excluded = [], []
    for ref in reference:
        key = pair(ref)
        row = unique.get(key)
        for f in FIELDS:
            if f in ref["uncertain_fields"]:
                excluded.append({"from": key[0], "to": key[1], "field": f})
                continue
            counts = counters[f]
            counts["assessed"] += 1
            wanted = ref["values"][f]
            if row is None:
                counts["missing"] += 1
                mismatches.append(
                    {
                        "from": key[0],
                        "to": key[1],
                        "field": f,
                        "reference": wanted,
                        "primary": None,
                        "status": "missing_pair",
                    }
                )
                continue
            got = row["values"][f]
            if got == wanted:
                counts["correct"] += 1
                counts["including_alternatives"] += 1
            else:
                counts["wrong"] += 1
                alternative = wanted in row.get("alternatives", {}).get(f, [])
                counts["including_alternatives"] += int(alternative)
                mismatches.append(
                    {
                        "from": key[0],
                        "to": key[1],
                        "field": f,
                        "line": row["line"],
                        "reference": wanted,
                        "primary": got,
                        "correct_in_alternatives": alternative,
                        "status": "different",
                    }
                )
    totals = sum(counters.values(), Counter())
    return {
        "counts": dict(totals),
        "by_field": {f: dict(c) for f, c in counters.items()},
        "mismatches": mismatches,
        "excluded": excluded,
        "rows_raw": len(rows),
        "pairs_unique": len(unique),
        "extra_pairs": [list(p) for p in unique if p not in set(PAIRS)],
        "missing_pairs": [list(p) for p in PAIRS if p not in unique],
        "repeat_conflicts": [v for v in unique.values() if v["repeat_conflicts"]],
    }


def cumulative(rows: list[dict], field: str, calculated: bool = False) -> dict[str, float]:
    by_pair = {pair(r): r for r in rows}
    result = {"0": 0.0}
    for start, end in PAIRS:
        row = by_pair[start, end]
        value = arithmetic(row["values"])["calculated_dh"] if calculated else row["values"][field]
        result[end] = result[start] + value
    return result


def written_dh_bounds(rows: list[dict], end: str, start: str = "0") -> list[float]:
    def path(station):
        limit = 6 if station in {"a", "b"} else int(station)
        legs = PAIRS[:limit]
        return legs + PAIRS[76 : 77 if station == "a" else 78] if station in {"a", "b"} else legs

    earlier, later = path(start), path(end)
    if later[: len(earlier)] != earlier:
        raise ValueError("Checkpoint interval must follow a single directed path")
    by_pair = {pair(row): row for row in rows}
    low, high = 0.0, 0.0
    for key in later[len(earlier) :]:
        row = by_pair[key]
        candidates = [row["values"]["dh"], *row.get("alternatives", {}).get("dh", [])]
        low += min(candidates)
        high += max(candidates)
    return [low, high]


def check_checkpoints(rows: list[dict], checkpoints: list[dict]) -> list[dict]:
    written, trig = cumulative(rows, "dh"), cumulative(rows, "dh", calculated=True)
    checked = []
    for cp in checkpoints:
        result = dict(cp)
        end = cp.get("station")
        if end is not None:
            result.update(
                sum_written_dh=written[end],
                sum_trig_dh=trig[end],
                residual_written=written[end] - cp["value"],
                residual_trig=trig[end] - cp["value"],
                written_dh_bounds=written_dh_bounds(rows, end),
            )
        previous = cp.get("previous_station")
        if previous is not None:
            result.update(
                interval_written=written[end] - written[previous],
                interval_checkpoints=cp["value"] - cp["previous_value"],
                interval_residual=(written[end] - written[previous])
                - (cp["value"] - cp["previous_value"]),
                interval_written_bounds=written_dh_bounds(rows, end, previous),
            )
        checked.append(result)
    return checked


def audit(cave: Path, reference_path: Path) -> dict:
    reference_document = json.loads(reference_path.read_text(encoding="utf-8"))
    for source in reference_document["reviewed_sources"]:
        if sha256(cave / source["path"]) != source["sha256"]:
            raise ValueError(f"Reviewed source changed: {source['path']}")
    refs = reference_document["rows"]
    if [pair(r) for r in refs] != PAIRS:
        raise ValueError("Reviewed reference must cover exactly the 78 ordered pairs")
    for row in refs:
        if set(row["values"]) != set(FIELDS) or not set(row["uncertain_fields"]) <= set(FIELDS):
            raise ValueError("Invalid reviewed fields")
        for field, value in row["values"].items():
            if value is None and field == "A" and abs(row["values"]["V"]) == 90:
                continue
            if not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError("Reference requires finite values, except blank vertical azimuth")
    reference_by_pair = {pair(row): row for row in refs}
    srv = cave / "CZ_GL_R.SRV"
    models = [
        read_model(cave / "ODCZYTY_MODELI" / f"{name}.md")
        for name in ("gemini_flash_3.8", "gemini_pro", "claude_opus_5")
    ]
    old_text = (cave / "KONTROLA_RACHUNKOW" / "CODEX_PIERWOTNY.SRV.txt").read_text(encoding="utf-8")
    models.append(
        {
            "model": "Codex_initial_7472374",
            "sha256": hashlib.sha256(old_text.encode()).hexdigest(),
            "git_commit": INITIAL_COMMIT,
            "rows": parse_srv(old_text),
            "aggregates": [],
        }
    )
    for model in models:
        model["comparison"] = compare_model(model["rows"], refs)
        for row in model["rows"]:
            row["arithmetic"] = arithmetic(row["values"])
            ref = reference_by_pair.get(pair(row))
            if ref is not None:
                values = {**row["values"], "Lh": ref["values"]["Lh"], "dh": ref["values"]["dh"]}
                row["arithmetic_against_reference_aux"] = arithmetic(values)
                row["single_alternative_checks"] = [
                    {
                        "field": field,
                        "alternative": value,
                        "arithmetic": arithmetic({**values, field: value}),
                    }
                    for field in ("D", "A", "V")
                    for value in row.get("alternatives", {}).get(field, [])
                ]
    current = parse_srv(srv.read_text(encoding="utf-8"))
    current_by_pair = {pair(r): r for r in current}
    for ref in refs:
        ref["arithmetic"] = arithmetic(ref["values"])
        ref["current_srv"] = current_by_pair[pair(ref)]
        ref["srv_differences"] = [
            f for f in FIELDS if ref["values"][f] != current_by_pair[pair(ref)]["values"][f]
        ]
    ranking = sorted(
        (
            {
                "model": m["model"],
                **m["comparison"]["counts"],
                "by_field": m["comparison"]["by_field"],
            }
            for m in models
        ),
        key=lambda x: (-x.get("correct", 0), x["model"]),
    )
    return {
        "schema_version": 1,
        "method": reference_document["method"],
        "findings": reference_document.get("findings", []),
        "reviewed_sources": reference_document["reviewed_sources"],
        "inputs": [
            {"path": str(p.relative_to(cave)), "sha256": sha256(p)}
            for p in [
                srv,
                reference_path,
                *sorted((cave / "_RAW" / "02").glob("*123*.jpg")),
                *sorted((cave / "ODCZYTY_MODELI").glob("*.md")),
            ]
            if p.name != "README.md"
        ],
        "rows": refs,
        "models": models,
        "ranking": ranking,
        "current_srv_comparison": compare_model(current, refs),
        "checkpoints": check_checkpoints(refs, reference_document["checkpoints"]),
        "unresolved_aggregates": reference_document["unresolved_aggregates"],
        "sums": {
            field: {
                "main": sum(r["values"][field] for r in refs[:76]),
                "branch": sum(r["values"][field] for r in refs[76:]),
            }
            for field in ("D", "Lh", "dh")
        },
    }


def number(value, digits=3):
    return "—" if value is None else f"{value:.{digits}f}"


def markdown(report: dict) -> str:
    lines = [
        "# Czarna — kontrola rachunkowa każdego wiersza i ranking odczytów",
        "",
        "Wynik odtwarzalny; wartości odczytane ze skanów pozostają oddzielone od obliczeń.",
        "",
        "## Metoda i ograniczenia",
        "",
        *[line for paragraph in report["method"] for line in (paragraph, "")],
        "",
        "## Wnioski z krzyżowej kontroli",
        "",
        *[line for paragraph in report["findings"] for line in (paragraph, "")],
        "",
        "## Ranking pierwszych odpowiedzi",
        "",
        "Jednakowy zestaw rozstrzygniętych pól D/A/V/Lh/Δh; niepewne pola referencji wyłączono. "
        "Powtórna fotografia nie zwiększa liczby głosów. Brak pary jest brakiem pięciu pól. "
        "Wynik ocenia te transkrypcje, nie ogólną jakość modeli ani poprawność pomiaru terenowego.",
        "",
        "| Odczyt | Poprawne / oceniane | D/A/V poprawne | Lh/Δh poprawne | Z alternatywami |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for m in report["ranking"]:
        fields = m["by_field"]
        dav = sum(fields[f].get("correct", 0) for f in ("D", "A", "V"))
        aux = sum(fields[f].get("correct", 0) for f in ("Lh", "dh"))
        lines.append(
            f"| {m['model']} | {m.get('correct', 0)}/{m['assessed']} | {dav} | {aux} | "
            f"{m.get('including_alternatives', 0)} |"
        )
    lines += [
        "",
        "Codex_initial to pierwotny SRV z 7472374, już po ówczesnej kontroli czytelników; "
        "nie jest surową odpowiedzią z odtworzonym promptem. Obecny SRV po wykorzystaniu wyników "
        "innych modeli nie uczestniczy w rankingu. "
        "Nazwy Gemini/Opus są etykietami dostarczonymi przez użytkownika.",
        "",
        "## Kontrola 78 wierszy",
        "",
        "ε = zapis − wynik trygonometrii. R oznacza oba |ε| ≤ 0,005 m (zaokrąglenie do cm), "
        "P oba |ε| ≤ 0,05 m, X co najmniej jedno > 0,05 m. P to wyłącznie próg diagnostyczny, "
        "nie dowód poprawności. ? wymienia pola bez rozstrzygnięcia wizualnego. "
        "A nie uczestniczy w żadnym z tych testów.",
        "",
        "| Odcinek | D / A / V | Lh zapis → oblicz. | Δh zapis → oblicz. | "
        "ε Lh / ε Δh | Kontrola / niepewne |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for r in report["rows"]:
        v, a = r["values"], r["arithmetic"]
        flag = (
            "R"
            if all(a["strict_rounding_0_005m"].values())
            else "P"
            if all(a["within_0_05m"].values())
            else "X"
        )
        eps = a["residual_scan_minus_calculated"]
        lines.append(
            f"| {r['from']}→{r['to']} | {number(v['D'], 2)} / "
            f"{number(v['A'], 0)} / {number(v['V'], 0)} | "
            f"{number(v['Lh'], 2)} → {number(a['calculated_Lh'])} | "
            f"{number(v['dh'], 2)} → {number(a['calculated_dh'])} | "
            f"{number(eps['Lh'])} / {number(eps['dh'])} | {flag}; "
            f"{', '.join(r['uncertain_fields']) or '—'} |"
        )
    lines += [
        "",
        "JSON zawiera także test Pitagorasa (D z Lh i Δh), kąt atan2(Δh,Lh), "
        "wartości literalne, numery linii, alternatywy modeli "
        "oraz rachunki dla każdego ich wiersza.",
        "",
        "## Sumy i punkty kontrolne",
        "",
        "Suma Δh to suma zapisanej kolumny. Wynik z D,V jest niezależnym przeliczeniem tych samych "
        "obserwacji, a nie niezależnym pomiarem terenowym. "
        "Przypisania dopisków do stacji są jawne w JSON.",
        "",
        "| Dopisek | Stacja | Zapis | Suma Δh | Różnica | Suma D sin V | "
        "Różnica przyrostu od poprzedniego dopisku |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for cp in report["checkpoints"]:
        lines.append(
            f"| {cp['label']} | {cp.get('station', '—')} | {number(cp['value'], 2)} | "
            f"{number(cp.get('sum_written_dh'))} | {number(cp.get('residual_written'))} | "
            f"{number(cp.get('sum_trig_dh'))} | {number(cp.get('interval_residual'))} |"
        )
    for item in report["unresolved_aggregates"]:
        lines += ["", f"- {item['raw']}: {item['note']}"]
    lines += [
        "",
        "## Rozbieżności ocenianych pól",
        "",
        "To rozbieżności względem ponownie obejrzanych, rozstrzygniętych pól skanu. "
        "Pola niepewne są wyłączone, a nie zaliczone żadnemu modelowi.",
        "",
    ]
    for model in report["models"]:
        lines += [
            f"### {model['model']}",
            "",
            "| Odcinek | Pole | Pierwszy wynik | Odczyt skanu | Poprawne w alternatywach |",
            "| --- | --- | --- | --- | --- |",
        ]
        for m in model["comparison"]["mismatches"]:
            lines.append(
                f"| {m['from']}→{m['to']} | {m['field']} | {number(m['primary'], 2)} | "
                f"{number(m['reference'], 2)} | "
                f"{'tak' if m.get('correct_in_alternatives') else 'nie'} |"
            )
    lines += [
        "",
        "## Odtworzenie",
        "",
        "```sh",
        "uv run jktz-czarna-kontrola",
        "```",
        "",
        "Wejścia: `KONTROLA_RACHUNKOW/odczyt_uzgodniony.json`, trzy fotografie `_RAW/02`, "
        "trzy surowe transkrypcje `ODCZYTY_MODELI`, bieżący SRV i SRV z commitu 7472374. "
        "SHA-256 w `KONTROLA_RACHUNKOW/wyniki.json`. Skrypt nie modyfikuje źródeł ani SRV.",
        "",
    ]
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cave", type=Path, default=CAVE)
    args = parser.parse_args(argv)
    folder = args.cave / "KONTROLA_RACHUNKOW"
    report = audit(args.cave, folder / "odczyt_uzgodniony.json")
    (folder / "wyniki.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (args.cave / "KONTROLA_RACHUNKOW.md").write_text(markdown(report), encoding="utf-8")
    print(json.dumps(report["ranking"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
