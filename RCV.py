from typing import List
import math
import random
from copy import deepcopy

type type_BALLOT = List[List[int]]
type type_ELIMINATED_CANDS = List[int]

class Ballot:
    def __init__(self, c: int) -> None:
        self.c: int = c
        self.ballot: type_BALLOT = self.generate_random_ballot(c)
        self.modified_ballot:type_BALLOT = deepcopy(self.ballot)
    
    def __str__(self) -> str:
        og_rows = [" ".join(map(str, row)) for row in self.ballot]
        og_formatted = "\n".join(og_rows)
        modified_rows = [" ".join(map(str, row)) for row in self.modified_ballot]
        modified_formatted = "\n".join(modified_rows)

        return f"""{modified_formatted}\n"""
        
    def generate_random_ballot(self, n: int) -> type_BALLOT:
        ranks = list(range(n))
        random.shuffle(ranks)
        
        ballot = [[0 for _ in range(n)] for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                ballot[i][j] = 1 if ranks[i] == j else 0

        return ballot
    
    def edit_ballot(self, row: int, col: int, new_val: int) -> None:
        self.modified_ballot[row][col] = new_val

    def get_modi_ballot_value(self, row:int, col: int) -> int:
        return self.modified_ballot[row][col]

    def remove_eliminated_candidates(self, eliminated_candidates: type_ELIMINATED_CANDS) -> None:
        for i in range(self.c):
            for j in range(self.c):
                current_value = self.ballot[i][j]
                new_value = current_value * (1 - eliminated_candidates[i])
                self.edit_ballot(i, j, new_value)

    def remove_non_highest_priority(self) -> None:
        preceding_columns = []
        highest_priorities = []

        # Compute highest priority
        for col in range(self.c):
            highest_priority = math.prod([1 - sum(preceding_columns[k]) for k in range(col)])
            highest_priorities.append(highest_priority)
            preceding_column = [self.get_modi_ballot_value(row = j, col = col) for j in range(self.c)]
            preceding_columns.append(preceding_column)

        for row in range(self.c):
            for col in range(self.c):
                current_val = self.get_modi_ballot_value(row, col)
                new_value = current_val * highest_priorities[col]
                self.edit_ballot(row, col, new_value)
        
    def sum_of_rows(self) -> List[int]:
        sums = []
        for row in self.modified_ballot:
            sums.append(sum(row))
        return sums