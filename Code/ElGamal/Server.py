from consts import *
import ElGamal
import Shamir

class Server:
    def __init__(self, params: ElGamal.ElGamalParams, key_share: Share, pk: PublicKey):
        self.params = params
        self.key_share = key_share
        self.pk = pk
        self.elgamal = ElGamal.ElGamalCrypto(params)
        self.active_candidates = [1] * NUM_CANDS  # All candidates start as active (1 = active, 0 = eliminated)
        self.encrypted_ballots = []

    def add_encrypted_ballot(self, encrypted_ballot: EncryptedBallot):
        self.encrypted_ballots.append(encrypted_ballot)

    def decrypt_ballot_entry(self, ciphertext: Ciphertext, key_shares: Shares, threshold: int) -> int:
        """Decrypt a single ballot entry using the server's key share and the shares from other servers."""
        # Combine the server's key share with the shares from other servers
        filtered_shares = [share for share in key_shares if share[0] != self.key_share[0]]
        selected_shares = [self.key_share] + filtered_shares
        if len(selected_shares) < threshold:
            raise ValueError("Not enough distinct shares to decrypt")
        decrypted_value = self.elgamal.decrypt_for_shamir(selected_shares, ciphertext, threshold)
        return decrypted_value
    
    def decrypt_ballot(self, encrypted_ballot: EncryptedBallot, key_shares: Shares, threshold: int) -> Ballot:
        decrypted_values = []
        for row in encrypted_ballot.values:
            decrypted_row = []
            for ciphertext in row:
                decrypted_value = self.decrypt_ballot_entry(ciphertext, key_shares, threshold)
                decrypted_row.append(decrypted_value)
            decrypted_values.append(decrypted_row)
        return Ballot(decrypted_values)
    
    def remove_eliminated_candidates(self):
        for eb in self.encrypted_ballots:
            for i, row in enumerate(eb.values):
                candidate_index = i
                if self.active_candidates[candidate_index] == 0:
                    for j, _ in enumerate(row):
                        fresh_zero_ciphertext = self.elgamal.enc(self.pk, 0)
                        eb.update_entry(i, j, fresh_zero_ciphertext)

    def update_active_candidates(self, candidate_to_eliminate: int):
        self.active_candidates[candidate_to_eliminate] = 0 

    def remove_non_highest_priority(self):
        for eb in self.encrypted_ballots:
            col = [eb.get_col(col) for col in range(NUM_CANDS)]
            col_sums = [sum(col[1:], col[0]) for col in col]

            for i, row in enumerate(eb.values):
                for j, _ in enumerate(row):
                    working_ciphertext = eb.get_entry(i, j)
                    intermediate_col_sums = self.elgamal.enc(self.pk, 0)
                    for k in range(j):
                        intermediate_col_sums += col_sums[k]


                    not_working_ciphertext = self.elgamal.enc(self.pk, 1) - working_ciphertext
                    new_ciphertext = self.elgamal.enc(self.pk, 1) - (not_working_ciphertext + intermediate_col_sums)
                    eb.update_entry(i, j, new_ciphertext)
            

