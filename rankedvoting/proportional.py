"""Party-list proportional representation"""


from collections import Counter
import json
from pathlib import Path
from typing import Mapping

import tabulate
import typer


def dhondt(vote_map: Mapping[str, int], seats: int) -> Counter[str]:
    seat_result = Counter()

    while sum(seat_result.values()) < seats:
        quotients = {}

        for party, votes in vote_map.items():
            quotients[party] = votes / (seat_result[party] + 1)

        winner = max(quotients, key=lambda x: quotients[x])

        seat_result[winner] += 1

    return seat_result


def display_result(vote_map: Mapping[str, int], result: Counter[str]):
    total_votes = sum(vote_map.values())
    total_seats = sum(result.values())
    headers = ["Party", "Votes", "Vote Share", "Seats", "Seat Share"]
    table = []

    for party, seats in result.most_common():
        votes = vote_map[party]
        vote_share = f"{votes/total_votes:.4%}"
        # seats = result[party]
        seat_share = f"{seats / total_seats:4%}"

        table.append([party, votes, vote_share, seats, seat_share])

    print(tabulate.tabulate(table, headers))


def main(party_file: str, seats: int = typer.Option(..., "--seats", "-s")):
    vote_map = get_votemap_from_file(party_file)
    result = dhondt(vote_map, seats)
    display_result(vote_map, result)

def get_votemap_from_file(party_file) -> dict[str, int]:
    return json.loads(Path(party_file).read_text())


if __name__ == "__main__":
    typer.run(main)
