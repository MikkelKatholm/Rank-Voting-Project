import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

data = pd.read_csv('Mix_nets_results.csv', sep=";")

def plot_varying_clients():
    filtered = data[
        (data['NUM_SERVERS'] == 5) &
        (data['NUM_CANDS'] == 5) &
        (data['THRESHOLD'] == 3) &
        (data['NUM_CLIENTS'] != 32)
    ]

    filtered['time_no_encrypt'] = filtered['time_total'] - filtered['t_encrypt_ballots']

    grouped = (
        filtered
        .groupby('NUM_CLIENTS')['time_no_encrypt']
        .mean()
        .reset_index()
    )

    plt.figure()
    plt.plot(grouped['NUM_CLIENTS'], grouped['time_no_encrypt'], marker='o')
    plt.grid()
    plt.xlabel('Number of Clients')
    plt.ylabel('Tallying Time (s)')
    #plt.title('Tallying time vs Number of Clients')
    plt.savefig('mix_net_varying_clients_plot.pdf', bbox_inches='tight')

def plot_varying_servers():
    filtered = data[
        (data['NUM_CLIENTS'] == 32) &
        (data['NUM_CANDS'] == 5)
    ]

    filtered['time_no_encrypt'] = filtered['time_total'] - filtered['t_encrypt_ballots']

    grouped = (
        filtered
        .groupby('NUM_SERVERS')['time_no_encrypt']
        .mean()
        .reset_index()
    )

    plt.figure()
    plt.plot(grouped['NUM_SERVERS'], grouped['time_no_encrypt'], marker='o')
    plt.grid()
    plt.xlabel('Number of Servers')
    plt.ylabel('Tallying time Time (s)')
    #plt.title('Tallying time vs Number of Servers')
    plt.savefig('mix_net_varying_servers_plot.pdf', bbox_inches='tight')

def plot_varying_candidates():
    filtered = data[
        (data['NUM_CLIENTS'] == 32) &
        (data['NUM_SERVERS'] == 5)
    ]

    filtered['time_no_encrypt'] = filtered['time_total'] - filtered['t_encrypt_ballots']

    grouped = (
        filtered
        .groupby('NUM_CANDS')['time_no_encrypt']
        .mean()
        .reset_index()
    )

    plt.figure()
    plt.plot(grouped['NUM_CANDS'], grouped['time_no_encrypt'], marker='o')
    plt.ylim(bottom=grouped['time_no_encrypt'].min() * 0.9, top=grouped['time_no_encrypt'].max() * 1.1)
    plt.grid()
    plt.xlabel('Number of Candidates')
    plt.ylabel('Tallying time Time (s)')
    #plt.title('Tallying time vs Number of Candidates')
    plt.savefig('mix_net_varying_candidates_plot.pdf', bbox_inches='tight')

plot_varying_candidates()
plot_varying_clients()
plot_varying_servers()