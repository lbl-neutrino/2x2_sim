#!/usr/bin/env bash

source ../util/reload_in_container.inc.sh
source ../util/init.inc.sh

dk2nuAll=("$ARCUBE_DK2NU_DIR"/*.dk2nu*)
dk2nuCount=${#dk2nuAll[@]}
dk2nuIdx=$((ARCUBE_INDEX % dk2nuCount))
dk2nuFile=${dk2nuAll[$dk2nuIdx]}
echo "dk2nuIdx is $dk2nuIdx"
echo "dk2nuFile is $dk2nuFile"

export GXMLPATH=$PWD/flux            # contains GNuMIFlux.xml
maxPathFile=$PWD/maxpath/$(basename "$ARCUBE_GEOM" .gdml).$ARCUBE_TUNE.maxpath.xml
USE_MAXPATH=1
if [ ! -f "$maxPathFile" ]; then
    echo ""
    echo "WARNING!!! .maxpath.xml file not found. Is this what you intended???"
    echo "           I WILL CONTINUE WITH NO maxPathFile"
    echo ""
    USE_MAXPATH=0
fi

genieOutPrefix=$tmpOutDir/$outName

# HACK: gevgen_fnal hardcodes the name of the status file (unlike gevgen, which
# respects -o), so run it in a temporary directory. Need to get absolute paths.

dk2nuFile=$(realpath "$dk2nuFile")
# The geometry file is given relative to the root of 2x2_sim
# ($baseDir is already an absoulte path)
geomFile=$baseDir/$ARCUBE_GEOM
ARCUBE_XSEC_FILE=$(realpath "$ARCUBE_XSEC_FILE")

tmpDir=$(mktemp -d)
pushd "$tmpDir"

rm -f "$genieOutPrefix".*

args_gevgen_fnal=( \
    -e "$ARCUBE_EXPOSURE" \
    -f "$dk2nuFile,$ARCUBE_DET_LOCATION" \
    -g "$geomFile" \
    -r "$runNo" \
    -L cm -D g_cm3 \
    --cross-sections "$ARCUBE_XSEC_FILE" \
    --tune "$ARCUBE_TUNE" \
    --seed "$seed" \
    -o "$genieOutPrefix" \
    )

[ "${USE_MAXPATH}" == 1 ] && args_gevgen_fnal+=( -m "$maxPathFile" )
[ -n "${ARCUBE_TOP_VOLUME}" ] && args_gevgen_fnal+=( -t "$ARCUBE_TOP_VOLUME" )
[ -n "${ARCUBE_FID_CUT_STRING}" ] && args_gevgen_fnal+=( -F "$ARCUBE_FID_CUT_STRING" )
[ -n "${ARCUBE_ZMIN}" ] && args_gevgen_fnal+=( -z "$ARCUBE_ZMIN" )
[ -n "${ARCUBE_EVENT_GEN_LIST}" ] && args_gevgen_fnal+=( --event-generator-list "$ARCUBE_EVENT_GEN_LIST" )

run gevgen_fnal "${args_gevgen_fnal[@]}"

statDir=$logBase/STATUS/$subDir
mkdir -p "$statDir"
mv genie-mcjob-"$runNo".status "$statDir/$outName.status"
popd
rmdir "$tmpDir"

# use consistent naming convention w/ rest of sim chain
mv "$genieOutPrefix"."$runNo".ghep.root "$genieOutPrefix".GHEP.root

run gntpc -i "$genieOutPrefix".GHEP.root -f rootracker \
    -o "$genieOutPrefix".GTRAC.root

mkdir -p "$outDir/GHEP/$subDir"  "$outDir/GTRAC/$subDir"
mv "$genieOutPrefix.GHEP.root" "$outDir/GHEP/$subDir"
mv "$genieOutPrefix.GTRAC.root" "$outDir/GTRAC/$subDir"
