import os
import Shamir
from consts import *
import random

Matrix = list[list[int]]

print_ballots = False

def build_matrix(priorities: list[int]) -> Matrix:
    size = len(priorities)
    matrix = [[0]*size for _ in range(size)]
    for row in range(size):
        for col in range(size):
            if priorities[col] == row:
                matrix[row][col] = 1
    return matrix                

def build_all_matrices(ballots: list[list[int]]) -> list[Matrix]:
    matrices = []
    for ballot in ballots:
        matrix = build_matrix(ballot)
        matrices.append(matrix)
    return matrices

def share_matrix(matrix: Matrix) -> list[Matrix]:
    size = len(matrix)
    share_matrices = [[[0]*size for _ in range(size)] for _ in range(NUM_PARTIES)]
    for row in range(size):
        for col in range(size):
            shares = gen_shares(matrix[row][col])
            for party in range(NUM_PARTIES):
                share_matrices[party][row][col] = shares[party]
    return share_matrices

def gen_rand_int(lower: int, upper: int) -> int:
    return random.randint(lower, upper)

def gen_shares(secret: int) -> list[int]:
    shares = [gen_rand_int(0, FIELD_SIZE-1) for _ in range(THRESHOLD-1)]
    last_share = (secret - sum(shares)) % FIELD_SIZE
    shares.append(last_share)
    return shares

def secret_share_matrices(matrices: list[Matrix]) -> list[list[Matrix]]:
    all_shared_matrices = []
    for matrix in matrices:
        shared_matrices = share_matrix(matrix)
        all_shared_matrices.append(shared_matrices)
    return all_shared_matrices

def reconstruct_matrix(shares: list[Matrix]) -> Matrix:
    size = len(shares[0])
    reconstructed_matrix = [[0]*size for _ in range(size)]
    for row in range(size):
        for col in range(size):
            share_list = []
            for party in range(NUM_PARTIES):
                share_list.append( (party+1, shares[party][row][col]) )
            secret = sum(shares) % FIELD_SIZE
            reconstructed_matrix[row][col] = secret
    return reconstructed_matrix

def gen_random_priorities(num_candidates: int, rank_all: bool = True) -> list[int]:
    priorities = list(range(num_candidates))
    random.shuffle(priorities)

    if not rank_all:
        cut_off = random.randint(1, num_candidates)
        priorities = priorities[:cut_off]
        priorities = priorities + [-1] * (num_candidates - cut_off)
    return priorities

def generate_ballots(num_ballots: int, num_candidates: int, rank_all: bool = True) -> list[list[int]]:
    ballots = []
    for _ in range(num_ballots):
        priorities = gen_random_priorities(num_candidates, rank_all)
        ballots.append(priorities)
    return ballots

def generate_blank_ballots(num_ballots: int, num_candidates: int) -> list[list[int]]:
    ballots = []
    for _ in range(num_ballots):
        priorities = [-1] * num_candidates
        ballots.append(priorities)
    return ballots

def simulate_election(ballots: list[list[int]]) -> int:
    # NOTE: There is a bug in this function.
    winner = None
    eliminated_candidates = {}

    while winner is None:
        print("New round of counting votes...")
        votes_in_round = {}
        for ballot in ballots:
            for cand in ballot:
                if cand in eliminated_candidates:
                    continue
                votes_in_round[cand] = votes_in_round.get(cand, 0) + 1
                break

        total_votes = sum(votes_in_round.values())
        for candidate, votes in votes_in_round.items():
            if votes > total_votes // 2:
                winner = candidate
                break
        
        if winner is not None:
            break
        min_votes = min(votes_in_round.values())
        for candidate, votes in sorted(votes_in_round.items(), key=lambda item: item[0]):
            if votes == min_votes:
                eliminated_candidates[candidate] = True 
                break
    return winner

def write_ballots_to_file(ballots: list[Matrix], party_id: int):
    file_name = f"Player-Data/matrix-P{party_id}-0"
    with open(file_name, 'a') as f:
        for ballot in ballots:
            for row in ballot:
                row_str = ' '.join(map(str, row))
                f.write(row_str + '\n')
            f.write('\n')  # Separate ballots by a blank line

def delete_existing_ballot_files(prefix: str):
    all_files = os.listdir("Player-Data/")
    for file_name in all_files:
        if file_name.startswith(prefix):
            os.remove(os.path.join("Player-Data/", file_name))

def write_all_ballots(ss_matrices: list[list[Matrix]]):
    delete_existing_ballot_files("matrix")
    for shared_matrices in ss_matrices:
        for party_id in range(NUM_PARTIES):
            write_ballots_to_file([shared_matrices[party_id]], party_id)

def main():
    NUM_REAL_VOTES = min(NUM_VOTES, NUM_VOTES)
    NUM_BLANK_VOTES = NUM_VOTES - NUM_REAL_VOTES
    
    ballots = generate_ballots(NUM_REAL_VOTES, NUM_CANDIDATES, rank_all=True)
    blank_ballots = generate_blank_ballots(NUM_BLANK_VOTES, NUM_CANDIDATES)
    ballots.extend(blank_ballots)
    matrices = build_all_matrices(ballots)
    if print_ballots:
        for matrix in matrices:
            print("Generated Matrix:")
            for row in matrix:
                print(row)
            print()
    secret_shared_matrices = secret_share_matrices(matrices)
        

    write_all_ballots(secret_shared_matrices)
    print("Ballots written to files.")
    print("Simulating election...")
    winner = simulate_election(ballots)
    print(f"The winner is candidate {winner}.")

if __name__ == "__main__":
    main()