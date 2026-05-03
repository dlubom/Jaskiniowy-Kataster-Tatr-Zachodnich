#!/usr/bin/env bash
# =============================================================================
# exports.sh — export pipeline, used both locally (Docker) and in GitHub Actions CI.
#
# Generates all derived files from KATASTER.wpj and writes them to
# <BASEDIR>/JKTZ-<VERSION>/.
#
# Usage (from repo root):
#   # Local — via Docker (output visible on host via bind mount):
#   docker run --rm -v "$(pwd):/project" jktz-survex bash docker/exports.sh [VERSION]
#
#   # CI — directly on the runner (Survex installed):
#   bash docker/exports.sh <VERSION> .
#
# Arguments:
#   $1  VERSION  — defaults to "local"
#   $2  BASEDIR  — output base directory, defaults to "exports"
# =============================================================================
set -euo pipefail

VERSION="${1:-local}"
BASEDIR="${2:-exports}"
OUTDIR="${BASEDIR}/JKTZ-${VERSION}"
TMPDIR_LOCAL="${BASEDIR}/tmp"
mkdir -p "${TMPDIR_LOCAL}"
trap 'rm -rf "${TMPDIR_LOCAL}"' EXIT

echo "=== JKTZ exports — version: ${VERSION} ==="
echo "    output: ${OUTDIR}/"
echo ""

mkdir -p "${OUTDIR}/caves"

# -----------------------------------------------------------------------------
# 1. Compile the survey network with cavern.
#    Reads KATASTER.wpj → writes KATASTER.3d and KATASTER.err.
#    The .log is saved alongside the other outputs.
# -----------------------------------------------------------------------------
echo "[1/4] cavern — compiling survey network"
cavern KATASTER.wpj 2>&1 | tee "${OUTDIR}/JKTZ-${VERSION}-cavern.log"
cp KATASTER.3d "${OUTDIR}/JKTZ-${VERSION}.3d"
cp KATASTER.err "${OUTDIR}/JKTZ-${VERSION}.err"

# Use the explicitly copied .3d (ensures we always read the cavern-fresh output,
# not a pre-existing Walls-format file that may be in the bind-mounted directory).
COMPILED_3D="${OUTDIR}/JKTZ-${VERSION}.3d"

# -----------------------------------------------------------------------------
# 2. Export a single DXF file containing all survey legs (no surface shots,
#    no splays). Coordinate system comes from KATASTER.3d (already projected).
# -----------------------------------------------------------------------------
echo "[2/4] survexport — full DXF"
survexport --legs --full-coordinates --dxf "${COMPILED_3D}" "${OUTDIR}/JKTZ-${VERSION}.dxf"

# -----------------------------------------------------------------------------
# 3. Convert the full DXF to a single ESRI Shapefile.
#    -dim XYZ preserves elevation.
#    -a_srs EPSG:32634 tags the output with UTM zone 34N (WGS84),
#    which is what Survex uses for this project's projected output.
#    -sql renames EntityHandle → EntHandle to fit the Shapefile/DBF
#    10-char field-name limit (otherwise ogr2ogr emits a "laundered field
#    name" warning and silently truncates).
# -----------------------------------------------------------------------------
SHP_SQL="SELECT Layer, PaperSpace, SubClasses, Linetype, EntityHandle AS EntHandle, Text FROM entities"

echo "[3/4] ogr2ogr — shapefile (all caves)"
ogr2ogr -f "ESRI Shapefile" -dim XYZ -a_srs EPSG:32634 \
    -sql "${SHP_SQL}" \
    "${OUTDIR}/JKTZ-${VERSION}-all.shp" "${OUTDIR}/JKTZ-${VERSION}.dxf"

# -----------------------------------------------------------------------------
# 4. Extract the list of cave IDs from entrance stations in the compiled data.
# -----------------------------------------------------------------------------
echo "[4/4] survexport — per-cave DXF + shapefiles"
survexport --entrances --csv "${COMPILED_3D}" ${TMPDIR_LOCAL}/entrances.csv
caves=$(tail -n+2 ${TMPDIR_LOCAL}/entrances.csv | cut -d, -f4 | sed 's/:.*//' | sort -u)

for cave in $caves; do
    echo "      → ${cave}"
    survexport --legs --full-coordinates --survey="${cave}" --dxf "${COMPILED_3D}" "${TMPDIR_LOCAL}/${cave}.dxf"
    ogr2ogr -f "ESRI Shapefile" -dim XYZ -a_srs EPSG:32634 \
        -sql "${SHP_SQL}" \
        "${OUTDIR}/caves/${cave}.shp" "${TMPDIR_LOCAL}/${cave}.dxf"
done

echo ""
echo "=== Done ==="
echo "    ${OUTDIR}/"
