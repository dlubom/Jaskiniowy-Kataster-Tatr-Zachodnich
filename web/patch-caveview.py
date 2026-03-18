#!/usr/bin/env python3
"""
Patch CaveView.js 2.9.0 bugs for Cesium terrain support.
Remove this script when CaveView releases a fixed version.

Bug 1: CRS regex is case-sensitive — EPSG:32634 (uppercase from Survex) not matched.
Bug 2: webMeshWorker sends raw ArrayBuffer instead of typed arrays, crashing hydrateGeometry.
"""
import sys
import os

def patch_crs_regex(path):
    """Add case-insensitive flag to EPSG/ESRI regex in CaveView2.js."""
    with open(path, 'r') as f:
        c = f.read()
    old = '/(epsg|esri):([0-9]+)/'
    new = '/(epsg|esri):([0-9]+)/i'
    if old not in c:
        print(f'  SKIP: CRS regex already patched or not found in {path}')
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

if __name__ == '__main__':
    caveview_dir = sys.argv[1] if len(sys.argv) > 1 else 'public/CaveView'
    print(f'Patching CaveView in {caveview_dir}...')
    patch_crs_regex(os.path.join(caveview_dir, 'js', 'CaveView2.js'))
    patch_web_mesh_worker(os.path.join(caveview_dir, 'js', 'workers', 'webMeshWorker.js'))
