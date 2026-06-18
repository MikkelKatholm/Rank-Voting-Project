import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib as mpl

online_only = True
optimized = True

data = pd.read_csv(f'mp-spdz_results_{"online" if online_only else "with_offline"}{"_optimized" if optimized else ""}.csv', sep=";")

x_axis_dict = {
    'NUM_SERVERS': 'Number of Servers',
    'NUM_CANDS': 'Number of Candidates',
    'NUM_VOTERS': 'Number of Voters'
}

variable_to_color_marker_label = {
    'total_time_s': ('black', 'o', 'Total'),
    'clean_ballots_time_s': ('green', 's', 'Ballot Validation'),
    'send_and_receive_ballots_time_s': ('darkorange', 'X', 'Send and Receive Ballots'),
    'convert_ballots_time_s': ('red', 'D', 'Convert Ballots'),
    'tally_time_s': ('blue', '*', 'Tally')
}

default_values = {
    'NUM_SERVERS': 5,
    'NUM_CANDS': 5,
    'NUM_VOTERS': 32,
}

fontpath = Path("fonts/AUPassata_Rg.ttf")
mpl.font_manager.fontManager.addfont(str(fontpath))
prop = mpl.font_manager.FontProperties(fname=str(fontpath))
font_name = prop.get_name()  # gets the actual registered name
font_dict = {'family': font_name, 'size': 12}


def plot_everything(data, x_axis, filename):
    plt.figure()
    if not optimized:
        plt.plot(
            data[x_axis],
            data['total_time_s'], 
            marker=variable_to_color_marker_label['total_time_s'][1],
            linestyle='',
            label=variable_to_color_marker_label['total_time_s'][2],
            color=variable_to_color_marker_label['total_time_s'][0]
        )
    plt.plot(
        data[x_axis],
        data['clean_ballots_time_s'],
        marker=variable_to_color_marker_label['clean_ballots_time_s'][1],
        label=variable_to_color_marker_label['clean_ballots_time_s'][2],
        linestyle='',
        color=variable_to_color_marker_label['clean_ballots_time_s'][0]
    )
    if not optimized:
        plt.plot(
            data[x_axis],
            data['send_and_receive_ballots_time_s'],
            marker=variable_to_color_marker_label['send_and_receive_ballots_time_s'][1],
            label=variable_to_color_marker_label['send_and_receive_ballots_time_s'][2],
            linestyle='',
            color=variable_to_color_marker_label['send_and_receive_ballots_time_s'][0]
        )
    plt.plot(
        data[x_axis],
        data['convert_ballots_time_s'],
        marker=variable_to_color_marker_label['convert_ballots_time_s'][1],
        label=variable_to_color_marker_label['convert_ballots_time_s'][2],
        linestyle='',
        color=variable_to_color_marker_label['convert_ballots_time_s'][0]
    )
    plt.plot(
        data[x_axis],
        data['tally_time_s'],
        marker=variable_to_color_marker_label['tally_time_s'][1],
        label=variable_to_color_marker_label['tally_time_s'][2],
        linestyle='',
        color=variable_to_color_marker_label['tally_time_s'][0]
    )
    plt.grid()
    plt.xlabel(x_axis_dict[x_axis], font_dict)
    plt.ylabel('Time (s)', font_dict)
    plt.legend(loc='upper left', prop=font_dict)
    if online_only:
        plt.savefig(f"mp-spdz_plots/online_only/{"non-optimized/" if not optimized else ""}{filename}_online.pdf", bbox_inches='tight')
    else:
        plt.savefig(f"mp-spdz_plots/with_offline_phase/{filename}.pdf", bbox_inches='tight')

def plot_tally_time(data, x_axis, filename):
    plt.figure()
    plt.plot(
        data[x_axis],
        data['tally_time_s'],
        marker=variable_to_color_marker_label['tally_time_s'][1],
        label=variable_to_color_marker_label['tally_time_s'][2],
        linestyle='',
        color=variable_to_color_marker_label['tally_time_s'][0]
    )
    
    plt.plot(
        data[x_axis],
        data['clean_ballots_time_s'],
        marker=variable_to_color_marker_label['clean_ballots_time_s'][1],
        label=variable_to_color_marker_label['clean_ballots_time_s'][2],
        linestyle='',
        color=variable_to_color_marker_label['clean_ballots_time_s'][0]
    )
    
    plt.grid()
    plt.xlabel(x_axis_dict[x_axis], font_dict)
    plt.ylabel('Time (s)', font_dict)
    plt.ylim(bottom=0, top=max(data['tally_time_s'].max(), data['clean_ballots_time_s'].max()) * 1.1)
    plt.legend(prop=font_dict)
    if online_only:
        plt.savefig(f"mp-spdz_plots/online_only/{"non-optimized/" if not optimized else ""}{filename}_online.pdf", bbox_inches='tight')
    else:
        plt.savefig(f"mp-spdz_plots/with_offline_phase/{filename}.pdf", bbox_inches='tight')

