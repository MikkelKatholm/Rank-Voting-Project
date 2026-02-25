import random
import Server
import Client
import TTP
import generate_ballots
import numpy as np
from consts import *



def decrypt_value(ciphertext, key_shares, threshold, server):
    other_shares = [share for share in key_shares if share[0] != server.key_share[0]]
    if threshold - 1 > len(other_shares):
        raise ValueError("Not enough distinct shares to decrypt")
    
    key_shares_for_decryption = random.sample(other_shares, threshold - 1)
    
    # Decrypt single value
    return server.decrypt_ballot_entry(
        ciphertext,
        key_shares_for_decryption,
        threshold,
    )


def decrypt_ballot(encrypted_ballot, key_shares, threshold, server):
    # Decrypt entire ballot entry by entry
    decrypted_rows = []
    
    # If encrypted_ballot is an object with .values:
    if hasattr(encrypted_ballot, 'values'):
        rows = encrypted_ballot.values
    else:
        # Assuming list of lists of ciphertexts if not object
        rows = encrypted_ballot
        
    for row in rows:
        decrypted_row = []
        for ciphertext in row:
            val = decrypt_value(ciphertext, key_shares, threshold, server)
            decrypted_row.append(val)
        decrypted_rows.append(decrypted_row)
        
    # Return a Ballot object (from consts)
    # We need to import Ballot if not available, but main imports consts.* so it should be there.
    return Ballot(decrypted_rows)


def decrypt_and_print_ballots(encrypted_ballots, key_shares, threshold, server):
    decrypted_ballots = []
    for encrypted_ballot in encrypted_ballots:
        decrypted_ballot = decrypt_ballot(
            encrypted_ballot,
            key_shares,
            threshold,
            server
        )
        decrypted_ballots.append(decrypted_ballot)

    print("\nDecrypted Ballots:")
    for i, ballot in enumerate(decrypted_ballots):
        print(f"Ballot {i}:")
        print(ballot)


def main():
    # 1. Generate some ballots
    num_ballots = 1
    generate_ballots.generate_fresh_ballots(num_ballots)

    # 2. Setup TTP and servers
    n = 5
    t = 3
    bit_length = 12
    params, key_shares, pk = TTP.setup_ttp(n, t, bit_length)
    servers = [Server.Server(params, key_shares[i], pk) for i in range(n)]

    # 3. Setup client and encrypt ballots
    clients = [Client.Client(i, params, pk) for i in range(num_ballots)]
    encrypted_ballots = [clients[i].encrypt_ballot() for i in range(num_ballots)]

    for server in servers:
        for encrypted_ballot in encrypted_ballots:
            server.add_encrypted_ballot(encrypted_ballot)

    print("Encrypted Ballots:")
    for i, eb in enumerate(encrypted_ballots):
        print(f"Ballot {i}:")
        print(eb)

    # 4. Decrypt ballots using servers
    decrypt_and_print_ballots(encrypted_ballots, key_shares, t, servers[0])

    # 5. Eliminate cand id = 1
    #candidate_to_eliminate = 1
    #for server in servers:
    #    server.update_active_candidates(candidate_to_eliminate)
    #    server.remove_eliminated_candidates()

    encrypted_ballots_after_elimination = servers[0].encrypted_ballots
    print(f"len(encrypted_ballots_after_elimination) = {len(encrypted_ballots_after_elimination)}")
    print("\nEncrypted Ballots After Eliminating Candidate 1:")
    decrypt_and_print_ballots(encrypted_ballots_after_elimination, key_shares, t, servers[0])


    for server in servers:
        server.remove_non_highest_priority()
    encrypted_ballots_after_priority_removal = servers[0].encrypted_ballots
    print("\nEncrypted Ballots After Removing Non-Highest Priority Candidates:")
    decrypt_and_print_ballots(encrypted_ballots_after_priority_removal, key_shares, t, servers[0])






if __name__ == "__main__":
    main()