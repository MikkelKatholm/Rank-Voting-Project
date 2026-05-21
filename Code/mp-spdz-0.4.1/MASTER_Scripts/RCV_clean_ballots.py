from Compiler.types import *
from Compiler.GC.types import *
from Compiler.library import *
from Compiler.util import if_else

from MASTER_Scripts.consts import *


def is_valid_entry(entry: sint) -> bool:
    exp = (entry * (entry - 1)).reveal()
    res = (exp == 0)
    return res

def entry_product(entry: sint) -> sint:
    return entry * (1 - entry)

def check_ballot_validity(ballot: Matrix) -> regint:
    """
    Verifies that a ballot is well-formed, i.e. each entry is either 0 or 1, 
    and the sum of each row and column is 0 or 1.

    :param ballot: A Matrix representing the ballot to be checked.
    :return: Boolean value indicating the validity of the ballot
    """

    entry_products = []
    sum_products = []

    for row in range(NUM_CANDS):
        for col in range(NUM_CANDS):
            entry_products.append(entry_product(ballot[row][col]))

    for row in range(NUM_CANDS):
        s = sum(ballot[row][col] for col in range(NUM_CANDS))
        sum_products.append(entry_product(s))

    for col in range(NUM_CANDS):
        s = sum(ballot[row][col] for row in range(NUM_CANDS))
        sum_products.append(entry_product(s))

    T_entry = sum(entry_products)
    T_sums = sum(sum_products)

    valid_entries = T_entry.reveal() == 0
    valid_sums = T_sums.reveal() == 0

    return valid_entries * valid_sums

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
            print_ln(f"Ballot {i} is invalid and has been set to 0.")

    return clean_ballots
