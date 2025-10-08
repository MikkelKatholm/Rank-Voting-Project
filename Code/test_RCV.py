from RCV import *
import random

def sandbox():
    random.seed(0)
    c = 4
    n = 5

    ballots = [Ballot(c) for _ in range(n)]

    elim_list: type_ELIMINATED_CANDS = [0 for _ in range(n)]
    #elim_list[0] = 1

    round = Round(ballots)

    sums = round.prepare_all_ballots(elim_list)
    result = round.sum_vectors(sums)
    
    print(result)
        

sandbox()