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


def webster(vote_map: Mapping[str, int], seats: int) -> Counter[str]:
    seat_result = Counter()

    while sum(seat_result.values()) < seats:
        quotients = {}

        for party, votes in vote_map.items():
            quotients[party] = votes / (2*seat_result[party] + 1)

        winner = max(quotients, key=lambda x: quotients[x])

        seat_result[winner] += 1

    return seat_result


def hamilton(vote_map: Mapping[str, int], seats: int) -> Counter[str]:
    seat_result = Counter()
    remainders = {}
    total_votes = sum(vote_map.values())
    quota = total_votes / seats
    # Apportion the int-part of the seats
    for party, votes in vote_map.items():
        quotient, remainder = divmod(votes, quota)
        seat_result[party] = quotient
        remainders[party] = remainder

    while sum(seat_result.values()) < seats:
        next_seat_earned = max(remainders, key=lambda party: remainders[party])
        seat_result[next_seat_earned] += 1
        del remainders[next_seat_earned]

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


def main(
    party_file: str,
    seats: int = typer.Option(..., "--seats", "-s"),
    method: str = typer.Option("dhondt", "--method", "-m")
):
    vote_map = get_votemap_from_file(party_file)
    match method:
        case "hamilton":
            result = hamilton(vote_map, seats)
        case "dhondt":
            result = dhondt(vote_map, seats)
        case "webster":
            result = webster(vote_map, seats)
    display_result(vote_map, result)


def get_votemap_from_file(party_file) -> dict[str, int]:
    return json.loads(Path(party_file).read_text())


if __name__ == "__main__":
    typer.run(main)
