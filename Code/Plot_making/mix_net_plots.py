import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

data = pd.read_csv('Mix_nets_results_with_network_delay.csv', sep=";")

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
    plt.figure()
    plt.plot(grouped['NUM_CLIENTS'], grouped['time_mixing'], marker='*', label='Mixing Time', linestyle='')
    plt.plot(grouped['NUM_CLIENTS'], grouped['time_verifying_proofs'], marker='x', label='Verification Time', linestyle='')
    plt.plot(grouped['NUM_CLIENTS'], grouped['t_decrypt'], marker='s', label='Decryption Time', linestyle='')
    plt.plot(grouped['NUM_CLIENTS'], grouped['t_tally'], marker='D', label='Tallying Time', linestyle='')
    plt.plot(grouped['NUM_CLIENTS'], grouped['total_time'], marker='o', label='Total Time', linestyle='', color='black')
    plt.grid()
    plt.xlabel('Number of Votes')
    plt.ylabel('Time (s)')
    plt.legend()
    plt.savefig('mix_net_varying_clients_plot.pdf', bbox_inches='tight')    


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
    plt.plot(grouped['NUM_SERVERS'], grouped['time_mixing'], marker='*', label='Mixing Time', linestyle='')
    plt.plot(grouped['NUM_SERVERS'], grouped['time_verifying_proofs'], marker='x', label='Verification Time', linestyle='')
    plt.plot(grouped['NUM_SERVERS'], grouped['t_decrypt'], marker='s', label='Decryption Time', linestyle='')
    plt.plot(grouped['NUM_SERVERS'], grouped['t_tally'], marker='D', label='Tallying Time', linestyle='')
    plt.plot(grouped['NUM_SERVERS'], grouped['total_time'], marker='o', label='Total Time', linestyle='', color='black')
    plt.grid()
    plt.xlabel('Number of Servers')
    plt.ylabel('Time (s)')
    plt.legend()
    plt.savefig('mix_net_varying_servers_plot.pdf', bbox_inches='tight')


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
    plt.plot(grouped['NUM_CANDS'], grouped['time_mixing'], marker='*', label='Mixing Time', linestyle='')
    plt.plot(grouped['NUM_CANDS'], grouped['time_verifying_proofs'], marker='x', label='Verification Time', linestyle='')
    plt.plot(grouped['NUM_CANDS'], grouped['t_decrypt'], marker='s', label='Decryption Time', linestyle='')
    plt.plot(grouped['NUM_CANDS'], grouped['t_tally'], marker='D', label='Tallying Time', linestyle='')
    plt.plot(grouped['NUM_CANDS'], grouped['total_time'], marker='o', label='Total Time', linestyle='', color='black')
    plt.grid()
    plt.xlabel('Number of Candidates')
    plt.ylabel('Time (s)')
    plt.legend()
    plt.savefig('mix_net_varying_candidates_plot.pdf', bbox_inches='tight')  


plot_varying_candidates()
plot_varying_clients()
plot_varying_servers()
