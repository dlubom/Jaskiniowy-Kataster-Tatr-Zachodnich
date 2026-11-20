from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path


def test_caveview_uses_entrance_notes_as_display_names(tmp_path, monkeypatch):
    source = tmp_path / "OTWORY.SRV"
    source.write_text(
        "#flag\tTest:Section:0\t/ENTRANCE\n"
        '#note\tTest:Section:0\t/Lower Entrance "A"\n'
        "; #note Test:9 /Archived label\n"
        "#note  Test:1.0  /Upper Entrance\n",
        encoding="ascii",
    )
    output = tmp_path / "KATASTER.json"
    generator = Path(__file__).parents[1] / "web" / "entrance-labels.py"
    monkeypatch.setattr(sys, "argv", [str(generator), str(source), str(output)])

    runpy.run_path(str(generator), run_name="__main__")

    assert json.loads(output.read_text(encoding="utf-8")) == {
        "entrances": {
            "Test:Section:0": {"name": 'Lower Entrance "A"'},
            "Test:1.0": {"name": "Upper Entrance"},
        }
    }
