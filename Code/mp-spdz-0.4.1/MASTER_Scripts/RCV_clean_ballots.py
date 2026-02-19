from Compiler.types import *
from Compiler.GC.types import *
from Compiler.library import *
from Compiler.util import if_else

from MASTER_Scripts.consts import *


def is_valid_entry(entry: sint) -> bool:
    exp = (entry * (entry - 1)).reveal()
    res = (exp == 0)
    return res

def check_ballot_validity(ballot: Matrix) -> regint:
    """
    Verifies that a ballot is well-formed, i.e. each entry is either 0 or 1, and the sum of each row and column is 0 or 1.

    :param ballot: A Matrix representing the ballot to be checked.
    :return: Boolean value indicating the validity of the ballot
    """
    result = Array(1, regint) # Only works if kept in a container (array in this case)
    result[0] = 1
    for row in range(NUM_CANDS):
        row_sum = sint(0)
        for col in range(NUM_CANDS):
            entry = ballot[row][col]
            row_sum += entry

            @if_(is_valid_entry(entry) == 0)
            def _():
                result[0] = 0
        @if_(is_valid_entry(row_sum) == 0)
        def _():
            result[0] = 0

    for col in range(NUM_CANDS):
        column = ballot.get_column(col)
        col_sum = sint(0)
        for entry in column:
            col_sum += entry

        @if_(is_valid_entry(col_sum) == 0)
        def _():
            result[0] = 0
    return result[0]

def clean_ballots(ballots: list[Matrix]) -> list[Matrix]:
    """
    Returns a list of ballots where the invalid ballots are set to 0.

    :param ballots: A list of Matrices representing the ballots to be checked.
    :return: A list of ballots where the invalid ballots are set to 0
    """
    clean_ballots = [0] * len(ballots)  # NOTE: If this is not initialized to a list of length of ballots the return list contains all the ballots twice.
    for i in range(len(ballots)):
        ballot = ballots[i]
        is_valid = check_ballot_validity(ballot)
        @if_e(is_valid == 1)
        def _():
            clean_ballots[i] = ballot
        @else_
        def _():
            clean_ballots[i] = ballot.assign_all(0)

    return clean_ballots
