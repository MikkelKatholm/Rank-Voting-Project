from consts import *
import ElGamal
import Shamir

class TTP:
    def __init__(self, bitLength: int = BIT_LENGTH):
        self.params = ElGamal.ElGamalParams(bitLength)
        self.crypto = ElGamal.ElGamalCrypto(self.params)
        self.key_pair: KeyPair = self.crypto.gen()
        self.pk = self.key_pair.pk
        self.sk = self.key_pair.sk
        self.shares: Shares = Shamir.gen_shares(self.sk, NUM_SERVERS, THRESHOLD, self.params.q)
    
    def return_info(self) -> tuple[ElGamal.ElGamalParams, PublicKey, Shares]:
        """Return the public parameters, public key, and shares of the secret key for the servers."""
        return self.params, self.pk, self.shares