def plot_varying_servers():
    filtered_data = data[
        (data['NUM_VOTERS'] == default_values['NUM_VOTERS']) &
        (data['NUM_CANDS'] == default_values['NUM_CANDS'])
    ]

    no_leak_data = filtered_data[filtered_data['RUN_LEAK_VERSION'] == 0]
    leak_data = filtered_data[filtered_data['RUN_LEAK_VERSION'] == 1]

    grouped_no_leak = (
        no_leak_data
        .groupby('NUM_SERVERS')
        .agg({
            'total_time_s': 'mean',
            'send_and_receive_ballots_time_s': 'mean',
            'clean_ballots_time_s' : 'mean',
            'convert_ballots_time_s': 'mean',
            'tally_time_s': 'mean'
        })
    )

    grouped_leak = (
        leak_data
        .groupby('NUM_SERVERS')
        .agg({
            'total_time_s': 'mean',
            'send_and_receive_ballots_time_s': 'mean',
            'clean_ballots_time_s' : 'mean',
            'convert_ballots_time_s': 'mean',
            'tally_time_s': 'mean'
        })
    )
    grouped_leak = grouped_leak.reset_index()
    grouped_no_leak = grouped_no_leak.reset_index()

    def plot_everything_leak():
        plot_everything(grouped_leak, "NUM_SERVERS", 'mp-spdz_varying_servers_plot_leak')

    def plot_everything_no_leak():
        plot_everything(grouped_no_leak, "NUM_SERVERS", 'mp-spdz_varying_servers_plot_no_leak')

    def plot_tally_time_servers():
        plot_tally_time(grouped_leak, "NUM_SERVERS", 'mp-spdz_varying_servers_plot_leak_tally_time')
        plot_tally_time(grouped_no_leak, "NUM_SERVERS", 'mp-spdz_varying_servers_plot_no_leak_tally_time')

    plot_everything_leak()
    plot_everything_no_leak()
    plot_tally_time_servers()

def plot_varying_candidates():
    filtered_data = data[
        (data['NUM_VOTERS'] == default_values['NUM_VOTERS']) &
        (data['NUM_SERVERS'] == default_values['NUM_SERVERS'])
    ]

    no_leak_data = filtered_data[filtered_data['RUN_LEAK_VERSION'] == 0]
    leak_data = filtered_data[filtered_data['RUN_LEAK_VERSION'] == 1]

    grouped_no_leak = (
        no_leak_data
        .groupby('NUM_CANDS')
        .agg({
            'total_time_s': 'mean',
            'send_and_receive_ballots_time_s': 'mean',
            'clean_ballots_time_s' : 'mean',
            'convert_ballots_time_s': 'mean',
            'tally_time_s': 'mean'
        })
    )

    grouped_leak = (
        leak_data
        .groupby('NUM_CANDS')
        .agg({
            'total_time_s': 'mean',
            'send_and_receive_ballots_time_s': 'mean',
            'clean_ballots_time_s' : 'mean',
            'convert_ballots_time_s': 'mean',
            'tally_time_s': 'mean'
        })
    )

    grouped_leak = grouped_leak.reset_index()
    grouped_no_leak = grouped_no_leak.reset_index()

    def plot_everything_leak():
        plot_everything(grouped_leak, "NUM_CANDS", 'mp-spdz_varying_candidates_plot_leak')

    def plot_everything_no_leak():
        plot_everything(grouped_no_leak, "NUM_CANDS", 'mp-spdz_varying_candidates_plot_no_leak')

    def plot_tally_time_candidates():
        plot_tally_time(grouped_leak, "NUM_CANDS", 'mp-spdz_varying_candidates_plot_leak_tally_time')
        plot_tally_time(grouped_no_leak, "NUM_CANDS", 'mp-spdz_varying_candidates_plot_no_leak_tally_time')

    plot_everything_leak()
    plot_everything_no_leak()
    plot_tally_time_candidates()

