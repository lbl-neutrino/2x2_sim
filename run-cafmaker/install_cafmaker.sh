#!/usr/bin/env bash

export ARCUBE_RUNTIME=SHIFTER
export ARCUBE_CONTAINER=fermilab/fnal-wn-sl7:latest

source ../util/reload_in_container.inc.sh

source /cvmfs/dune.opensciencegrid.org/products/dune/setup_dune.sh
setup edepsim v3_2_0c -q e20:prof

mkdir install
cd install

git clone -b main https://github.com/DUNE/ND_CAFMaker.git
cd ND_CAFMaker

./build.sh
source ndcaf_setup.sh
make -j8
