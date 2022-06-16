from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import itertools
import tabulate
import typer

from .base import Ballot, Candidate, get_ballots_from_file, get_candidates_from_ballots


def get_candidates_from_matrix(matrix: PreferenceMatrix | Counter) -> list[Candidate]:
    if isinstance(matrix, PreferenceMatrix):
        matrix = matrix.counter
    seen = set()
    candidates = []

    for pair in matrix.keys():
        if pair[0] not in seen:
            candidates.append(pair[0])
        if pair[1] not in seen:
            candidates.append(pair[1])
        seen.add(pair[0])
        seen.add(pair[1])

    return candidates


@dataclass
class PreferenceMatrix:
    """A basic class representing a preference matrix between candidates.

    The `counter` field is simply a `collections.Counter` object whose keys are
    tuples where `counter[runner, opponent] = <# of voters who prefer runner to opponent>`
    """

    counter: Counter[Candidate]

    def __str__(self) -> str:
        candidates = get_candidates_from_matrix(self.counter)
        headers = ["vs."] + candidates
        table = []

        for runner in candidates:
            table.append(
                [runner] + [self.counter[runner, opponent] for opponent in candidates]
            )

        return tabulate.tabulate(table, headers)

    def difference_display(self) -> str:
        candidates = get_candidates_from_matrix(self.counter)
        headers = ["vs."] + candidates
        table = []

        for runner in candidates:
            table.append(
                [runner]
                + [
                    self.counter[runner, opponent] - self.counter[opponent, runner]
                    for opponent in candidates
                ]
            )

        return tabulate.tabulate(table, headers)

    def __getitem__(self, key: tuple[Candidate, Candidate]) -> str:
        return self.counter[key]


def get_preference_matrix_from_ballots(ballots: list[Ballot]) -> PreferenceMatrix:
    candidates = get_candidates_from_ballots(ballots)

    counter = Counter()
    for runner, opponent in itertools.combinations(candidates, 2):
        for ballot in ballots:
            if ballot.outranks(runner, opponent):
                counter[runner, opponent] += 1
                counter[opponent, runner] += 0
            elif ballot.outranks(opponent, runner):
                counter[runner, opponent] += 0
                counter[opponent, runner] += 1
            else:
                counter[runner, opponent] += 0
                counter[opponent, runner] += 0

    return PreferenceMatrix(counter)


def copeland_from_ballots(ballots: list[Ballot]) -> Counter[Candidate]:
    preferences = get_preference_matrix_from_ballots(ballots)
    copeland_result = copeland_from_preference_matrix(preferences)
    return copeland_result


def copeland_from_preference_matrix(prefers: PreferenceMatrix) -> Counter[Candidate]:
    candidates = get_candidates_from_matrix(prefers)
    result = Counter()
    for runner, opponent in itertools.combinations(candidates, 2):
        if runner == opponent:
            continue
        if prefers[runner, opponent] > prefers[opponent, runner]:
            result[runner] += 1
            result[opponent] += 0
        elif prefers[runner, opponent] < prefers[opponent, runner]:
            result[runner] += 0
            result[opponent] += 1
        else:  # prefers[runner, opponent] == prefers[opponent, runner]:
            result[runner] += 0.5
            result[opponent] += 0.5

    return result


def condorcet_winner(ballots: list[Ballot]) -> str:
    candidates = get_candidates_from_ballots(ballots)
    copeland_scores = copeland_from_ballots(ballots)

    winner = max(copeland_scores, key=lambda x: copeland_scores[x])

    if copeland_scores[winner] == len(candidates) - 1:
        return winner
    return f"No Condorcet winner (most pairwise wins is {winner})"


def main(ballot_file: str, diff: bool = False):
    ballots = get_ballots_from_file(ballot_file)
    candidates = get_candidates_from_ballots(ballots)
    matrix = get_preference_matrix_from_ballots(ballots)
    copeland = copeland_from_preference_matrix(matrix)

    print("Preference Matrix:")
    if diff:
        print(matrix.difference_display())
    else:
        print(matrix)

    print(tabulate.tabulate(copeland.most_common()))

    winner = max(copeland, key=lambda x: copeland[x])

    if copeland[winner] == len(candidates) - 1:
        print("Condorcet winner found: ", end="")
    print(winner)


if __name__ == "__main__":
    typer.run(main)
