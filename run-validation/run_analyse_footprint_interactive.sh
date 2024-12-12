#!/bin/bash


module load python

source validation.venv/bin/activate


BASEDIR=/pscratch/sd/a/abooth/MicroProdN3p1/output
OUTDIR=/pscratch/sd/a/abooth/MicroProdN3p1/output/run-validation/PLOTS/analyses_footprint
mkdir -p $OUTDIR


# Make a basic file with size of each subdirectory
# in BASEDIR.
inFile=$(mktemp --suffix .in)
cd $BASEDIR
for dir in `ls`
do
  if [[ $dir == *"run-validation"* ]]; then continue
  elif [[ $dir == *"tmp"* ]]; then continue
  fi
  du -hk ${dir} | tail -n 1 >> $inFile
done
cd -


python analyse_footprint.py --in_file $inFile --out_dir $OUTDIR


# Remove the temporary file.
rm $inFile
