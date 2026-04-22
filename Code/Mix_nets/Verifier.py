from Consts import *
from ElGamal import ElGamalParams
from Shamir import div_mod
from math import prod
import ElGamal_Eplitic
from typing import Any

class Verifier:
    def __init__(self, elgamal_params: Any, public_key: Any):
        self.params = elgamal_params
        self.public_key = public_key
        self.generator = elgamal_params.g

    def sum_ec(self, points):
        result = ElGamal_Eplitic.INFINITY
        for pt in points:
            if result.is_infinity():
                result = pt
            else:
                result = result + pt
        return result

    def verify_shuffle_elgamal_pairs(self, input_ciphertexts: list[Any], output_ciphertexts: list[Any], transcript: dict):
        p = self.params.p
        q = self.params.q
        g = self.generator
        Gamma = transcript["Gamma"]
        sigma = transcript["sigma"]
        W = transcript["W"]
        D = transcript["D"]
        k = len(input_ciphertexts)
        # Step 1: compute challenge
        rho = []
        for i in range(k):
            rho.append(hash([Gamma, transcript["A"][i], transcript["C"][i], transcript["U"][i], transcript["W"][i], transcript["Lambda1"], transcript["Lambda2"], input_ciphertexts[i], output_ciphertexts[i]], q))
        
        if USE_ELLIPTIC_CURVE:
            B = [((rho[i] % q) * g) - transcript["U"][i] for i in range(k)]
        else:
            B = [div_mod(pow(g, rho[i], p), transcript["U"][i], p) for i in range(k)]

        lambda_challenge = hash([Gamma, transcript["A"], transcript["C"], transcript["U"], transcript["W"], transcript["Lambda1"], transcript["Lambda2"], input_ciphertexts, output_ciphertexts, transcript["D"]], q)
        
        if USE_ELLIPTIC_CURVE:
            X = [transcript["A"][i] + ((lambda_challenge % q) * B[i]) for i in range(k)]
            Y = [transcript["C"][i] + ((lambda_challenge % q) * transcript["D"][i]) for i in range(k)]
            
            Phi1 = self.sum_ec([(sigma[i] * output_ciphertexts[i].c1) + (((-rho[i]) % q) * input_ciphertexts[i].c1) for i in range(k)])
            Phi2 = self.sum_ec([(sigma[i] * output_ciphertexts[i].c2) + (((-rho[i]) % q) * input_ciphertexts[i].c2) for i in range(k)])
        else:
            X = [(transcript["A"][i] * pow(B[i], lambda_challenge, p)) % p for i in range(k)]
            Y = [(transcript["C"][i] * pow(transcript["D"][i], lambda_challenge, p)) % p for i in range(k)]

            Phi1 = (prod([pow(output_ciphertexts[i].c1, sigma[i], p) * pow(input_ciphertexts[i].c1, (-rho[i]) % q, p) for i in range(k)])) % p
            Phi2 = (prod([pow(output_ciphertexts[i].c2, sigma[i], p) * pow(input_ciphertexts[i].c2, (-rho[i]) % q, p) for i in range(k)])) % p

        # Step 2: check Simple shuffle proof
        if not self.verify_simple_shuffle_proof(X, Y, transcript):
            raise ValueError("The proof is invalid: Simple shuffle proof failed.")
        
        # Step 3: check the equations
        for i in range(k):
            if USE_ELLIPTIC_CURVE:
                left_side = sigma[i] * Gamma
                right_side = W[i] + D[i]
            else:
                left_side = pow(Gamma, sigma[i], p)
                right_side = (W[i] * D[i]) % p
                
            if left_side != right_side:
                raise ValueError(f"The proof is invalid: Equation 1 does not hold for i={i}.")
        
        if USE_ELLIPTIC_CURVE:
            left_side_Phi1 = transcript["Lambda1"] + (transcript["tau"] * g)
            if left_side_Phi1 != Phi1:
                raise ValueError("The proof is invalid: Equation 2 does not hold for Phi1.")
            left_side_Phi2 = transcript["Lambda2"] + (transcript["tau"] * self.public_key)
            if left_side_Phi2 != Phi2:
                raise ValueError("The proof is invalid: Equation 2 does not hold for Phi2.")
        else:
            left_side_Phi1 = (transcript["Lambda1"] * pow(g, transcript["tau"], p)) % p
            if left_side_Phi1 != Phi1:
                raise ValueError("The proof is invalid: Equation 2 does not hold for Phi1.")
            left_side_Phi2 = (transcript["Lambda2"] * pow(self.public_key, transcript["tau"], p)) % p
            if left_side_Phi2 != Phi2:
                raise ValueError("The proof is invalid: Equation 2 does not hold for Phi2.")
        
        return True

    def verify_simple_shuffle_proof(self, X, Y, full_transcript) -> bool|ValueError:
        transcript = full_transcript["ss_transcript"]
        p = self.params.p
        q = self.params.q
        g = self.generator
        Theta = transcript["Theta"] 
        Gamma = transcript["Gamma"]
        k = len(X)

        # Step 1: compute challenge
        t = hash([self.generator, Gamma, X, Y], q)
        c = hash([self.generator, Gamma, X, Y, Theta], q)

        # Step 2: check proof
        if t != transcript["t"]:
            raise ValueError("The proof is invalid: t' does not match t in the transcript.")
        if c != transcript["c"]:
            raise ValueError("The proof is invalid: c' does not match c in the transcript.")
        
        # Check the equations
        if USE_ELLIPTIC_CURVE:
            U = ((-t) % q) * g
            W = ((-t) % q) * Gamma
            X_hat = [X[i] + U for i in range(k)]
            Y_hat = [Y[i] + W for i in range(k)]
        else:
            U = pow(g, -t, p)
            W = pow(Gamma, -t, p)
            X_hat = [(X[i] * U) % p for i in range(k)]
            Y_hat = [(Y[i] * W) % p for i in range(k)]

        alpha = transcript["alpha"]
        
        if USE_ELLIPTIC_CURVE:
            right_side1 = (c * X_hat[0]) + (((-alpha[0]) % q) * Y_hat[0])
            if Theta[0] != right_side1:
                raise ValueError("The proof is invalid: Theta[0] does not match the right side of the equation.")
                
            for i in range(1, k):
                right_side = (alpha[i-1] * X_hat[i]) + (((-alpha[i]) % q) * Y_hat[i])
                if Theta[i] != right_side:
                    raise ValueError(f"The proof is invalid: Theta[{i}] does not match the right side of the equation.")
                    
            for i in range(k, 2*k - 2):
                right_side = (alpha[i-1] * Gamma) + (((-alpha[i]) % q) * g)
                if Theta[i] != right_side:
                    raise ValueError(f"The proof is invalid: Theta[{i}] does not match the right side of the equation.")
                    
            right_side2k_1 = (alpha[2*k - 2] * Gamma) + (((-c) % q) * g)
            if Theta[2*k - 1] != right_side2k_1:
                raise ValueError("The proof is invalid: Theta[2k-1] does not match the right side of the equation.")
        else:
            right_side1 = (pow(X_hat[0], c, p) * pow(Y_hat[0], (-alpha[0]) % q, p)) % p
            
            if Theta[0] !=  right_side1:
                raise ValueError("The proof is invalid: Theta[0] does not match the right side of the equation.")
            for i in range(1, k):
                right_side = (pow(X_hat[i], alpha[i-1], p) * pow(Y_hat[i], (-alpha[i]) % q, p)) % p
                if Theta[i] != right_side:
                    raise ValueError(f"The proof is invalid: Theta[{i}] does not match the right side of the equation.")
            for i in range(k, 2*k - 2):
                right_side = (pow(Gamma, alpha[i-1], p) * pow(g, (-alpha[i]) % q, p)) % p
                if Theta[i] != right_side:
                    raise ValueError(f"The proof is invalid: Theta[{i}] does not match the right side of the equation.")
            right_side2k_1 = (pow(Gamma, alpha[2*k - 2], p) * pow(g, - c, p)) % p
            if Theta[2*k - 1] != right_side2k_1:
                raise ValueError("The proof is invalid: Theta[2k-1] does not match the right side of the equation.")
        return True
