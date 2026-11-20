#!/usr/bin/env python3
"""
Apply JKTZ compatibility fixes and entrance marker styling to CaveView.js 2.9.0.

Bug 1: Uppercase CRS codes are missed and EPSG:32634 triggers an unnecessary remote lookup.
Bug 2: webMeshWorker sends raw ArrayBuffer instead of typed arrays, crashing hydrateGeometry.
Bug 3: Tree traversal is recursive and overflows the browser stack on large/deep surveys.
Bug 4: StationPosition lacks own tree fields when a station is also a path prefix.
"""

import os
import re
import sys
from pathlib import Path
from textwrap import indent

ENTRANCE_CLUSTER_SIZE = 20


def patch_crs_regex(path):
    """Recognize EPSG/ESRI and use bundled Proj4's UTM 34N definition for JKTZ."""
    with open(path) as f:
        source = f.read()
    pattern = "/(epsg|esri):([0-9]+)/"
    patched = re.sub(re.escape(pattern) + "i*", pattern + "i", source)
    patched = patched.replace(
        "sourceCRS = await this.lookupCRS( code[ 2 ] );",
        "sourceCRS = code[ 0 ].toUpperCase() === 'EPSG:32634' "
        "? 'EPSG:32634' : await this.lookupCRS( code[ 2 ] );",
    )
    if patched == source:
        print(f"  SKIP: CRS handling already patched or not found in {path}")
        return
    with open(path, "w") as f:
        f.write(patched)
    print(f"  OK: patched CRS handling in {path}")


def patch_web_mesh_worker(path):
    """Fix webMeshWorker to send typed arrays instead of raw ArrayBuffer."""
    with open(path) as f:
        c = f.read()

    # Worker file uses \t indentation (2 levels deep)
    old = (
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
        "\t\t\t\tindex: indexBuffer,"
    )
    new = (
        "const index = terrainTile.index;\n"
        "\t\tconst attributes = {};\n"
        "\t\tconst transferable = [];\n"
        "\n"
        "\t\ttransferable.push( index.array.buffer );\n"
        "\n"
        "\t\tconst srcAttributes = terrainTile.attributes;\n"
        "\n"
        "\t\tfor ( const attributeName in srcAttributes ) {\n"
        "\n"
        "\t\t\tconst attribute = srcAttributes[ attributeName ];\n"
        "\n"
        "\t\t\tattributes[ attributeName ] = "
        "{ array: attribute.array, itemSize: attribute.itemSize };\n"
        "\n"
        "\t\t\ttransferable.push( attribute.array.buffer );\n"
        "\n"
        "\t\t}\n"
        "\n"
        "\t\tpostMessage(\n"
        "\t\t\t{\n"
        "\t\t\t\tstatus: 'ok',\n"
        "\t\t\t\tindex: { array: index.array },"
    )

    # Handle both \n and \r\n line endings
    if old not in c:
        old = old.replace("\n", "\r\n")
        new = new.replace("\n", "\r\n")

    if old not in c:
        print(f"  SKIP: webMeshWorker already patched or not found in {path}")
        return

    c = c.replace(old, new, 1)
    with open(path, "w") as f:
        f.write(c)
    print(f"  OK: patched webMeshWorker in {path}")


