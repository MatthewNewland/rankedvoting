from collections import Counter
from typing import Mapping

from .proportional import webster


def mmp(
    party_vote: Mapping[str, int],
    district_seats: Mapping[str, int],
    num_seats: int = -1,
) -> Counter[str]:
    seats = Counter(district_seats)
    num_seats = sum(district_seats.values()) * 2 if num_seats < 0 else num_seats
    # total_votes = sum(party_vote.values())

    # ideal_share = {
    #     party: (party_votes / total_votes) * num_seats
    #     for party, party_votes in party_vote.items()
    # }

    # print(ideal_share)

    # while sum(seats.values()) < num_seats:
    ideal_share = webster(party_vote, num_seats)

    for party in party_vote:
        if district_seats.get(party, 0) >= ideal_share[party]:
            num_seats -= district_seats.get(party, 0)
            del ideal_share[party]

    ideal_share = webster({party: party_vote[party] for party in ideal_share}, num_seats)

    for party, nseats in ideal_share.items():
        seats[party] = nseats

    return seats


# party_vote = {"R": 54, "D": 31, "S": 14}

# district_seats = {"D": 2, "R": 6}

# print(mmp(party_vote, district_seats, num_seats=15))
