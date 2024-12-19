#!/usr/bin/env bash

# CORSIKA needs the FNAL environment to run
# So override the container definition and put it back at the end
ORG_CONTAINER=${ARCUBE_CONTAINER}
export ARCUBE_RUNTIME=SHIFTER
export ARCUBE_CONTAINER=fermilab/fnal-wn-sl7:latest

source ../util/reload_in_container.inc.sh
source ../util/init.inc.sh

# Need to unset these options to allow UPS to not exit on error
set +o errexit
set +o pipefail

# Run the necessary UPS setup commands and finally CORSIKA
source /cvmfs/dune.opensciencegrid.org/products/dune/setup_dune.sh
source /cvmfs/mu2e.opensciencegrid.org/setupmu2e-art.sh
setup corsika
# setup python v3_9_15

NSHOW=${ARCUBE_NSHOW:-10000}
RNDSEED=110
RNDSEED2=1210

if [ "${ARCUBE_LOC}" == "BERN" ]; then
    # Bern (single module tests)
    DETNAME=BERN
    OBSLEV=550E2
    Bx=21.793
    Bz=42.701
elif [ "${ARCUBE_LOC}" == "MINOS" ]; then
    # MINOS Hall (2x2)
    DETNAME=MINOS_HALL
    OBSLEV=119E2
    Bx=19.310
    Bz=49.433
else
    echo "Invalid location for cosmic simulation: ${ARCUBE_LOC}"
    echo "Set \$ARCUBE_LOC to a valid choice"
    exit 1
fi

echo "Generating ${NSHOW} showers / events."
echo "Using observation level of ${OBSLEV} cm and magnetic field values of Bx = ${Bx} and Bz = ${Bz} microteslas, corresponding to ${DETNAME}."

##################################################
# Run CORSIKA

gen_corsika_config() {
cat << EOF > corsika_${runNo}.cfg
RUNNR   ${runNo}                       run number
EVTNR   1                              number of first shower event
NSHOW   ${NSHOW}                       number of showers to generate
PRMPAR  14                             particle type of prim. particle  (14=p)
ESLOPE  -2.7                           slope of primary energy spectrum
ERANGE  1.3 100000                    energy range of primary (GeV)
THETAP  0.  84.9                        range of zenith angle (degree)
PHIP    -180.  180.                    range of azimuth angle (degree)
SEED    ${RNDSEED}   0  0                 seed for 1. random number sequence
SEED    ${RNDSEED2}   0  0                 seed for 2. random number sequence
QGSJET  T   0                              QGSJET for high energy & debug level
QGSSIG  T                                    QGSJET cross-sections enable
OBSLEV  ${OBSLEV}                         observation level in cm
CURVOUT F
MAGNET  ${Bx} ${Bz}                 Earth's mag. field at detector- Bx & Bz
HADFLG  0  0  0  0  0  2               flags hadr.interact.&fragmentation
ECUTS   0.05 0.05 0.05 0.05            energy cuts for particles
MUADDI  F                              additional info for muons
MUMULT  T                              muon multiple scattering angle
ELMFLG  F   T                          em. interaction flags (NKG,EGS)
STEPFC  1.0                            mult. scattering step length fact.
RADNKG  200.E2                         outer radius for NKG lat.dens.distr.
ARRANG  0                              rotation of array to north
ATMOD   1                                    U.S. standard atmosphere (1-Linsley; 22-Keilhauer)
LONGI   F  20.  F  F                   longit.distr. & step size & fit & out
ECTMAP  1.E2                           cut on gamma factor for printout
MAXPRT  0                            max. number of printed events
DIRECT  ${PWD}/                             output directory
DATDIR  /cvmfs/mu2e.opensciencegrid.org/artexternals/corsika/v77400/Linux64bit+3.10-2.17/run                      CORSIKA directory
DATBAS  F                              write .dbase file
USER    ${USER}                         user
DEBUG   F  6  F  1000000               debug flag and log.unit for out
EXIT                                   terminates input
EOF
}
gen_corsika_config

corsika77400Linux_QGSJET_fluka < corsika_${runNo}.cfg #> ${logDir}/corsika.${runNo}.log

printf -v CORSIKA_OUTPUT "DAT%.6d" ${runNo}
# mv ${CORSIKA_OUTPUT} ${outDir}/${outName}.dat

export ARCUBE_CONTAINER=$ORG_ARCUBE_CONTAINER

# Clean up after CORSIKA
if [ -f .timer.out ]; then
    rm .timer.out
fi
