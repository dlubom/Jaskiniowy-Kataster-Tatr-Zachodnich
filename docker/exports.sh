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

echo "[3/5] ogr2ogr — shapefile (all caves)"
ogr2ogr -f "ESRI Shapefile" -dim XYZ -a_srs EPSG:32634 \
    -sql "${SHP_SQL}" \
    "${OUTDIR}/JKTZ-${VERSION}-all.shp" "${OUTDIR}/JKTZ-${VERSION}.dxf"

# -----------------------------------------------------------------------------
# 4. Per-cave DXF + shapefile, one .shp per cave under caves/.
#
#    Steps:
#      1. Scrape unique #prefix values from Poligony/**/*.SRV (skip _RAW/).
#      2. Group prefixes by the part before the first dot — that's the cave
#         (e.g. Czarna, Czarna.Borowiec → "Czarna"; Goryczkowa.G1..G5 →
#         "Goryczkowa"). CAVE_ID metadata is NOT used; grouping is pure
#         string match on the prefix.
#      3. For each cave, run survexport --survey=<prefix> once per prefix
#         (Survex treats each #prefix as an independent survey, so peers
#         like Czarna.Kujat are exported separately).
#      4. First DXF creates caves/<cave>.shp via ogr2ogr; each subsequent
#         DXF is merged in with ogr2ogr -append.
#   Files produced for each cave (ESRI Shapefile is a multi-file format):
#     caves/<cave>.shp  — geometry (3D polylines of survey legs)
#     caves/<cave>.shx  — geometry index
#     caves/<cave>.dbf  — attribute table (Layer, PaperSpace, SubClasses,
#                         Linetype, EntHandle, Text)
#     caves/<cave>.prj  — projection definition (EPSG:32634, UTM 34N WGS84)
# -----------------------------------------------------------------------------

echo "[4/5] survexport — per-cave DXF + shapefiles"

# 4a. Collect every #prefix from SRV files and group by base (part before the
#     first dot) into CAVE_PREFIXES[cave] = "prefix1 prefix2 ...".
declare -A CAVE_PREFIXES
while read -r prefix; do
    cave="${prefix%%.*}"
    CAVE_PREFIXES[$cave]+="${prefix} "
done < <(LC_ALL=C grep -rh '^#prefix ' Poligony --include='*.SRV' \
         | grep -v '/_RAW/' \
         | tr -d '\r' \
         | awk '{print $2}' \
         | grep -v '^$' \
         | sort -u)

# 4b. For each cave (sorted), export each of its prefixes to a temp DXF,
#     then build caves/<cave>.shp from the first DXF and append the rest.
for cave in $(printf '%s\n' "${!CAVE_PREFIXES[@]}" | sort); do
    echo "      → ${cave}"
    cave_shp="${OUTDIR}/caves/${cave}.shp"

    first=1
    for prefix in ${CAVE_PREFIXES[$cave]}; do
        # Per-prefix DXF in TMPDIR_LOCAL (cleaned by the EXIT trap).
        tmp_dxf="${TMPDIR_LOCAL}/${prefix//./_}.dxf"
        survexport --legs --full-coordinates --survey="${prefix}" \
                   --dxf "${COMPILED_3D}" "${tmp_dxf}"
        if (( first )); then
            # First prefix: create the shapefile.
            ogr2ogr -f "ESRI Shapefile" -dim XYZ -a_srs EPSG:32634 \
                -sql "${SHP_SQL}" \
                "${cave_shp}" "${tmp_dxf}"
            first=0
        else
            # Subsequent prefixes: merge into the existing shapefile.
            ogr2ogr -append -f "ESRI Shapefile" -dim XYZ -a_srs EPSG:32634 \
                -sql "${SHP_SQL}" \
                "${cave_shp}" "${tmp_dxf}"
        fi
    done
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
