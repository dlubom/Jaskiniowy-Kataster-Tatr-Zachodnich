#!/usr/bin/env bash
# =============================================================================
# exports.sh — export pipeline, used both locally (Docker) and in GitHub Actions CI.
#
# Generates all derived files from KATASTER.wpj and writes them to
# <BASEDIR>/JKTZ-<VERSION>/ together with a ZIP archive.
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
echo "[1/5] cavern — compiling survey network"
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
echo "[2/5] survexport — full DXF"
survexport --legs --dxf "${COMPILED_3D}" "${OUTDIR}/JKTZ-${VERSION}.dxf"

# -----------------------------------------------------------------------------
# 3. Convert the full DXF to a single ESRI Shapefile.
#    -dim XYZ preserves elevation.
#    -a_srs EPSG:32634 tags the output with UTM zone 34N (WGS84),
#    which is what Survex uses for this project's projected output.
# -----------------------------------------------------------------------------
echo "[3/5] ogr2ogr — shapefile (all caves)"
ogr2ogr -f "ESRI Shapefile" -dim XYZ -a_srs EPSG:32634 \
    "${OUTDIR}/JKTZ-${VERSION}-all.shp" "${OUTDIR}/JKTZ-${VERSION}.dxf"

# -----------------------------------------------------------------------------
# 4. Extract the list of cave IDs from entrance stations in the compiled data.
#    survexport --csv writes one row per entrance; column 4 is the station
#    name (e.g. "tc1601.0"), stripping everything after the dot gives the
#    cave prefix used in --survey= filtering below.
#
# TODO: This step currently fails with:
#   survexport: error: No survey data in 3d file "exports/JKTZ-<VERSION>/JKTZ-<VERSION>.3d"
# Root cause: cavern only recognises Survex *entrance directives, not Walls
# #flag STATION /ENTRANCE — so no entrance stations are present in the .3d.
# Fix needed: expose entrance stations to Survex (e.g. via *entrance directives
# in a thin .svx wrapper or by converting #flag /ENTRANCE in .SRV files).
# -----------------------------------------------------------------------------
echo "[4/5] survexport — per-cave DXF + shapefiles"
survexport --entrances --csv "${COMPILED_3D}" ${TMPDIR_LOCAL}/entrances.csv
caves=$(tail -n+2 ${TMPDIR_LOCAL}/entrances.csv | cut -d, -f4 | sed 's/:.*//' | sort -u)

for cave in $caves; do
    echo "      → ${cave}"
    survexport --legs --survey="${cave}" --dxf "${COMPILED_3D}" "${TMPDIR_LOCAL}/${cave}.dxf"
    ogr2ogr -f "ESRI Shapefile" -dim XYZ -a_srs EPSG:32634 \
        "${OUTDIR}/caves/${cave}.shp" "${TMPDIR_LOCAL}/${cave}.dxf"
done

# -----------------------------------------------------------------------------
# 5. Bundle everything into a ZIP archive next to the output directory.
# -----------------------------------------------------------------------------
echo "[5/5] zip — bundling output"
(cd "${BASEDIR}" && zip -r "JKTZ-exports-${VERSION}.zip" "JKTZ-${VERSION}/")

echo ""
echo "=== Done ==="
echo "    ${OUTDIR}/"
echo "    ${BASEDIR}/JKTZ-exports-${VERSION}.zip"