def patch_tree_traversal(path):
    """Replace recursive Tree traversal with iterative traversal for large surveys."""
    with open(path) as f:
        c = f.read()

    replacements = [
        (
            (
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
                "\t};"
            ),
            (
                "Tree.prototype.traverse = function ( func ) {\n"
                "\n"
                "\t\tconst stack = [ this ];\n"
                "\t\tconst seen = new Set();\n"
                "\n"
                "\t\twhile ( stack.length > 0 ) {\n"
                "\n"
                "\t\t\tconst node = stack.pop();\n"
                "\n"
                "\t\t\tif ( seen.has( node ) ) continue;\n"
                "\n"
                "\t\t\tseen.add( node );\n"
                "\n"
                "\t\t\tfunc( node );\n"
                "\n"
                "\t\t\tconst children = node.children;\n"
                "\n"
                "\t\t\tif ( children === undefined ) continue;\n"
                "\n"
                "\t\t\tfor ( let i = children.length - 1; i >= 0; i-- ) {\n"
                "\n"
                "\t\t\t\tstack.push( children[ i ] );\n"
                "\n"
                "\t\t\t}\n"
                "\n"
                "\t\t}\n"
                "\n"
                "\t};"
            ),
            "Tree.traverse",
        ),
        (
            (
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
                "\t};"
            ),
            (
                "Tree.prototype.traverseDepthFirst = function ( func ) {\n"
                "\n"
                "\t\tconst stack = [ { node: this, visited: false } ];\n"
                "\t\tconst seen = new Set();\n"
                "\n"
                "\t\twhile ( stack.length > 0 ) {\n"
                "\n"
                "\t\t\tconst entry = stack.pop();\n"
                "\t\t\tconst node = entry.node;\n"
                "\n"
                "\t\t\tif ( entry.visited ) {\n"
                "\n"
                "\t\t\t\tfunc( node );\n"
                "\t\t\t\tcontinue;\n"
                "\n"
                "\t\t\t}\n"
                "\n"
                "\t\t\tif ( seen.has( node ) ) continue;\n"
                "\n"
                "\t\t\tseen.add( node );\n"
                "\n"
                "\t\t\tstack.push( { node: node, visited: true } );\n"
                "\n"
                "\t\t\tconst children = node.children;\n"
                "\n"
                "\t\t\tif ( children === undefined ) continue;\n"
                "\n"
                "\t\t\tfor ( let i = children.length - 1; i >= 0; i-- ) {\n"
                "\n"
                "\t\t\t\tstack.push( { node: children[ i ], visited: false } );\n"
                "\n"
                "\t\t\t}\n"
                "\n"
                "\t\t}\n"
                "\n"
                "\t};"
            ),
            "Tree.traverseDepthFirst",
        ),
    ]

    patched = False

    for old, new, label in replacements:
        old_candidate = old
        new_candidate = new

        if old_candidate not in c:
            old_candidate = old_candidate.replace("\n", "\r\n")
            new_candidate = new_candidate.replace("\n", "\r\n")

        if old_candidate in c:
            c = c.replace(old_candidate, new_candidate, 1)
            patched = True
            print(f"  OK: patched {label} in {path}")
        elif new in c or new.replace("\n", "\r\n") in c:
            print(f"  SKIP: {label} already patched in {path}")
        else:
            print(f"  SKIP: {label} pattern not found in {path}")

    if patched:
        with open(path, "w") as f:
            f.write(c)


def patch_station_position_tree_fields(path):
    """Give each station node its own tree fields for station-as-prefix cases."""
    with open(path) as f:
        c = f.read()

    old = "\t\t\tthis.stationVertexIndex = -1;\n\n\t\t}\n"
    new = (
        "\t\t\tthis.stationVertexIndex = -1;\n"
        "\t\t\tthis.children = [];\n"
        "\t\t\tthis.boundingBox = new Box3();\n"
        "\t\t\tthis.stationCount = 0;\n"
        "\n"
        "\t\t}\n"
    )

    if new in c:
        print(f"  SKIP: StationPosition tree fields already patched in {path}")
        return

    if old not in c:
        old = old.replace("\n", "\r\n")
        new = new.replace("\n", "\r\n")

    if old not in c:
        print(f"  SKIP: StationPosition tree fields pattern not found in {path}")
        return

    c = c.replace(old, new, 1)

    with open(path, "w") as f:
        f.write(c)

    print(f"  OK: patched StationPosition tree fields in {path}")


def patch_required(path, replacements, *, section=None):
    """Apply all required substitutions before writing a vendor file."""
    js = Path(path)
    source = js.read_text(encoding="utf-8")
    start, end = 0, len(source)
    if section is not None:
        matches = list(re.finditer(section, source, re.S))
        if len(matches) != 1:
            raise ValueError(f"{path}: expected one vendor section matching {section}")
        start, end = matches[0].span()

    original = source[start:end]
    patched = original
    for label, old, new in replacements:
        pattern = re.escape(old) if isinstance(old, str) else old
        without_patch = patched.replace(new, "", 1)
        if without_patch != patched:
            if new in without_patch or re.search(pattern, without_patch):
                raise ValueError(f"{path}: ambiguous {label} match")
            continue

        patched, count = re.subn(pattern, lambda _, replacement=new: replacement, patched)
        if count != 1:
            raise ValueError(f"{path}: expected one {label} match, found {count}")

    if patched != original:
        js.write_text(source[:start] + patched + source[end:], encoding="utf-8")


