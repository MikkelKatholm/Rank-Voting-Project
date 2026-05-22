import pandas as pd

with_online = True

# Read data
data = pd.read_csv(
    f'mp-spdz_results_{"online" if with_online else "with_offline"}_optimized.csv',
    sep=";"
)

default_values = {
    'NUM_SERVERS': 5,
    'NUM_CANDS': 5,
    'NUM_VOTERS': 32,
}


def print_rows(variable):
    # Start with full dataframe
    filtered_data = data.copy()

    # Filter on default values except for the variable we want to vary
    default_values_except_variable = {
        k: v for k, v in default_values.items() if k != variable
    }

    print(default_values_except_variable)

    for k, v in default_values_except_variable.items():
        filtered_data = filtered_data[filtered_data[k] == v]

    # Split into leak / no leak
    no_leak = filtered_data[filtered_data['RUN_LEAK_VERSION'] == 0]
    leak = filtered_data[filtered_data['RUN_LEAK_VERSION'] == 1]

    # Group and average
    grouped_no_leak = (
        no_leak.groupby(variable)
        .agg({
            'tally_time_s': 'mean',
            'clean_ballots_time_s': 'mean'
        })
        .reset_index()
    )

    grouped_leak = (
        leak.groupby(variable)
        .agg({
            'tally_time_s': 'mean',
            'clean_ballots_time_s': 'mean'
        })
        .reset_index()
    )

    # Merge both tables
    table = pd.merge(
        grouped_no_leak,
        grouped_leak,
        on=variable,
        suffixes=('_no_leak', '_leak')
    )

    # Print LaTeX rows
    for _, row in table.iterrows():
        print(
            f"{int(row[variable])} "
            f"& {row['tally_time_s_no_leak']:.2f} "
            f"& {row['clean_ballots_time_s_no_leak']:.2f} "
            f"& {row['tally_time_s_leak']:.2f} "
            f"& {row['clean_ballots_time_s_leak']:.2f} \\\\"
        )

if __name__ == "__main__":
    print_rows('NUM_VOTERS')