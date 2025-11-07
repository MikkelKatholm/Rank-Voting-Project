import os
import Shamir
from consts import *

Matrix = list[list[int]]

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

def share_matrix(matrix: Matrix, ss_scheme: Shamir.Shamir) -> list[Matrix]:
    size = len(matrix)
    share_matrices = [[[0]*size for _ in range(size)] for _ in range(NUM_PARTIES)]

    for row in range(size):
        for col in range(size):
            shares = ss_scheme.gen_shares(matrix[row][col])
            for party in range(NUM_PARTIES):
                share_matrices[party][row][col] = shares[party][1]
    return share_matrices

def secret_share_matrices(matrices: list[Matrix], ss_scheme: Shamir.Shamir) -> list[list[Matrix]]:
    all_shared_matrices = []
    for matrix in matrices:
        shared_matrices = share_matrix(matrix, ss_scheme)
        all_shared_matrices.append(shared_matrices)
    return all_shared_matrices

def reconstruct_matrix(shares: list[Matrix], ss_scheme: Shamir.Shamir) -> Matrix:
    size = len(shares[0])
    reconstructed_matrix = [[0]*size for _ in range(size)]

    for row in range(size):
        for col in range(size):
            share_list = []
            for party in range(NUM_PARTIES):
                share_list.append( (party+1, shares[party][row][col]) )
            secret = ss_scheme.reconstruct_secrets(share_list, 1)
            reconstructed_matrix[row][col] = secret[0]
    return reconstructed_matrix

def gen_random_priorities(num_candidates: int) -> list[int]:
    from random import shuffle
    priorities = list(range(num_candidates))
    shuffle(priorities)
    return priorities

def generate_ballots(num_ballots: int, num_candidates: int) -> list[list[int]]:
    ballots = []
    for _ in range(num_ballots):
        priorities = gen_random_priorities(num_candidates)
        ballots.append(priorities)
    return ballots

def simulate_election(ballots: list[list[int]]) -> int:
    winner = None
    eliminated_candidates = {}

    while winner is None:
        votes_in_round = {}
        for ballot in ballots:
            for prio in ballot:
                if prio in eliminated_candidates:
                    continue
                votes_in_round[prio] = votes_in_round.get(prio, 0) + 1
                break

        total_votes = sum(votes_in_round.values())
        for candidate, votes in votes_in_round.items():
            if votes > total_votes / 2:
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
    file_name = f"My_scripts/Player-Data/matrix-P{party_id}-0"
    with open(file_name, 'a') as f:
        for ballot in ballots:
            for row in ballot:
                row_str = ' '.join(map(str, row))
                f.write(row_str + '\n')
            f.write('\n')  # Separate ballots by a blank line

def delete_existing_ballot_files(prefix: str):
    all_files = os.listdir("My_scripts/Player-Data/")
    for file_name in all_files:
        if file_name.startswith(prefix):
            os.remove(os.path.join("My_scripts/Player-Data/", file_name))

def write_all_ballots(ss_matrices: list[list[Matrix]]):
    delete_existing_ballot_files("matrix")
    for shared_matrices in ss_matrices:
        for party_id in range(NUM_PARTIES):
            write_ballots_to_file([shared_matrices[party_id]], party_id)
    

if __name__ == "__main__":
    ballots = generate_ballots(NUM_VOTES, NUM_CANDIDATES)
    matrices = build_all_matrices(ballots)
    ss_scheme = Shamir.Shamir(FIELD_SIZE, NUM_SHARES, THRESHOLD)
    secret_shared_matrices = secret_share_matrices(matrices, ss_scheme)    

    write_all_ballots(secret_shared_matrices)
    print("Ballots written to files.")
    print("Simulating election...")
    winner = simulate_election(ballots)
    print(f"The winner is candidate {winner}.")