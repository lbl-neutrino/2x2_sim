#!/usr/bin/env bash

export ARCUBE_RUNTIME=SHIFTER
export ARCUBE_CONTAINER=fermilab/fnal-wn-sl7:latest
export ARCUBE_DIR=$(realpath "$PWD"/..)

source $ARCUBE_DIR/util/reload_in_container.inc.sh

source setup_pandora.sh

# Create install directory
cd $ARCUBE_DIR
mkdir -p $ARCUBE_PANDORA_INSTALL

# PandoraPFA (cmake files)
cd $ARCUBE_PANDORA_INSTALL
git clone https://github.com/PandoraPFA/PandoraPFA.git
cd PandoraPFA
git checkout $ARCUBE_PANDORA_PFA_VERSION

# PandoraSDK (Abstract interface and software development kit)
cd $ARCUBE_PANDORA_INSTALL
git clone https://github.com/PandoraPFA/PandoraSDK.git
cd PandoraSDK
git checkout $ARCUBE_PANDORA_SDK_VERSION
mkdir build
cd build
cmake -DCMAKE_MODULE_PATH=$ARCUBE_PANDORA_INSTALL/PandoraPFA/cmakemodules ..
make -j4 install

# PandoraMonitoring (ROOT event displays and output)
cd $ARCUBE_PANDORA_INSTALL
git clone https://github.com/PandoraPFA/PandoraMonitoring.git
cd PandoraMonitoring
git checkout $ARCUBE_PANDORA_MONITORING_VERSION
mkdir build
cd build
cmake -DCMAKE_MODULE_PATH="$ARCUBE_PANDORA_INSTALL/PandoraPFA/cmakemodules;$ROOTSYS/etc/cmake" \
-DPandoraSDK_DIR=$ARCUBE_PANDORA_INSTALL/PandoraSDK ..
make -j4 install

# LArContent (algorithms) without LibTorch (no Deep Learning Vertexing)
cd $ARCUBE_PANDORA_INSTALL
git clone https://github.com/PandoraPFA/LArContent.git
cd LArContent
git checkout $ARCUBE_PANDORA_LAR_CONTENT_VERSION
mkdir build
cd build
cmake -DCMAKE_MODULE_PATH="$ARCUBE_PANDORA_INSTALL/PandoraPFA/cmakemodules;$ROOTSYS/etc/cmake" \
-DPANDORA_MONITORING=ON -DPandoraSDK_DIR=$ARCUBE_PANDORA_INSTALL/PandoraSDK \
-DPandoraMonitoring_DIR=$ARCUBE_PANDORA_INSTALL/PandoraMonitoring \
-DEigen3_DIR=$EIGEN_DIR/Eigen3/share/eigen3/cmake/ ..
make -j4 install

# LArRecoND (DUNE ND reco)
cd $ARCUBE_PANDORA_INSTALL
git clone https://github.com/PandoraPFA/LArRecoND.git
cd LArRecoND
git checkout $ARCUBE_PANDORA_LAR_RECO_ND_VERSION
mkdir build
cd build
cmake -DCMAKE_MODULE_PATH="$ARCUBE_PANDORA_INSTALL/PandoraPFA/cmakemodules;$ROOTSYS/etc/cmake" \
-DPANDORA_MONITORING=ON -DPandoraSDK_DIR=$ARCUBE_PANDORA_INSTALL/PandoraSDK/ \
-DPandoraMonitoring_DIR=$ARCUBE_PANDORA_INSTALL/PandoraMonitoring/ \
-DLArContent_DIR=$ARCUBE_PANDORA_INSTALL/LArContent ..
make -j4 install

# LArMachineLearningData (BDT, MVA & Deep Learning training files)
cd $ARCUBE_PANDORA_INSTALL
git clone https://github.com/PandoraPFA/LArMachineLearningData.git
cd LArMachineLearningData
git checkout $ARCUBE_PANDORA_LAR_MLDATA_VERSION
# Download training files: only do this once to avoid google drive's access restrictions (up to 24 hrs wait)
. download.sh sbnd
. download.sh dune
. download.sh dunend

# Install h5flow for converting HDF5 input files to ROOT for LArRecoND
cd $ARCUBE_PANDORA_INSTALL
git clone https://github.com/lbl-neutrino/h5flow.git
echo "Setting up pandora.venv for h5flow"
python3 -m venv pandora.venv
source pandora.venv/bin/activate
cd h5flow
pip3 install .
deactivate

# Convert GDML geometry file to ROOT for LArRecoND (using cm length units)
root -l -b -q -e "TGeoManager::LockDefaultUnits(kFALSE); TGeoManager::SetDefaultUnits(TGeoManager::kRootUnits); TGeoManager::Import(\"${ARCUBE_GEOM}\"); gGeoManager->Export(\"${ARCUBE_PANDORA_GEOM}\");"
