import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib as mpl
from pathlib import Path

data = pd.read_csv('Mix_nets_results_with_network_delay.csv', sep=";")

variable_to_color_marker_label = {
    'total_time': ('black', 'o', 'Total'),
    't_tally': ('blue', '*', 'Tally'),
    'time_verifying_proofs': ('orange', 'x', 'Verification'),
    't_decrypt': ('green', 's', 'Decryption'),
    'time_mixing': ('red', 'D', 'Mixing')
}

font_dict = {
    'family': mpl.font_manager.FontProperties(fname=Path(mpl.get_data_path(), "fonts/ttf/cmr10.ttf")).get_name(),
    'size': 12
}

def plot_varying_clients():
    filtered = data[
        (data['NUM_SERVERS'] == 5) &
        (data['NUM_CANDS'] == 5) &
        (data['THRESHOLD'] == 3) &
        (data['NUM_CLIENTS'] != 32)
    ]

    # time_mixing;time_verifying_proofs;t_decrypt;t_tally;total_time
    grouped = (
        filtered
        .groupby('NUM_CLIENTS')
        .agg({
            'time_mixing': 'mean',
            'time_verifying_proofs': 'mean',
            't_decrypt': 'mean',
            't_tally': 'mean',
            'total_time': 'mean'
        })
        .reset_index()
    )

    a,b = np.polyfit(grouped['NUM_CLIENTS'], grouped['total_time'], 1)
    print(f"Total time linear fit: Time = {a:.4f} * Voters + {b:.4f}")
    plt.figure()
    plt.plot(grouped['NUM_CLIENTS'], grouped['time_mixing'], color=variable_to_color_marker_label['time_mixing'][0], marker=variable_to_color_marker_label['time_mixing'][1], label=variable_to_color_marker_label['time_mixing'][2], linestyle='')
    plt.plot(grouped['NUM_CLIENTS'], grouped['time_verifying_proofs'], color=variable_to_color_marker_label['time_verifying_proofs'][0], marker=variable_to_color_marker_label['time_verifying_proofs'][1], label=variable_to_color_marker_label['time_verifying_proofs'][2], linestyle='')
    plt.plot(grouped['NUM_CLIENTS'], grouped['t_decrypt'], color=variable_to_color_marker_label['t_decrypt'][0], marker=variable_to_color_marker_label['t_decrypt'][1], label=variable_to_color_marker_label['t_decrypt'][2], linestyle='')
    plt.plot(grouped['NUM_CLIENTS'], grouped['t_tally'], color=variable_to_color_marker_label['t_tally'][0], marker=variable_to_color_marker_label['t_tally'][1], label=variable_to_color_marker_label['t_tally'][2], linestyle='')
    plt.plot(grouped['NUM_CLIENTS'], grouped['total_time'], color=variable_to_color_marker_label['total_time'][0], marker=variable_to_color_marker_label['total_time'][1], label=variable_to_color_marker_label['total_time'][2], linestyle='')
    plt.grid()
    plt.xlabel('Number of Votes', fontdict=font_dict)
    plt.ylabel('Time (s)', fontdict=font_dict)
    plt.legend(loc='upper left', prop=font_dict)
    plt.savefig('mix_net_plots/mix_net_varying_clients_plot.pdf', bbox_inches='tight')    


