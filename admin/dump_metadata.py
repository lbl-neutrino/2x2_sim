#!/usr/bin/env python3

# Data tiers: https://samweb.fnal.gov:8483/sam/dune/api/values/data_tiers
# File types: https://samweb.fnal.gov:8483/sam/dune/api/values/file_types
# Run types: https://samweb.fnal.gov:8483/sam/dune/api/values/run_types

import argparse
import json
import subprocess
from multiprocessing import Pool
import os
from pathlib import Path
import zlib

import h5py
import numpy as np
import ROOT as R

g4evtdir = os.getenv('LIBTG4EVENT_DIR', 'libTG4Event')
R.gSystem.Load(f'{g4evtdir}/libTG4Event.so')


def get_event_stats_edep(datapath: Path):
    f = R.TFile(datapath.as_posix())
    m = f.event_spill_map
    t = f.EDepSimEvents

    def spill_of(entry):
        t.GetEntry(entry)
        e = t.Event
        idstr = f'{e.RunId} {e.EventId}'
        return int(m.GetValue(idstr).GetString().Data())

    first = spill_of(0)
    last = spill_of(t.GetEntries() - 1)
    count = last - first + 1

    f.Close()
    return count, first, last


def get_event_stats_hdf5(datapath: Path, dset_name: str, event_id_var: str):
    with h5py.File(datapath) as f:
        spills = np.unique(f[dset_name][event_id_var])
        first = spills.min()
        last = spills.max()
        count = last - first + 1

        return int(count), int(first), int(last)

def get_event_stats_tms(datapath: Path):
    f = R.TFile(datapath.as_posix())
    t = f.Line_Candidates
    count = t.GetEntries()
    first = t.GetEntry(0)
    last = t.GetEntries() - 1
    return int(count), int(first), int(last)

# NOTE: According to
# https://github.com/DUNE/data-mgmt-testing/blob/main/metacat/rawDataExample.md
# the checksums are generated automatically by the system. Does this only apply
# to metacat, not SAM/FTS? Apparently.
def get_checksum(datapath: Path, chunksize=1_000_000_000):
    cksum = 1
    with open(datapath, 'rb') as f:
        while data := f.read(chunksize):
            cksum = zlib.adler32(data, cksum)
    return cksum & 0xffffffff

# TODO: the repos are all on NERSC, so would need to get the branch names yourself (if using GPVMS),
#  or run this script on NERSC directly
def get_current_git_branch(repopath: str) -> str:
    try:
        result = subprocess.run(
            ['git', '-C', repopath, 'branch'],
            capture_output=True, text=True, check=True
        )
        for line in result.stdout.splitlines():
            if line.startswith('*'): # this is the branch checked out
                return line.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running git command: {e}")

def file_format(datapath: Path):
    if datapath.suffix == '.h5':
        return 'hdf5'
    return datapath.suffix[1:]


def get_runtype(args: argparse.Namespace):
    if args.app == 'run-spill-build':
        return 'neardet-2x2'
    elif args.app in ['run-larnd-sim', 'run-ndlar-flow']:
        return 'neardet-2x2-lar'
    elif args.app == 'run-tms-reco':
        return 'neardet-lar-tms'


def get_data_tier(args: argparse.Namespace):
    if args.app == 'run-spill-build':
        return 'simulated'
    elif args.app == 'run-larnd-sim':
        return 'detector-simulated'
    elif args.app == 'run-ndlar-flow':
        return 'hit-reconstructed'
    elif args.app == 'run-tms-reco':  # TODO: This is to be decided.
        return 'root-tuple'


def get_event_stats(datapath: Path, args: argparse.Namespace):
    if args.app == 'run-spill-build':
        return get_event_stats_edep(datapath)
    elif args.app == 'run-larnd-sim':
        return get_event_stats_hdf5(datapath, 'vertices', args.event_id_var)
    elif args.app == 'run-ndlar-flow':
        return get_event_stats_hdf5(datapath, '/mc_truth/trajectories/data',
                                    args.event_id_var)
    elif args.app == 'run-tms-reco':
        return get_event_stats_tms(datapath)


def get_parents(datapath: Path, args: argparse.Namespace):
    parts = datapath.name.split('.')
    fileno = parts[-3]              # 00321
    basename = '.'.join(parts[:-4]) # MiniRun4_1E19_RHC

    if args.app == 'run-spill-build':
        return None
    elif args.app in ['run-larnd-sim', 'run-tms-reco']:
        if not (base := args.parents):
            base = f'{basename}.spill'
        return [f'{base}.{fileno}.EDEPSIM_SPILLS.root']
    elif args.app == 'run-ndlar-flow':
        if not (base := args.parents):
            base = f'{basename}.larnd'
        return [f'{base}.{fileno}.LARNDSIM.hdf5']


def get_runno(datapath: Path):
    return int(datapath.name.split('.')[-3])

def get_data_stream(f, args: argparse.Namespace):
    if ds := args.data_stream:
        return ds
    return 'physics'

