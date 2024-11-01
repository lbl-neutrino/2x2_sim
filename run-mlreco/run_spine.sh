#!/usr/bin/env bash

source ../util/reload_in_container.inc.sh
source ../util/init.inc.sh

source load_mlreco.inc.sh

[ -z "$ARCUBE_SPINE_CONFIG" ] && export ARCUBE_SPINE_CONFIG="2x2_full_chain_240819.cfg"

# Only export onwards if the vars are filled. The exports are a tip from Kazu and
# required for NDLAr.
[ -n "$ARCUBE_SPINE_NUM_THREADS" ] && export NUM_THREADS=$ARCUBE_SPINE_NUM_THREADS
[ -n "$ARCUBE_SPINE_OPENBLAS_NUM_THREADS" ] && export OPENBLAS_NUM_THREADS=$ARCUBE_SPINE_OPENBLAS_NUM_THREADS

outFile=${tmpOutDir}/${outName}.MLRECO_SPINE.hdf5
inName=${ARCUBE_IN_NAME}.${globalIdx}
inFile=${ARCUBE_OUTDIR_BASE}/run-mlreco/${ARCUBE_IN_NAME}/LARCV/${subDir}/${inName}.LARCV.root
config=$ARCUBE_SPINE_CONFIG

tmpDir=$(mktemp -d)
mkdir "${tmpDir}/log_trash" 

sed "s!%TMPDIR%!${tmpDir}!g" "configs/${config}" > "${tmpDir}/${config}"

run python3 install/spine/bin/run.py \
    --config "${tmpDir}/${config}" \
    --log_dir "$logDir" \
    --source "$inFile" \
    --output "$outFile"


infOutDir=${outDir}/MLRECO_SPINE/${subDir}
mkdir -p "$infOutDir"
mv "$outFile" "$infOutDir"

rm -rf "$tmpDir"
