from Compiler.GC.types import *
from Compiler.types import *
from Compiler.library import *

from Compiler.util import if_else
from MASTER_Scripts.consts import *

program.use_edabit(True)

def initialize_active_candidates() -> Array:
    """ Initialize all candidates as active (1). 
    :return: A list of clear bits indicating all candidates are active.
    """
    active_candidates = Array(NUM_CANDS, sb)
    active_candidates.assign_all(sb(1))
    return active_candidates


def compute_round_ballot(ballot: Matrix, active_candidates: Array) -> list[sb]:
    """ For the given ballot, compute a list of sbits indicating which candidate receives the vote in the current round.
    :param ballot: A NUM_CANDS x NUM_CANDS secret-shared ballot matrix. 
    :param active_candidates: A list of 0/1 sbits indicating active candidates.
    :return: A list of sbits indicating which candidate receives the vote in the current round.
    """
    res = [sb(0) for _ in range(NUM_CANDS)]
    is_highest_found = sb(0)

    for col in range(NUM_CANDS):
        one_in_col = sb(0)
        for row in range(NUM_CANDS):
            is_highest_available = ballot[row][col] & active_candidates[row] & ~is_highest_found    # Will only be 1 if ballot[row][col] is 1, the candidate is active, and we haven't found a higher priority candidate yet
            res[row] = res[row] ^ is_highest_available                                              # Attribute the vote to this candidate if it's the highest available
            one_in_col = one_in_col ^ is_highest_available                                          # Track if we found a candidate in this column
        is_highest_found = is_highest_found ^ one_in_col                                            # Once we find a candidate in this column, we set is_highest_found to 1 so that lower priority candidates won't get the vote
    return res

def sb_vector_to_sint_vector(sb_vector: list[sb]) -> list[sint]:
    """ Convert a list of secret-shared bits to a list of secret-shared integers.
    
    :param sb_vector: A list of secret-shared bits.
    :return: A list of secret-shared integers representing the same values as the input bits.
    """
    return [sb_to_sint(bit) for bit in sb_vector]

def sb_to_sint(sb_bit: sb) -> sint:
    """ Convert a secret-shared bit to a secret-shared integer.
    
    :param sb_bit: A secret-shared bit.
    :return: A secret-shared integer representing the same value as the input bit.
    """
    return sint(sb_bit)[0]

def update_active_candidates(round_result: list[sint], active_candidates: Array) -> Array:
    """ Update the list of active candidates based on the round result.
    :param round_result: A list of secret-shared integers representing the number of votes each candidate received in the current round.
    :param active_candidates: A list of 0/1 sbits indicating active candidates.
    :return: An updated list of active candidates where candidates with the least votes are set to inactive (0).
    """

    high_value = NUM_CLIENTS + 1
    adjusted_votes = [None] * NUM_CANDS
    for cand_id in range(NUM_CANDS):
        adjusted_votes[cand_id] = round_result[cand_id] + (sint(1) - sb_to_sint(active_candidates[cand_id])) * high_value
    
    min_votes = adjusted_votes[0]
    elim_flag = Array(NUM_CANDS, sint)
    elim_flag[0] = sint(1)

    for i in range(1, NUM_CANDS):
        is_smaller = adjusted_votes[i] < min_votes
        min_votes = if_else(is_smaller, adjusted_votes[i], min_votes)
        
        for j in range(i):
            elim_flag[j] = elim_flag[j] * (1 - is_smaller)
        elim_flag[i] = is_smaller

    for cand_id in range(NUM_CANDS):
        active_candidates[cand_id] = active_candidates[cand_id] & ~sb(elim_flag[cand_id])

    return active_candidates



def tally(ballots: list[Matrix]):
    """ Run the RCV protocol. 
    :param ballots: A list of secret-shared ballot matrices with the sbit type
    """

    active_candidates = initialize_active_candidates()
    for round in range(NUM_CANDS - 1):
        round_result = Array(NUM_CANDS, sint)
        round_result.assign_all(sint(0))
        for ballot in range(NUM_CLIENTS):
            ballot_result = sb_vector_to_sint_vector(compute_round_ballot(ballots[ballot], active_candidates))
            for cand_id in range(NUM_CANDS):
                round_result[cand_id] = round_result[cand_id] + ballot_result[cand_id]
        new_active_candidates = update_active_candidates(round_result, active_candidates)
        #print_ln("Round %s result: %s", round, [i.reveal() for i in round_result])
        #print_ln("Active candidates after round %s: %s", round, new_active_candidates.reveal_list())
        active_candidates.assign(new_active_candidates)
            
    clear_cands = active_candidates.reveal_list()
    clear_cands_array = Array(NUM_CANDS, cbit)
    clear_cands_array.assign(clear_cands)
    winner = cint(-1)

    @for_range(NUM_CANDS)
    def _(i):
        winner_is_i = clear_cands_array[i] == cbit(1)
        @if_(winner_is_i)
        def _():
            winner.update(i)

    return winner