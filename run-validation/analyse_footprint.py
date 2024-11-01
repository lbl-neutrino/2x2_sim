#!/usr/bin/env python3

import argparse
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os

from matplotlib.backends.backend_pdf import PdfPages


def convert_to_gb_float(kb_string):
        
    return float(kb_string)/1.0e6


def main(in_file, out_dir):
    production_steps = []
    with open (in_file) as f:
        production_steps = np.array([ production_step.rstrip("\n").split("\t") for production_step in f ])
   
    production_step_sizes = production_steps[:,0]
    production_step_names = production_steps[:,1]

    production_step_sizes = np.array([ convert_to_gb_float(production_step_size) for production_step_size in production_step_sizes ])
    size_order = np.argsort(production_step_sizes)


    with PdfPages(out_dir+"/analyse_footprint.pdf") as output:
        fig, ax = plt.subplots()
        plt.gcf().subplots_adjust(left=0.2)
        y_pos = np.arange(len(production_steps))
        ax.barh(y_pos, production_step_sizes[size_order], align='center')
        ax.set_yticks(y_pos, labels=production_step_names[size_order])
        ax.set_title("Total Footprint: "+str(int(sum(production_step_sizes)))+" GB")
        ax.set_xlabel("Output File Footprint (GB)")
        output.savefig()
        plt.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--in_file', default=None, required=True, type=str, help='''string corresponding to file with output of du -hk command.''')
    parser.add_argument('--out_dir', default="./", required=True, type=str, help='''string corresponding to the directory path to write output pdf.''')
    args = parser.parse_args()
    main(**vars(args))
