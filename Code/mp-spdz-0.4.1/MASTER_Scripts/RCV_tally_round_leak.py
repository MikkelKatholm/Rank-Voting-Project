from Compiler.GC.types import *
from Compiler.types import *
from Compiler.library import *
from MASTER_Scripts.RCV_tally_no_leak import remove_non_highest_priority, remove_eliminated_candidates, sum_rows

program.use_edabit(True)

from MASTER_Scripts.consts import *

def eliminate_candidate(active_candidates: Array, cand_id: cint) -> Array:
    """ Eliminate a candidate by setting their active flag to 0
    
    :param active_candidates: A list of 0/1 clear bits indicating active candidates.
    :param cand_id: The candidate ID to eliminate.
    :return: Updated active_candidates list with the specified candidate eliminated.
    """
    active_candidates[cand_id] = cbits(0)

    return active_candidates

def sum_vectors(vectors: list[list[sint]]) -> Array:

    result = Array(NUM_CANDS, sint)
    result.assign_all(cint(0))
    for vector in vectors:
        for i in range(NUM_CANDS):
            result[i] += vector[i]

    res_clear = result.reveal_list()
    res_array = Array(NUM_CANDS, cint)
    res_array.assign_vector(res_clear)
    return res_array

def initialize_active_candidates() -> Array:
    """ Initialize all candidates as active (1). 
    :return: A list of clear bits indicating all candidates are active.
    """
    active_candidates = Array(NUM_CANDS, cbits)
    active_candidates.assign_all(cbits(1))
    return active_candidates

def reveal_winner(winner_id: sint) -> int:
    """ Reveal the winning candidate ID to all parties.
    :param winner_id: The candidate ID (sint) to reveal.
    :return: The revealed candidate ID as an integer.
    """
    return winner_id.reveal()

def update_eliminated_candidates(vector: list[sint], active_candidates: Array) -> Array:
    """ Find the candidate with the lowest votes among active candidates.

    If there is a tie for lowest votes, the candidate with the lowest index is eliminated.

    :param vector: List of ints representing candidate vote counts.
    :param active_candidates: A list of 0/1 clear bits indicating active candidates.
    :return: The updated active_candidates list with the lowest vote candidate eliminated. 
    """

    smallest_index = cint(-1)
    smallest_value = cint(NUM_CLIENTS + 1)

    @for_range(NUM_CANDS)
    def _(i):
        @if_(active_candidates[i] != 0)
        def _():
            @if_(vector[i] < smallest_value)
            def _():
                smallest_value.update(vector[i])
                smallest_index.update(i)
    
    return eliminate_candidate(active_candidates, smallest_index)

def copy_matrix(matrix: Matrix) -> Matrix:
    """ Create a deep copy of a secret-shared matrix.
    
    :param matrix: A secret-shared matrix to copy.
    :return: A new secret-shared matrix that is a copy of the input matrix.
    """
    new_m = Matrix(NUM_CANDS, NUM_CANDS, value_type=sb)
    @for_range(NUM_CANDS)
    def _(i):
        @for_range(NUM_CANDS)
        def _(j):
            new_m[i][j] = matrix[i][j]
    return new_m

def find_winner_leak(vector: Array, last_round: bool) -> cint:
    """ Finds the winner.
    
    :param vector: A revealed integer array representing candidate vote counts.
    :param last_round: A boolean indicating if this is the last round.
    :return: The winning candidate ID as a cint.
    """

    # If last round, find and reveal the winner
    winner_id = cint(-1)

    @if_(last_round)
    def _():
        @for_range(NUM_CANDS)
        def _(i):
            @if_(vector[i] > cint(0))
            def _():
                winner_id.update(cint(i))
    
    # check for majority
    votes_needed = cint(NUM_CLIENTS // 2)

    @for_range(NUM_CANDS)
    def _(i):
        @if_(vector[i] > votes_needed)
        def _():
            winner_id.update(cint(i))
        return winner_id

    return winner_id

def tally(ballots: list[Matrix]):
    """ Run the RCV protocol. """
    active_candidates = initialize_active_candidates()                                                             
    winner = cint(-1)

    # Do a round
    for round in range(NUM_CANDS):
        # Run round only if no winner yet, if is_leaking is false run all rounds
        @if_e(winner == cint(-1))
        def _():
            round_ballots: list[Matrix] = [copy_matrix(b) for b in ballots]                                             
            row_sums_array: list[list[sint]] = []
            for ballot_id in range(NUM_CLIENTS):
                round_ballots[ballot_id] = remove_eliminated_candidates(round_ballots[ballot_id], active_candidates)    
                round_ballots[ballot_id] = remove_non_highest_priority(round_ballots[ballot_id])                        
                row_sums = sum_rows(round_ballots[ballot_id])
                row_sums_array.append(row_sums)
            vote_vector = sum_vectors(row_sums_array)
            active_candidates.assign(update_eliminated_candidates(vote_vector, active_candidates))

            winner_id = find_winner_leak(vote_vector, round == NUM_CANDS - 1)
            winner.update(winner_id)
        @else_
        def _():
            print_ln(" ")
            break_loop
    
    return winner