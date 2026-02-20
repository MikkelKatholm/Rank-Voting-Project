from consts import *
import random
import Shamir
import sympy as sp

class ElGamalParams:
    def __init__(self, bits: int):
        self.p = self._get_prime(bits)
        self.q = (self.p - 1) // 2
        g = self._find_primitive_root(self.p)
        self.g = pow(g, 2, self.p)  # Make sure generator has order q

    @staticmethod
    def _get_prime(bits: int) -> int:
        """Generate a safe prime of given bit length."""
        while True:
            prime_candidate = sp.randprime(2 ** (bits - 1), 2 ** bits)
            if not isinstance(prime_candidate, int):
                raise ValueError("Generated prime is not an integer.")
            if sp.isprime((prime_candidate - 1) // 2):
                return prime_candidate

    @staticmethod
    def _find_primitive_root(p: int) -> int:
        """Find a primitive root modulo p."""
        if p == 2:
            return 1
        p1 = 2
        p2 = (p - 1) // p1
        while True:
            g = random.SystemRandom().randint(2, p - 1)
            if pow(g, (p - 1) // p1, p) != 1:
                if pow(g, (p - 1) // p2, p) != 1:
                    return g

class ElGamalCrypto:
    def __init__(self, params: ElGamalParams):
        self.params = params
    
    def gen(self) -> KeyPair:
        """Generate the sk at random and calculate pk"""
        sk = random.SystemRandom().randint(1, self.params.q - 1)
        pk = pow(self.params.g, sk, self.params.p)
        return KeyPair(pk, sk)

    def enc(self, pk: PublicKey, m: Message) -> Ciphertext:
        """Encrypt a message m using pk.
        
        :param pk: The public key to encrypt with
        :param m: The message to encrypt (must be 0 or 1)
        :return: A tuple (c1, c2) = (g^r mod p, (g^m * pk^r) mod p) where r is a random integer in [1, q-1]
        """
        q = self.params.q
        p = self.params.p
        g = self.params.g

        r = random.SystemRandom().randint(1, q - 1)

        c1 = pow(g, r, p)
        c2 = (pow(g, m, p) * pow(pk, r, p)) % p
        return Ciphertext(c1, c2, self.params)

    def dec(self, sk: SecretKey, ciphertext: Ciphertext) -> Message:
        """Decrypt a ciphertext using sk."""
        p = self.params.p
        c1, c2 = ciphertext
        x = pow(c1, sk, p)

        gm = c2 * pow(x, -1, p) % p

        for m in range(self.params.q):
            if pow(self.params.g, m, p) == gm:
                return m
        raise ValueError("Decryption failed: message not found.")


    def decrypt_for_shamir(self, shares, ciphertext, threshold):
        if threshold <= 0:
            raise ValueError("threshold must be a positive integer")

        if threshold > len(shares):
            raise ValueError("threshold cannot exceed number of shares")

        c1, c2 = ciphertext
        x_points, share_values = zip(*shares)

        # Convert secret shares to partial decryptions di = c1^{share_i} (mod p)
        d_i_values = [pow(c1, share, self.params.p) for share in share_values]

        # Lagrange basis polynomial uses prime q
        basis = [
            Shamir.lagrange_basis_at_zero(x_points, i, threshold, self.params.q)
            for i in range(threshold)
        ]

        d_i_power_basis = [
            pow(d_i_values[i], basis[i], self.params.p) for i in range(threshold)
        ]

        d = 1
        for value in d_i_power_basis:
            d = (d * value) % self.params.p

        gm = (c2 * pow(d, -1, self.params.p)) % self.params.p

        for m in range(self.params.q):
            if m % 50_000 == 0:
                print(f"Trying m={m} of {self.params.q}...")

            if pow(self.params.g, m, self.params.p) == gm:
                return m
        raise ValueError("Decryption failed")

    def calculate_di_for_shamir(self, c1, share):
        return pow(c1, share[1], self.params.p)



