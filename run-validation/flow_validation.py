#!/usr/bin/env python

import matplotlib as mlp
import matplotlib.pyplot as plt
import numpy as np
import h5py
import argparse
from matplotlib.backends.backend_pdf import PdfPages

from validation_utils import rasterize_plots
rasterize_plots()

SPILL_PERIOD = 1.2e7 # units = ticks
RESET_PERIOD = 1.0e7 # units = ticks

def main(flow_file, charge_only):

    flow_h5 = h5py.File(flow_file,'r')
    plt.rcParams["figure.figsize"] = (10,8)

    print('\n----------------- File content -----------------')
    print('File:',flow_file)
    print('Keys in file:',list(flow_h5.keys()))
    for key in flow_h5.keys():
        print('Number of',key,'entries in file:', len(flow_h5[key]))
        if isinstance(flow_h5[key],h5py.Group):
            for key2 in flow_h5[key].keys():
                full_key = key+'/'+key2+'/data'
                print('  ** ',full_key,'entries in file:', len(flow_h5[full_key]))
    print('------------------------------------------------\n')

    output_pdf_name = flow_file.split('.h5')[0]+'_validations.pdf'
    # temperarily, put output in this directory, not the same as the
    # simulation file itself
    output_pdf_name = output_pdf_name.split('/')[-1] # !!
    with PdfPages(output_pdf_name) as output:

        hits = flow_h5['/charge/calib_prompt_hits/data']
        final_hits = flow_h5['/charge/calib_prompt_hits/data']

        if not charge_only:
           ### Event display
           sipm_hits_data = flow_h5['light/sipm_hits/data']

           # Extracting channel IDs and maximum values
           channel_ids = sipm_hits_data['chan'][:]
           max_values = sipm_hits_data['max'][:]
           pos_data = sipm_hits_data['pos'][:]
           z_coordinates = pos_data[:, 2]
           x_coordinates = pos_data[:, 0]
           y_coordinates = pos_data[:, 1]

           unique_x, xcounts = np.unique(x_coordinates, return_counts=True)
           unique_y, ycounts = np.unique(y_coordinates, return_counts=True)
           unique_z, zcounts = np.unique(z_coordinates, return_counts=True)

           plt.figure(figsize=(10, 6))
           plt.bar(unique_x, xcounts)
           plt.xlabel('X-coordinate')
           plt.ylabel('Counts')
           plt.title('X-coordinate')
           plt.grid(True)
           output.savefig()  
           plt.close()

           plt.figure(figsize=(10, 6))
           plt.bar(unique_y, ycounts)
           plt.xlabel('Y-coordinate')
           plt.ylabel('Counts')
           plt.title('Y-coordinate')
           plt.grid(True)
           output.savefig()  
           plt.close()
 
           plt.figure(figsize=(10, 6))
           plt.bar(unique_z, zcounts)
           plt.xlabel('Z-coordinate')
           plt.ylabel('Counts')
           plt.title('Z-coordinate')
           plt.grid(True)
           output.savefig()  
           plt.close()


           # Plot scatter plot for channel IDs versus maximum values
           plt.figure(figsize=(10, 6))
           plt.scatter(channel_ids, max_values, marker='.', color='blue')
           plt.xlabel('Channel ID')
           plt.ylabel('Maximum Value')
           plt.title('Maximum Values vs. Channel IDs')
           plt.grid(True)
           plt.xlim(0, 60)
           output.savefig()  
           plt.close()    

           sum_hits_data = flow_h5['light/sum_hits/data']
           tpc_values = sum_hits_data['tpc'][:]
           det_values = sum_hits_data['det'][:]
           unique_tpc, counts_tpc = np.unique(tpc_values, return_counts=True)
           unique_det, counts_det = np.unique(det_values, return_counts=True)

           plt.figure(figsize=(8, 6))
           plt.bar(unique_tpc, counts_tpc, color='purple')
           plt.xlabel('tpc_values')
           plt.ylabel('Counts')
           plt.title(f'Histogram of TPC index')
           plt.grid(True)
           output.savefig()  
           plt.close()    

           plt.figure(figsize=(8, 6))
           plt.bar(unique_det, counts_det, color='purple')
           plt.xlabel('det_values')
           plt.ylabel('Counts')
           plt.title(f'Histogram of detector index')
           plt.grid(True)
           output.savefig()  
           plt.close()   


        # 3D - all spills
        fig = plt.figure(figsize=(10,10))
        ax = fig.add_subplot(projection='3d')
        ax.set_facecolor('none')
        fig.tight_layout()        
        dat = ax.scatter(hits['z'],hits['x'],
                   hits['y'],c=hits['Q'],
                   s=1,cmap='viridis',norm=mlp.colors.LogNorm())
                   #norm=mpl.colors.LogNorm())#, cmap='Greys')
        fig.colorbar(dat,ax=ax,label="detected charge",shrink=0.5)
        ax.set_title("charge hits",fontsize=20)
        ax.set_xlabel('z [cm]')
        ax.set_ylabel('x [cm]')
        ax.set_zlabel('y [cm]')
        #ax.set_xlim([-65.,65])
        #ax.set_ylim([-65.,65])
        #ax.set_zlim([-65.,65])
        del ax, fig
        output.savefig()
        plt.close()

        # 2D hit projections
        fig = plt.figure(figsize=(10,6))
        gs  = fig.add_gridspec(1,3)
        ax1 = fig.add_subplot(gs[0,0],aspect=1.0)
        ax2 = fig.add_subplot(gs[0,1],aspect=1.0)
        ax3 = fig.add_subplot(gs[0,2],aspect=1.0)

        io_group_count = 1
        io_groups_uniq = set(hits['io_group'])
        for iog in io_groups_uniq:
            iog_mask = hits['io_group'] == iog
            iog_hits = hits[iog_mask]      
            ax1.scatter(iog_hits['z'],iog_hits['y'],s=0.5,alpha=0.1,label='IO Group '+str(iog))
            ax1.set_xlabel(r'z [cm]')
            ax1.set_ylabel(r'y [cm]')

            ax2.scatter(iog_hits['x'],iog_hits['z'],s=0.5,alpha=0.1)#,label='IO Group'+str(iog))
            ax2.set_xlabel(r'x [cm]')
            ax2.set_ylabel(r'z [cm]')

            ax3.scatter(iog_hits['x'],iog_hits['y'],s=0.5,alpha=0.1)#,label='IO Group'+str(iog))
            ax3.set_xlabel(r'x [cm]')
            ax3.set_ylabel(r'y [cm]')

            if io_group_count % 8 == 0 or io_group_count == len(io_groups_uniq):
                leg = fig.legend(bbox_to_anchor=(0.2, 0.8), loc='lower left', ncols=4, markerscale=10.,fontsize=13)
                for lh in leg.legend_handles:
                    lh.set_alpha(1)
                plt.tight_layout()
                output.savefig()
                plt.close()

                fig = plt.figure(figsize=(10,6))
                gs  = fig.add_gridspec(1,3)
                ax1 = fig.add_subplot(gs[0,0],aspect=1.0)
                ax2 = fig.add_subplot(gs[0,1],aspect=1.0)
                ax3 = fig.add_subplot(gs[0,2],aspect=1.0)
                
            io_group_count += 1

        ### Hit level 1D position distributions
        fig = plt.figure(figsize=(10,10),layout="constrained")
        gs = fig.add_gridspec(2,2)
        ax_x = fig.add_subplot(gs[0,0])
        ax_y = fig.add_subplot(gs[0,1])
        ax_z = fig.add_subplot(gs[1,0])
        #fig.title('/charge/calib_prompt_hits/data')

        ax_z.hist(hits['z'],bins=298) # assuming hits at min/max z, each bin is approx 1 pixel = 0.434 cm
        ax_z.set_xlabel('z [cm]',fontsize=16)
        ax_z.set_ylabel('number of hits per bin',fontsize=16)
        ax_z.set_yscale('log')
        ax_z.set_ylim([1,2e3])

        ax_y.hist(hits['y'],bins=287) # assuming hits at min/max y, each bin is approx 1 pixel = 0.434 cm
        ax_y.set_xlabel('y [cm]',fontsize=16)
        ax_y.set_ylabel('number of hits per bin',fontsize=16)
        ax_y.set_yscale('log')
        ax_y.set_ylim([1,2e3])

        ax_x.hist(hits['x'],bins=256) # assuming hits at min/max x, each bin is approx 0.5 cm
        ax_x.set_xlabel('x [cm]',fontsize=16)
        ax_x.set_ylabel('number of hits per bin',fontsize=16)
        ax_x.set_yscale('log')
        ax_x.set_ylim([1,2e3])
        output.savefig()
        plt.close()

        # 3D - "event" spills
        n_evts = len(flow_h5['charge/events/ref/charge/calib_prompt_hits/ref_region'])
        io_group_contrib = np.zeros(shape=(n_evts,len(io_groups_uniq)))
        for a in range(n_evts):
            fig = plt.figure(figsize=(10,10),layout="constrained")
            ax = fig.add_subplot(projection='3d')
            ax.set_facecolor('none')
            hit_ref_slice = flow_h5['charge/events/ref/charge/calib_prompt_hits/ref_region'][a]
            spill_hits = final_hits[hit_ref_slice[0]:hit_ref_slice[1]]
            event_charge = np.sum(spill_hits['Q'])
            if event_charge==0:
                plt.close()
                continue
            for iog in io_groups_uniq:
                iog_mask = spill_hits['io_group'] == iog
                iog_hits = spill_hits[iog_mask]
                iog_evt_charge = 0.
                if len(iog_hits) > 0:
                    iog_evt_charge = np.sum(iog_hits['Q'])
                io_group_contrib[a][int(iog-1)] = float(iog_evt_charge)/float(event_charge)
            dat = ax.scatter(spill_hits['z'],spill_hits['x'],
                       spill_hits['y'],c=spill_hits['Q'],
                       s=1,cmap='viridis',norm=mlp.colors.LogNorm())
            ax.set_title(f"Hits in charge events",fontsize=24)
            ax.set_xlabel('z [cm]',fontsize=16)
            ax.set_ylabel('x [cm]',fontsize=16)
            ax.set_zlabel('y [cm]',fontsize=16)
            ##ax.set_xlim([-65.,65])
            ##ax.set_ylim([-65.,65])
            ##ax.set_zlim([-65.,65])
            output.savefig()
            plt.close()

        # io_group contribution for each spill
        fig = plt.figure(figsize=(10,8))
        ax = fig.add_subplot()
        ax.set_facecolor('none')
        bottom = np.zeros(n_evts)
        for iog in io_groups_uniq:
            iog_cont = (io_group_contrib[:,int(iog-1):iog]).flatten()
            ax.bar(range(n_evts), iog_cont, bottom=bottom, label='IO Group '+str(iog), width=1.0)
            bottom += iog_cont
        #ax.legend(ncols=4,fontsize=13)
        ax.set_xlabel('charge event number',fontsize=18)
        ax.set_ylabel('io_group contribution',fontsize=18)
        #ax.set_ylim([-0.1,1.5])
        del ax, fig
        output.savefig()
        plt.close()

        # true spill ID vs. reconstructed charge event
        fig = plt.figure(figsize=(10,8))
        ax = fig.add_subplot()
        flow_evt_to_hit = flow_h5['/charge/events/ref/charge/calib_prompt_hits/ref_region']
        flow_evts = flow_h5['/charge/events/data']
        final_hits = flow_h5['/charge/calib_prompt_hits/data']
        hits_bt = flow_h5['mc_truth/calib_prompt_hit_backtrack/data']
        segments = flow_h5['mc_truth/segments/data']

        # Construct a lookup array from segment ID to segment index :`(
        min_segment_id = np.min(segments['segment_id'])
        max_segment_id = np.max(segments['segment_id'])
        n_segment_ids = max_segment_id - min_segment_id + 1
        segment_indices = np.array([-1]*n_segment_ids, dtype=np.int32)
        for i, seg_id in enumerate(segments['segment_id']):
            segment_indices[seg_id - min_segment_id] = i

        true_ids = []
        reco_ids = []
        for c_evt in flow_evts['id']:
            hit_ref_slice = flow_evt_to_hit[c_evt]
            hts = final_hits[hit_ref_slice[0]:hit_ref_slice[1]]
            hts_bt = hits_bt[hit_ref_slice[0]:hit_ref_slice[1]]
            spill_ids = {}
            for h in hts_bt:
                for cont in range(len(h['fraction'])):
                    if abs(h['fraction'][cont]) > 0.0001:
                        seg_id = h['segment_ids'][cont]
                        seg = segments[segment_indices[seg_id - min_segment_id]]
                        if not seg['segment_id'] == seg_id:
                            print('WARNING: segment id not the same as segment index!')
                        sid = seg['event_id']
                        if not sid in spill_ids.keys():
                            spill_ids[sid] = 1
                        else: spill_ids[sid] += 1
            reco_ids.extend([c_evt]*len(spill_ids))
            true_ids.extend(spill_ids)
        ax.scatter(reco_ids,true_ids)
        ax.set_xlabel('reco event ID',fontsize=18)
        ax.set_ylabel('true event ID',fontsize=18)
        del ax, fig
        output.savefig()
        plt.close()


        # 3D - several individual spills
        fig = plt.figure(figsize=(10,10),layout="constrained")
        gs = fig.add_gridspec(3,3)
        ax = []
        for a in range(9):
            hit_ref_slice = flow_h5['charge/events/ref/charge/calib_prompt_hits/ref_region'][a]
            spill_hits = final_hits[hit_ref_slice[0]:hit_ref_slice[1]]
            ax.append(fig.add_subplot(gs[a//3,a%3],projection='3d'))
            dat = ax[a].scatter(spill_hits['z'],spill_hits['x'],
                       spill_hits['y'],c=spill_hits['Q'],
                       s=1,cmap='viridis',norm=mlp.colors.LogNorm())
            #cb = fig.colorbar(dat, ax=ax[a], label="detected charge",
            #                  shrink=0.5, location='left', pad = 0.)
            #cb.ax.yaxis.set_ticks([matplotlib.ticker.FixedLocator([])])
            ax[a].set_title(f"spill {a+1}",fontsize=12)
            ax[a].set_xlabel('z [cm]')
            ax[a].set_ylabel('x [cm]')
            ax[a].set_zlabel('y [cm]')
            #ax[a].set_xlim([-65.,65])
            #ax[a].set_ylim([-65.,65])
            #ax[a].set_zlim([-65.,65])
        output.savefig()
        plt.close()


        ### charge/event information
        fig = plt.figure(figsize=(10,6))
        gs  = fig.add_gridspec(3,1)
        # share x-axis = event id
        ax1 = fig.add_subplot(gs[0,0])
        ax2 = fig.add_subplot(gs[1,0],sharex=ax1)
        ax3 = fig.add_subplot(gs[2,0],sharex=ax1)
        fig.subplots_adjust(left=0.075,bottom=0.075,wspace=None, hspace=0.)
        event_data = flow_h5['charge/events/data']
        ax1.plot(event_data['id'],event_data['unix_ts'],linestyle='None',marker='o',ms=3)
        ax1.set_ylim([0,500])
        ax1.set_ylabel('unix_ts',fontsize=18)
        ax1.set_title('charge/events/data',fontsize=18)
        ax1.grid()
        ax2.plot(event_data['id'],event_data['ts_start'],linestyle='None',marker='o',ms=3)
        ax2.set_ylabel('ts_start',fontsize=18)
        ax2.grid()
        ax3.plot(event_data['id'],event_data['nhit'],linestyle='None',marker='o',ms=3)
        ax3.set_ylabel('nhit',fontsize=18)
        ax3.set_xlabel('event ID',fontsize=18)
        ax3.grid()
        ax1.tick_params(labelbottom=False)
        ax2.tick_params(labelbottom=False)
        output.savefig()
        plt.close()

        # get the packet data, references to calib_prompt_hits, and create some masks:
        packets = flow_h5['/charge/packets/data']
        packets_hits_ref = flow_h5['charge/calib_prompt_hits/ref/charge/packets/ref']
        packets_hits = packets[:][packets_hits_ref[:,1]]
        packet_index = np.array(list(range(0,len(packets))))
        data_packet_mask = packets['packet_type'] == 0
        trig_packet_mask = packets['packet_type'] == 7
        sync_packet_mask = packets['packet_type'] == 4
        other_packet_mask= ~(data_packet_mask | trig_packet_mask | sync_packet_mask)

        ### Plot time structure of packets: 
        plt.clf()
        plt.plot(packets['timestamp'][data_packet_mask],packet_index[data_packet_mask],'o',label='data packets',linestyle='None')
        plt.plot(packets['timestamp'][trig_packet_mask],packet_index[trig_packet_mask],'o',label='lrs triggers',linestyle='None')
        plt.plot(packets['timestamp'][sync_packet_mask],packet_index[sync_packet_mask],'o',label='PPS packets',linestyle='None')
        plt.plot(packets['timestamp'][other_packet_mask],packet_index[other_packet_mask],'o',label='other',linestyle='None')
        plt.title('/charge/packets/data')
        plt.xlabel('timestamp')
        plt.ylabel('packet index')
        plt.legend()
        output.savefig()
        plt.close()

        plt.hist(packets['timestamp'],bins=100)
        plt.title('/charge/packets/data')
        plt.xlabel('timestamp')
        plt.ylabel('number of packets per bin')
        output.savefig()
        plt.close()

        plt.plot(packets['receipt_timestamp'][data_packet_mask],packet_index[data_packet_mask],'o',label='data packets',linestyle='None')
        plt.plot(packets['receipt_timestamp'][trig_packet_mask],packet_index[trig_packet_mask],'o',label='lrs triggers',linestyle='None')
        plt.plot(packets['receipt_timestamp'][sync_packet_mask],packet_index[sync_packet_mask],'o',label='PPS packets',linestyle='None')
        plt.plot(packets['receipt_timestamp'][other_packet_mask],packet_index[other_packet_mask],'o',label='other',linestyle='None')
        plt.title('/charge/packets/data')
        plt.xlabel('receipt_timestamp')
        plt.ylabel('packet index')
        plt.legend()
        output.savefig()
        plt.close()

        plt.hist(packets['receipt_timestamp'],bins=100)
        plt.title('/charge/packets/data')
        plt.xlabel('receipt_timestamp')
        plt.ylabel('number of packets per bin')
        output.savefig()
        plt.close()

        ### Plot charge vs. time per io_group/tpc
        packets_stack = []
        weights_stack = []
        for iog in io_groups_uniq:
            iog_mask = (packets['io_group'] == iog) & data_packet_mask
            packets_stack.append(packets['timestamp'][iog_mask]%(SPILL_PERIOD%RESET_PERIOD))
            weights_stack.append(packets['dataword'][iog_mask])
        plt.hist(packets_stack, weights=weights_stack, stacked=True, bins=200, label='io_group '+str(iog),alpha=0.5)
        plt.title('/charge/packets/data')
        plt.xlabel('timestamp%(spill_period%reset_period)')
        plt.ylabel('charge [ADC]')
        #plt.legend(ncol=4,bbox_to_anchor=(-0.05,1.00),loc='lower left')
        output.savefig()
        plt.close()

        # comparisons of prompt hits and final hits
        # currently correspondes to comparisons before and after merging multi-hits
        fig = plt.figure(figsize=(10,8),layout='constrained')
        gs = fig.add_gridspec(2,3)
        ax1 = fig.add_subplot(gs[0,0])
        ax2 = fig.add_subplot(gs[0,1])
        ax3 = fig.add_subplot(gs[0,2])
        ax4 = fig.add_subplot(gs[1,0])
        ax5 = fig.add_subplot(gs[1,1])
        ax6 = fig.add_subplot(gs[1,2])
        
        ax1.hist(flow_h5['charge/calib_prompt_hits/data']['x'],bins=100,alpha=0.5,label='prompt hits')
        ax1.hist(flow_h5['charge/calib_prompt_hits/data']['x'],bins=100,alpha=0.5,label='merged hits')
        ax1.set_xlabel('x [cm]')
        ax1.set_ylabel('N hits')
        #ax1.legend()
        
        ax2.hist(flow_h5['charge/calib_prompt_hits/data']['y'],bins=100,alpha=0.5,label='prompt hits')
        ax2.hist(flow_h5['charge/calib_prompt_hits/data']['y'],bins=100,alpha=0.5,label='merged hits')
        ax2.set_xlabel('y [cm]')
        ax2.set_ylabel('N hits')
        ax2.legend()
        
        ax3.hist(flow_h5['charge/calib_prompt_hits/data']['z'],bins=100,alpha=0.5,label='prompt hits')
        ax3.hist(flow_h5['charge/calib_prompt_hits/data']['z'],bins=100,alpha=0.5,label='merged hits')
        ax3.set_xlabel('z [cm]')
        ax3.set_ylabel('N hits')
        #ax3.legend()
        
        ax4.hist(flow_h5['charge/calib_prompt_hits/data']['x'],weights=flow_h5['charge/calib_prompt_hits/data']['E'],bins=100,alpha=0.5,label='prompt hits')
        ax4.hist(flow_h5['charge/calib_prompt_hits/data']['x'],weights=flow_h5['charge/calib_prompt_hits/data']['E'],bins=100,alpha=0.5,label='merged hits')
        ax4.set_xlabel('x [cm]')
        ax4.set_ylabel('Energy [MeV]')
        #ax4.legend()
        
        ax5.hist(flow_h5['charge/calib_prompt_hits/data']['y'],weights=flow_h5['charge/calib_prompt_hits/data']['E'],bins=100,alpha=0.5,label='prompt hits')
        ax5.hist(flow_h5['charge/calib_prompt_hits/data']['y'],weights=flow_h5['charge/calib_prompt_hits/data']['E'],bins=100,alpha=0.5,label='merged hits')
        ax5.set_xlabel('y [cm]')
        ax5.set_ylabel('Energy [MeV]')
        #ax5.legend()
        
        ax6.hist(flow_h5['charge/calib_prompt_hits/data']['z'],weights=flow_h5['charge/calib_prompt_hits/data']['E'],bins=100,alpha=0.5,label='prompt hits')
        ax6.hist(flow_h5['charge/calib_prompt_hits/data']['z'],weights=flow_h5['charge/calib_prompt_hits/data']['E'],bins=100,alpha=0.5,label='merged hits')
        ax6.set_xlabel('z [cm]')
        ax6.set_ylabel('Energy [MeV]')
        #ax6.legend()
        
        output.savefig()
        plt.close()
        
        #ax4.hist(flow_h5['charge/calib_prompt_hits/data']['ts_pps'],bins=100,alpha=0.5,label='prompt hits')
        #ax4.hist(flow_h5['charge/calib_prompt_hits/data']['ts_pps'],bins=100,alpha=0.5,label='merged hits')
        #ax4.set_xlabel('ts_pps [ticks = 0.1 us]')
        #ax4.set_ylabel('N hits')
        #ax4.legend()

        # Add if statement for io_group hit dataset validations for backwards compatibility
        if 'io_group' in list(hits.dtype.names):
            fig = plt.figure(figsize=(10,8), layout='constrained')
            gs = fig.add_gridspec(2,1)
            ax1 = fig.add_subplot(gs[0,0])
            ax2 = fig.add_subplot(gs[1,0])

            # Histograms of io_group in hits and packet datasets
            ax1.set_ylim(0,30000)
            ax1.hist(packets_hits['io_group'], 
                     label="packets", bins=len(io_groups_uniq), range=(1, len(io_groups_uniq)+1), 
                     alpha=1.0, color='#377eb8', 
                     edgecolor='#377eb8', linestyle='-')
            ax1.hist(hits['io_group'], 
                     label="calib_prompt_hits", bins=len(io_groups_uniq), range=(1, len(io_groups_uniq)+1),
                     alpha=1.0, color='#ff7f00', 
                     edgecolor='#ff7f00', linestyle='-', 
                     linewidth=1.5,fill=False)
            ax1.hist(final_hits['io_group'], 
                     label="calib_prompt_hits", bins=len(io_groups_uniq), range=(1, len(io_groups_uniq)+1),
                     alpha=0.8, color='#4daf4a', 
                     edgecolor='#4daf4a', linestyle='--', 
                     linewidth=1.5,fill=False)
            ax1.set_title("Hits per IO Group Distribution in Different Datasets")
            ax1.set_xlabel("IO Group")
            ax1.set_ylabel("Hits / IO Group")
            ax1.legend()

            p_iog, p_iog_bins = np.histogram(hits['io_group'], bins=len(io_groups_uniq), range=(1, len(io_groups_uniq)+1),)
            f_iog, f_iog_bins = np.histogram(final_hits['io_group'], bins=len(io_groups_uniq), range=(1, len(io_groups_uniq)+1),)
            iog_resid = 100*(p_iog - f_iog)/p_iog
            mean_iog_resid = np.mean(iog_resid)
            final_prompt_resid = 100*(len(hits['io_group']) - len(final_hits['io_group']))/len(hits['io_group'])

            ax2.set_ylim(0,np.max(iog_resid)+10)
            ax2.plot(np.arange(len(io_groups_uniq)+1)+1, np.ones(len(io_groups_uniq)+1)*mean_iog_resid, \
                     linestyle='--', color='blue', \
                     label="Mean % Decr. over IO Groups ("+str(round(mean_iog_resid, 1))+"%)")
            ax2.plot(np.arange(len(io_groups_uniq)+1)+1, np.ones(len(io_groups_uniq)+1)*final_prompt_resid, \
                     linestyle='--', color='black', \
                     label="Total % Decr. Prompt to Final Hits ("+str(round(final_prompt_resid, 1))+"%)")
            ax2.hist(np.arange(len(io_groups_uniq))+1, weights=iog_resid, bins=len(io_groups_uniq), range=(1, len(io_groups_uniq)+1),
                    alpha=1.0, color='#f781bf', 
                    edgecolor='#f781bf', linestyle='-', 
                    linewidth=1.5)
            ax2.set_title("Percent Decrease in Hits per IO Group from Prompt to Final Hits")
            ax2.set_xlabel("IO Group")
            ax2.set_ylabel("Percent Decrease in Hits / IO Group")
            ax2.legend()

            output.savefig()
            plt.close()

        # Add if statement for io_channel hit dataset validations for backwards compatibility
        if 'io_channel' in list(hits.dtype.names):
            fig = plt.figure(figsize=(10,8), layout='constrained')
            gs = fig.add_gridspec(2,1)
            ax1 = fig.add_subplot(gs[0,0])
            ax2 = fig.add_subplot(gs[1,0])

            # Histograms of io_channel in hits datasets
            io_channel_uniq = set(packets_hits['io_channel'])
            ax1.set_ylim(0,12000)
            ax1.hist(packets_hits['io_channel'], 
                     label="packets", bins=len(io_channel_uniq), range=(1, len(io_channel_uniq)+1),
                     alpha=1.0, color='#377eb8', 
                     edgecolor='#377eb8', linestyle='-')
            ax1.hist(hits['io_channel'], 
                     label="calib_prompt_hits", bins=len(io_channel_uniq), range=(1, len(io_channel_uniq)+1),
                     alpha=1.0, color='#ff7f00', 
                     edgecolor='#ff7f00', linestyle='-', 
                     linewidth=1.5,fill=False)
            ax1.hist(final_hits['io_channel'], 
                     label="calib_prompt_hits", bins=len(io_channel_uniq), range=(1, len(io_channel_uniq)+1), 
                     alpha=0.8, color='#4daf4a', 
                     edgecolor='#4daf4a', linestyle='--', 
                     linewidth=1.5,fill=False)
            ax1.set_title("Hits per IO Channel Distribution in Different Datasets")
            ax1.set_xlabel("IO Channel")
            ax1.set_ylabel("Hits / IO Channel")
            ax1.legend()

            p_io_channel, p_io_channel_bins = np.histogram(hits['io_channel'], bins=len(io_channel_uniq), range=(1, len(io_channel_uniq)+1))
            f_io_channel, f_io_channel_bins = np.histogram(final_hits['io_channel'], bins=len(io_channel_uniq), range=(1, len(io_channel_uniq)+1))
            io_channel_resid = 100* (p_io_channel - f_io_channel)/p_io_channel
            mean_io_channel_resid = np.mean(io_channel_resid)

            ax2.set_ylim(0,np.max(io_channel_resid)+10)
            ax2.plot(np.arange(len(io_channel_uniq)+1)+1, np.ones(len(io_channel_uniq)+1)*mean_io_channel_resid, \
                     linestyle='--', color='blue', \
                     label="Mean % Decr. over IO Channels ("+str(round(mean_io_channel_resid, 1))+"%)")
            ax2.plot(np.arange(len(io_channel_uniq)+1)+1, np.ones(len(io_channel_uniq)+1)*final_prompt_resid, \
                     linestyle='--', color='black', \
                     label="Total % Decr. Prompt to Final Hits ("+str(round(final_prompt_resid, 1))+"%)")
            ax2.hist(np.arange(len(io_channel_uniq))+1, weights=io_channel_resid, bins=len(io_channel_uniq), range=(1, len(io_channel_uniq)+1),
                     alpha=1.0, color='#f781bf', 
                     edgecolor='#f781bf', linestyle='-', 
                     linewidth=1.5)
            ax2.set_title("Percent Decrease in Hits per IO Channel from Prompt to Final Hits")
            ax2.set_xlabel("IO Channel")
            ax2.set_ylabel("Percent Decrease in Hits / IO Channel")
            ax2.legend()

            output.savefig()
            plt.close()

        # Check the sums of the fraction field for charge deposition. They should add to 1.
        if 'mc_truth' in flow_h5.keys():
            fractions = flow_h5['mc_truth/packet_fraction/data']['fraction']
            summed_fractions = fractions.sum(axis=-1)
            fig, ax = plt.subplots(constrained_layout = True)
            ax.hist(summed_fractions, bins= np.arange(-0.05, summed_fractions.max(), 0.1))
            ax.set_title("Sum of packet fractions in each event")
            ax.set_yscale('log')
            ax.set_xlabel("Sum")
            ax.set_ylabel("Count")

            output.savefig()
            plt.close() 

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--flow_file', default=None, type=str,help='''string corresponding to the path of the ndlar_flow output file to be considered''')
    parser.add_argument('--charge_only', action='store_true', help='''boolean to flag that light has not been simualted''')
    args = parser.parse_args()
    main(**vars(args))


