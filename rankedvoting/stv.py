from collections import Counter
from dataclasses import dataclass
from typing import Mapping

from tabulate import tabulate
import typer

from .base import Ballot, Candidate, get_ballots_from_file, get_candidates_from_ballots


@dataclass
class Round:
    scores: Mapping[Candidate, int | float]
    winners: list[Candidate]
    losers: list[Candidate]
    ballots: list[Ballot]
    nexhausted: int = 0

    def __str__(self) -> str:
        headers = ["Name", "Votes", "Percentage", "Won"]
        table = []
        total_votes = len(self.ballots)

        for cand, score in Counter(self.scores).most_common():
            note = "No"
            if cand in self.winners:
                note = "Yes"
            table.append(
                [
                    cand,
                    score,
                    score / total_votes,
                    note,
                ]
            )

        table.append(
            ["EXHAUSTED", self.nexhausted, self.nexhausted / total_votes, "No"]
        )

        result = tabulate(table, headers, floatfmt=("", "", ".4%", ""))

        # if self.preference_matrix:
        #     result += "\n" + str(self.preference_matrix)

        return result


@dataclass
class Result:
    winners: list[Candidate]
    rounds: list[Round]
    ballots: list[Ballot]

    def __str__(self) -> str:
        out = []

        out.append(f"{len(self.ballots)} ballots cast")
        out.append(f"{len(self.winners)} seats elected")
        out.append(f"{int(len(self.ballots) / (len(self.winners) + 1)) + 1} votes to be elected")

        for i, round in enumerate(self.rounds):
            out.append(f"Round {i + 1}:")
            out.append(str(round))

        for i, winner in enumerate(self.winners):
            out.append(f"Seat {i + 1}: {winner} wins")

        return "\n".join(out)


def stv(ballots: list[Ballot], seats: int = 1) -> Result:
    winners = []
    rounds = []
    eliminated = Counter()
    nexhausted = 0

    threshold = int(len(ballots) / (seats + 1)) + 1

    while len(winners) < seats:
        scores = Counter()

        for ballot in ballots:
            if ballot.top_live_choice is None:
                continue
            scores[ballot.top_live_choice] += ballot.weight

        if not scores:
            highest_scored_eliminated = [
                x for (x, _) in eliminated.most_common(seats - len(winners))
            ]
            winners.extend(highest_scored_eliminated)
            break

        top = max(scores, key=lambda x: scores[x])

        if scores[top] >= threshold:
            winners.append(top)
            round_winners = [top]
            round_losers = []

            for ballot in ballots:
                if ballot.top_live_choice == top:
                    surplus = (scores[top] - threshold) / scores[top]
                    ballot.weight *= surplus
                    ballot.remove(top)
        else:
            round_winners = []
            worst_loser = min(scores, key=lambda x: scores[x])
            round_losers = [
                cand for (cand, score) in scores.items() if score == scores[worst_loser]
            ]

            for loser in round_losers:
                eliminated[loser] = scores[loser]
                for ballot in ballots:
                    ballot.remove(loser)

        nexhausted = sum(ballot.top_live_choice is None for ballot in ballots)
        rounds.append(Round(scores, round_winners, round_losers, ballots, nexhausted))

    return Result(winners, rounds, ballots)

def rcv_bottom_up(ballots: list[Ballot], seats: int = 1) -> Result:
    candidates = get_candidates_from_ballots(ballots)
    rounds = []

    while len(candidates) > seats:
        scores = Counter()
        for ballot in ballots:
            scores[ballot.top_live_choice] += 1

        # Eliminate lowest scorer
        remove_me = min(scores, key=lambda x: scores[x])
        candidates.remove(remove_me)
        for ballot in ballots:
            ballot.remove(remove_me)

        rounds.append(Round(scores, [], losers=[remove_me], ballots=ballots))

    scores = Counter()
    for ballot in ballots:
        scores[ballot.top_live_choice] += 1

    rounds.append(Round(scores, winners=candidates, losers=[], ballots=ballots))

    result = Result(candidates, rounds, ballots)
    return result


def main(ballot_file: str, seats: int = 1, top: bool = False):
    ballots = get_ballots_from_file(ballot_file)
    if top:
        result = rcv_bottom_up(ballots, seats)
    else:
        result = stv(ballots, seats)
    print(result)


if __name__ == "__main__":
    typer.run(main)