def patch_walls_station_paths(path):
    """Keep non-dot Survex station names intact in the CaveView tree."""
    header = "\t\t\tconst auxInfo = readNSLF();"
    station_map = "\t\t\tconst xGroups    = [];\n\t\t\tconst stationMap = this.stationMap;"
    coords = "\t\t\t\tconst coords = readCoordinates();\n"
    patch_required(
        path,
        [
            (
                "Survex auxiliary header",
                header,
                header + "\n\t\t\tthis.stationSeparator = auxInfo[ 2 ]?.charAt( 0 ) || '.';",
            ),
            (
                "Survex loader separator",
                station_map,
                station_map + "\n\t\t\tconst stationSeparator = this.stationSeparator;",
            ),
            (
                "Survex station path",
                coords + "\t\t\t\tconst path = label.split( '.' );",
                coords
                + "\t\t\t\tconst path = stationSeparator === '.' ? label.split( '.' ) : [ label ];",
            ),
        ],
    )


def patch_entrance_aliases(path):
    """Keep distinct entrance names together when they share one location."""
    old = re.compile(r"\t{3}function _addEntrance \( node \) \{.*?\n\t{3}\}", re.S)
    new = indent(
        """\
function _addEntrance ( node ) {

\tif ( ! ( ( node.ownType ?? node.type ) & STATION_ENTRANCE ) ) return;

\tconst name = entrances[ node.getPath() ]?.name ?? node.comment ?? node.getPath( endNode );
\tconst names = new Set( [ name ] );

\t// Draw one label for the lowest-ID entrance at this position.
\tfor ( let next = node.next; next && next !== node; next = next.next ) {
\t\tif ( ! ( next.ownType & STATION_ENTRANCE ) ) continue;
\t\tif ( Math.abs( node.id ) > Math.abs( next.id ) ) return;

\t\tconst otherName = entrances[ next.getPath() ]?.name;
\t\tif ( otherName !== undefined ) names.add( otherName );
\t}

\tvertices.push( node );
\tnames.delete( '-skip' );

\tif ( names.size > 0 ) self.addMarker( node, ` ${[ ...names ].join( ' / ' )} ` );

}""",
        "\t" * 3,
    )
    patch_required(path, [("co-located entrance labels", old, new)])


def patch_entrance_labels(path):
    """Keep labels legible against the terrain at the surveyed entrance positions."""
    material = "const material = ctx.materials.getLabelMaterial( 'stations.entrances' );"
    depth = "\n\n\t\t\tmaterial.depthTest = "
    old = material + depth + "true;\n\t\t\tmaterial.transparent = false;"
    # Match the glyph's rendered size to its collision box before the first resize.
    new = (
        material + "\n\t\t\tmaterial.uniforms.scale.value.set( "
        "material.scaleFactor / material.toScreenSpace.x, "
        "material.scaleFactor / material.toScreenSpace.y );"
        + depth
        + "false;\n\t\t\tmaterial.depthWrite = false;"
        "\n\t\t\tmaterial.transparent = true;"
    )
    layer = "marker.layers.set( FEATURE_ENTRANCES );"
    patch_required(
        path,
        [
            ("entrance label material", old, new),
            (
                "entrance label render order",
                layer + "\n\t\t\tmarker.position.copy( node );",
                layer + "\n\t\t\tmarker.renderOrder = 2;\n\t\t\tmarker.position.copy( node );",
            ),
        ],
    )


