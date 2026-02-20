import ElGamal
import Shamir
from consts import *

def setup_ttp(n: int, t: int, bit_length: int) -> tuple[ElGamal.ElGamalParams, Shares, PublicKey]:
    # 1. Generate ElGamal parameters and a key pair for the TTP
    params = ElGamal.ElGamalParams(bit_length)
    elgamal = ElGamal.ElGamalCrypto(params)
    keyPair = elgamal.gen()
    pk, sk = keyPair.pk, keyPair.sk

    # 2. Generate Shamir shares of the TTP's secret key
    key_shares = Shamir.gen_shares(sk, n, t, params.q)

    return params, key_shares, pk
