#!/usr/bin/env bash

# Example run environment setup
#export ARCUBE_RUNTIME=SHIFTER
#export ARCUBE_CONTAINER=fermilab/fnal-wn-sl7:latest
#export ARCUBE_DIR=$(realpath "$PWD"/..)
#export ARCUBE_IN_NAME=Tutorial.flow
#export ARCUBE_OUT_NAME=Tutorial.flow2root
#export ARCUBE_INDEX=0

# Container
source $ARCUBE_DIR/util/reload_in_container.inc.sh

# Setup Pandora environment
source $ARCUBE_DIR/run-pandora/setup_pandora.sh

# Set other environment variables: globalIdx, ARCUBE_OUTDIR_BASE, tmpOutDir, outDir, outName, subDir
source $ARCUBE_DIR/util/init.inc.sh

# Input HDF5 file
inName=${ARCUBE_IN_NAME}.${globalIdx}
inFile=${ARCUBE_OUTDIR_BASE}/run-ndlar-flow/${ARCUBE_IN_NAME}/FLOW/${subDir}/${inName}.FLOW.hdf5

# Convert input HDF5 file to ROOT
source $ARCUBE_PANDORA_INSTALL/pandora.venv/bin/activate
python3 $ARCUBE_PANDORA_INSTALL/LArRecoND/ndlarflow/h5_to_root_ndlarflow.py $inFile 0 $tmpOutDir
deactivate

# Move ROOT file from tmpOutDir to output directory
rootOutDir=$outDir/FLOW/$subDir
mkdir -p "${rootOutDir}"
rootFile=${rootOutDir}/${outName}.FLOW.hdf5_hits.root
tmpRootFile=${tmpOutDir}/${inName}.FLOW.hdf5_hits.root
mv "${tmpRootFile}" "${rootFile}"
