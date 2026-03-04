import os
from consts import BALLOT_FOLDER, NUM_CANDS
import numpy as np


def generate_fresh_ballots(num_ballots: int):
    # Create ballot folder if it doesn't exist
    if not os.path.exists(BALLOT_FOLDER):
        os.makedirs(BALLOT_FOLDER)
    
    # Deleta all existing ballots
    for filename in os.listdir(BALLOT_FOLDER):
        file_path = os.path.join(BALLOT_FOLDER, filename)
        
        if os.path.isfile(file_path):
            os.remove(file_path)

    for i in range(num_ballots):
        perm = np.random.permutation(NUM_CANDS)
        perm = [x + 1 for x in perm]  # Convert to 1-based indexing


        with open(f"{BALLOT_FOLDER}/{i}_ballot", "w") as f:
            f.write(' '.join(map(str, perm)) + '\n')

if __name__ == "__main__":
    generate_fresh_ballots(10)