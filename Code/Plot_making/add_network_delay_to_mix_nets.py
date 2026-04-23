import pandas as pd

PRIME_SIZE = 3072               # Bits
BANDWIDTH = 500                 # Mbps
LATENCY = 20                    # ms
BALLOT_SIZE = PRIME_SIZE * 2    # Bits


def transcript_size(num_ballots):
    """
    Gamma
    A               1 to num_ballots
    C               1 to num_ballots
    U               1 to num_ballots
    W               1 to num_ballots
    Lambda1
    Lambda2
    Input_ballots
    Output_ballots
    D               1 to num_ballots
    sigma           1 to num_ballots
    T_ss =
        Phi         1 to 2*num_ballots
        a           1 to 2*num_ballots
    """
    _p = PRIME_SIZE     # Bits  (p is safe prime)
    _q = _p // 2        # Bits  (q is prime)

    Gamma_size = _p
    A_size = _p * num_ballots
    C_size = _p * num_ballots
    U_size = _p * num_ballots
    W_size = _p * num_ballots
    Lambda1_size = _p
    Lambda2_size = _p
    Input_ballots_size = BALLOT_SIZE * num_ballots
    Output_ballots_size = BALLOT_SIZE * num_ballots
    D_size = _p * num_ballots
    sigma_size = _q * num_ballots
    Phi_size = _p * 2 * num_ballots
    a_size = _q * 2 * num_ballots
    total_size_bits = (Gamma_size + A_size + C_size + U_size + W_size +
                       Lambda1_size + Lambda2_size + Input_ballots_size +
                       Output_ballots_size + D_size + sigma_size +
                       Phi_size + a_size)
    return total_size_bits


    
def calculate_com_time(data_size_bits):
    # Convert bandwidth from Mbps to bits per second
    bandwidth_bps = BANDWIDTH * 1_000_000

    # Calculate transmission time in seconds
    transmission_time_seconds = data_size_bits / bandwidth_bps

    # Convert latency from ms to seconds
    latency_seconds = LATENCY / 1000

    # Total communication time in seconds
    total_communication_time_seconds = transmission_time_seconds + latency_seconds * 2

    return total_communication_time_seconds

def network_delay_communication_with_bulletin(num_ballot):
    # Convert bandwidth from Mbps to bits per second
    total_data_bits = num_ballot * BALLOT_SIZE
    return calculate_com_time(total_data_bits)


def total_communication_time_mixing(num_servers, num_ballot):
    # servers get ballots from the bulletin board, do mixing and post to the bulletin board

    # Communication time for servers to get ballots from the bulletin board
    get_and_post_time = network_delay_communication_with_bulletin(num_ballot) * 2  # Get and post
    
    total = get_and_post_time * num_servers

    return total

def total_communication_time_verifying_proofs(num_ballot):
        return calculate_com_time(transcript_size(num_ballot))  # Get proof from the bulletin board

    
def total_communication_time_decryption(num_ballots):
    # servers get ballots from the bulletin board, do decryption and post to the bulletin board

    # Communication time for servers to get ballots from the bulletin board
    get_and_post_time = network_delay_communication_with_bulletin(num_ballots) * 2  # Get and post

    return get_and_post_time

def total_communication_time_tallying(num_ballots):
    get_time = network_delay_communication_with_bulletin(num_ballots)  # Get ballots from the bulletin board
    post_results_time = calculate_com_time(1024)  # Post results to the bulletin board (assuming results are small)
    return get_time + post_results_time

def get_test_data(filename):
    df = pd.read_csv(filename, sep=';')
    return df

def main():
    df = get_test_data('Mix_nets_results.csv')
    
    # Clone the first 6 columns of the dataframe to a new dataframe
    new_df = df.iloc[:, :5].copy()
    for index, row in df.iterrows():
        num_servers = row['NUM_SERVERS']
        num_ballots = row['NUM_CLIENTS']
        time_mixing_data = row['time_mixing']
        time_verifying_proofs = row['time_verifying_proofs']
        time_decryption = row['t_decrypt']
        time_tally = row['t_tally']

        new_time_mixing = float(time_mixing_data) + total_communication_time_mixing(num_servers, num_ballots)
        new_time_verifying = float(time_verifying_proofs) + total_communication_time_verifying_proofs(num_ballots)
        new_time_decryption = float(time_decryption) + total_communication_time_decryption(num_ballots)
        new_time_tally = float(time_tally) + total_communication_time_tallying(num_ballots)
        new_total_time = new_time_mixing + new_time_verifying + new_time_decryption + new_time_tally

        # Make a new dataframe to store the new results
        new_df.at[index, 'time_mixing'] = new_time_mixing
        new_df.at[index, 'time_verifying_proofs'] = new_time_verifying
        new_df.at[index, 't_decrypt'] = new_time_decryption
        new_df.at[index, 't_tally'] = new_time_tally
        new_df.at[index, 'total_time'] = new_total_time

    new_df.to_csv('Mix_nets_results_with_network_delay.csv', index=False, sep=';')
    print("New results with network delay have been saved to Mix_nets_results_with_network_delay.csv")

if __name__ == "__main__":
    main()