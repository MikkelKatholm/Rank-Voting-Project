from Compiler.GC.types import *
from Compiler.types import *
from Compiler.library import *

from Compiler.util import if_else
from MASTER_Scripts.consts import *
from MASTER_Scripts.RCV_tally_no_leak import get_round_votes as get_round_votes_no_leak

program.use_edabit(True)    # type: ignore
program.bit_length = 12     # type: ignore
sint.bit_length = 12        # type: ignore


def get_round_votes(ballots: list[Array], active_candidates: Array) -> Array:
    """ Tally votes for the current round using MPC.
    active_candidates is a plain Python list of 0/1 public ints at this point.
    """
    vote_vector = get_round_votes_no_leak(ballots, active_candidates)
    vote_list = vote_vector.reveal_list()    # type: ignore
    vote_array = Array(NUM_CANDS, cint)
    for i in range(NUM_CANDS):
        vote_array[i] = cint(vote_list[i])
    return vote_array


def initialize_active_candidates() -> Array:
    active_candidates = Array(NUM_CANDS, cint)
    active_candidates.assign_all(1)
    return active_candidates


def check_for_winner(vote_vector: Array, active_candidates: Array) -> cint:
    votes_needed = cint(NUM_CANDS // 2)
    winner_ID = cint(-1)

    @for_range(NUM_CANDS)
    def _(i):
        @if_(vote_vector[i] > votes_needed)
        def _():
            winner_ID.update(cint(i))
    
    #Check for last round. If only one candidate left, they win by default even without majority.
    active_count = cint(0)
    last_active_id = cint(-1)
    @if_(sum(active_candidates) == cint(1))
    def _():
        @for_range(NUM_CANDS)
        def _(i):
            @if_(active_candidates[i] == cint(1))
            def _():
                last_active_id.update(cint(i))
        winner_ID.update(last_active_id)
    return winner_ID


def find_candidates_with_fewest_votes(vote_vector: Array, active_candidates: Array) -> cint:
    min_votes = cint(NUM_CANDS + 1)
    elim_id = cint(-1)
    @for_range(NUM_CANDS)
    def _(i):
        @if_(active_candidates[i] == cint(1))
        def _():
            @if_(vote_vector[i] < min_votes)
            def _():
                min_votes.update(vote_vector[i])
                elim_id.update(cint(i))
    return elim_id
    
def eliminate_candidate(elim_id: cint, active_candidates: Array):
    @for_range(NUM_CANDS)
    def _(i):
        @if_(i == elim_id)
        def _():
            active_candidates[i].update(cint(0))

def tally(ballots: list[Array]):
    # active_candidates and vote counts are plain Python — fully public after reveal
    active_candidates = initialize_active_candidates()

    winner = cint(-1)

    for round in range(NUM_CANDS - 1):
        @if_(winner == cint(-1))
        def _():
             print_ln("🔄 Starting round %s", round + 1)
             vote_vector = get_round_votes(ballots, active_candidates)
             print_ln("📊 Current round votes: %s", vote_vector)  # type: ignore
             winner.update(check_for_winner(vote_vector, active_candidates))
             @if_(winner == cint(-1))
             def _():
                 elim_id = find_candidates_with_fewest_votes(vote_vector, active_candidates)
                 print_ln("🚫 Eliminating candidate with ID: %s", elim_id)
                 eliminate_candidate(elim_id, active_candidates)
    return winner