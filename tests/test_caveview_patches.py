from __future__ import annotations

import importlib.util
import shutil
import subprocess
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


def test_project_crs_uses_builtin_utm_and_other_codes_keep_their_lookup(tmp_path, patches):
    node = shutil.which("node")
    if node is None:
        pytest.skip("JavaScript runtime unavailable")
    path = tmp_path / "CaveView2.js"
    path.write_text(
        "const viewer = {\n"
        "  async lookupCRS(code) { return `remote:${code}`; },\n"
        "  async resolve(sourceCRS) {\n"
        "    const code = sourceCRS.match( /(epsg|esri):([0-9]+)/ );\n"
        "    sourceCRS = await this.lookupCRS( code[ 2 ] );\n"
        "    return sourceCRS;\n"
        "  }\n"
        "};\n"
        "(async () => {\n"
        "  for (const code of process.argv.slice(2)) console.log(await viewer.resolve(code));\n"
        "})();\n"
    )
    patches.patch_crs_regex(path)
    once = path.read_bytes()
    patches.patch_crs_regex(path)
    assert path.read_bytes() == once

    result = subprocess.run(
        [node, path, "EPSG:32634", "epsg:32634", "ESRI:32634", "EPSG:27701"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.splitlines() == [
        "EPSG:32634",
        "EPSG:32634",
        "remote:32634",
        "remote:27701",
    ]


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


def test_entrance_clusters_use_small_neutral_badges(tmp_path, patches):
    path = tmp_path / "CaveView2.js"
    path.write_text(
        "class ClusterMaterial extends PointsMaterial {\n"
        "\t\tconstructor ( count ) {\n"
        "\t\t\tconst gradient = ctx.createRadialGradient( halfSize, halfSize, 30, "
        "halfSize, halfSize, 0 );\n"
        "\t\t\tgradient.addColorStop( 1.0, 'rgba( 255, 255, 0, 255 )' );\n"
        "\t\t\tctx.fillStyle = gradient;\n"
        "\t\t\tctx.fillStyle = 'rgba( 0, 0, 0, 255 )';\n"
        "\t\t\tsuper( { map: texture, size: 32, depthTest: false } );\n"
        "\t\t}\n"
        "\t}\n"
        "const unrelated = { size: 32 };\n"
    )

    patches.patch_entrance_clusters(path)
    once = path.read_text()
    patches.patch_entrance_clusters(path)

    assert "createRadialGradient" not in once
    assert "ctx.fillStyle = '#232928';" in once
    assert "ctx.fillStyle = '#f1f3f2';" in once
    assert "map: texture, size: 20, depthTest: false" in once
    assert "const unrelated = { size: 32 };" in once
    assert path.read_text() == once


def test_entrance_labels_render_above_terrain_at_their_projected_position(tmp_path, patches):
    path = tmp_path / "CaveView2.js"
    path.write_text(
        "const material = ctx.materials.getLabelMaterial( 'stations.entrances' );\n"
        "\n"
        "\t\t\tmaterial.depthTest = true;\n"
        "\t\t\tmaterial.transparent = false;\n"
        "\t\t\tmaterial.alphaTest = 0;\n"
        "\t\t\tmarker.layers.set( FEATURE_ENTRANCES );\n"
        "\t\t\tmarker.position.copy( node );\n",
    )
    patches.patch_entrance_labels(path)
    once = path.read_text()
    patches.patch_entrance_labels(path)

    assert "material.scaleFactor / material.toScreenSpace.x" in once
    assert "material.depthTest = false;" in once
    assert "material.depthWrite = false;" in once
    assert "material.transparent = true;" in once
    assert "marker.renderOrder = 2;" in once
    assert "marker.position.copy( node );" in once
    assert path.read_text() == once


def test_mismatched_label_material_fails_without_writing_partial_patch(tmp_path, patches):
    path = tmp_path / "CaveView2.js"
    original = (
        "const material = ctx.materials.getLabelMaterial( 'stations.entrances' );"
        " // vendor comment\n"
        "\n\t\t\tmaterial.depthTest = true;\n\t\t\tmaterial.transparent = false;\n"
        "\t\t\tmarker.layers.set( FEATURE_ENTRANCES );\n"
        "\t\t\tmarker.position.copy( node );\n"
    )
    path.write_text(original)

    with pytest.raises(ValueError, match="entrance label material"):
        patches.patch_entrance_labels(path)

    assert path.read_text() == original


def test_walls_station_name_with_dots_is_kept_as_one_leaf(tmp_path, patches):
    path = tmp_path / "CaveView2.js"
    path.write_text(
        "function parseStation(header, label) {\n"
        "\t\t\tconst auxInfo = readNSLF();\n"
        "\t\t\tfunction readNSLF() { return header; }\n"
        "\t\t\tconst xGroups    = [];\n"
        "\t\t\tconst stationMap = this.stationMap;\n\n"
        "\t\t\t// init cmd handler\n"
        "\t\t\t\tconst coords = readCoordinates();\n"
        "\t\t\t\tconst path = label.split( '.' );\n"
        "\t\t\tfunction readCoordinates() {}\n"
        "return path;\n}\n"
        "const loader = {parseStation};\n"
        "const station = 'Pawlikowskiego:Oblazkowa:0.0';\n"
        "console.log(JSON.stringify(loader.parseStation(['title', 'EPSG:32634', ':'], station)));\n"
        "console.log(JSON.stringify(loader.parseStation(['title'], 'survey.0')));\n"
    )

    patches.patch_walls_station_paths(path)
    node = shutil.which("node")
    if node is None:
        pytest.skip("JavaScript runtime unavailable")
    result = subprocess.check_output([node, path], text=True)

    assert result.splitlines() == ['["Pawlikowskiego:Oblazkowa:0.0"]', '["survey","0"]']


def test_colocated_named_entrances_share_one_label(tmp_path, patches):
    path = tmp_path / "CaveView2.js"
    path.write_text(
        """\
const STATION_ENTRANCE = 2;
const vertices = [];
const self = { addMarker(node, name) { console.log(node.id, name.trim()); } };
const entrances = { a: {name: 'Turnia'}, b: {name: 'Piwnica'}, c: {name: '-skip'} };
			function _addEntrance ( node ) {

				if ( ! ( ( node.ownType ?? node.type ) & STATION_ENTRANCE ) ) return;

				if ( node.next ) {

					let next = node.next;

					// skip labels for all expect lowest id station
					while ( next !== node ) {

						if ( ( next.ownType & STATION_ENTRANCE ) && node.id > next.id ) return;
						next = next.next;

					}

				}

				vertices.push( node );

				let name;

				const entranceInfo = entrances[ node.getPath() ];

				if ( entranceInfo?.name !== undefined ) {

					name = entranceInfo.name;
					if ( name === '-skip' ) return;

				} else if ( node.comment !== undefined ) {

					name = node.comment;

				} else {

					name = node.getPath( endNode );

				}

				self.addMarker( node, ` ${name} ` );

			}
const a = { id: 1, ownType: 2, getPath: () => 'a' };
const b = { id: 2, ownType: 2, getPath: () => 'b' };
const c = { id: 3, ownType: 2, getPath: () => 'c' };
a.next = b;
b.next = c;
c.next = a;
for (const entrance of [b, a, c]) _addEntrance(entrance);
console.log(vertices.length);
"""
    )

    patches.patch_entrance_aliases(path)
    node = shutil.which("node")
    if node is None:
        pytest.skip("JavaScript runtime unavailable")
    result = subprocess.check_output([node, path], text=True)

    assert result.splitlines() == ["1 Turnia / Piwnica", "1"]


def test_entrance_groups_fit_the_badge_in_screen_pixels(tmp_path, patches):
    path = tmp_path / "CaveView2.js"
    path.write_text(
        """\
class Vector3 {
    copy(point) { Object.assign(this, point); return this; }
    applyMatrix4() { return this; }
    project() { return this; }
}
class Vector2 {}
class Box2 {
    points = [];
    expandByPoint(point) { this.points.push({...point}); }
    getSize() {
        const span = axis => Math.max(...this.points.map(p => p[axis]))
            - Math.min(...this.points.map(p => p[axis]));
        return {x: span('x'), y: span('y')};
    }
}
\t// preallocated objects for projected area calculation and cluster visibility checks
\tconst __a$1 = new Vector3();
\tconst __v = new Vector3();

\tclass QuadTree {
\t\tcheck ( cluster, target, angleFactor, selection ) {
\t\t\tfor (const subQuad of this.nodes) {
\t\t\t\tconst area = subQuad.projectedArea( cluster );
\t\t\t\tif (area < 10 * angleFactor) subQuad.clusterMarkers();
\t\t\t}
\t\t}

\t\tprojectedArea ( cluster ) {
\t\t\treturn 0.05;
\t\t}
\t}

function runGrouping(dx, dy, width, height) {
    const tree = new QuadTree();
    const subQuad = new QuadTree();
    tree.nodes = [subQuad];
    subQuad.nodes = [];
    subQuad.count = 2;
    subQuad.markers = [{position: {x: 0, y: 0, z: 0}}, {position: {x: dx, y: dy, z: 0}}];
    subQuad.clusterMarkers = () => console.log('cluster');
    subQuad.showMarkers = () => console.log('labels');
    const selection = {};
    const selectedStationSet = selection;
    const target = {};
    this.quadTree = tree;
    const cluster = this;
    cluster.camera = {getWorldDirection: () => ({dot: () => 0}), updateWorldMatrix() {}};
    cluster.ctx = {container: {clientWidth: width, clientHeight: height}};
    const Object3D = {};
\t\t\tconst angle = this.camera.getWorldDirection( __v ).dot( Object3D.DEFAULT_UP );

\t\t\tthis.quadTree.check( this, target, Math.max( 0.05, 1 - Math.cos( angle ) ), """
        """selectedStationSet );
}
runGrouping(0.025, 0.01, 1280, 720);
runGrouping(0.35, 0.01, 1280, 720);
runGrouping(0.01, 0.08, 1280, 720);
runGrouping(0.025, 0.01, 1920, 720);
runGrouping(0.03, 0.05, 1280, 720);
"""
    )

    patches.patch_entrance_grouping(path)
    node = shutil.which("node")
    if node is None:
        pytest.skip("JavaScript runtime unavailable")
    result = subprocess.check_output([node, path], text=True)

    assert result.splitlines() == ["cluster", "labels", "labels", "labels", "labels"]


@pytest.mark.parametrize("double_patch", [False, True])
def test_cluster_badge_match_is_scoped_and_unambiguous(tmp_path, patches, double_patch):
    path = tmp_path / "CaveView2.js"
    badge = "map: texture, size: 20, " if double_patch else "map: texture, size: 31, "
    original = (
        "class ClusterMaterial extends PointsMaterial {\n"
        "\t\tctx.fillStyle = '#232928';\n"
        "\t\tctx.fillStyle = '#f1f3f2';\n"
        f"\t\tsuper( {{ {badge}depthTest: false }} );\n"
        + ("\t\t// map: texture, size: 32,\n" if double_patch else "")
        + "\t}\n"
        "const unrelated = { map: texture, size: 32, depthTest: true };\n"
    )
    path.write_text(original)
    with pytest.raises(ValueError, match="cluster badge size"):
        patches.patch_entrance_clusters(path)
    assert path.read_text() == original
