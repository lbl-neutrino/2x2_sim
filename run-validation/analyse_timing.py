#!/usr/bin/env python3

import argparse
import matplotlib
import matplotlib.pyplot as plt
import os

from matplotlib.backends.backend_pdf import PdfPages


def convert_to_minutes(time_string):
    time_string_list = time_string.split(':')
    # Ignore subseconds.
    time_string_list[-1] = time_string_list[-1].split(".")[0]
        
    conversion = [60,1,1.0/60.0]
    if len(time_string_list) == 2:
        conversion = conversion[1:]

    return sum([a*b for a,b in zip(conversion, map(int,time_string_list))])


def get_commands(production_step, n_timing_files):
    if production_step == 'genie':
        return {'gevgen_fnal' : [-1.0]*n_timing_files, 'gntpc' : [-1.0]*n_timing_files}
    if production_step == 'edep':
        return {'edep-sim' : [-1.0]*n_timing_files}
    if production_step == 'hadd':
        return {'./getGhepPOT' : [-1.0]*n_timing_files, 'hadd' : [-1]*n_timing_files}
    if production_step == 'spill':
        return {'root' : [-1.0]*n_timing_files}
    if production_step == 'convert2h5':
        return {'convert_edepsim_roottoh5' : [-1.0]*n_timing_files}
    if production_step == 'larndsim':
        return {'simulate_pixels' : [-1.0]*n_timing_files}
    if production_step == 'flow':
        return {'h5flow' : [-1.0]*n_timing_files}
    if production_step == 'flow2supera':
        return {'install/flow2supera/bin/run_flow2supera.py' : [-1.0]*n_timing_files}
    if production_step == 'mlreco_inference' or production_step == 'mlreco_analysis' or production_step == 'mlreco_spine':
        return {'python3' : [-1.0]*n_timing_files}
    if production_step == 'cafmaker':
        return {'makeCAF' : [-1.0]*n_timing_files}
    if production_step == 'tmsreco':
        return {'ConvertToTMSTree' : [-1.0]*n_timing_files}


def main(timing_directory, production_step, sample_type, out_dir, remove_fail_on_startup):
    # Grab all of the files ending in .time below the directory passed to timing_directory
    timing_files = [] 
    for b, _, fs in os.walk(timing_directory):
        if not fs: continue
        timing_files += [ os.path.join(b,f) for f in fs if f.endswith(".time") ]
        
    timing = get_commands(production_step, len(timing_files))
    count = 0
    for timing_file in timing_files:
        with open (timing_file) as f:
            lines = f.read().split('\n')
            for line in lines:
                for key in timing.keys():
                    if key in line:
                        timing[key][count] = convert_to_minutes(line.split(" ")[-1])
                        if timing[key][count] > 200. and key=='root':
                            print(timing_file)
                            print(timing[key][count])
                            print(line.split(" ")[-1])
                            print("")
        count += 1

    time_lower_bound = -1.0
    if remove_fail_on_startup: time_lower_bound = 1.0
    with PdfPages(out_dir+"/analyse_timing_"+sample_type+"_"+production_step+".pdf") as output:
        for key in timing.keys():
            non_zero_timing = [ time for time in timing[key] if time > time_lower_bound ]
            plt.hist(non_zero_timing, bins=50)
            plt.title(key+"\nTotal: "+str(sum(non_zero_timing)/60.0)+" raw hours.")
            #plt.xlabel('Run time / 10^15 POT (minutes)')
            plt.xlabel('Run time / 10^16 POT (minutes)')
            plt.ylabel(r'Number of executions')
            output.savefig()
            plt.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--timing_directory', default=None, required=True, type=str, help='''string corresponding to the directory path containing subdirecties with .time files to be analysed.''')
    parser.add_argument('--production_step', default='edep', choices=['genie', 'edep', 'hadd', 'spill', 'convert2h5', 'larndsim', 'flow', 'tmsreco', 'flow2supera', 'mlreco_inference', 'mlreco_analysis', 'mlreco_spine', 'cafmaker'], type=str, help='''string corresponding to the directory path containing .time files to be analysed.''')
    parser.add_argument('--sample_type', default='spill', choices=['fiducial', 'rock', 'spill'], type=str, help='''string corresponding to the sample type. For output naming purposes only.''')
    parser.add_argument('--out_dir', default="", required=True, type=str, help='''string corresponding to the directory path to write output pdf.''')
    parser.add_argument('--remove_fail_on_startup', default=True, type=bool, help='''dont show processes which fail in the first 1 minute.''')
    args = parser.parse_args()
    main(**vars(args))
