#!/usr/bin/env bash

export ARCUBE_CONTAINER='mjkramer/sim2x2:ndlar011'
export ARCUBE_EDEP_MAC='macros/particle-gun.mac'
export ARCUBE_GEOM='geometry/nd_hall_with_lar_tms_sand_TDR_Production_geometry_v_1.0.3.gdml'
export ARCUBE_LOGDIR_BASE='/pscratch/sd/t/tta20/Particle_Gun3/test1/logs'
export ARCUBE_OUTDIR_BASE='/pscratch/sd/t/tta20/Particle_Gun3/test1/output'
export ARCUBE_RUNTIME='SHIFTER'
export ARCUBE_BEAM_TYPE='particle_gun'
export ARCUBE_EXPOSURE='1E6'
export ARCUBE_PARTICLE_TYPE='mu-'
export ARCUBE_ENERGY_MINIMUM='300 MeV'
export ARCUBE_ENERGY_MAXIMUM='3 GeV'

for i in $(seq 10); do
    ARCUBE_INDEX=$i ./run_edep_sim.sh &
done

wait