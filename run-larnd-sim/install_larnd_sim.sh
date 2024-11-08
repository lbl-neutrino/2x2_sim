#!/usr/bin/env bash

set -o errexit

## CUDA 12.2 makes us crash :(
# module load cudatoolkit/12.2
module load cudatoolkit/11.7
module load python/3.11

installDir=${1:-.}
venvName=larnd.venv

if [[ -e "$installDir/$venvName" ]]; then
  echo "$installDir/$venvName already exists; delete it then run me again"
  exit 1
fi

if [[ -e "$installDir/larnd-sim" ]]; then
  echo "$installDir/larnd-sim already exists; delete it then run me again"
  exit 1
fi

mkdir -p "$installDir"
cd "$installDir"

python -m venv "$venvName"
source "$venvName"/bin/activate
pip install --upgrade pip setuptools wheel

# Might need to remove larnd-sim from this requirements file. DONE.
# pip install -r requirements.txt
# exit

# If installation via requirements.txt doesn't work, the below should rebuild
# the venv. Ideally, install everything *except* larnd-sim using the
# requirements.txt, then just use the block at the bottom to install larnd-sim.

# pip install -U pip wheel setuptools
# pip install cupy-cuda11x

# pip install cupy-cuda12x
pip install cupy-cuda11x==13.1.0

# https://docs.nersc.gov/development/languages/python/using-python-perlmutter/#installing-with-pip
( git clone -b MiniRun6.1 https://github.com/DUNE/larnd-sim.git
  cd larnd-sim
  # used for MiniRun4
  # git checkout 383ead57929c15ebcb2d619e79ab6c8a3f610b89
  # HACK: Replace cupy with cupy-cuda11x (no longer necessary; setup.py is smarter now)
  # mv setup.py setup.py.orig
  # sed 's/cupy/cupy-cuda11x/' setup.py.orig > setup.py
  pip install -e . )
  # mv setup.py.orig setup.py )