def plot_varying_servers():
    filtered = data[
        (data['NUM_CLIENTS'] == 32) &
        (data['NUM_CANDS'] == 5)
    ]

    # time_mixing;time_verifying_proofs;t_decrypt;t_tally;total_time
    grouped = (
        filtered
        .groupby('NUM_SERVERS')
        .agg({
            'time_mixing': 'mean',
            'time_verifying_proofs': 'mean',
            't_decrypt': 'mean',
            't_tally': 'mean',
            'total_time': 'mean'
        })
        .reset_index()
    )
    plt.figure()
    plt.plot(grouped['NUM_SERVERS'], grouped['time_mixing'], color=variable_to_color_marker_label['time_mixing'][0], marker=variable_to_color_marker_label['time_mixing'][1], label=variable_to_color_marker_label['time_mixing'][2], linestyle='')
    plt.plot(grouped['NUM_SERVERS'], grouped['time_verifying_proofs'], color=variable_to_color_marker_label['time_verifying_proofs'][0], marker=variable_to_color_marker_label['time_verifying_proofs'][1], label=variable_to_color_marker_label['time_verifying_proofs'][2], linestyle='')
    plt.plot(grouped['NUM_SERVERS'], grouped['t_decrypt'], color=variable_to_color_marker_label['t_decrypt'][0], marker=variable_to_color_marker_label['t_decrypt'][1], label=variable_to_color_marker_label['t_decrypt'][2], linestyle='')
    plt.plot(grouped['NUM_SERVERS'], grouped['t_tally'], color=variable_to_color_marker_label['t_tally'][0], marker=variable_to_color_marker_label['t_tally'][1], label=variable_to_color_marker_label['t_tally'][2], linestyle='')
    plt.plot(grouped['NUM_SERVERS'], grouped['total_time'], color=variable_to_color_marker_label['total_time'][0], marker=variable_to_color_marker_label['total_time'][1], label=variable_to_color_marker_label['total_time'][2], linestyle='')
    plt.grid()
    plt.xlabel('Number of Servers', fontdict=font_dict)
    plt.ylabel('Time (s)', fontdict=font_dict)
    plt.legend(loc='upper left', prop=font_dict)
    plt.savefig('mix_net_plots/mix_net_varying_servers_plot.pdf', bbox_inches='tight')


def plot_varying_candidates():
    filtered = data[
        (data['NUM_CLIENTS'] == 32) &
        (data['NUM_SERVERS'] == 5) &
        (data['NUM_CANDS'] != 5)
    ]

    # time_mixing;time_verifying_proofs;t_decrypt;t_tally;total_time
    grouped = (
        filtered
        .groupby('NUM_CANDS')
        .agg({
            'time_mixing': 'mean',
            'time_verifying_proofs': 'mean',
            't_decrypt': 'mean',
            't_tally': 'mean',
            'total_time': 'mean'
        })
        .reset_index()
    )
    plt.figure()
    plt.plot(grouped['NUM_CANDS'], grouped['time_mixing'], color=variable_to_color_marker_label['time_mixing'][0], marker=variable_to_color_marker_label['time_mixing'][1], label=variable_to_color_marker_label['time_mixing'][2], linestyle='')
    plt.plot(grouped['NUM_CANDS'], grouped['time_verifying_proofs'], color=variable_to_color_marker_label['time_verifying_proofs'][0], marker=variable_to_color_marker_label['time_verifying_proofs'][1], label=variable_to_color_marker_label['time_verifying_proofs'][2], linestyle='')
    plt.plot(grouped['NUM_CANDS'], grouped['t_decrypt'], color=variable_to_color_marker_label['t_decrypt'][0], marker=variable_to_color_marker_label['t_decrypt'][1], label=variable_to_color_marker_label['t_decrypt'][2], linestyle='')
    plt.plot(grouped['NUM_CANDS'], grouped['t_tally'], color=variable_to_color_marker_label['t_tally'][0], marker=variable_to_color_marker_label['t_tally'][1], label=variable_to_color_marker_label['t_tally'][2], linestyle='')
    plt.plot(grouped['NUM_CANDS'], grouped['total_time'], color=variable_to_color_marker_label['total_time'][0], marker=variable_to_color_marker_label['total_time'][1], label=variable_to_color_marker_label['total_time'][2], linestyle='')
    plt.grid()
    plt.xlabel('Number of Candidates', fontdict=font_dict)
    plt.ylabel('Time (s)', fontdict=font_dict)
    plt.legend(loc='upper left', prop=font_dict)
    plt.savefig('mix_net_plots/mix_net_varying_candidates_plot.pdf', bbox_inches='tight')  


plot_varying_candidates()
plot_varying_clients()
plot_varying_servers()
