#!/usr/bin/env bash

export ARCUBE_RUNTIME='SHIFTER'
export ARCUBE_CONTAINER='mjkramer/sim2x2:ndlar011'
export ARCUBE_ACTIVE_VOLUME='TPCActive_shape'
export ARCUBE_LOGDIR_BASE='/pscratch/sd/t/tta20/Muon_Gun_test/logs'
export ARCUBE_OUTDIR_BASE='/pscratch/sd/t/tta20/Muon_Gun_test/output'
export ARCUBE_KEEP_ALL_DETS='1'
export ARCUBE_SINGLE_NAME='Muon_Gun_Test.edep.nu'
export ARCUBE_OUT_NAME='Muon_Gun_Test.convert2h5.nu'

for i in $(seq 0 9); do
    ARCUBE_INDEX=$i ./run_convert2h5.sh &
done

wait