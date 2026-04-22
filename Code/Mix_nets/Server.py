from Consts import *
from ElGamal import ElGamalCrypto, ElGamalParams
from Crypto.Random import random as crypto_random
import Commitment
import ElGamal_Eplitic
from typing import Any, cast, Union

class Server:
    def __init__(self, params: Any, pk: Any, t: int, n: int, sk_share: Share):
        if USE_ELLIPTIC_CURVE:
            self.crypto = ElGamal_Eplitic.ElGamalCrypto_EC(cast(ElGamal_Eplitic.ElGamalParams_EC, params))
        else:
            self.crypto = ElGamalCrypto(cast(ElGamalParams, params))
        self.pk = pk
        self.t = t
        self.n = n
        self.beta = []
        self.sk_share = sk_share
        self.ballots: list[Any] = []
        self.new_ballots: list[Any] = []
        self.perm = list(range(len(self.ballots)))
        crypto_random.shuffle(self.perm)

    def receive_ballot(self, ballot: Any):
        """Receive an encrypted ballot and store it for later decryption."""
        self.ballots.append(ballot)
    
    def shuffle(self):
        """Shuffle the received ballots using a random permutation."""
        self.new_ballots = [self.new_ballots[i] for i in self.perm]

    def re_encrypt(self):
        """Re-encrypt the shuffled ballots to further obfuscate them."""
        re_encrypted_ballots = []
        for ballot in self.ballots:
            if USE_ELLIPTIC_CURVE:
                randomness = crypto_random.randint(1, self.crypto.params.q - 1)
                self.beta.append(randomness)
                c1 = randomness * cast(ElGamal_Eplitic.ECPoint, self.crypto.params.g)
                c2 = randomness * cast(ElGamal_Eplitic.ECPoint, self.pk)
                random_enc = ElGamal_Eplitic.Ciphertext_EC(cast(ElGamal_Eplitic.ECPoint, c1), cast(ElGamal_Eplitic.ECPoint, c2))
                re_encrypted_ballots.append(ballot + random_enc)
            else:
                randomness = crypto_random.randint(0, self.crypto.params.q - 1)
                self.beta.append(randomness)
                # Ensure we only use int parameters for pow
                crypto_params = cast(ElGamalParams, self.crypto.params)
                c1 = pow(crypto_params.g, randomness, crypto_params.p)
                c2 = pow(cast(int, self.pk), randomness, crypto_params.p)
                random_enc = Ciphertext(c1, c2, crypto_params)          
                re_encrypted_ballots.append(ballot * random_enc)
        self.new_ballots = re_encrypted_ballots

    def run_mixing_protocol(self) -> tuple[list[Any], Any]:
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
    
    def decrypt_ballots(self, shares: Shares, ciphertexts: list[Any]):
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