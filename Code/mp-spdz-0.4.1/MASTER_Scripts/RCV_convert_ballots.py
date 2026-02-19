from Compiler.types import *
from Compiler.GC.types import *
from Compiler.library import *

from MASTER_Scripts.consts import *

def sint_to_sbit(s: sint) -> sb:
    return s - sb(0)

def convert_ballot(ballot: Matrix) -> Matrix:
    # Convert from sint to sb
    new_ballot = Matrix(NUM_CANDS, NUM_CANDS, value_type=sb)
    for row in range(NUM_CANDS):
        for col in range(NUM_CANDS):
            new_ballot[row][col] = sint_to_sbit(ballot[row][col])
    return new_ballot

def convert_ballots(ballots: list[Matrix]):
    converted_ballots = []#[0] * len(ballots)
    for ballot in ballots:
        converted_ballots.append(convert_ballot(ballot))
    return converted_ballots
