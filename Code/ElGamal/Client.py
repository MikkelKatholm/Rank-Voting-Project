from consts import *
import ElGamal

class Client:
    def __init__(self, client_id: int, params: ElGamal.ElGamalParams, pk: PublicKey):
        self.client_id = client_id
        self.params = params
        self.pk = pk
        self.elgamal = ElGamal.ElGamalCrypto(params)
        self.ballot = self.read_ballot_from_file()
    
    def read_ballot_from_file(self) -> Ballot:
        filename = f"{BALLOT_FOLDER}/{self.client_id}_ballot"
        with open(filename, 'r') as f:
            lines = f.readlines()
            values = [list(map(int, line.strip().split())) for line in lines]
            ballot = Ballot(values)
            print(f"Client {self.client_id} read ballot:\n{ballot}\n")
            return ballot
    
    def encrypt_ballot(self) -> EncryptedBallot:
        encrypted_values = []    
        for row in self.ballot.values:
            encrypted_row = []
            for m in row:
                ciphertext = self.elgamal.enc(self.pk, m)
                encrypted_row.append(ciphertext)
            encrypted_values.append(encrypted_row)
        return EncryptedBallot(encrypted_values)

