#!/usr/bin/env python3
"""
Patch CaveView.js 2.9.0 bugs for Cesium terrain support.
Remove this script when CaveView releases a fixed version.

Bug 1: CRS regex is case-sensitive — EPSG:32634 (uppercase from Survex) not matched.
Bug 2: webMeshWorker sends raw ArrayBuffer instead of typed arrays, crashing hydrateGeometry.
Bug 3: Tree traversal is recursive and overflows the browser stack on large/deep surveys.
Bug 4: StationPosition lacks own tree fields when a station is also a path prefix.
"""
import sys
import os

def patch_crs_regex(path):
    """Add case-insensitive flag to EPSG/ESRI regex in CaveView2.js."""
    with open(path, 'r') as f:
        c = f.read()
    old = '/(epsg|esri):([0-9]+)/'
    new = '/(epsg|esri):([0-9]+)/i'
    double = '/(epsg|esri):([0-9]+)/ii'
    if double in c:
        while double in c:
            c = c.replace(double, new)
        with open(path, 'w') as f:
            f.write(c)
        print(f'  OK: normalized CRS regex in {path}')
        return
    if new in c:
        print(f'  SKIP: CRS regex already patched in {path}')
        return
    if old not in c:
        print(f'  SKIP: CRS regex not found in {path}')
        return
    c = c.replace(old, new)
    with open(path, 'w') as f:
        f.write(c)
    print(f'  OK: patched CRS regex in {path}')

def patch_web_mesh_worker(path):
    """Fix webMeshWorker to send typed arrays instead of raw ArrayBuffer."""
    with open(path, 'r') as f:
        c = f.read()

    # Worker file uses \t indentation (2 levels deep)
    old = (
        'const indexBuffer = terrainTile.index.array.buffer;\n'
        '\t\tconst attributes = {};\n'
        '\t\tconst transferable = [];\n'
        '\n'
        '\t\tconst srcAttributes = terrainTile.attributes;\n'
        '\n'
        '\t\tfor ( const attributeName in srcAttributes ) {\n'
        '\n'
        '\t\t\tconst attribute = srcAttributes[ attributeName ];\n'
        '\t\t\tconst arrayBuffer = attribute.array.buffer;\n'
        '\n'
        '\t\t\tattributes[ attributeName ] = { array: arrayBuffer, itemSize: attribute.itemSize };\n'
        '\n'
        '\t\t\ttransferable.push( arrayBuffer );\n'
        '\n'
        '\t\t}\n'
        '\n'
        '\t\tpostMessage(\n'
        '\t\t\t{\n'
        '\t\t\t\tstatus: \'ok\',\n'
        '\t\t\t\tindex: indexBuffer,'
    )
    new = (
        'const index = terrainTile.index;\n'
        '\t\tconst attributes = {};\n'
        '\t\tconst transferable = [];\n'
        '\n'
        '\t\ttransferable.push( index.array.buffer );\n'
        '\n'
        '\t\tconst srcAttributes = terrainTile.attributes;\n'
        '\n'
        '\t\tfor ( const attributeName in srcAttributes ) {\n'
        '\n'
        '\t\t\tconst attribute = srcAttributes[ attributeName ];\n'
        '\n'
        '\t\t\tattributes[ attributeName ] = { array: attribute.array, itemSize: attribute.itemSize };\n'
        '\n'
        '\t\t\ttransferable.push( attribute.array.buffer );\n'
        '\n'
        '\t\t}\n'
        '\n'
        '\t\tpostMessage(\n'
        '\t\t\t{\n'
        '\t\t\t\tstatus: \'ok\',\n'
        '\t\t\t\tindex: { array: index.array },'
    )

    # Handle both \n and \r\n line endings
    if old not in c:
        old = old.replace('\n', '\r\n')
        new = new.replace('\n', '\r\n')

    if old not in c:
        print(f'  SKIP: webMeshWorker already patched or not found in {path}')
        return

    c = c.replace(old, new, 1)
    with open(path, 'w') as f:
        f.write(c)
    print(f'  OK: patched webMeshWorker in {path}')

