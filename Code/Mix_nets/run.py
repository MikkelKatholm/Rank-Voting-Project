from gen_ballots import generate_fresh_ballots
from Consts import *
import random
import ElGamal
import Server
import Client
import TTP
import pytest
import Tally
import Verifier
import time
import pandas as pd

def run_all():    
    time_total_start = time.time()

    # Setup TTP and servers
    t0 = time.time()
    ttp = TTP.TTP()
    params, pk, shares = ttp.return_info()
    servers = [Server.Server(params, pk, THRESHOLD, NUM_SERVERS, shares[i]) for i in range(NUM_SERVERS)]
    verifier = Verifier.Verifier(params, pk)
    t_setup = time.time() - t0

    # Generate ballots and save to files
    t0 = time.time()
    generate_fresh_ballots(NUM_CLIENTS)
    t_gen_ballots = time.time() - t0

    # Initialize clients
    t0 = time.time()
    clients = [Client.Client(params, pk, idx) for idx in range(NUM_CLIENTS)]
    t_make_clients = time.time() - t0

    # Clients encrypt and send ballots to first server
    t0 = time.time()
    encrypted_ballots = []
    for client in clients:
        encrypted_ballot = client.read_and_encrypt_ballot()
        encrypted_ballots.append(encrypted_ballot)
    t_encrypt_ballots = time.time() - t0

    # Send encrypted ballots to first server
    t0 = time.time()
    for ballot in encrypted_ballots:
        servers[0].receive_ballot(ballot)
    t_send_ballots = time.time() - t0

    # Run mixing protocol through all servers
    time_verifying_proofs = 0
    time_mixing = 0

    t_mix_start = time.time()
    current_ballots, proof = servers[0].run_mixing_protocol()
    time_mixing += time.time() - t_mix_start
    
    t_ver_start = time.time()
    if not verifier.verify_shuffle_elgamal_pairs(encrypted_ballots, current_ballots, proof):
        raise ValueError("The proof is invalid: Shuffle proof verification failed at server 0.")
    time_verifying_proofs += time.time() - t_ver_start
    
    for i in range(1, NUM_SERVERS):
        for ballot in current_ballots:
            servers[i].receive_ballot(ballot)
        last_round_ballots = current_ballots
        t_mix_start = time.time()
        current_ballots, proof = servers[i].run_mixing_protocol()
        time_mixing += time.time() - t_mix_start
        
        t_ver_start = time.time()
        if not verifier.verify_shuffle_elgamal_pairs(last_round_ballots, current_ballots, proof):
            raise ValueError(f"The proof is invalid: Shuffle proof verification failed at server {i}.")
        time_verifying_proofs += time.time() - t_ver_start

    # Pool shares from all servers
    t0 = time.time()
    all_shares = []
    for server in servers:
        all_shares.append(server.sk_share)
    t_pool_shares = time.time() - t0

    # All servers collaborate to decrypt the ballots and use majority vote to check correctness
    t0 = time.time()
    server_results = []
    for server in servers:
        decrypted = server.decrypt_ballots(all_shares, current_ballots)
        server_results.append(decrypted)
    t_decrypt = time.time() - t0

            
    # Run the tally function on the decrypted ballots to find the winner
    t0 = time.time()
    winners = []
    for server in servers:
        winner = Tally.tally(server_results[0])
        winners.append(winner)
    t_tally = time.time() - t0

    time_total = time.time() - time_total_start
    

    # Save the timeing results to a CSV file with the constants used in a column for reference
    results_df = pd.DataFrame({
        "NUM_SERVERS": [NUM_SERVERS],
        "NUM_CLIENTS": [NUM_CLIENTS],
        "NUM_CANDS": [NUM_CANDS],
        "THRESHOLD": [THRESHOLD],
        "BIT_LENGTH": [BIT_LENGTH],
        "Use_Elliptic_Curve": [USE_ELLIPTIC_CURVE],
        "t_setup": [t_setup],
        "t_gen_ballots": [t_gen_ballots],
        "t_make_clients": [t_make_clients],
        "t_encrypt_ballots": [t_encrypt_ballots],
        "t_send_ballots": [t_send_ballots],
        "time_mixing": [time_mixing],
        "time_verifying_proofs": [time_verifying_proofs],
        "t_pool_shares": [t_pool_shares],
        "t_decrypt": [t_decrypt],
        "t_tally": [t_tally],
        "time_total": [time_total]
    })

    return results_df

def save_results_to_csv(results_df, filename="results.csv"):
    # append results to CSV file, create it with headers if it doesn't exist, make the file if it doesn't exist
    try:
        with open(filename, 'x') as f:
            results_df.to_csv(f, index=False, sep=';')
    except FileExistsError:
        with open(filename, 'a') as f:
            results_df.to_csv(f, index=False, header=False, sep=';')

def main():
    results_df = run_all()
    save_results_to_csv(results_df)

if __name__ == "__main__":
    main()