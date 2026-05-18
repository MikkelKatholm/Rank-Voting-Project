from Compiler.GC.types import *
from Compiler.types import *
from Compiler.library import *

from Compiler.util import if_else
from MASTER_Scripts.consts import *

program.use_edabit(True)    # type: ignore
program.bit_length = 12     # type: ignore
sint.bit_length = 12        # type: ignore

# Largest value that fits in bit_length=12 signed: 2^11 - 1 = 2047
# Used as sentinel for inactive candidates in the min tree
LARGE_NUM = 2**11 - 1


def initialize_active_candidates() -> Array:
    active_candidates = Array(NUM_CANDS, sint)
    active_candidates.assign_all(sint(1))
    return active_candidates


def get_highest_priority_from_ballot(ballot: Array) -> sint:
    return ballot[0]


def get_round_votes(ballots, active_candidates) -> Array:
    vote_vector = Array(NUM_CANDS, sint)
    vote_vector.assign_all(0)
    for ballot in ballots:
        # Walk the ballot and find the first active candidate
        # using a "found" latch — pure multiplications, no comparisons
        found = sint(0)
        for pos in range(NUM_CANDS):
            candidate = ballot[pos]
            # is this position's candidate still active?
            is_active = sint(0)
            for i in range(NUM_CANDS):
                is_active += (candidate == i) * active_candidates[i]  # sint==int, free
            # only count this if we haven't found one yet
            counts = is_active * (1 - found)
            for i in range(NUM_CANDS):
                vote_vector[i] += (candidate == i) * counts  # sint==int, free
            found = found + counts
    return vote_vector


def update_eliminated_candidates(vote_vector: Array, active_candidates: Array):

    adjusted_votes = Array(NUM_CANDS, sint)
    for i in range(NUM_CANDS):
        adjusted_votes[i] = vote_vector[i] + (1 - active_candidates[i]) * LARGE_NUM

    min_votes = adjusted_votes[0]
    for i in range(1, NUM_CANDS):
        min_votes = if_else(adjusted_votes[i] < min_votes, adjusted_votes[i], min_votes)

    # Lowest-index candidate at min votes wins — sequential if_else chain
    # but stable and proven to work with the SPDZ2k OT layer
    elim_id = sint(-1)
    for i in range(NUM_CANDS):
        is_min = (adjusted_votes[i] == min_votes)
        is_first = (elim_id == sint(-1))
        elim_id = if_else(is_min * is_first, sint(i), elim_id)

    # Build elim_flags as a one-hot vector from elim_id
    # so prep_ballots can use sint==int comparisons instead of sint==sint
    elim_flags = Array(NUM_CANDS, sint)
    for i in range(NUM_CANDS):
        elim_flags[i] = (elim_id == i)  # sint==int, free

    for i in range(NUM_CANDS):
        active_candidates[i] = active_candidates[i] * (1 - elim_flags[i])

    return active_candidates


def remove_eliminated_candidates(ballot: Array) -> Array:
    new_ballot = Array(len(ballot), sint)
    for i in range(len(ballot) - 1):
        new_ballot[i] = ballot[i + 1]
    new_ballot[len(ballot) - 1] = sint(-1)
    return new_ballot


def find_winner(active_candidates: Array) -> sint:
    # active_candidates[i] == sint(1) is sint==int — no bit decomposition.
    winner_id = sint(-1)
    for candidate_id in range(NUM_CANDS):
        winner_id = if_else(active_candidates[candidate_id] == sint(1), candidate_id, winner_id)
    return winner_id    # type: ignore


def tally(ballots: list[Array]):
    active_candidates = initialize_active_candidates()

    for round in range(NUM_CANDS - 1):
        vote_vector = get_round_votes(ballots, active_candidates)
        active_candidates = update_eliminated_candidates(vote_vector, active_candidates)

    winner_id = find_winner(active_candidates)
    return winner_id