#!/usr/bin/env bash

source ../util/init.inc.sh

echo "Running CORSIKA..."
./run_corsika.sh

echo "Running conversion..."
./run_convert.sh
