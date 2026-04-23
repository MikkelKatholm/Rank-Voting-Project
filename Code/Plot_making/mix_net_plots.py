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

    grouped = filtered.groupby('NUM_CLIENTS')['time_total'].mean().reset_index()

    plt.figure()
    plt.plot(grouped['NUM_CLIENTS'], grouped['time_total'], marker='o')
    plt.grid()
    plt.xlabel('Number of Clients')
    plt.ylabel('Total Time (s)')
    plt.show()

plot_varying_clients()