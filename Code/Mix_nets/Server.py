from Consts import *
from ElGamal import ElGamalCrypto, ElGamalParams
from Crypto.Random import random as crypto_random
import Commitment

class Server:
    def __init__(self, params: ElGamalParams, pk: PublicKey, t: int, n: int, sk_share: Share):
        self.crypto = ElGamalCrypto(params)
        self.pk = pk
        self.t = t
        self.n = n
        self.beta = []
        self.sk_share = sk_share
        self.ballots: list[Ciphertext] = []
        self.new_ballots: list[Ciphertext] = []
        self.perm = list(range(len(self.ballots)))
        crypto_random.shuffle(self.perm)

    def receive_ballot(self, ballot: Ciphertext):
        """Receive an encrypted ballot and store it for later decryption."""
        self.ballots.append(ballot)
    
    def shuffle(self):
        """Shuffle the received ballots using a random permutation."""
        self.new_ballots = [self.new_ballots[i] for i in self.perm]

    def re_encrypt(self):
        """Re-encrypt the shuffled ballots to further obfuscate them."""
        re_encrypted_ballots = []
        for ballot in self.ballots:
            randomness = crypto_random.randint(0, self.crypto.params.q - 1)
            self.beta.append(randomness)
            random_enc = self.crypto.enc(self.pk, 1, randomness)
            re_encrypted_ballots.append(ballot * random_enc)
        self.new_ballots = re_encrypted_ballots

    def run_mixing_protocol(self) -> tuple[list[Ciphertext], dict]:
        self.perm = list(range(len(self.ballots)))
        crypto_random.shuffle(self.perm)
        """Run the full mixing protocol: re-encrypt and shuffle."""
        # 1. Re-encrypt
        self.re_encrypt()
            
        # 2. Shuffle
        self.shuffle()
                
        #gen proof
        proof = self.gen_proof()
        return self.new_ballots, proof
    
    def decrypt_ballots(self, shares: Shares, ciphertexts: list[Ciphertext]):
        """Decrypt the ballots using the shares of the secret key."""
        decrypted_messages = []
        for ct in ciphertexts:
            decrypted = self.crypto.decrypt_for_shamir(shares, ct, self.t)
            ballot_as_list = int_to_perm(decrypted)
            decrypted_messages.append(ballot_as_list)
        return decrypted_messages
    
    def gen_proof(self):
        prover = Commitment.Prover(self.beta, self.perm, self.ballots, self.new_ballots, self.crypto.params, self.pk)
        proof = prover.shuffle_elgamal_pairs()
        return proof 