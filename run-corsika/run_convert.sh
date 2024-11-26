#!/usr/bin/env bash

source ../util/reload_in_container.inc.sh
source ../util/init.inc.sh

printf -v CORSIKA_OUTPUT "DAT%.6d" ${runNo}

./corsikaConverter.exe ${CORSIKA_OUTPUT}

mv ${CORSIKA_OUTPUT}.root ${outDir}/${outName}.root
mv ${CORSIKA_OUTPUT} ${outDir}/${outName}.dat
