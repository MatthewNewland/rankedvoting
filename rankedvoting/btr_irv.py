from collections import Counter

import typer
from .base import Ballot, Candidate, get_ballots_from_file
from .stv import Round, Result


def _pairwise_loser(ballots: list[Ballot], first: Candidate, second: Candidate) -> Candidate:
    scores = {first: 0, second: 0}

    for ballot in ballots:
        if first not in ballot.ranking or second not in ballot.ranking:
            continue
        if ballot.ranking.index(first) < ballot.ranking.index(second):
            scores[first] += 1
        if ballot.ranking.index(first) > ballot.ranking.index(second):
            scores[second] += 1

    return min(scores, key=lambda x: scores[x])


def btr_irv(ballots: list[Ballot]) -> Result:
    threshold = len(ballots) // 2
    rounds = []
    winner = None

    while winner is None:
        scores = Counter()
        for ballot in ballots:
            scores[ballot.top_live_choice] += 1

        top_cand = max(scores, key=lambda x: scores[x])
        if scores[top_cand] <= threshold:
            *_, (bot, _), (tom, _) = scores.most_common()
            cand_to_eliminate = _pairwise_loser(ballots, bot, tom)
            for ballot in ballots:
                ballot.remove(cand_to_eliminate)
            rounds.append(Round(scores, winners=[], losers=[cand_to_eliminate], ballots=ballots))
            continue

        rounds.append(Round(scores, winners=[top_cand], losers=[], ballots=ballots))
        winner = top_cand

    return Result([winner], rounds, ballots)


def main(ballot_file: str):
    ballots = get_ballots_from_file(ballot_file)
    result = btr_irv(ballots)
    print(result)


if __name__ == "__main__":
    typer.run(main)
