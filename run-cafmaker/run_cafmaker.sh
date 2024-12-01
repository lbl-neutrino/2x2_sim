#!/usr/bin/env bash

source ../util/reload_in_container.inc.sh

cd install/ND_CAFMaker
source ndcaf_setup.sh
cd ../..

# Must go after ndcaf_setup.sh
source ../util/init.inc.sh

outFile=${tmpOutDir}/${outName}.CAF.root
flatOutFile=${tmpOutDir}/${outName}.CAF.flat.root
cfgFile=$(mktemp --suffix .cfg)

# Compulsory arguments.
args_gen_cafmaker_cfg=( \
    --base-dir "$ARCUBE_OUTDIR_BASE" \
    --spine-name "$ARCUBE_SPINE_NAME" \
    --pandora-name "$ARCUBE_PANDORA_NAME" \
    --caf-path "$outFile" \
    --cfg-file "$cfgFile" \
    --file-id "$ARCUBE_INDEX" \
    )

[ -n "${ARCUBE_GHEP_NU_NAME}" ] && args_gen_cafmaker_cfg+=( --ghep-nu-name "$ARCUBE_GHEP_NU_NAME" )
[ -n "${ARCUBE_GHEP_ROCK_NAME}" ] && args_gen_cafmaker_cfg+=( --ghep-rock-name "$ARCUBE_GHEP_ROCK_NAME" )
[ -n "${ARCUBE_SPILL_NAME}" ] && args_gen_cafmaker_cfg+=( --edepsim-name "$ARCUBE_SPILL_NAME" )
[ -n "${ARCUBE_MINERVA_NAME}" ] && args_gen_cafmaker_cfg+=( --minerva-name "$ARCUBE_MINERVA_NAME" )
[ -n "${ARCUBE_TMSRECO_NAME}" ] && args_gen_cafmaker_cfg+=( --tmsreco-name "$ARCUBE_TMSRECO_NAME" )
[ -n "${ARCUBE_HADD_FACTOR}" ] && args_gen_cafmaker_cfg+=( --hadd-factor "$ARCUBE_HADD_FACTOR" )
[ -n "${ARCUBE_EXTRA_LINES}" ] && args_gen_cafmaker_cfg+=( --extra-lines "$ARCUBE_EXTRA_LINES" )

./gen_cafmaker_cfg.py "${args_gen_cafmaker_cfg[@]}"

echo ===================
cat "$cfgFile"
echo ""
echo ===================

run makeCAF "--fcl=$cfgFile"

cafOutDir=$outDir/CAF/$subDir
flatCafOutDir=$outDir/CAF.flat/$subDir
mkdir -p "$cafOutDir" "$flatCafOutDir"
mv "$outFile" "$cafOutDir"
mv "$flatOutFile" "$flatCafOutDir"

rm "$cfgFile"
