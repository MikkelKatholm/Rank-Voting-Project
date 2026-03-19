from Consts import *
from ElGamal import ElGamalParams
from Shamir import div_mod
from math import prod

class Verifier:
    def __init__(self, elgamal_params: ElGamalParams, Gamma: int, input_ciphertexts: list[Ciphertext], output_ciphertexts: list[Ciphertext], public_key: PublicKey, transcript, ):
        self.params = elgamal_params
        self.Gamma = Gamma
        self.input_ciphertexts = input_ciphertexts
        self.output_ciphertexts = output_ciphertexts
        self.public_key = public_key
        self.transcript = transcript
        self.generator = elgamal_params.g
        self.k = len(input_ciphertexts)

    def verify_shuffle_elgamal_pairs(self):
        transcript = self.transcript
        sigma = transcript["sigma"]
        W = transcript["W"]
        D = transcript["D"]
        # Step 1: compute challenge
        rho = []
        for i in range(self.k):
            rho.append(hash([self.Gamma, transcript["A"][i], transcript["C"][i], transcript["U"][i], transcript["W"][i], transcript["Lambda1"], transcript["Lambda2"], self.input_ciphertexts[i], self.output_ciphertexts[i]], self.params.q))
        
        B = [div_mod(pow(self.generator, rho[i], self.params.p), transcript["U"][i], self.params.p) for i in range(self.k)]

        lambda_challenge = hash([self.Gamma, transcript["A"], transcript["C"], transcript["U"], transcript["W"], transcript["Lambda1"], transcript["Lambda2"], self.input_ciphertexts, self.output_ciphertexts, transcript["D"]], self.params.q)
        
        X = [transcript["A"][i] * pow(transcript["B"][i], lambda_challenge, self.params.p) % self.params.p for i in range(self.k)]
        Y = [transcript["C"][i] * pow(transcript["D"][i], lambda_challenge, self.params.p) % self.params.p for i in range(self.k)]

        Phi1 = prod([pow(self.output_ciphertexts[i].c1, sigma[i], self.params.p) * pow(self.input_ciphertexts[i].c1, -rho[i], self.params.p) for i in range(self.k)]) % self.params.p
        Phi2 = prod([pow(self.output_ciphertexts[i].c2, sigma[i], self.params.p) * pow(self.input_ciphertexts[i].c2, -rho[i], self.params.p) for i in range(self.k)]) % self.params.p

        # Step 2: check Simple shuffle proof
        if not self.verify_simple_shuffle_proof(X, Y):
            raise ValueError("The proof is invalid: Simple shuffle proof failed.")
        
        # Step 3: check the equations
        for i in range(self.k):
            left_side = pow(self.Gamma, sigma[i], self.params.p)
            right_side = (W[i] * D[i]) % self.params.p
            if left_side != right_side:
                raise ValueError(f"The proof is invalid: Equation 1 does not hold for i={i}.")
        
        left_side_Phi1 = transcript["Lambda1"] * pow(self.generator, transcript["tau"], self.params.p) % self.params.p
        if left_side_Phi1 != Phi1:
            raise ValueError("The proof is invalid: Equation 2 does not hold for Phi1.")
        left_side_Phi2 = transcript["Lambda2"] * pow(self.public_key, transcript["tau"], self.params.p) % self.params.p
        if left_side_Phi2 != Phi2:
            raise ValueError("The proof is invalid: Equation 2 does not hold for Phi2.")
        
        return True

    def verify_simple_shuffle_proof(self, X, Y) -> bool|ValueError:
        transcript = self.transcript["ss_transcript"]
        Theta = transcript["Theta"] 
        
        # Step 1: compute challenge
        t = hash([self.generator, self.Gamma, X, Y], self.params.q)
        c = hash([self.generator, self.Gamma, X, Y, Theta], self.params.q)

        # Step 2: check proof
        if t != transcript["t"]:
            raise ValueError("The proof is invalid: t' does not match t in the transcript.")
        if c != transcript["c"]:
            raise ValueError("The proof is invalid: c' does not match c in the transcript.")
        
        # Check the equations
        U = pow(self.generator, -t, self.params.p)
        W = pow(self.Gamma, -t, self.params.p)
        X_hat = [X[i] * U for i in range(self.k)]
        Y_hat = [Y[i] * W for i in range(self.k)]


        alpha = transcript["alpha"]
        right_side1 = pow(X_hat[0], c, self.params.p) * pow(Y_hat[0], - alpha[0], self.params.p) % self.params.p
        if Theta[0] !=  right_side1:
            raise ValueError("The proof is invalid: Theta[0] does not match the right side of the equation.")
        for i in range(1, self.k):
            right_side = pow(X_hat[i], alpha[i-1], self.params.p) * pow(Y_hat[i], - alpha[i], self.params.p) % self.params.p
            if Theta[i] != right_side:
                raise ValueError(f"The proof is invalid: Theta[{i}] does not match the right side of the equation.")
        for i in range(self.k, 2*self.k - 2):
            right_side = pow(self.Gamma, alpha[i-1], self.params.p) * pow(self.generator, - alpha[i], self.params.p) % self.params.p
            if Theta[i] != right_side:
                raise ValueError(f"The proof is invalid: Theta[{i}] does not match the right side of the equation.")
        right_side2k_1 = pow(self.Gamma, alpha[2*self.k - 2], self.params.p) * pow(self.generator, - c, self.params.p) % self.params.p
        if Theta[2*self.k - 1] != right_side2k_1:
            raise ValueError("The proof is invalid: Theta[2k-1] does not match the right side of the equation.")
        
        return True