def patch_entrance_clusters(path):
    """Use smaller, neutral markers for groups of nearby entrances."""
    patch_required(
        path,
        [
            (
                "cluster background",
                re.compile(
                    r"const gradient = ctx\.createRadialGradient.*?ctx\.fillStyle = gradient;",
                    re.S,
                ),
                "ctx.fillStyle = '#232928';",
            ),
            (
                "cluster text",
                "ctx.fillStyle = 'rgba( 0, 0, 0, 255 )';",
                "ctx.fillStyle = '#f1f3f2';",
            ),
            (
                "cluster badge size",
                "map: texture, size: 32,",
                f"map: texture, size: {ENTRANCE_CLUSTER_SIZE},",
            ),
        ],
        section=r"class ClusterMaterial extends PointsMaterial \{.*?\n\t\}",
    )


def patch_entrance_grouping(path):
    """Group entrances only when their positions fit within one badge on screen."""
    check = indent(
        f"""\
check ( cluster, selection ) {{
\tfor ( let i = 0; i < this.nodes.length; i++ ) {{
\t\tconst subQuad = this.nodes[ i ];
\t\tif ( subQuad === undefined ) continue;

\t\tif ( subQuad.count < 2 ) {{
\t\t\tthis.nodes[ i ] = undefined;
\t\t\tcontinue;
\t\t}}

\t\tif ( subQuad.projectedSpan( cluster ) <= {ENTRANCE_CLUSTER_SIZE} ) {{
\t\t\tsubQuad.clusterMarkers( cluster );
\t\t}} else {{
\t\t\tsubQuad.showMarkers( selection );
\t\t\tsubQuad.check( cluster, selection );
\t\t}}
\t}}
}}""",
        "\t" * 2,
    )
    span = indent(
        """\
projectedSpan ( cluster ) {
\tconst bounds = new Box2();
\tfor ( const marker of this.markers ) {
\t\tprojectedEntrance.copy( marker.position ).applyMatrix4( cluster.matrixWorld )
\t\t\t.project( cluster.camera );
\t\tif ( Math.abs( projectedEntrance.z ) > 1 ) return Infinity;
\t\tbounds.expandByPoint( projectedEntrance );
\t}

\tconst size = bounds.getSize( new Vector2() );
\tconst { clientWidth, clientHeight } = cluster.ctx.container;
\treturn Math.hypot( size.x * clientWidth, size.y * clientHeight ) / 2;
}""",
        "\t" * 2,
    )
    patch_required(
        path,
        [
            (
                "cluster projection variables",
                re.compile(
                    r"\t// preallocated objects for projected area calculation"
                    r".*?(?=\n\n\tclass QuadTree \{)",
                    re.S,
                ),
                "\tconst projectedEntrance = new Vector3();",
            ),
            (
                "QuadTree grouping",
                re.compile(
                    r"\t{2}check \( cluster, target, angleFactor, selection \) \{.*?\n\t{2}\}",
                    re.S,
                ),
                check,
            ),
            (
                "QuadTree projection",
                re.compile(r"\t{2}projectedArea \( cluster \) \{.*?\n\t{2}\}", re.S),
                span,
            ),
            (
                "entrance grouping call",
                "const angle = this.camera.getWorldDirection( __v ).dot( Object3D.DEFAULT_UP );"
                "\n\n\t\t\tthis.quadTree.check( this, target, "
                "Math.max( 0.05, 1 - Math.cos( angle ) ), selectedStationSet );",
                "this.camera.updateWorldMatrix( true, false );\n\t\t\t"
                "this.quadTree.check( this, selectedStationSet );",
            ),
        ],
    )


if __name__ == "__main__":
    caveview_dir = sys.argv[1] if len(sys.argv) > 1 else "public/CaveView"
    print(f"Patching CaveView in {caveview_dir}...")
    caveview_js = os.path.join(caveview_dir, "js", "CaveView2.js")
    patch_crs_regex(caveview_js)
    patch_station_position_tree_fields(caveview_js)
    patch_tree_traversal(caveview_js)
    patch_walls_station_paths(caveview_js)
    patch_entrance_labels(caveview_js)
    patch_entrance_aliases(caveview_js)
    patch_entrance_clusters(caveview_js)
    patch_entrance_grouping(caveview_js)
    patch_web_mesh_worker(os.path.join(caveview_dir, "js", "workers", "webMeshWorker.js"))