def plot_varying_voters():
    filtered_data = data[
        (data['NUM_SERVERS'] == default_values['NUM_SERVERS']) &
        (data['NUM_CANDS'] == default_values['NUM_CANDS']) &
        (data['NUM_VOTERS'] != 32)
    ]

    no_leak_data = filtered_data[filtered_data['RUN_LEAK_VERSION'] == 0]
    leak_data = filtered_data[filtered_data['RUN_LEAK_VERSION'] == 1]

    grouped_no_leak = (
        no_leak_data
        .groupby('NUM_VOTERS')
        .agg({
            'total_time_s': 'mean',
            'send_and_receive_ballots_time_s': 'mean',
            'clean_ballots_time_s' : 'mean',
            'convert_ballots_time_s': 'mean',
            'tally_time_s': 'mean'
        })
    )

    grouped_leak = (
        leak_data
        .groupby('NUM_VOTERS')
        .agg({
            'total_time_s': 'mean',
            'send_and_receive_ballots_time_s': 'mean',
            'clean_ballots_time_s' : 'mean',
            'convert_ballots_time_s': 'mean',
            'tally_time_s': 'mean'
        })
    )
    grouped_leak = grouped_leak.reset_index()
    grouped_no_leak = grouped_no_leak.reset_index()

    a,b = np.polyfit(grouped_leak['NUM_VOTERS'].values.tolist(), grouped_leak['tally_time_s'].values.tolist(), 1)
    print(f"Leak version: Tally time = {a} * NUM_VOTERS + {b}")

    a,b = np.polyfit(grouped_no_leak['NUM_VOTERS'].values.tolist(), grouped_no_leak['tally_time_s'].values.tolist(), 1)
    print(f"No leak version: Tally time = {a} * NUM_VOTERS + {b}")

    def plot_everything_leak():
        plot_everything(grouped_leak, "NUM_VOTERS", 'mp-spdz_varying_voters_plot_leak')

    def plot_everything_no_leak():
        plot_everything(grouped_no_leak, "NUM_VOTERS", 'mp-spdz_varying_voters_plot_no_leak')

    def plot_tally_time_voters():
        plot_tally_time(grouped_leak, "NUM_VOTERS", 'mp-spdz_varying_voters_plot_leak_tally_time')
        plot_tally_time(grouped_no_leak, "NUM_VOTERS", 'mp-spdz_varying_voters_plot_no_leak_tally_time')

    plot_everything_leak()
    plot_everything_no_leak()
    plot_tally_time_voters()

def linear_regression():
    data = pd.read_csv(f'mp-spdz_results_online.csv', sep=";")
    optimized_data = pd.read_csv(f'mp-spdz_results_online_optimized.csv', sep=";")


    def print_regression_coefficients(data):
        filtered_data = data[
            (data['NUM_SERVERS'] == default_values['NUM_SERVERS']) &
            (data['NUM_CANDS'] == default_values['NUM_CANDS']) &
            (data['NUM_VOTERS'] != default_values['NUM_VOTERS'])
        ]
        leak_data = filtered_data[filtered_data['RUN_LEAK_VERSION'] == 0]
        grouped_leak = (
            leak_data
            .groupby('NUM_VOTERS')
            .agg({
                'total_time_s': 'mean',
                'send_and_receive_ballots_time_s': 'mean',
                'clean_ballots_time_s' : 'mean',
                'convert_ballots_time_s': 'mean',
                'tally_time_s': 'mean'
            })
        )
        grouped_leak = grouped_leak.reset_index()
        a,b = np.polyfit(grouped_leak['NUM_VOTERS'].values.tolist(), grouped_leak['tally_time_s'].values.tolist(), 1)
        print(f"Leak version: Tally time = {a} * NUM_VOTERS + {b}")

        a,b,= np.polyfit(grouped_leak['NUM_VOTERS'].values.tolist(), grouped_leak['clean_ballots_time_s'].values.tolist(), 1)
        print(f"Leak version: Ballot validation time = {a} * NUM_VOTERS + {b}")

    print("Non-optimized version:")
    print_regression_coefficients(data)
    print("\nOptimized version:")
    print_regression_coefficients(optimized_data)

if __name__ == "__main__":
    # linear_regression()
    
    plot_varying_servers()
    plot_varying_candidates()
    plot_varying_voters()
    
    