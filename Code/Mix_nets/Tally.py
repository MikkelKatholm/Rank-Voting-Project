from Consts import *

def tally(ballots: Ballots) -> int|ValueError:

    active_candidates = set(range(NUM_CANDS))
    voted_needed_for_majority = (NUM_CLIENTS) // 2 + 1

    for _ in range(NUM_CANDS):
        # Count first-choice votes
        counts = {c: 0 for c in active_candidates}
        for ballot in ballots:
            first_choice = ballot[0]
            if first_choice in active_candidates:
                counts[first_choice] += 1
        # Check for majority
        for c, count in counts.items():
            if count >= voted_needed_for_majority:
                return c
        # No majority, eliminate candidate(s) with fewest votes. If tie, eliminate the one with lowest index.


        candidate_to_eliminate = find_candidate_to_eliminate(counts, active_candidates)
        active_candidates.remove(candidate_to_eliminate)
        ballots = remove_non_active_candidates(ballots, active_candidates)

        # If only one candidate left, return it
        if len(active_candidates) == 1:
            return next(iter(active_candidates))

    raise ValueError("No winner found")


def find_candidate_to_eliminate(counts: dict[int, int], active_candidates: set[int]) -> int:
    min_count = min(counts[c] for c in active_candidates)
    candidates_to_eliminate = [c for c in active_candidates if counts[c] == min_count]
    candidate_to_eliminate = min(candidates_to_eliminate)
    return candidate_to_eliminate

def remove_non_active_candidates(ballots: Ballots, active_candidates: set[int]) -> Ballots:
    new_ballots = []
    for ballot in ballots:
        new_ballot = [c for c in ballot if c in active_candidates]
        new_ballots.append(new_ballot)
    return new_ballots