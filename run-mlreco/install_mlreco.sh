#!/usr/bin/env bash

export ARCUBE_RUNTIME=SHIFTER
# export ARCUBE_CONTAINER=deeplearnphysics/larcv2:ub20.04-cuda11.3-cudnn8-pytorch1.10.0-larndsim-2022-11-03
## Above but with venv support:
# export ARCUBE_CONTAINER=mjkramer/sim2x2:mlreco001
# This is the one that Francois has actually been using:
export ARCUBE_CONTAINER=deeplearnphysics/larcv2:ub20.04-cuda11.6-pytorch1.13-larndsim

source ../util/reload_in_container.inc.sh

set -o errexit

# recommended by Jeremy
unset which

mkdir weights
cd weights
wget https://portal.nersc.gov/project/dune/data/2x2/simulation/mlreco_weights/2x2_240819_snapshot.ckpt
cd ..

mkdir install
cd install

# The Ubuntu container doesn't support Python's built-in "venv" module unless we
# globally "apt install python3.8-venv". To avoid the pain of modifying the
# container, instead let's use virtualenv.
wget https://bootstrap.pypa.io/virtualenv/3.8/virtualenv.pyz
python virtualenv.pyz --system-site-packages mlreco.venv
rm virtualenv.pyz

# python3 -m venv --system-site-packages mlreco.venv
source mlreco.venv/bin/activate
# setuptools 70 doesn't like SparseConvNet
# (pkg_resources.packaging is the culprit)
pip install --upgrade pip setuptools==69 wheel
# pip install 'ruamel.yaml<0.18.0' # for deprecated load()

## Need the following?
# pip install scikit-build # for SuperaAtomic
# pip install scikit-learn # for flow2supera
# pip install --upgrade torch_geometric # for mlreco

git clone -b v2_3_0 https://github.com/DeepLearnPhysics/larcv2.git
cd larcv2
source configure.sh
make -j16
cd ..

git clone -b v1.8.0 https://github.com/DeepLearnPhysics/SuperaAtomic.git

cd SuperaAtomic
git submodule update --init     # pybind11
pip install .
cd ..

git clone -b nd-production-v02.01 https://github.com/YifanC/larpix_readout_parser.git
cd larpix_readout_parser
pip install .
cd ..

git clone -b main https://github.com/larpix/h5flow.git
cd h5flow
pip install .
cd ..


git clone -b v4.1.2 https://github.com/DeepLearnPhysics/flow2supera.git
## Don't pip install because e.g. config files are expected to live near
## __file__
# cd flow2supera
# pip install .
# cd ..

git clone https://github.com/facebookresearch/SparseConvNet.git
cd SparseConvNet
# These paths don't exist in the container
# They lead to `nvcc' being sought in the wrong place`
unset CUDATOOLKIT_HOME
unset CUDA_HOME
pip install .
cd ..

# commit 8103996
# git clone -b jw_dune_nd_lar https://github.com/chenel/lartpc_mlreco3d.git

#git clone -b v2.9.5 https://github.com/DeepLearnPhysics/lartpc_mlreco3d.git
git clone -b v0.1.1-hotfix https://github.com/alexbooth92/spine.git

# git clone https://github.com/chenel/dune-nd-lar-reco.git
# the old yaml.load API has been removed
# sed -i 's/yaml.load(open(filename))/yaml.load(open(filename), yaml.Loader)/' \
#     dune-nd-lar-reco/load_helpers.py