def patch_tree_traversal(path):
    """Replace recursive Tree traversal with iterative traversal for large surveys."""
    with open(path, 'r') as f:
        c = f.read()

    replacements = [
        (
            (
                'Tree.prototype.traverse = function ( func ) {\n'
                '\n'
                '\t\tfunc ( this );\n'
                '\n'
                '\t\tif ( this.children === undefined ) return;\n'
                '\n'
                '\t\tconst children = this.children;\n'
                '\n'
                '\t\tfor ( let i = 0; i < children.length; i++ ) {\n'
                '\n'
                '\t\t\tchildren[ i ].traverse( func );\n'
                '\n'
                '\t\t}\n'
                '\n'
                '\t};'
            ),
            (
                'Tree.prototype.traverse = function ( func ) {\n'
                '\n'
                '\t\tconst stack = [ this ];\n'
                '\t\tconst seen = new Set();\n'
                '\n'
                '\t\twhile ( stack.length > 0 ) {\n'
                '\n'
                '\t\t\tconst node = stack.pop();\n'
                '\n'
                '\t\t\tif ( seen.has( node ) ) continue;\n'
                '\n'
                '\t\t\tseen.add( node );\n'
                '\n'
                '\t\t\tfunc( node );\n'
                '\n'
                '\t\t\tconst children = node.children;\n'
                '\n'
                '\t\t\tif ( children === undefined ) continue;\n'
                '\n'
                '\t\t\tfor ( let i = children.length - 1; i >= 0; i-- ) {\n'
                '\n'
                '\t\t\t\tstack.push( children[ i ] );\n'
                '\n'
                '\t\t\t}\n'
                '\n'
                '\t\t}\n'
                '\n'
                '\t};'
            ),
            'Tree.traverse',
        ),
        (
            (
                'Tree.prototype.traverseDepthFirst = function ( func ) {\n'
                '\n'
                '\t\tconst children = this.children;\n'
                '\n'
                '\t\tfor ( let i = 0; i < children.length; i++ ) {\n'
                '\n'
                '\t\t\tchildren[ i ].traverseDepthFirst( func );\n'
                '\n'
                '\t\t}\n'
                '\n'
                '\t\tfunc( this );\n'
                '\n'
                '\t};'
            ),
            (
                'Tree.prototype.traverseDepthFirst = function ( func ) {\n'
                '\n'
                '\t\tconst stack = [ { node: this, visited: false } ];\n'
                '\t\tconst seen = new Set();\n'
                '\n'
                '\t\twhile ( stack.length > 0 ) {\n'
                '\n'
                '\t\t\tconst entry = stack.pop();\n'
                '\t\t\tconst node = entry.node;\n'
                '\n'
                '\t\t\tif ( entry.visited ) {\n'
                '\n'
                '\t\t\t\tfunc( node );\n'
                '\t\t\t\tcontinue;\n'
                '\n'
                '\t\t\t}\n'
                '\n'
                '\t\t\tif ( seen.has( node ) ) continue;\n'
                '\n'
                '\t\t\tseen.add( node );\n'
                '\n'
                '\t\t\tstack.push( { node: node, visited: true } );\n'
                '\n'
                '\t\t\tconst children = node.children;\n'
                '\n'
                '\t\t\tif ( children === undefined ) continue;\n'
                '\n'
                '\t\t\tfor ( let i = children.length - 1; i >= 0; i-- ) {\n'
                '\n'
                '\t\t\t\tstack.push( { node: children[ i ], visited: false } );\n'
                '\n'
                '\t\t\t}\n'
                '\n'
                '\t\t}\n'
                '\n'
                '\t};'
            ),
            'Tree.traverseDepthFirst',
        ),
    ]

    patched = False

    for old, new, label in replacements:
        old_candidate = old
        new_candidate = new

        if old_candidate not in c:
            old_candidate = old_candidate.replace('\n', '\r\n')
            new_candidate = new_candidate.replace('\n', '\r\n')

        if old_candidate in c:
            c = c.replace(old_candidate, new_candidate, 1)
            patched = True
            print(f'  OK: patched {label} in {path}')
        elif new in c or new.replace('\n', '\r\n') in c:
            print(f'  SKIP: {label} already patched in {path}')
        else:
            print(f'  SKIP: {label} pattern not found in {path}')

    if patched:
        with open(path, 'w') as f:
            f.write(c)

def patch_station_position_tree_fields(path):
    """Give each station node its own tree fields for station-as-prefix cases."""
    with open(path, 'r') as f:
        c = f.read()

    old = (
        '\t\t\tthis.stationVertexIndex = -1;\n'
        '\n'
        '\t\t}\n'
    )
    new = (
        '\t\t\tthis.stationVertexIndex = -1;\n'
        '\t\t\tthis.children = [];\n'
        '\t\t\tthis.boundingBox = new Box3();\n'
        '\t\t\tthis.stationCount = 0;\n'
        '\n'
        '\t\t}\n'
    )

    if new in c:
        print(f'  SKIP: StationPosition tree fields already patched in {path}')
        return

    if old not in c:
        old = old.replace('\n', '\r\n')
        new = new.replace('\n', '\r\n')

    if old not in c:
        print(f'  SKIP: StationPosition tree fields pattern not found in {path}')
        return

    c = c.replace(old, new, 1)

    with open(path, 'w') as f:
        f.write(c)

    print(f'  OK: patched StationPosition tree fields in {path}')

if __name__ == '__main__':
    caveview_dir = sys.argv[1] if len(sys.argv) > 1 else 'public/CaveView'
    print(f'Patching CaveView in {caveview_dir}...')
    caveview_js = os.path.join(caveview_dir, 'js', 'CaveView2.js')
    patch_crs_regex(caveview_js)
    patch_station_position_tree_fields(caveview_js)
    patch_tree_traversal(caveview_js)
    patch_web_mesh_worker(os.path.join(caveview_dir, 'js', 'workers', 'webMeshWorker.js'))
