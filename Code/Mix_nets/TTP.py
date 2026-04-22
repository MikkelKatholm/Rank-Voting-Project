from Consts import *
import ElGamal
import ElGamal_Eplitic

import Shamir

class TTP:
    def __init__(self, bitLength: int = BIT_LENGTH):
        if USE_ELLIPTIC_CURVE:
            self.params = ElGamal_Eplitic.ElGamalParams_EC()
            self.crypto = ElGamal_Eplitic.ElGamalCrypto_EC(self.params)
        else:
            self.params = ElGamal.ElGamalParams(bitLength)
            self.crypto = ElGamal.ElGamalCrypto(self.params)
            
        self.key_pair = self.crypto.gen()
        self.pk = self.key_pair[0]
        self.sk = self.key_pair[1]
        self.shares: Shares = Shamir.gen_shares(self.sk, NUM_SERVERS, THRESHOLD, self.params.q)
    
    def return_info(self) -> tuple[ElGamal.ElGamalParams | ElGamal_Eplitic.ElGamalParams_EC, PublicKey, Shares]:
        """Return the public parameters, public key, and shares of the secret key for the servers."""
        return self.params, self.pk, self.shares