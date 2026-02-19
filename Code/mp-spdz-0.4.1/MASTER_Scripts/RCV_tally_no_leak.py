from Compiler.GC.types import *
from Compiler.types import *
from Compiler.library import *

from MASTER_Scripts.consts import *



def remove_eliminated_candidates(ballot: Matrix, active_candidates: Array) -> Matrix:
    """ Remove eliminated candidates from the ballot matrix. 
    
    :param ballot: A NUM_CANDS x NUM_CANDS secret-shared ballot matrix.
    :param active_candidates: A list of 0/1 sbits indicating active candidates.
    :return: A modified ballot matrix with eliminated candidates removed.
    """

    for row in range(NUM_CANDS):
        for col in range(NUM_CANDS):
            ballot[row][col] = ballot[row][col] & active_candidates[row]
    return ballot

def remove_non_highest_priority(ballot: Matrix) -> Matrix:
    """ Remove non-highest priority candidates from the ballot matrix.
    
    :param ballot: A NUM_CANDS x NUM_CANDS secret-shared ballot matrix.
    :return: A modified ballot matrix with only the highest priority candidate retained.

    Example:
    >>> remove_non_highest_priority(ballot)
        If the ballot matrix is:
           [[0, 0, 0]  # Candidate 0 is eliminated
            [0, 0, 1]  # Candidate 1 has priority 2
            [1, 0, 0]] # Candidate 2 has priority 0
        Then the resulting ballot matrix will be:
            [[0, 0, 0]  # Candidate 0 is eliminated
             [0, 0, 0]  # Candidate 1 is not highest priority
             [1, 0, 0]] # Candidate 2 is highest priority
    """


    found_highest = sb(1)
    @for_range(NUM_CANDS)
    def _(col):
        @for_range(NUM_CANDS)
        def _(row):
            is_highest = ballot[row][col] & (found_highest)
            ballot[row][col] = is_highest
            found_highest.update(found_highest ^ is_highest)

    return ballot

def eliminate_candidate(active_candidates: Array, cand_id: sint) -> Array:
    """ Eliminate a candidate by setting their active flag to 0
    
    :param active_candidates: A list of 0/1 sbits indicating active candidates.
    :param cand_id: The candidate ID to eliminate.
    :return: Updated active_candidates list with the specified candidate eliminated.
    """
    @for_range(NUM_CANDS)
    def _(i):
        ci = sint(i)
        condition = sb((ci == cand_id))
        active_candidates[i] = condition.if_else(sb(0), active_candidates[i])
    return active_candidates

def initialize_active_candidates() -> Array:
    """ Initialize all candidates as active (1). 
    :return: A list of clear bits indicating all candidates are active.
    """
    active_candidates = Array(NUM_CANDS, sb)
    active_candidates.assign_all(sb(1))
    return active_candidates

def sum_rows(ballot: Matrix) -> sbitintvec:
    """ Sum each row of the ballot matrix.
    
    :param ballot: A NUM_CANDS x NUM_CANDS secret-shared ballot matrix.
    :return: An array of secret-shared integers representing the sum of each row.
    """

    # get rows as list of sbits
    rows_as_lists = []
    for row in range(NUM_CANDS):
        row_list = []
        for col in range(NUM_CANDS):
            row_list.append(ballot[col][row])
        rows_as_lists.append(row_list)

    summed_list = siv([sb(0) for _ in range(NUM_CANDS)])
    for row in range(NUM_CANDS):
        row_vector = siv(rows_as_lists[row])
        summed_list = (summed_list + row_vector)
    return summed_list


def sum_vectors(vectors: list[sbitintvec]) -> Array:
    """ Sum a list of secret-shared bit arrays element-wise.
    
    :param vectors: A list of secret-shared bits arrays.
    :return: A single secret-shared integers array representing the element-wise sum.
    
    # Example:
    >>> sum_vectors([Array([1,0,1]), Array([0,1,1]), Array([1,1,0])])
        returns Array([2,2,2])
    """
    result = siv([sb(0) for _ in range(NUM_CANDS)])
    for v in vectors:
        result = (result + v)

    as_array = Array(NUM_CANDS, sint)                     # Works if type is sint. Find workaround please
    as_array.assign_vector(result)

    return as_array

def majority(vector: Array) -> tuple[sint, Array]:
    """ Determine if any candidate has a majority and return the winner.
    :param vector: A secret-shared integer array representing candidate vote counts.
    :return: A tuple (has_majority, input) where has_majority is a secret-shared bit indicating if a candidate has majority, and winner_vector is a secret-shared bit array indicating the winning candidate.
    """
    has_majority = sint(0)
    @for_range(NUM_CANDS)
    def _(i): 
        condition = (vector[i] > sint(NUM_CLIENTS // 2))
        has_majority = condition.if_else(has_majority + sint(1), has_majority + sint(0))

    return has_majority, vector

def find_winner(vector: Array) -> sint:
    """ Find the candidate with the highest votes.
    :param vector: A secret-shared integer array representing candidate vote counts.
    :return: The candidate ID (sint) with the highest votes.
    """
 
    winner_id = sint(-1)
 
    @for_range(NUM_CANDS)
    def _(i):
        #is_winner = (vector[i] > sint(NUM_CLIENTS // 2))
        is_winner = (vector[i] != cint(0))  # Since we only call this in the last round where one candidate must win
        winner_id.update(is_winner.if_else(cint(i), winner_id))

    return winner_id

def update_eliminated_candidates(vector: Array, active_candidates: Array) -> Array:
    """ Find the candidate with the lowest votes among active candidates.

    If there is a tie for lowest votes, the candidate with the lowest index is eliminated.

    :param vector: List of sint representing candidate vote counts.
    :param active_candidates: A list of 0/1 sbits indicating active candidates.
    :return: The updated active_candidates list with the lowest vote candidate eliminated. 
    """

    smallest_index = sint(-1)
    smallest_value = sint(NUM_CLIENTS + 1)

    @for_range(NUM_CANDS)
    def _(i):
        active = sint(active_candidates[i])[0]
        adjusted_value = vector[i] + (sint(1) - active) * sint(NUM_CLIENTS + 1)
        is_smallest = (adjusted_value < smallest_value)
        smallest_value.update(is_smallest.if_else(adjusted_value, smallest_value))
        smallest_index.update(is_smallest.if_else(sint(i), smallest_index))
    
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

def tally(ballots: list[Matrix]):
    """ Run the RCV protocol. """

    active_candidates = initialize_active_candidates()
    winner = sint(-1)                                                                                                   

    # Do a round
    for round in range(NUM_CANDS):
        round_ballots: list[Matrix] = [copy_matrix(b) for b in ballots]
        row_sums_array: list[sbitintvec] = []                                                                       
        for ballot_id in range(NUM_CLIENTS):
            round_ballots[ballot_id] = remove_eliminated_candidates(round_ballots[ballot_id], active_candidates)
            round_ballots[ballot_id] = remove_non_highest_priority(round_ballots[ballot_id])                        
            row_sums = sum_rows(round_ballots[ballot_id])
            row_sums_array.append(row_sums)
        vote_vector = sum_vectors(row_sums_array)
        active_candidates.assign(update_eliminated_candidates(vote_vector, active_candidates))

        winner_id = find_winner(vote_vector)
        winner.update(winner_id)
    return winner


def l_print(stuff, msg=""):
    print_ln_to(0, '%s %s', msg, stuff)
