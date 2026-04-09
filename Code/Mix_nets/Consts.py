from typing import Tuple, Optional, NamedTuple, TYPE_CHECKING, List, Any
import hashlib
import math

if TYPE_CHECKING:
    import ElGamal

BALLOT_FILE = 'ballots.txt'
BALLOT_LINE_LENGTH = 100
NUM_SERVERS = 3
THRESHOLD = 2
NUM_CLIENTS = 10 #1_000_000
NUM_CANDS = 3


BIT_LENGTH = 1536 # Diego says to use 3072
PublicKey = int
SecretKey = int
KeyPair = NamedTuple('KeyPair', [('pk', PublicKey), ('sk', SecretKey)])

Message = int
Share = Tuple[int, int]
Shares = list[Share]
Ballot = list[int]
Ballots = list[Ballot]



def P(n: int, k: int) -> int:
    """Number of k-permutations of n."""
    return math.factorial(n) // math.factorial(n - k)

def perm_to_int(perm: List[int]) -> int:
    """
    Encode a partial permutation of candidates [0..NUM_CANDS-1]
    into a unique integer in
    [0, sum_{k=0}^{NUM_CANDS} P(NUM_CANDS, k) - 1]
    """
    C = NUM_CANDS
    k = len(perm)

    # --- 1. Compute block offset ---
    offset = sum(P(C, i) for i in range(k))

    # --- 2. Rank inside the block ---
    unused = list(range(C))
    rank = 0

    for i in range(k):
        idx = unused.index(perm[i])
        rank += idx * P(C - 1 - i, k - 1 - i)
        unused.pop(idx)

    return offset + rank


def int_to_perm(value: int) -> List[int]:
    """
    Decode integer into a partial permutation
    of candidates [0..NUM_CANDS-1].
    """

    C = NUM_CANDS

    # ---- 1. Find correct block (determine k) ----
    offset = 0
    k = 0
    while k <= C:
        block_size = P(C, k)
        if value < offset + block_size:
            break
        offset += block_size
        k += 1

    if k > C:
        raise ValueError("value out of range")

    # rank inside block
    rank = value - offset

    # ---- 2. Unrank partial permutation ----
    unused = list(range(C))
    perm: List[int] = []

    for i in range(k):
        weight = P(C - 1 - i, k - 1 - i)
        idx = rank // weight
        rank %= weight
        perm.append(unused.pop(idx))

    return perm


class Ciphertext:
    def __init__(self, c1: int, c2: int, params: "ElGamal.ElGamalParams"):
        self.c1 = c1
        self.c2 = c2
        self.params = params

    def __repr__(self):
        return f"Ciphertext(c1={self.c1}, c2={self.c2})"
    
    def __str__(self):
        return self.__repr__()
    
    def __add__(self, other):
        return NotImplemented
    
    def __sub__(self, other):
        if not isinstance(other, Ciphertext):
            return NotImplemented
        new_c1 = (self.c1 * pow(other.c1, -1, self.params.p)) % self.params.p
        new_c2 = (self.c2 * pow(other.c2, -1, self.params.p)) % self.params.p
        return Ciphertext(new_c1, new_c2, self.params)
    
    def __mul__(self, other):
        if not isinstance(other, Ciphertext):
            return NotImplemented
        new_c1 = (self.c1 * other.c1) % self.params.p
        new_c2 = (self.c2 * other.c2) % self.params.p
        return Ciphertext(new_c1, new_c2, self.params)

    def __iter__(self):
        yield self.c1
        yield self.c2

def hash(msg: Any, prime: int) -> int:
    def _update_hasher(obj: Any, h: "hashlib._Hash"):
        if isinstance(obj, bytes):
            h.update(b'B')
            h.update(len(obj).to_bytes(4, 'big'))
            h.update(obj)
        elif isinstance(obj, str):
            b = obj.encode()
            h.update(b'S')
            h.update(len(b).to_bytes(4, 'big'))
            h.update(b)
        elif isinstance(obj, int):
            if obj == 0:
                b = b"\x00"
            else:
                nbytes = (obj.bit_length() + 7) // 8
                b = obj.to_bytes(nbytes, 'big', signed=False)
            h.update(b'I')
            h.update(len(b).to_bytes(4, 'big'))
            h.update(b)
        elif isinstance(obj, Ciphertext):
            _update_hasher(obj.c1, h)
            _update_hasher(obj.c2, h)
        elif isinstance(obj, (list, tuple)):
            h.update(b'L')
            h.update(len(obj).to_bytes(4, 'big'))
            for el in obj:
                _update_hasher(el, h)
        else:
            # Fallback: use string representation as bytes (should be rare)
            b = str(obj).encode()
            h.update(b'U')
            h.update(len(b).to_bytes(4, 'big'))
            h.update(b)

    h = hashlib.sha256()
    _update_hasher(msg, h)
    return int.from_bytes(h.digest(), 'big') % prime

if __name__ == "__main__":
    input = [0, 2]
    encoded = perm_to_int(input)
    print(f"Encoded {input} to {encoded}")
    decoded = int_to_perm(encoded)
    print(f"Decoded {encoded} back to {decoded}") 