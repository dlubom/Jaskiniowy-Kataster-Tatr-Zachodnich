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
#    Source of truth for the cave list is #prefix directives in the .SRV
#    files (not the entrances CSV) — some caves have sub-prefixes where
#    only one sub-prefix has an /ENTRANCE flag (e.g. Goryczkowa: G1 has
#    the entrance, G2..G5 don't but still hold legs). Grouping is by the
#    first dotted component of the prefix:
#       Czarna, Czarna.Borowiec, Czarna.Kujat, …  → cave "Czarna"
#       Goryczkowa.G1 .. Goryczkowa.G5            → cave "Goryczkowa"
#       BandziochKom                              → cave "BandziochKom"
#
#    Survex treats each #prefix value as an independent survey name —
#    the dot in `Czarna.Kujat` is part of the name, NOT a parent/child
#    separator (cavern sees `Czarna` and `Czarna.Kujat` as peer
#    surveys). So `--survey=Czarna` returns ONLY legs in the survey
#    literally named `Czarna`, never its sub-prefix peers. We iterate
#    every declared prefix and merge the resulting DXFs into a single
#    per-cave shapefile via ogr2ogr -append. A prefix file with only a
#    #fix and no legs (e.g. CZ_Z_M.SRV) yields an empty DXF — harmless,
#    other sub-prefixes populate the shapefile.
# -----------------------------------------------------------------------------
echo "[4/5] survexport — per-cave DXF + shapefiles"

# Entrances list — emitted as a release artifact (UTM coords of every
# /ENTRANCE-flagged station). Not the source of truth for the cave list.
survexport --entrances --csv "${COMPILED_3D}" "${OUTDIR}/JKTZ-${VERSION}-entrances.csv"

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

for cave in $(printf '%s\n' "${!CAVE_PREFIXES[@]}" | sort); do
    echo "      → ${cave}"
    cave_shp="${OUTDIR}/caves/${cave}.shp"

    first=1
    for prefix in ${CAVE_PREFIXES[$cave]}; do
        tmp_dxf="${TMPDIR_LOCAL}/${prefix//./_}.dxf"
        survexport --legs --full-coordinates --survey="${prefix}" \
                   --dxf "${COMPILED_3D}" "${tmp_dxf}"
        if (( first )); then
            ogr2ogr -f "ESRI Shapefile" -dim XYZ -a_srs EPSG:32634 \
                -sql "${SHP_SQL}" \
                "${cave_shp}" "${tmp_dxf}"
            first=0
        else
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
