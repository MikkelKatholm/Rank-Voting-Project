from Consts import *
from ElGamal import ElGamalCrypto, ElGamalParams
import Shamir
import random

class Server:
    def __init__(self, params: ElGamalParams, pk: PublicKey, t: int, n: int, sk_share: Share):
        self.crypto = ElGamalCrypto(params)
        self.pk = pk
        self.t = t
        self.n = n
        self.sk_share = sk_share
        self.ballots: list[Ciphertext] = []

    def receive_ballot(self, ballot: Ciphertext):
        """Receive an encrypted ballot and store it for later decryption."""
        self.ballots.append(ballot)
    
    def shuffle(self):
        """Shuffle the received ballots using a random permutation."""
        random.shuffle(self.ballots)
        
    def re_encrypt(self):
        """Re-encrypt the shuffled ballots to further obfuscate them."""
        re_encrypted_ballots = []
        for ballot in self.ballots:
            # Re-encrypt by encrypting the ciphertext again with a random r
            random_enc = self.crypto.enc(self.pk, 1)
            # Combine the original ciphertext with the random encryption
            re_encrypted_ballots.append(ballot * random_enc)
        # Destroy all knowledge of the original ballot (in a real implementation, we would also need to securely erase the original ciphertext)
        self.ballots = []
        return re_encrypted_ballots

    def run_mixing_protocol(self):
        """Run the full mixing protocol: shuffle and re-encrypt."""
        self.shuffle()
        return self.re_encrypt()
    
    def decrypt_ballots(self, shares: Shares, ciphertexts: list[Ciphertext]):
        """Decrypt the ballots using the shares of the secret key."""
        decrypted_messages = []
        for ct in ciphertexts:
            decrypted = self.crypto.decrypt_for_shamir(shares, ct, self.t)
            ballot_as_list = int_to_perm(decrypted)
            decrypted_messages.append(ballot_as_list)
        return decrypted_messages
    