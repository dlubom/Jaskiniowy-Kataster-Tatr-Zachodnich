from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


@pytest.fixture
def patches():
    path = Path(__file__).parents[1] / "web" / "patch-caveview.py"
    spec = importlib.util.spec_from_file_location("patch_caveview", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("flags", ["", "i", "ii", "iiii"])
def test_crs_patch_is_case_insensitive_and_idempotent(tmp_path, patches, flags):
    path = tmp_path / "CaveView2.js"
    path.write_text(f"const crs = /(epsg|esri):([0-9]+)/{flags};\n")

    patches.patch_crs_regex(path)
    once = path.read_bytes()
    patches.patch_crs_regex(path)

    assert path.read_text() == "const crs = /(epsg|esri):([0-9]+)/i;\n"
    assert path.read_bytes() == once


@pytest.mark.parametrize(
    "function",
    [
        "patch_crs_regex",
        "patch_web_mesh_worker",
        "patch_tree_traversal",
        "patch_station_position_tree_fields",
    ],
)
def test_missing_vendor_pattern_does_not_change_file(tmp_path, patches, function, capsys):
    path = tmp_path / "unrelated.js"
    original = b"// unrelated vendor file\r\nconst value = 42;\r\n"
    path.write_bytes(original)

    getattr(patches, function)(path)

    assert path.read_bytes() == original
    assert "SKIP:" in capsys.readouterr().out


@pytest.mark.parametrize("newline", ["\n", "\r\n"])
def test_station_prefix_patch_creates_independent_tree_fields(tmp_path, patches, newline):
    path = tmp_path / "CaveView2.js"
    original = "class StationPosition {\n\t\t\tthis.stationVertexIndex = -1;\n\n\t\t}\n"
    path.write_bytes(original.replace("\n", newline).encode())

    patches.patch_station_position_tree_fields(path)
    once = path.read_bytes()
    patches.patch_station_position_tree_fields(path)

    assert "this.stationVertexIndex = -1;" in once.decode()
    assert "this.children = [];" in once.decode()
    assert "this.boundingBox = new Box3();" in once.decode()
    assert "this.stationCount = 0;" in once.decode()
    assert path.read_bytes() == once


def test_worker_transfers_buffers_but_sends_typed_arrays(tmp_path, patches):
    path = tmp_path / "webMeshWorker.js"
    path.write_text(
        "const indexBuffer = terrainTile.index.array.buffer;\n"
        "\t\tconst attributes = {};\n"
        "\t\tconst transferable = [];\n"
        "\n"
        "\t\tconst srcAttributes = terrainTile.attributes;\n"
        "\n"
        "\t\tfor ( const attributeName in srcAttributes ) {\n"
        "\n"
        "\t\t\tconst attribute = srcAttributes[ attributeName ];\n"
        "\t\t\tconst arrayBuffer = attribute.array.buffer;\n"
        "\n"
        "\t\t\tattributes[ attributeName ] = "
        "{ array: arrayBuffer, itemSize: attribute.itemSize };\n"
        "\n"
        "\t\t\ttransferable.push( arrayBuffer );\n"
        "\n"
        "\t\t}\n"
        "\n"
        "\t\tpostMessage(\n"
        "\t\t\t{\n"
        "\t\t\t\tstatus: 'ok',\n"
        "\t\t\t\tindex: indexBuffer,\n"
        "\t\t\t\tattributes\n"
        "\t\t\t}, transferable );\n"
    )

    patches.patch_web_mesh_worker(path)
    once = path.read_bytes()
    patches.patch_web_mesh_worker(path)

    result = once.decode()
    assert "index: { array: index.array }," in result
    assert "{ array: attribute.array, itemSize: attribute.itemSize }" in result
    assert "transferable.push( index.array.buffer );" in result
    assert "transferable.push( attribute.array.buffer );" in result
    assert "indexBuffer" not in result
    assert "arrayBuffer" not in result
    assert path.read_bytes() == once


@pytest.mark.parametrize("newline", ["\n", "\r\n"])
def test_recursive_traversals_become_iterative_and_remain_idempotent(tmp_path, patches, newline):
    path = tmp_path / "CaveView2.js"
    source = (
        "Tree.prototype.traverse = function ( func ) {\n"
        "\n"
        "\t\tfunc ( this );\n"
        "\n"
        "\t\tif ( this.children === undefined ) return;\n"
        "\n"
        "\t\tconst children = this.children;\n"
        "\n"
        "\t\tfor ( let i = 0; i < children.length; i++ ) {\n"
        "\n"
        "\t\t\tchildren[ i ].traverse( func );\n"
        "\n"
        "\t\t}\n"
        "\n"
        "\t};\n"
        "Tree.prototype.traverseDepthFirst = function ( func ) {\n"
        "\n"
        "\t\tconst children = this.children;\n"
        "\n"
        "\t\tfor ( let i = 0; i < children.length; i++ ) {\n"
        "\n"
        "\t\t\tchildren[ i ].traverseDepthFirst( func );\n"
        "\n"
        "\t\t}\n"
        "\n"
        "\t\tfunc( this );\n"
        "\n"
        "\t};\n"
    )
    path.write_bytes(source.replace("\n", newline).encode())

    patches.patch_tree_traversal(path)
    once = path.read_bytes()
    patches.patch_tree_traversal(path)

    result = once.decode()
    assert "children[ i ].traverse" not in result
    assert result.count("while ( stack.length > 0 )") == 2
    assert result.count("const seen = new Set();") == 2
    assert result.count("let i = children.length - 1; i >= 0; i--") == 2
    assert "{ node: node, visited: true }" in result
    assert path.read_bytes() == once
