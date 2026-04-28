import matplotlib.pyplot as plt
import pandas as pd

data = pd.read_csv('mp-spdz_results.csv', sep=";")

x_axis_dict = {
    'NUM_SERVERS': 'Number of Servers',
    'NUM_CANDS': 'Number of Candidates',
    'NUM_VOTERS': 'Number of Voters'
}

variable_to_color_marker_label = {
    'total_time_s': ('black', 'o', 'Total Time'),
    'clean_ballots_time_s': ('green', 's', 'Clean Ballots Time'),
    'send_and_receive_ballots_time_s': ('darkorange', 'X', 'Send and Receive Ballots Time'),
    'convert_ballots_time_s': ('red', 'D', 'Convert Ballots Time'),
    'tally_time_s': ('blue', '*', 'Tally Time')
}

default_values = {
    'NUM_SERVERS': 5,
    'NUM_CANDS': 5,
    'NUM_VOTERS': 32,
}

def plot_everything(data, x_axis, filename):
    plt.figure()
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
    plt.xlabel(x_axis_dict[x_axis])
    plt.ylabel('Time (s)')
    plt.legend()
    plt.savefig(f"mp-spdz_plots/{filename}.pdf", bbox_inches='tight')

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
    plt.grid()
    plt.xlabel(x_axis_dict[x_axis])
    plt.ylabel('Time (s)')
    plt.legend()
    plt.savefig(f"mp-spdz_plots/{filename}.pdf", bbox_inches='tight')

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
    #plot_tally_time()

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

if __name__ == "__main__":
    plot_varying_servers()
    plot_varying_candidates()