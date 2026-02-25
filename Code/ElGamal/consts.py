from typing import Tuple, Optional, NamedTuple, TYPE_CHECKING

if TYPE_CHECKING:
    import ElGamal

bitLength = 64
NUM_CANDS = 3
BALLOT_FOLDER = "ballots"


PublicKey = int
SecretKey = int
KeyPair = NamedTuple('KeyPair', [('pk', PublicKey), ('sk', SecretKey)])

Message = int
Share = Tuple[int, int]
Shares = list[Share]

class Ciphertext:
    def __init__(self, c1: int, c2: int, params: "ElGamal.ElGamalParams"):
        self.c1 = c1
        self.c2 = c2
        self.params = params

    def __repr__(self):
        return f"Ciphertext(c1={self.c1}, c2={self.c2})"
    
    def __add__(self, other):
        if not isinstance(other, Ciphertext):
            return NotImplemented
        new_c1 = (self.c1 * other.c1) % self.params.p
        new_c2 = (self.c2 * other.c2) % self.params.p
        return Ciphertext(new_c1, new_c2, self.params)
    
    def __sub__(self, other):
        if not isinstance(other, Ciphertext):
            return NotImplemented
        new_c1 = (self.c1 * pow(other.c1, -1, self.params.p)) % self.params.p
        new_c2 = (self.c2 * pow(other.c2, -1, self.params.p)) % self.params.p
        return Ciphertext(new_c1, new_c2, self.params)
    
    def __mul__(self, other):
        if not isinstance(other, int):
            return NotImplemented
        new_c1 = pow(self.c1, other, self.params.p)
        new_c2 = pow(self.c2, other, self.params.p)
        return Ciphertext(new_c1, new_c2, self.params)

    def __iter__(self):
        yield self.c1
        yield self.c2



class Ballot:
    def __init__(self, values: list[list[int]]) -> None:
        self.values = values
        
    def __str__(self) -> str:
        return '\n'.join([' '.join(map(str, row)) for row in self.values])
    
    def get_entry(self, row, col):
        return self.values[row][col]
    
    def update_entry(self, row, col, value):
        self.values[row][col] = value

class EncryptedBallot:
    def __init__(self, values: list[list[Ciphertext]]) -> None:
        self.values = values
        
    def __str__(self) -> str:
        return '\n'.join(['\t'.join([f"({c.c1}, {c.c2})" for c in row]) for row in self.values])
    
    def get_entry(self, row, col):
        return self.values[row][col]
    
    def update_entry(self, row, col, value):
        self.values[row][col] = value

    def get_col(self, col):
        return [self.values[i][col] for i in range(len(self.values))]        

