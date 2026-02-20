import pytest
import random
import ElGamal
import Shamir
import consts
import math

class Test_ElGamal(): 
    @pytest.mark.parametrize("i", range(10))
    def test_encryption_roundtrip(self,i):
        params = ElGamal.ElGamalParams(ElGamal.bitLength)
        elgamal = ElGamal.ElGamalCrypto(params)

        pk, sk = elgamal.gen()  # fresh keypair each time
        m = random.randint(0, 1)  # valid message
        ciphertext = elgamal.enc(pk, m)
        decmsg = elgamal.dec(sk, ciphertext)
        assert decmsg == m


    def test_elgamal_minus(self):
        params = ElGamal.ElGamalParams(ElGamal.bitLength)
        elgamal = ElGamal.ElGamalCrypto(params)

        pk, sk = elgamal.gen()  # fresh keypair each time
        five= elgamal.enc(pk, 5)
        three = elgamal.enc(pk, 3)
        
        # Compute ciphertext for 5 - 3 = 2

        diff_ciphertext = five - three 

        decrypted_diff = elgamal.dec(sk, diff_ciphertext)
        assert decrypted_diff == 2


    def test_sum(self):
        params = ElGamal.ElGamalParams(ElGamal.bitLength)
        elgamal = ElGamal.ElGamalCrypto(params)

        pk, sk = elgamal.gen()  # fresh keypair each time
        nums_to_sum = [random.randint(0, 10) for _ in range(5)]
        ciphertexts = [elgamal.enc(pk, m) for m in nums_to_sum]

        # Compute ciphertext for the sum
        sum_ciphertext = sum(ciphertexts[1:], ciphertexts[0])  # Start with the first ciphertext and add the rest

        decrypted_sum = elgamal.dec(sk, sum_ciphertext)
        assert decrypted_sum == sum(nums_to_sum)
        

    def test_product(self):
        params = ElGamal.ElGamalParams(ElGamal.bitLength)
        elgamal = ElGamal.ElGamalCrypto(params)

        pk, sk = elgamal.gen()  # fresh keypair each time
        nums_to_mult = [random.randint(1, 10) for _ in range(3)]
        ciphertexts = [elgamal.enc(pk, m) for m in nums_to_mult]

        result = math.prod(nums_to_mult)

        # Compute ciphertext for the product
        product_ciphertext = elgamal.enc(pk, 1)  # Start with encryption of 1 (multiplicative identity)
        for ct in ciphertexts:
            product_ciphertext *= ct

        decrypted_product = elgamal.dec(sk, product_ciphertext)
        assert decrypted_product == result

class Test_Shamir():
    @pytest.mark.parametrize("i", range(10))
    def test_shamir_roundtrip(self, i):
        n = 5
        t = 3
        fieldsize = 1613
        secret = random.randint(0, fieldsize - 1)
        shares = Shamir.gen_shares(secret, n, t, fieldsize)
        selected_shares = random.sample(shares, t)
        reconstructed_secret = Shamir.reconstruct_secret(selected_shares, fieldsize)
        assert reconstructed_secret == secret

class Test_ElGamal_Shamir_Integration():
    @pytest.mark.parametrize("i", range(10))
    def test_integration(self, i):
        # Setup ElGamal
        bit_length = 12
        params = ElGamal.ElGamalParams(bit_length)
        elgamal = ElGamal.ElGamalCrypto(params)
        pk, sk = elgamal.gen()

        # Setup Shamir
        n = 5
        t = 3
        secret_to_share = random.randint(0, 10)

        key_shares = Shamir.gen_shares(sk, n, t, params.q)

        # Encrypt a message
        ciphertext = elgamal.enc(pk, secret_to_share)

        c1, c2 = ciphertext.c1, ciphertext.c2
        assert c1 != 0 and c2 != 0
        # Decrypt using Shamir shares
        selected_shares = random.sample(key_shares, t)
        decrypted_message = elgamal.decrypt_for_shamir(selected_shares, ciphertext, t)
        assert decrypted_message == secret_to_share