import os
from consts import BALLOT_FOLDER, NUM_CANDS
import numpy as np


def generate_fresh_ballots(num_ballots: int):
    # Deleta all existing ballots
    for filename in os.listdir(BALLOT_FOLDER):
        file_path = os.path.join(BALLOT_FOLDER, filename)
        
        if os.path.isfile(file_path):
            os.remove(file_path)

    for i in range(num_ballots):
        perm = np.random.permutation(NUM_CANDS)
        ballot = np.eye(NUM_CANDS, dtype=int)[perm]

        with open(f"{BALLOT_FOLDER}/{i}_ballot", "w") as f:
            for row in ballot:
                f.write(' '.join(map(str, row)) + '\n')

if __name__ == "__main__":
    generate_fresh_ballots(10)