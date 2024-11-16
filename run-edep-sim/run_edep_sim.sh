#!/usr/bin/env bash

source ../util/reload_in_container.inc.sh
source ../util/init.inc.sh

if [ $(echo "$ARCUBE_BEAM_TYPE") = "particle_gun" ]; 
<<<<<<< HEAD
    then nEvents=$(printf "%.0f" $(echo "$ARCUBE_EXPOSURE" | awk '{printf "%f", $1}')) # Convert exposure to integer
    
    # Make a temporary macro file to replace the energy values and particle type 
=======
    then nEvents=$(printf "%.0f" $(echo "$ARCUBE_EXPOSURE" | awk '{printf "%f", $1}'))
    echo 'ARCUBE_EXPOSURE' $ARCUBE_EXPOSURE
    echo "nEvents: $nEvents"
>>>>>>> 9b2a4eadf6356266d19d3a17799e66b51644ae19
    tempMacroFile=$(mktemp)
    rm -f "macros/particle-gun-modified.mac"
    sed -e "s/@ARCUBE_PARTICLE_TYPE@/$ARCUBE_PARTICLE_TYPE/g" \
        -e "s/@ARCUBE_ENERGY_MINIMUM@/$ARCUBE_ENERGY_MINIMUM/g" \
        -e "s/@ARCUBE_ENERGY_MAXIMUM@/$ARCUBE_ENERGY_MAXIMUM/g" \
        $ARCUBE_EDEP_MAC > "$tempMacroFile"
    export ARCUBE_EDEP_MAC="$tempMacroFile"
<<<<<<< HEAD

=======
>>>>>>> 9b2a4eadf6356266d19d3a17799e66b51644ae19
else
    genieOutPrefix=${ARCUBE_OUTDIR_BASE}/run-genie/${ARCUBE_GENIE_NAME}/GTRAC/$subDir/${ARCUBE_GENIE_NAME}.$globalIdx
    genieFile="$genieOutPrefix".GTRAC.root
    rootCode='
    auto t = (TTree*) _file0->Get("gRooTracker");
    std::cout << t->GetEntries() << std::endl;'
    nEvents=$(echo "$rootCode" | root -l -b "$genieFile" | tail -1)

    edepCode="/generator/kinematics/rooTracker/input $genieFile
    /edep/runId $runNo"
fi

edepRootFile=$tmpOutDir/${outName}.EDEPSIM.root
rm -f "$edepRootFile"

# The geometry file is given relative to the root of 2x2_sim
export ARCUBE_GEOM_EDEP=$baseDir/${ARCUBE_GEOM_EDEP:-$ARCUBE_GEOM}

run edep-sim -C -g "$ARCUBE_GEOM_EDEP" -o "$edepRootFile" -e "$nEvents" \
    <(echo "$edepCode") "$ARCUBE_EDEP_MAC"

mkdir -p "$outDir/EDEPSIM/$subDir"
mv "$edepRootFile" "$outDir/EDEPSIM/$subDir"

<<<<<<< HEAD
rm -f "$tempMacroFile"
=======
if [ -f "$tempMacroFile" ]; then
    rm -f "$tempMacroFile"
fi
>>>>>>> 9b2a4eadf6356266d19d3a17799e66b51644ae19
