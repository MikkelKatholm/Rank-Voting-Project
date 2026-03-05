from Consts import *
from ElGamal import ElGamalCrypto, ElGamalParams

class Client:
    def __init__(self, params: ElGamalParams, pk: PublicKey, ID: int):
        self.crypto = ElGamalCrypto(params)
        self.pk = pk
        self.ID = ID
     
    def send_ballot(self) -> Ciphertext:
        """Read the ballot from file, encrypt it, and return the ciphertext."""
        ballot = self.read_and_encrypt_ballot()
        return ballot

    def read_and_encrypt_ballot(self) -> Ciphertext:
        """Read the ballot from a file and encrypt it using the public key."""
        filename = f'{BALLOT_FOLDER}/{self.ID}_ballot'
        with open(filename, 'r') as f:
            ballot = [int(x) for x in f.read().strip().split()]
        print(f"Client {self.ID} read ballot: {ballot}")
        message = perm_to_int(ballot)
        if message >= self.crypto.params.q:
            raise ValueError("Encoded ballot does not fit in group (must be < q)")
        
        return self.crypto.enc(self.pk, message)