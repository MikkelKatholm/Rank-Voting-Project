from RCV import *
import random

def sandbox():
    random.seed(0)
    c = 4
    n = 5

    ballots = [Ballot(c) for _ in range(n)]

    elim_list: type_ELIMINATED_CANDS = [0 for _ in range(n)]
    elim_list[0] = 1

    votes = [0 for _ in range(c)]
    for i, ballot in enumerate(ballots):
        print(f"------------------------------Ballot {i}------------------------------")
        print(f"Original ballot = \n{ballot}")
        ballot.remove_eliminated_candidates(elim_list)
        print(f"remove_elim ballot = \n{ballot}")
        ballot.remove_non_highest_priority()
        print(f"remove_highest_priority = \n{ballot}")
        sum_of_rows = ballot.sum_of_rows()
        print(sum_of_rows)
        votes = [votes[i] + sum_of_rows[i] for i in range(c)]
        
    print(votes)

sandbox()