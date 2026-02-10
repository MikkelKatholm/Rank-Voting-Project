import numpy as np
from dotenv import load_dotenv
import os

# Load from the same directory as this script
script_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(script_dir, "consts.env"))
ballot_folder = os.getenv("BALLOT_FOLDER")
num_voters = int(os.getenv("NUM_VOTERS"))
num_cands = int(os.getenv("NUM_CANDS"))

def generate_random_ballot(num_cands):
    perm = np.random.permutation(num_cands)
    ballot = np.eye(num_cands, dtype=int)[perm]
    return ballot

def write_to_file(ballot, filename):
    with open(filename, 'w') as f:
        for row in ballot:
            f.write(' '.join(map(str, row)) + '\n')

def generate_all_ballots(num_voters, num_cands):
    for i in range(num_voters):
        ballot = generate_random_ballot(num_cands)
        filename = os.path.join(ballot_folder, f"{i}_ballot.txt")
        write_to_file(ballot, filename)

def clear_ballots():
    if os.path.exists(ballot_folder):
        for filename in os.listdir(ballot_folder):
            file_path = os.path.join(ballot_folder, filename)
            if os.path.isfile(file_path):
                os.remove(file_path) 

def main():
    if not os.path.exists(ballot_folder):
        os.makedirs(ballot_folder)
    clear_ballots()
    generate_all_ballots(num_voters, num_cands)

if __name__ == "__main__":
    main()