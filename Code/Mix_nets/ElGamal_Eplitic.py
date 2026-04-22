from Consts import *
import secrets
import Shamir
import sympy as sp
from typing import NamedTuple, Tuple, Optional, Any

# NIST P-256 Curve Parameters
P_CURVE = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
A = P_CURVE - 3
B = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
Gx = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
Gy = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5
Q = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

class ECPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def is_infinity(self):
        return self.x is None and self.y is None
        
    def is_on_curve(self):
        if self.is_infinity():
            return True
        return (self.y**2 - (self.x**3 + A * self.x + B)) % P_CURVE == 0

    def __repr__(self):
        if self.is_infinity(): return "Infinity"
        return f"ECPoint({self.x}, {self.y})"

    def __eq__(self, other):
        if not isinstance(other, ECPoint):
            return False
        return self.x == other.x and self.y == other.y

    def __add__(self, other):
        if self.is_infinity():
            return other
        if other.is_infinity():
            return self
        
        if self.x == other.x and self.y != other.y:
            return ECPoint(None, None) # Infinity
            
        if self.x == other.x:
            if self.y == 0:
                return ECPoint(None, None)
            m = (3 * self.x**2 + A) * pow(2 * self.y, -1, P_CURVE) % P_CURVE
        else:
            m = (other.y - self.y) * pow(other.x - self.x, -1, P_CURVE) % P_CURVE
            
        x_r = (m**2 - self.x - other.x) % P_CURVE
        y_r = (m * (self.x - x_r) - self.y) % P_CURVE
        return ECPoint(x_r, y_r)

    def __mul__(self, scalar):
        if scalar < 0:
            raise ValueError("Negative scalar not allowed")
        scalar = scalar % Q
        result = ECPoint(None, None)
        addend = self
        
        while scalar:
            if scalar & 1:
                result += addend
            addend += addend
            scalar >>= 1
        return result

    def __rmul__(self, scalar):
        return self.__mul__(scalar)
        
    def __neg__(self):
        if self.is_infinity():
            return self
        return ECPoint(self.x, -self.y % P_CURVE)
        
    def __sub__(self, other):
        return self + (-other)

INFINITY = ECPoint(None, None)
G = ECPoint(Gx, Gy)

class Ciphertext_EC:
    def __init__(self, c1: ECPoint, c2: ECPoint):
        self.c1 = c1
        self.c2 = c2

    def __repr__(self):
        return f"Ciphertext_EC(c1=({self.c1.x}, {self.c1.y}), c2=({self.c2.x}, {self.c2.y}))"
    
    def __add__(self, other):
        if not isinstance(other, Ciphertext_EC):
            return NotImplemented
        new_c1 = self.c1 + other.c1
        new_c2 = self.c2 + other.c2
        return Ciphertext_EC(new_c1, new_c2)
    
    def __sub__(self, other):
        if not isinstance(other, Ciphertext_EC):
            return NotImplemented
        new_c1 = self.c1 - other.c1
        new_c2 = self.c2 - other.c2
        return Ciphertext_EC(new_c1, new_c2)

    def __iter__(self):
        yield self.c1
        yield self.c2

class ElGamalParams_EC:
    def __init__(self):
        self.p = P_CURVE
        self.a = A
        self.b = B
        self.g = G
        self.q = Q

class ElGamalCrypto_EC:
    def __init__(self, params: ElGamalParams_EC):
        self.params = params
        self.K = 100 # Koblitz encoding factor
    
    def gen(self) -> Tuple[ECPoint, int]:
        sk = secrets.randbelow(self.params.q - 1) + 1
        pk = sk * self.params.g
        return (pk, sk)

    def _encode_to_point(self, m: int) -> ECPoint:
        if m >= self.params.p // self.K:
            raise ValueError("Message too large for encoding")
        for i in range(self.K):
            x = (m * self.K + i) % self.params.p
            z = (x**3 + self.params.a * x + self.params.b) % self.params.p
            
            # Since P = 3 (mod 4) for P-256, we can use fast square root
            if pow(z, (self.params.p - 1) // 2, self.params.p) == 1:
                y = pow(z, (self.params.p + 1) // 4, self.params.p)
                return ECPoint(x, y)
        raise ValueError("Failed to encode message to point")

    def _decode_from_point(self, pt: ECPoint) -> int:
        if pt.is_infinity():
            raise ValueError("Cannot decode infinity point")
        if not pt.is_on_curve():
            raise ValueError("Point is not on the curve")
        m_int = (pt.x % self.params.p) // self.K
        # Guard against cases where decoded value could be invalid
        if m_int >= self.params.p // self.K:
            raise ValueError("Decoded message is out of expected bounds")
        return m_int

    def enc(self, pk: ECPoint, m, r: int|None = None) -> Ciphertext_EC:
        if not pk.is_on_curve():
            raise ValueError("Public key must be on the curve")
            
        q = self.params.q

        if isinstance(m, list):
            m_int = perm_to_int(m)
        else:
            m_int = int(m)

        M = self._encode_to_point(m_int)
        
        if r is None:
            r = secrets.randbelow(q - 1) + 1

        c1 = r * self.params.g
        if c1.is_infinity():
            raise ValueError("Invalid randomness resulted in point at infinity")
            
        c2 = M + (r * pk)
        return Ciphertext_EC(c1, c2)

    def dec(self, sk: int, ciphertext: Ciphertext_EC) -> int:
        c1, c2 = ciphertext
        if not c1.is_on_curve() or not c2.is_on_curve():
            raise ValueError("Ciphertext points must be on the curve")
            
        S = sk * c1
        M = c2 - S
        return self._decode_from_point(M)

    def calculate_di_for_shamir(self, c1: ECPoint, share: Tuple[int, int]) -> ECPoint:
        # share is (x, y) where y is the share value
        return share[1] * c1

    def decrypt_for_shamir(self, shares, ciphertext: Ciphertext_EC, threshold: int):
        if threshold <= 0:
            raise ValueError("threshold must be a positive integer")
        if threshold > len(shares):
            raise ValueError("threshold cannot exceed number of shares")

        c1, c2 = ciphertext
        x_points, share_values = zip(*shares)

        # Convert secret shares to partial decryptions di = share_i * c1
        d_i_values = [self.calculate_di_for_shamir(c1, share) for share in shares]

        # Lagrange basis polynomial uses order q
        basis = [
            Shamir.lagrange_basis_at_zero(x_points, i, threshold, self.params.q)
            for i in range(threshold)
        ]

        # Sum of l_i * d_i
        S = ECPoint(None, None)
        for i in range(threshold):
            weighted_di = basis[i] * d_i_values[i]
            S = S + weighted_di

        M = c2 - S
        return self._decode_from_point(M)


if __name__ == "__main__":
    params = ElGamalParams_EC()
    crypto = ElGamalCrypto_EC(params)
    pk, sk = crypto.gen()
    
    msg = 42
    print(f"Original Message: {msg}")
    
    ctx = crypto.enc(pk, msg)
    print(f"Ciphertext: {ctx}")
    
    dec = crypto.dec(sk, ctx)
    print(f"Decrypted: {dec}")
    
    shares = Shamir.gen_shares(sk, n=5, t=3, fieldsize=params.q)
    print(f"Shares: {shares}")
    
    dec_t = crypto.decrypt_for_shamir(shares[:3], ctx, 3)
    print(f"Threshold Decrypted (from 3 shares): {dec_t}")
