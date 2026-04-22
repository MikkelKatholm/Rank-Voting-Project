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
import Shamir
import ElGamal_Eplitic

def test_perm_roundtrip():
    perm = [i for i in range(NUM_CANDS)]
    random.shuffle(perm)
    
    v = perm_to_int(perm)
    perm2 = int_to_perm(v)
    assert perm == perm2

def test_elgamal_encrypt_decrypt_perm():
    params = ElGamal.ElGamalParams(16)  # small safe prime for test speed
    crypto = ElGamal.ElGamalCrypto(params)
    pk, sk = crypto.gen()
    perm = [i for i in range(NUM_CANDS)]
    
    encoded = perm_to_int(perm)
    
    assert encoded < params.q
    c = crypto.enc(pk, perm)
    m_decoded = crypto.dec(sk, c)
    
    # decode decrypted integer back to permutation
    perm_out = int_to_perm(m_decoded)
    assert perm_out == perm

def test_tally():
    ballot1 = [i for i in range(NUM_CANDS)]
    n = NUM_CANDS//2
    ballot2 = ballot1[n:] + ballot1[:n]
    ballots = [ballot1 if i % 2 == 0 else ballot2 for i in range(NUM_CLIENTS)]

    expected_winner = ballot1[n:][0] if NUM_CLIENTS % 2 == 0 else ballot1[0]

    winner = Tally.tally(ballots)
    assert winner == expected_winner


class TestMixNet:

    #@pytest.mark.skip(reason="This test is very slow since it runs the full protocol, but it can be used for manual testing.")
    @pytest.mark.parametrize("i", range(1))  # Run the test 10 times to catch randomness issues
    def test_full_protocol(self, i):
        from typing import cast
        
        # Setup TTP and servers
        ttp = TTP.TTP()
        params, pk, shares = ttp.return_info()
        servers = [Server.Server(params, pk, THRESHOLD, NUM_SERVERS, shares[i]) for i in range(NUM_SERVERS)]
        verifier = Verifier.Verifier(cast(ElGamal.ElGamalParams, params), cast(int, pk))

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
        current_ballots, proof = servers[0].run_mixing_protocol()
        if not cast(Verifier.Verifier, verifier).verify_shuffle_elgamal_pairs(encrypted_ballots, current_ballots, proof):
            raise ValueError("The proof is invalid: Shuffle proof verification failed at server 0.")
        for i in range(1, NUM_SERVERS):
            for ballot in current_ballots:
                servers[i].receive_ballot(ballot)
            last_round_ballots = current_ballots
            current_ballots, proof = servers[i].run_mixing_protocol()
            if not cast(Verifier.Verifier, verifier).verify_shuffle_elgamal_pairs(last_round_ballots, current_ballots, proof):
                raise ValueError(f"The proof is invalid: Shuffle proof verification failed at server {i}.")

        # Pool shares from all servers
        all_shares = []
        for server in servers:
            all_shares.append(server.sk_share)
        
        # All servers collaborate to decrypt the ballots and use majority vote to check correctness
        server_results = []
        for server in servers:
            decrypted = server.decrypt_ballots(all_shares, current_ballots)
            server_results.append(decrypted)

        # Sort the results.
        sorted_results = [sorted(res) for res in server_results]

        # Compare to the ballots in the ballot file
        original_ballots = []
        with open(BALLOT_FILE, 'r') as f:
            for _ in range(NUM_CLIENTS):
                line = f.read(BALLOT_LINE_LENGTH).strip()
                original_ballots.append([int(x) for x in line.split()])
        
        # Check that all servers got the same decrypted ballots and that they match the original ballots
        for res in sorted_results:
            assert res == sorted(original_ballots)
                
        # Run the tally function on the decrypted ballots to find the winner
        winners = []
        for server in servers:
            winner = Tally.tally(server.decrypt_ballots(all_shares, current_ballots))
            winners.append(winner)
        # Check that all servers got the same winner and that it is a valid candidate
        assert all(w == winners[0] for w in winners)
        assert winners[0] in range(NUM_CANDS)


class TestElipticElGamal:

    def test_encrypt_decrypt_perm(self):
        params = ElGamal_Eplitic.ElGamalParams_EC()
        crypto = ElGamal_Eplitic.ElGamalCrypto_EC(params)
        pk, sk = crypto.gen()
        perm = [i for i in range(NUM_CANDS)]
        
        c = crypto.enc(pk, perm)
        m_decoded = crypto.dec(sk, c)
        
        # decode decrypted integer back to permutation
        perm_out = int_to_perm(m_decoded)
        assert perm_out == perm

    def test_shamir_threshold_decryption_positive(self):
        import Shamir
        params = ElGamal_Eplitic.ElGamalParams_EC()
        crypto = ElGamal_Eplitic.ElGamalCrypto_EC(params)
        pk, sk = crypto.gen()
        msg = 42
        
        ctx = crypto.enc(pk, msg)
        
        # Split the secret using your default Shamir implementation
        shares = Shamir.gen_shares(sk, n=5, t=3, fieldsize=params.q)
        
        # Decrypt using exactly the threshold number of shares (3)
        dec_msg = crypto.decrypt_for_shamir(shares[:3], ctx, threshold=3)
        assert dec_msg == msg
        
        # Optionally, check that taking a different combination of 3 shares also works
        dec_msg_alt = crypto.decrypt_for_shamir([shares[0], shares[2], shares[4]], ctx, threshold=3)
        assert dec_msg_alt == msg

    def test_shamir_threshold_decryption_negative(self):
        import Shamir
        params = ElGamal_Eplitic.ElGamalParams_EC()
        crypto = ElGamal_Eplitic.ElGamalCrypto_EC(params)
        pk, sk = crypto.gen()
        msg = 42
        
        ctx = crypto.enc(pk, msg)
        shares = Shamir.gen_shares(sk, n=5, t=3, fieldsize=params.q)
        
        # Scenario 1: Not enough shares given compared to the requested threshold
        with pytest.raises(ValueError, match="threshold cannot exceed number of shares"):
            crypto.decrypt_for_shamir(shares[:2], ctx, threshold=3)
            
        # Scenario 2: Attempting to bypass by lying about the threshold (providing 2 shares, threshold=2).
        # Since the actual threshold was 3, standard Shamir will reconstruct garbage.
        # This will either throw a ValueError or map to some random int that absolutely isn't our message.
        try:
            wrong_decryption = crypto.decrypt_for_shamir(shares[:2], ctx, threshold=2)
            assert wrong_decryption != msg, "Threshold decryption inexplicably decoded correctly with wrong shares!"
        except ValueError:
            pass # ValueError is also completely acceptable for invalid points
    
       


if __name__ == '__main__':
	pytest.main([__file__])
