from dataclasses import dataclass, field
import json
import os
from pathlib import Path


Candidate: type = str


@dataclass
class Ballot:
    ranking: list[Candidate]
    weight: int | float = 1
    _initial_ranking: list[Candidate] | None = field(default=None, init=False, repr=False)

    @property
    def top_live_choice(self) -> str:
        try:
            return self.ranking[0]
        except IndexError:
            return None

    def outranks(self, runner: Candidate, opponent: Candidate) -> bool:
        try:
            return self.ranking.index(runner) < self.ranking.index(opponent)
        except ValueError:
            return False

    def remove(self, candidate: Candidate) -> None:
        if self._initial_ranking is None:
            self._initial_ranking = self.ranking
        try:
            self.ranking.remove(candidate)
        except ValueError:
            pass

    def reset(self) -> None:
        self.ranking = self._initial_ranking



def get_counted_ballots(data: list[dict]) -> list[Ballot]:
    ballots: list[Ballot] = []

    for datum in data:
        count = datum.get("count", 1)
        ranking = datum["ranking"]

        for _ in range(count):
            # Copy necessary or all ballots share same reference
            ballots.append(Ballot(ranking.copy()))

    return ballots


def get_candidates_from_ballots(ballots: list[Ballot]) -> list[Candidate]:
    seen: set[Candidate] = set()
    candidates: list[Candidate] = []

    for ballot in ballots:
        for cand in ballot.ranking:
            if cand in seen:
                continue
            seen.add(cand)
            candidates.append(cand)

    return candidates


def get_ballots_from_file(path: os.PathLike) -> list[Ballot]:
    data = json.loads(Path(path).read_text())
    return get_counted_ballots(data)
