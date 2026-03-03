from typing import Tuple, Optional, NamedTuple, TYPE_CHECKING, List
import math

if TYPE_CHECKING:
    import ElGamal

BALLOT_FOLDER = 'ballots'
NUM_SERVERS = 3
THRESHOLD = 2
NUM_CLIENTS = 3
NUM_CANDS = 4


BIT_LENGTH = 64
PublicKey = int
SecretKey = int
KeyPair = NamedTuple('KeyPair', [('pk', PublicKey), ('sk', SecretKey)])

Message = int
Share = Tuple[int, int]
Shares = list[Share]


def perm_to_int(perm: List[int]) -> int:
    """Encode a permutation of [1..n] to an integer in [0, n! - 1] using Lehmer (factorial) code.

    Example: perm = [2,1,3] (1-based elements) -> integer
    """
    n = len(perm)
    elements = list(range(1, n + 1))
    result = 0

    for i in range(n):
        index = elements.index(perm[i])
        result += index * math.factorial(n - i - 1)
        elements.pop(index)

    return result


def int_to_perm(value: int, n: int) -> List[int]:
    """Decode an integer in [0, n! - 1] to a permutation of [1..n] using Lehmer/inversion vector.

    :param value: integer to decode
    :param n: size of permutation
    :return: permutation as list of integers from 1..n
    """
    if value < 0 or value >= math.factorial(n):
        raise ValueError("value out of range for given n")

    elements = list(range(1, n + 1))
    perm: List[int] = []
    remaining = value

    for i in range(n - 1, -1, -1):
        fact = math.factorial(i)
        idx = remaining // fact
        remaining = remaining % fact
        perm.append(elements.pop(idx))

    return perm


class Ciphertext:
    def __init__(self, c1: int, c2: int, params: "ElGamal.ElGamalParams"):
        self.c1 = c1
        self.c2 = c2
        self.params = params

    def __repr__(self):
        return f"Ciphertext(c1={self.c1}, c2={self.c2})"
    
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