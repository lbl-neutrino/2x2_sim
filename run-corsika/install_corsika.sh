#!/usr/bin/env bash

# assume Shifter if ARCUBE_RUNTIME is unset
export ARCUBE_RUNTIME=${ARCUBE_RUNTIME:-SHIFTER}

# Keep track of what container was set before.
export ORG_ARCUBE_CONTAINER=$ARCUBE_CONTAINER
export ARCUBE_CONTAINER=mjkramer/sim2x2:ndlar011

if [[ "$ARCUBE_RUNTIME" == "SHIFTER" ]]; then
    # Reload in Shifter
    if [[ "$SHIFTER_IMAGEREQUEST" != "$ARCUBE_CONTAINER" ]]; then
        shifter --image=$ARCUBE_CONTAINER --module=none -- "$0" "$@"
        exit
    fi

else
    echo "Unsupported \$ARCUBE_RUNTIME"
    exit
fi

if ! [ -f ./corsikaConverter.exe ]; then
  rm corsikaConverter.exe
fi

pushd corsika_converter
make
chmod +x corsikaConverter
mv corsikaConverter ../corsikaConverter.exe
popd

# Put back the original container
export ARCUBE_CONTAINER=$ORG_ARCUBE_CONTAINER

exit
