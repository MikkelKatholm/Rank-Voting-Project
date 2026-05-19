from Compiler.GC.types import *
from Compiler.types import *
from Compiler.library import *
from MASTER_Scripts.RCV_tally_no_leak import compute_round_ballot, sb_vector_to_sint_vector

program.use_edabit(True)

from MASTER_Scripts.consts import *

def initialize_active_candidates() -> Array:
    """ Initialize all candidates as active (1). 
    :return: A list of clear bits indicating all candidates are active.
    """
    active_candidates = Array(NUM_CANDS, cbit)
    active_candidates.assign_all(cbit(1))
    return active_candidates

def update_active_candidates(round_result: list[cint], active_candidates: Array) -> Array:
    """ Update the list of active candidates based on the round result.
    :param round_result: A list of integers (cint) representing the number of votes each candidate received in the current round
    :param active_candidates: A list of 0/1 clear bits indicating active candidates
    :return: The updated list of active candidates
    """
    smallest_index = cint(-1)
    smallest_value = cint(NUM_CLIENTS + 1)

    @for_range(NUM_CANDS)
    def _(i):
        @if_(active_candidates[i] != cint(0))
        def _():
            @if_(round_result[i] < smallest_value)
            def _():
                smallest_value.update(round_result[i])
                smallest_index.update(i)

    active_candidates[smallest_index] = cbits(0)
    return active_candidates

def majority_check(round_result: list[cint]) -> cint:
    """ Check if any candidate has a majority of the votes in the current round.
    :param round_result: A list of integers (cint) representing the number of votes each candidate received in the current round
    :return: The index of the winning candidate if there is a majority, otherwise -1
    """
    votes_needed = (NUM_CLIENTS // 2)
    winner = cint(-1)

    @for_range(NUM_CANDS)
    def _(i):
        @if_(round_result[i] > votes_needed)
        def _():
            winner.update(i)
    
    return winner
    
def winner_last_round(active_candidates: Array) -> cint:
    """ If we are in the last round, return the index of the remaining candidate as the winner.
    :param active_candidates: A list of 0/1 clear bits indicating active candidates
    :return: The index of the winning candidate
    """
    winner = cint(-1)

    @for_range(NUM_CANDS)
    def _(i):
        @if_(active_candidates[i] == cbit(1))
        def _():
            winner.update(i)
    
    return winner


def tally(ballots: list[Matrix]):
    """ Run the RCV protocol. """
    active_candidates = initialize_active_candidates()                                                             
    winner = cint(-1)

    for round in range(NUM_CANDS - 1):
        @if_(winner == cint(-1))
        def _():
            round_result = Array(NUM_CANDS, sint)
            round_result.assign_all(sint(0))
            for ballot in range(NUM_CLIENTS):
                round_result = sb_vector_to_sint_vector(compute_round_ballot(ballots[ballot], active_candidates))
                for cand_id in range(NUM_CANDS):
                    round_result[cand_id] = round_result[cand_id] + round_result[cand_id]
            clear_round_result = [round_result[i].reveal() for i in range(NUM_CANDS)]
            clear_round_result_array = Array(NUM_CANDS, cint)
            clear_round_result_array.assign(clear_round_result)
            active_candidates.assign(update_active_candidates(clear_round_result_array, active_candidates))
            winner.update(majority_check(clear_round_result_array))

    @if_(winner == cint(-1))
    def _():
        winner.update(winner_last_round(active_candidates))

    
    return winner