import math
import hashlib
from Shamir import div_mod
from Crypto.Random import random as crypto_random
from Consts import *
from math import prod

class Prover:
    def __init__(self, Beta: list[int], perm: list[int], input_ciphertexts: list[Ciphertext], output_ciphertexts: list[Ciphertext], params: ElGamal.ElGamalParams, public_key: PublicKey):
        self.Beta = Beta
        self.perm = perm
        self.input_ciphertexts = input_ciphertexts
        self.output_ciphertexts = output_ciphertexts
        self.params = params
        self.generator = params.g
        self.public_key = public_key
        self.k = len(input_ciphertexts)
        self.inv_perm = [0 for _ in range(self.k)]
        for i, num in enumerate(self.perm):
            self.inv_perm[num] = i

    def shuffle_elgamal_pairs(self):
        # Step 1: sample stuff
        u = [self._get_from_Zq() for _ in range(self.k)]
        w = [self._get_from_Zq() for _ in range(self.k)]

        tau_0 = self._get_from_Zq()
        nu = self._get_from_Zqstar()
        gamma = self._get_from_Zqstar()
        a = self._unique_from_Zqstar(self.k)

        print(f"len(a): {len(a)}")
        print(f"len(perm): {len(self.perm)}")

        # Step 2: compute stuff
        Gamma = pow(self.generator, gamma, self.params.p)
        A = [pow(self.generator, a[i], self.params.p) for i in range(self.k)]
        a_pi = [a[self.perm[i]] for i in range(self.k)]
        C = [pow(Gamma, a_pi[i], self.params.p) for i in range(self.k)]
        U = [pow(self.generator, u[i], self.params.p) for i in range(self.k)]
        W = [pow(Gamma, w[i], self.params.p) for i in range(self.k)]
        

        exp = (tau_0 + sum([w[i]*self.Beta[i] for i in range(self.k)])) % self.params.q         # NOTE: Might need to remove mod 
        Lambda1 = (pow(self.generator, exp, self.params.p) * prod([pow(self.input_ciphertexts[i].c1, (w[self.inv_perm[i]] - u[i]) % self.params.q, self.params.p) for i in range(self.k)])) % self.params.p
        Lambda2 = (pow(self.public_key, exp, self.params.p) * prod([pow(self.input_ciphertexts[i].c2, (w[self.inv_perm[i]] - u[i]) % self.params.q, self.params.p) for i in range(self.k)])) % self.params.p

        # Step 3: compute challenge
        rho = []
        for i in range(self.k):
            rho.append(hash([Gamma, A[i], C[i], U[i], W[i], Lambda1, Lambda2, self.input_ciphertexts[i], self.output_ciphertexts[i]], self.params.q))

        b = [rho[i] - u[i] for i in range(self.k)]
        d = [gamma * b[self.perm[i]] for i in range(self.k)]
        D = [pow(self.generator, d[i], self.params.p) for i in range(self.k)]

        # Step 4: Compute hash
        lambda_challenge = hash([Gamma, A, C, U, W, Lambda1, Lambda2, self.input_ciphertexts, self.output_ciphertexts, D], self.params.q)

        # Step 5: Compute some skrammel
        r = [a[i] + lambda_challenge * b[i] for i in range(self.k)]
        s = [gamma * r[self.perm[i]] for i in range(self.k)]
        sigma = [w[i] + b[self.perm[i]] for i in range(self.k)]
        tau = (- tau_0 + sum([b[i] * self.Beta[i] for i in range(self.k)])) % self.params.q

        # Step 6: Run
        X = [pow(self.generator, r[i], self.params.p) for i in range(self.k)]
        Y = [pow(self.generator, s[i], self.params.p) for i in range(self.k)]

        mini_transcript = self.simple_k_shuffle(Gamma, X,Y, gamma, r, s)

        # Step 7: output transcript
        transcript = {
            "Gamma": Gamma,
            "A": A,
            "C": C,
            "U": U,
            "W": W,
            "Lambda1": Lambda1,
            "Lambda2": Lambda2,
            "input_ciphertexts": self.input_ciphertexts,
            "output_ciphertexts": self.output_ciphertexts,
            "D": D,
            "tau": tau,
            "sigma": sigma,
            "ss_transcript": mini_transcript
        }
        return transcript


    def simple_k_shuffle(self, Gamma: int, X: list[int], Y: list[int], gamma: int, x: list[int], y: list[int]) -> dict:
        # Step 1: compute challenge
        t = hash([self.generator, Gamma, X, Y], self.params.q)
        
        # Step 2: Make hats
        x_hat = [(x[i] - t) % self.params.q for i in range(self.k)]
        y_hat = [(y[i] - gamma * t) % self.params.q for i in range(self.k)]

        # Step 3: 
        theta = [self._get_from_Zq() for _ in range(2*self.k - 1)]
        Theta = [pow(self.generator, (-theta[0] * y_hat[0]) % self.params.q, self.params.p)]                                                     # Theta_0
        Theta += [pow(self.generator, (theta[i-1] * x_hat[i] - theta[i] * y_hat[i]) % self.params.q, self.params.p) for i in range(1, self.k)]   # Theta_1 -> Theta_(k-1)
        Theta += [pow(self.generator, (gamma * theta[i - 1] - theta[i]) % self.params.q, self.params.p) for i in range(self.k, 2*self.k - 1)]    # Theta_k -> Theta_(2k-2)
        Theta += [pow(self.generator, (gamma * theta[2 * self.k - 2]) % self.params.q, self.params.p)]                                           # Theta_(2k-1)

        # Step 4: Compute hash
        c = hash([self.generator, Gamma, X, Y, Theta], self.params.q)

        # Step 5: Compute some skrammel
        prod0 = div_mod(x_hat[0], y_hat[0], self.params.q)
        prods = [prod0]
        for i in range(1, self.k):
            prod = (div_mod(x_hat[i], y_hat[i], self.params.q) * prods[i-1]) % self.params.q
            prods.append(prod)        


        alpha = [(theta[i] + c * prods[i]) % self.params.q for i in range(self.k)]
        alpha += [(theta[i] + c * pow(gamma, i - 2*self.k + 1, self.params.q)) % self.params.q for i in range(self.k, 2*self.k - 1)]

        # Step 6: output transcript
        transcript = {
            "t": t,
            "c": c,
            "generator": self.generator,
            "Gamma": Gamma,
            "Theta": Theta,
            "alpha": alpha
        }
        return transcript


    def _unique_from_Zqstar(self, n):
        seen = set()
        while len(seen) < n:
            x = self._get_from_Zqstar()
            if x not in seen:
                seen.add(x)
        return list(seen)

    def _get_from_Zq(self):
        return crypto_random.randint(0, self.params.q - 1)
    
    def _get_from_Zqstar(self):
        while True:
            x = crypto_random.randint(1, self.params.q - 1)
            if math.gcd(x, self.params.q) == 1:
                return x