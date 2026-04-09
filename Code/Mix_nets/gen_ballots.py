import os
from Consts import BALLOT_FILE, BALLOT_LINE_LENGTH, NUM_CANDS
import numpy as np

def generate_fresh_ballots(num_ballots: int):
    # Remove existing ballot file if it exists
    if os.path.exists(BALLOT_FILE):
        os.remove(BALLOT_FILE)

    with open(BALLOT_FILE, "w") as f:
        for i in range(num_ballots):
            perm = np.random.permutation(NUM_CANDS)
            line = ' '.join(map(str, perm))
            
            if len(line) > BALLOT_LINE_LENGTH - 1:
                raise ValueError("BALLOT_LINE_LENGTH is too short for the generated ballot string.")
                
            padded_line = line.ljust(BALLOT_LINE_LENGTH - 1) + '\n'
            f.write(padded_line)

if __name__ == "__main__":
    generate_fresh_ballots(10)