def dump_metadata(datapath: Path, args: argparse.Namespace):
    meta = {}

    meta['file_name'] = datapath.name
    meta['namespace'] = 'neardet-lar-tms'
    meta['file_size'] = datapath.stat().st_size

    if args.sam:                # for samweb validate-metadata
        meta['checksum'] = [f'adler32:{get_checksum(datapath):08x}']
    else:                       # for declaration daemon
        meta['checksum'] = f'{get_checksum(datapath):08x}'

    if parents := get_parents(datapath, args):
        meta['parents'] = parents

    meta['dune.campaign'] = args.campaign   # e.g. "MiniProdN1p1_NDLAr_1E19_RHC"

    # meta['dune.horn_current'] = args.horn_current  # TODO: add the horn current

    md = meta['metadata'] = {
        'core.application.family': args.family,
        'core.application.name': args.app,
        'core.application.version' : 'xx',          # TODO: what DUNESW version?
        'core.data_stream': get_data_stream(datapath, args),
        'core.data_tier': get_data_tier(args),
        'core.event_count': get_event_stats(datapath, args)[0],
        'core.first_event': get_event_stats(datapath, args)[1],
        'core.last_event': get_event_stats(datapath, args)[2],
        'core.file_type': 'mc' if args.mc else 'detector',
        'core.file_format': file_format(datapath),
        'core.group': 'dune',
        'core.run_type': get_runtype(args),
        'core.runs': [get_runno(datapath)],
        'core.file_content_status': 'good',

        'retention.class': 'physics',
        'retention.status': 'active',
    }
    if args.mc:
        mc_metadata = {
            'dune_mc.name' : args.campaign,
            'dune_mc.generators' :  'genie',
            'dune_mc.genie_tune' : args.genie_tune,
            'dune_mc.top_volume' : args.top_vol,
            'dune_mc.geometry_version' : args.geom,

            # NOTE: default to Jan 2025 latest versions...
            'dune_mc.2x2_sim.tag': get_current_git_branch(args.repo_2x2sim) if args.repo_2x2sim  else 'nd-production-v02.01',   # TODO: should we have a default?
            'dune_mc.fireworks4dune.tag': get_current_git_branch(args.repo_fw) if args.repo_fw else 'main',
            'dune_mc.ND_Production.tag': get_current_git_branch(args.repo_ndprod) if args.repo_ndprod else 'nd-production-v02.01',

            'dune_mc.nu': args.nu,
            'dune_mc.rock': not args.nu,

            'cluster.gen_site': 'nersc',
            'cluster.hostname' : 'xx',                       # todo: do we want these at all.....?
            'cluster.os' : 'xx',
            'cluster.os_version' : 'xx',
            'cluster.compiler' : 'xx',

        }
        meta['metadata'].update(mc_metadata)


    jsonpath = datapath.with_suffix(datapath.suffix + '.json')
    print(f'Dumping to {jsonpath}')
    with open(jsonpath, 'w') as f:
        json.dump(meta, f, indent=4)
        f.write('\n')


def main():
    ap = argparse.ArgumentParser()
    inputs = ap.add_mutually_exclusive_group(required=True)
    inputs.add_argument('--one', type=Path, help='One file to process')
    inputs.add_argument('--all', type=Path, help='Whole directory to process')
    ap.add_argument('--campaign', help='Name of campaign', required=True)
    ap.add_argument('--mc', action='store_true',)
    ap.add_argument('--genie-tune', help='Name of genie tune (CMC)', required=True)
    ap.add_argument('--nu', action='store_true', help='true for nu, false for rock')
    ap.add_argument('--parents', help='record parent info')
    ap.add_argument('--app', help='Name of application', required=True,
                    choices=['run-spill-build',
                             'run-larnd-sim',
                             'run-ndlar-flow',
                             'run-tms-reco']) # TODO: will need to add the further processes
    ap.add_argument('--family', help='Name of family', required=True, 
                    choices=['2x2_sim', 'ND_Production'], default='ND_Production') # TODO: Are we happy with ND_Production as the family?
    ap.add_argument('--geom', help='Name of geometry', required=True)
    ap.add_argument('--top-vol', help='Name of top volume', required=True)
    ap.add_argument('--repo-2x2sim', help='Path to 2x2sim repo')
    ap.add_argument('--repo-fw', help='Path to Fireworks4Dune repo')
    ap.add_argument('--repo-ndprod', help='Path to ND_Production repo')
    # ap.add_argument('--horn-current', help='Horn current in kA', type=float, required=True)
    # eventID was used for MiniRun3:
    ap.add_argument('--event-id-var', help='Name of event ID variable',
                    choices=['event_id', 'eventID'], default='event_id')
    ap.add_argument('--nproc', help='Number of parallel processes', type=int, default=8)
    ap.add_argument('--sam', help='SAM compatibility mode (only affects checksum syntax)',
                    action='store_true')
    args = ap.parse_args()

    if args.one:
        dump_metadata(args.one, args)
    else:
        ext = file_format(args.all)
        paths = args.all.glob(f'*.{ext}')
        pool = Pool(args.nproc)
        pool.starmap(dump_metadata,
                    [(p, args) for p in paths])


if __name__ == '__main__':
    main()
