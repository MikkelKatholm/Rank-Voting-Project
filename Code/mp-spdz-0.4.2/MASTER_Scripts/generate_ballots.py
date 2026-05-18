import numpy as np
import random
from dotenv import load_dotenv
import os

# Load from the same directory as this script
script_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(script_dir, "consts.env"))
BALLOT_FOLDER = os.getenv("BALLOT_FOLDER")
NUM_VOTERS = int(os.getenv("NUM_VOTERS"))
NUM_CANDS = int(os.getenv("NUM_CANDS"))
PARTIAL_BALLOT_PERCENTAGE = float(os.getenv("PARTIAL_BALLOT_PERCENTAGE"))


def is_partial_ballot():
    return random.random() < PARTIAL_BALLOT_PERCENTAGE

def generate_random_ballot(num_cands):
    perm = np.random.permutation(num_cands)
    if is_partial_ballot():
        # Randomly decide how many candidates to include in the ballot (at least 1). Pad the rest with -1.
        num_included = random.randint(1, num_cands)
        perm[num_included:] = -1
    return perm

def write_to_file(ballot, filename):
    with open(filename, 'w') as f:
        f.write(' '.join(map(str, ballot)) + '\n')

def generate_all_ballots(num_voters, num_cands):
    for i in range(num_voters):
        ballot = generate_random_ballot(num_cands)
        filename = os.path.join(BALLOT_FOLDER, f"{i}_ballot.txt")
        write_to_file(ballot, filename)

def clear_ballots():
    if os.path.exists(BALLOT_FOLDER):
        for filename in os.listdir(BALLOT_FOLDER):
            file_path = os.path.join(BALLOT_FOLDER, filename)
            if os.path.isfile(file_path):
                os.remove(file_path) 

def main():
    if not os.path.exists(BALLOT_FOLDER):
        os.makedirs(BALLOT_FOLDER)
    clear_ballots()
    generate_all_ballots(NUM_VOTERS, NUM_CANDS)
    
if __name__ == "__main__":
    main()