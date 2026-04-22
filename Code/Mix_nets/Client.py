from Consts import *
from ElGamal import ElGamalCrypto, ElGamalParams
from ElGamal_Eplitic import ElGamalCrypto_EC, ElGamalParams_EC, Ciphertext_EC
from typing import Union, cast, Any

class Client:
    def __init__(self, params: Any, pk: Any, ID: int):
        if USE_ELLIPTIC_CURVE:
            self.crypto = ElGamalCrypto_EC(cast(ElGamalParams_EC, params))
        else:
            self.crypto = ElGamalCrypto(cast(ElGamalParams, params))
        self.pk = pk
        self.ID = ID
     
    def send_ballot(self) -> Union[Ciphertext, Ciphertext_EC]:
        """Read the ballot from file, encrypt it, and return the ciphertext."""
        ballot = self.read_and_encrypt_ballot()
        return ballot

    def read_and_encrypt_ballot(self) -> Union[Ciphertext, Ciphertext_EC]:
        """Read the ballot from a file and encrypt it using the public key."""
        with open(BALLOT_FILE, 'r') as f:
            f.seek(self.ID * BALLOT_LINE_LENGTH)
            line = f.read(BALLOT_LINE_LENGTH).strip()
            
        ballot = [int(x) for x in line.split()]
        
        message = perm_to_int(ballot)
        if message >= self.crypto.params.q:
            raise ValueError("Encoded ballot does not fit in group (must be < q)")
        
        return self.crypto.enc(self.pk, message)