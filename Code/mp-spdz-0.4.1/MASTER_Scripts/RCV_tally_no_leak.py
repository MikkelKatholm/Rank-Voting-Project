from Compiler.GC.types import *
from Compiler.types import *
from Compiler.library import *

from Compiler.util import if_else
from MASTER_Scripts.consts import *

program.use_edabit(True)


def initialize_active_candidates() -> Array:
    """ Initialize all candidates as active (1). 
    :return: A list of secret-shared integers indicating all candidates are active.
    """
    active_candidates = Array(NUM_CANDS, sint)
    active_candidates.assign_all(sint(1))
    return active_candidates


def get_highest_priority_from_ballot(ballot: Array) -> sint:
    return ballot[0]

def is_candidate_active(candidates, candidate_id) -> sint:
    """ Check if a candidate is active based on the active candidates array. 
    :param candidates: An array of secret-shared integers indicating which candidates are active.
    :param candidate_id: The ID of the candidate to check.
    :return: A secret-shared integer that is 1 if the candidate is active, 0 otherwise.
    """

    is_active = sint(0)
    for i in range(NUM_CANDS):
        is_active += (candidate_id == i) * candidates[i]
    return is_active

def get_round_votes(ballots: list[Array]) -> Array:
    """ Get the votes for the current round based on the active candidates. 
    :param ballots: A list of secret-shared ballot arrays.
    :return: An array of secret-shared integers representing the vote count for each candidate in the current round.
    """
    vote_vector = Array(NUM_CANDS, sint)
    vote_vector.assign_all(0)

    for ballot in ballots:
        highest_priority_candidate = get_highest_priority_from_ballot(ballot)


        for candidate_id in range(NUM_CANDS):
            is_vote_for_candidate = (highest_priority_candidate == candidate_id)
            vote_vector[candidate_id] += is_vote_for_candidate

    return vote_vector

def update_eliminated_candidates(vote_vector: Array, active_candidates: Array) -> Array:
    """ Update the active candidates array by eliminating the candidate(s) with the fewest votes. 
    :param vote_vector: An array of secret-shared integers representing the vote count for each candidate in the current round.
    :param active_candidates: An array of secret-shared integers indicating which candidates are currently active.
    :return: An updated array of secret-shared integers indicating which candidates are active after elimination.
    """
    large_num = sint(1000)
    adjusted_votes = Array(NUM_CANDS, sint)
    for i in range(NUM_CANDS):
        adjusted_votes[i] = vote_vector[i] + (1 - active_candidates[i]) * large_num

    min_votes = adjusted_votes[0]
    for candidate_id in range(1, NUM_CANDS):
        min_votes = if_else(adjusted_votes[candidate_id] < min_votes, adjusted_votes[candidate_id], min_votes)

    is_min = Array(NUM_CANDS, sint)
    for candidate_id in range(NUM_CANDS):
        is_min[candidate_id] = (adjusted_votes[candidate_id] == min_votes)

    random_scores = Array(NUM_CANDS, sint)
    for i in range(NUM_CANDS):
        random_scores[i] = sint.get_random_int(31)

    max_rand = sint(-1)
    elim_id = sint(-1)

    for i in range(NUM_CANDS):
        is_greater = (random_scores[i] > max_rand)
        is_new_elim = is_min[i] * is_greater
        max_rand = if_else(is_new_elim, random_scores[i], max_rand)
        elim_id = if_else(is_new_elim, sint(i), elim_id)

    for candidate_id in range(NUM_CANDS):
        is_eliminated = (elim_id == candidate_id)
        active_candidates[candidate_id] *= (1 - is_eliminated)

    return active_candidates    

def remove_eliminated_candidates(ballot: Array) -> Array:
    new_ballot = Array(len(ballot), sint)
    for i in range(len(ballot) - 1):
        new_ballot[i] = ballot[i + 1]
    new_ballot[len(ballot) - 1] = sint(-1)
    return new_ballot

def prep_ballots_for_next_round(ballots: list[Array], active_candidates: Array) -> list[Array]:
    updated_ballots = []
    for ballot in ballots:
        highest_priority_candidate = get_highest_priority_from_ballot(ballot)
        is_highest_candidate_active = is_candidate_active(active_candidates, highest_priority_candidate)
        updated_ballot = if_else(is_highest_candidate_active, ballot, remove_eliminated_candidates(ballot))
        updated_ballots.append(updated_ballot)
    return updated_ballots

def find_winner(active_candidates: Array) -> sint:
    """ The winner is the only remaining active candidate."""
    winner_id = sint(-1)
    for candidate_id in range(NUM_CANDS):
        winner_id = if_else(active_candidates[candidate_id] == sint(1), candidate_id, winner_id)
    return winner_id

def tally(ballots: list[Array]):
    """ Run the RCV protocol. 
    : param ballots: A list of secret-shared ballot matrices with the sbit type
    """

    active_candidates = initialize_active_candidates()
    

    for round in range(NUM_CANDS-1):
        vote_vector = get_round_votes(ballots)
        active_candidates = update_eliminated_candidates(vote_vector, active_candidates)
        ballots = prep_ballots_for_next_round(ballots, active_candidates)
    winner_id = find_winner(active_candidates)
    print_ln("🏆 Winner is candidate ID: %s", winner_id.reveal())
