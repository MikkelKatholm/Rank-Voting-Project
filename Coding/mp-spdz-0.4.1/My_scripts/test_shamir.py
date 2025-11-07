import pytest

import Shamir
from consts import *

class Test_Shamir:
    def setup_method(self):
        self.Shamir = Shamir.Shamir(1613, NUM_SHARES, THRESHOLD)

    @pytest.mark.parametrize("secrets", [1234, 0, 1])
    def test_split_and_reconstruct(self, secrets):
        shares = self.Shamir.gen_shares(secrets)
        print("Shares:", shares)
        reconstructed = self.Shamir.reconstruct_secrets(shares[:self.Shamir.threshold], 1)
        assert reconstructed[0] == secrets

