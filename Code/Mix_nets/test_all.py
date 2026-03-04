from consts import perm_to_int, int_to_perm
from gen_ballots import generate_fresh_ballots
from consts import *
import ElGamal
import Server
import Client
import TTP
import pytest



def test_perm_roundtrip():
    perm = [3, 1, 4, 2]
    n = len(perm)
    v = perm_to_int(perm)
    perm2 = int_to_perm(v, n)
    assert perm == perm2


def test_elgamal_encrypt_decrypt_perm():
    params = ElGamal.ElGamalParams(16)  # small safe prime for test speed
    crypto = ElGamal.ElGamalCrypto(params)
    pk, sk = crypto.gen()
    perm = [1, 2, 3]
    
    n = len(perm)
    encoded = perm_to_int(perm)
    
    assert encoded < params.q
    c = crypto.enc(pk, perm)
    m_decoded = crypto.dec(sk, c)
    
    # decode decrypted integer back to permutation
    perm_out = int_to_perm(m_decoded, n)
    assert perm_out == perm


class TestMixNet:
    def test_full_protocol(self):
        # Setup TTP and servers
        ttp = TTP.TTP()
        params, pk, shares = ttp.return_info()
        servers = [Server.Server(params, pk, THRESHOLD, NUM_SERVERS, shares[i]) for i in range(NUM_SERVERS)]

        # Generate ballots and save to files
        generate_fresh_ballots(NUM_CLIENTS)

        # Initialize clients
        clients = [Client.Client(params, pk, idx) for idx in range(NUM_CLIENTS)]

        # Clients encrypt and send ballots to first server
        encrypted_ballots = []
        for client in clients:
            encrypted_ballot = client.read_and_encrypt_ballot()
            encrypted_ballots.append(encrypted_ballot)
        
        # Send encrypted ballots to first server
        for ballot in encrypted_ballots:
            servers[0].receive_ballot(ballot)
        
        # Run mixing protocol through all servers
        current_ballots = servers[0].run_mixing_protocol()
        for i in range(1, NUM_SERVERS):
            for ballot in current_ballots:
                servers[i].receive_ballot(ballot)
            current_ballots = servers[i].run_mixing_protocol()
        
        # Pool shares from all servers
        all_shares = []
        for server in servers:
            all_shares.append(server.sk_share)
        
        # All servers collaborate to decrypt the ballots and use majority vote to check correctness
        server_results = []
        for server in servers:
            decrypted = server.decrypt_ballots(all_shares, current_ballots)
            server_results.append(decrypted)

        print("Decrypted ballots from servers:")
        for idx, res in enumerate(server_results):
            print(f"Server {idx}: {res}")
        # Sort the results.
        sorted_results = [sorted(res) for res in server_results]

        # Compare to the ballots in the ballot folder
        original_ballots = []
        for idx in range(NUM_CLIENTS):
            with open(f'{BALLOT_FOLDER}/{idx}_ballot', 'r') as f:
                original_ballot = [int(x) for x in f.read().strip().split()]
                original_ballots.append(original_ballot)
        
        # Check that all servers got the same decrypted ballots and that they match the original ballots
        for res in sorted_results:
            assert res == sorted(original_ballots)
                



if __name__ == '__main__':
	pytest.main([__file__])
