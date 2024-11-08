#!/usr/bin/env bash

set -o errexit

module load python/3.11

installDir=${1:-.}
venvName=flow.venv

if [[ -e "$installDir/$venvName" ]]; then
  echo "$installDir/$venvName already exists; delete it then run me again"
  exit 1
fi

if [[ -e "$installDir/h5flow" ]]; then
  echo "$installDir/h5flow already exists; delete it then run me again"
  exit 1
fi

if [[ -e "$installDir/ndlar_flow" ]]; then
  echo "$installDir/ndlar_flow already exists; delete it then run me again"
  exit 1
fi

staticDir=$(realpath ./static)

mkdir -p "$installDir"
cd "$installDir"

python -m venv "$venvName"
source "$venvName"/bin/activate

pip install --upgrade pip setuptools wheel

pip install pyyaml-include==1.3.2

# install h5flow
git clone -b main https://github.com/larpix/h5flow.git
cd h5flow
pip install -e .
cd ..

# install ndlar_flow
git clone -b MiniRun6.1 https://github.com/larpix/ndlar_flow.git
cd ndlar_flow
pip install -e .
cd scripts/proto_nd_scripts
./get_proto_nd_input.sh
# AB August 6th 2024: ../ndlar_scripts only exists in development branch at the moment.
if [ -d ../ndlar_scripts ]; then
  cd ../ndlar_scripts
  ./get_ndlar_input.sh
fi
cd ../../..
