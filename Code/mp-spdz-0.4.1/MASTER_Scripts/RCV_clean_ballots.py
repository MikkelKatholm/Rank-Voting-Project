
from Compiler.types import *
from Compiler.GC.types import *
from Compiler.library import *
from Compiler.util import if_else

from MASTER_Scripts.consts import *

def check_ballot_validity_deferred(ballot: Matrix) -> tuple[sint, sint]:
    """ Computes T_entry and T_sums for a ballot without revealing them. Returns the two aggregates as sint values for batched opening later.
    :param ballot: A Matrix representing the ballot to be checked.
    :return: A tuple (T_entry, T_sums) where T_entry is the sum of entry products and T_sums is the sum of row and column sum products.
     Both values will be 0 for a valid ballot and non-zero for an invalid ballot.
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

    return sum(entry_products), sum(sum_products)


def clean_ballots(ballots: list[Matrix]) -> list[Matrix]:
    """ Returns a list of ballots where invalid ballots are zeroed out. All validity products are computed first, then opened in two batched rounds regardless of the number of ballots.
    :param ballots: A list of Matrices representing the ballots to be checked.
    :return: A list of ballots where invalid ballots are set to all 0. Valid ballots are returned unchanged.
    """
    B = len(ballots)

    # Phase 1: compute all products under secret sharing — no interaction
    T_entries = []
    T_sums = []
    for ballot in ballots:
        t_e, t_s = check_ballot_validity_deferred(ballot)
        T_entries.append(t_e)
        T_sums.append(t_s)

    # Phase 2: open all aggregates in two batched rounds
    revealed_entries = [T_entries[i].reveal() for i in range(B)]
    revealed_sums    = [T_sums[i].reveal()   for i in range(B)]

    print_ln("Revealed T_entries: %s", revealed_entries)
    print_ln("Revealed T_sums: %s", revealed_sums)

    # Phase 3: apply results — no further interaction needed
    result = [0] * B
    for i in range(B):
        is_valid = (revealed_entries[i] == 0) * (revealed_sums[i] == 0)
        @if_e(is_valid == 1)
        def _():
            result[i] = ballots[i]
        @else_
        def _():
            result[i] = ballots[i].assign_all(0)
            print_ln(f"Ballot {i} is invalid and has been set to 0.")

    return result

def entry_product(entry: sint) -> sint:
    return entry * (1 - entry)