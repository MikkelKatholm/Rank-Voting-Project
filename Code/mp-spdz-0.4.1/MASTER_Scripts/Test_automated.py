import pytest
import os
from dotenv import load_dotenv, set_key
from pathlib import Path
import subprocess
import re

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
CONSTS_FILE = SCRIPT_DIR / "consts.env"

import sys
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

############################################
#        Helper types and functions        #
############################################

Ballot = list[list[int]]
Candidate = int
Candidates = list[Candidate]

ballot = [
    [0, 1, 0],
    [1, 0, 0],
    [0, 0, 1],
]

ballots = [
    [
        [0, 1, 0],
        [1, 0, 0],
        [0, 0, 1],
    ],
    [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
    ],
    [
        [0, 0, 1],
        [0, 1, 0],
        [1, 0, 0],
    ]
]

def sum_cols(ballot: Ballot) -> list[int]:
    return [sum(row[i] for row in ballot) for i in range(len(ballot[0]))]

def initialize_candidates(num_cands: int) -> Candidates:
    return [1] * num_cands

def eliminate_candidate(candidates: Candidates, candidate_to_eliminate: Candidate) -> Candidates:
    candidates[candidate_to_eliminate] = 0
    return candidates

def who_to_eliminate(candidates: Candidates, round_results: list[int]) -> Candidate:
    min_votes = float('inf')
    candidate_to_eliminate = -1
    for i, votes in enumerate(round_results):
        if candidates[i] == 1 and votes < min_votes:

            min_votes = votes
            candidate_to_eliminate = i
    print(f"Candidate to eliminate: {candidate_to_eliminate} with {min_votes} votes")
    return candidate_to_eliminate

def update_active_candidates(candidates: Candidates, round_results: list[int]) -> Candidates:
    candidate_to_eliminate = who_to_eliminate(candidates, round_results)
    return eliminate_candidate(candidates, candidate_to_eliminate)

def tally_round(ballots: list[Ballot], candidates: Candidates) -> list[int]:
    result = [0] * len(candidates)
    for ballot in ballots:
        for p in range(len(ballot[0])):
            # Find which candidate has priority p
            col_values = [ballot[c][p] for c in range(len(ballot))]
            if 1 in col_values:
                first_choice = col_values.index(1)
                result[first_choice] += 1
                break
    print(f"        Round results:     {result}")
    print(f"        Active candidates: {candidates}")
    return result

def remove_eliminated_candidates(ballots: list[Ballot], candidates: Candidates) -> list[Ballot]:
    new_ballots = []
    for ballot in ballots:
        new_ballot = []
        for c, row in enumerate(ballot):
            if candidates[c] == 1:
                new_ballot.append(list(row))
            else:
                new_ballot.append([0] * len(row))
        new_ballots.append(new_ballot)
    return new_ballots

def simulate_election(ballots: list[Ballot], num_cands: int) -> Candidate:
    candidates = initialize_candidates(num_cands)

    for _ in range(len(candidates) - 1):
        ballots = remove_eliminated_candidates(ballots, candidates)
        round_res = tally_round(ballots, candidates)
        candidates = update_active_candidates(candidates, round_res)
    winner = candidates.index(1)
    return winner

def update_consts(consts: dict):
    if not CONSTS_FILE.exists():
        raise FileNotFoundError(f"No consts.env file found at {CONSTS_FILE}")

    load_dotenv(CONSTS_FILE, override=True)

    for key, value in consts.items():
        set_key(str(CONSTS_FILE), key, str(value), quote_mode="never")

    load_dotenv(CONSTS_FILE, override=True)

def get_winner_from_output(output: str) -> Candidate:
    match = re.search(r"🏆 Winner is candidate ID: (\d+)", output)
    if match:
        return int(match.group(1))
    else:
        raise ValueError("Winner not found in output")

def load_ballots_from_folder(folder_path: Path) -> list[Ballot]:
    ballots: list[Ballot] = []
    for file_path in folder_path.iterdir():
        if file_path.name.endswith("_ballot.txt") and file_path.is_file():
            ballot: Ballot = []
            with file_path.open('r') as f:
                for line in f:
                    parts = line.split()
                    if not parts:
                        continue
                    row = [int(x) for x in parts]
                    ballot.append(row)
            ballots.append(ballot)
    return ballots

def run_test(num_servers: int, num_clients: int, num_cands: int, leak_version: int) -> bool:
    consts = {
        "NUM_SERVERS": num_servers,
        "NUM_VOTERS": num_clients,
        "NUM_CANDS": num_cands,
        "RUN_LEAK_VERSION": leak_version
    }
    update_consts(consts)

    try:
        result = subprocess.run(
            ["bash", str(SCRIPT_DIR / "run_RCV.sh"), "-g", "true"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        
        winner = get_winner_from_output(result.stdout)

        ballots = load_ballots_from_folder(SCRIPT_DIR / "Ballots")
        expected_winner = simulate_election(ballots, num_cands)

        return winner == expected_winner

    except subprocess.CalledProcessError as e:
        print(f"Error running test: {e.stderr}")
        return False

class TestAutomated:
    def test_run(self):
        num_cands = 3
        num_servers = 2
        num_clients = 2
        leak_version = 1

        success = run_test(num_servers, num_clients, num_cands, leak_version)
        assert success, "Test failed after multiple attempts"    

    @pytest.mark.parametrize("num_voters", [2, 5, 10])
    @pytest.mark.parametrize("leak_version", [0, 1])
    def test_voter_configs(self, num_voters, leak_version):
        num_servers = 2
        num_cands = 3
        result = run_test(num_servers, num_voters, num_cands, leak_version)
        assert result, f"Test failed for {num_voters} voters and leak version {leak_version}"

    @pytest.mark.parametrize("num_cands", [3, 5, 10])
    @pytest.mark.parametrize("leak_version", [0, 1])
    def test_candidate_configs(self, num_cands, leak_version):
        num_servers = 2
        num_voters = 2
        result = run_test(num_servers, num_voters, num_cands, leak_version)
        assert result, f"Test failed for {num_cands} candidates and leak version {leak_version}"

        

if __name__ == "__main__":
    ballots = load_ballots_from_folder(SCRIPT_DIR / "Ballots")
    winner = simulate_election(ballots, 3)
    print(f"Simulated winner: {winner}")