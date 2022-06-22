import json
import typer
from .proportional import get_votemap_from_file


def main(
    infile: str,
    outfile: str = typer.Option(..., "--output", "--out", "-o"),
    seats: int = typer.Option(..., "--seats", "-s"),
):
    votemap: dict[str, int] = get_votemap_from_file(infile)

    total_votes = sum(votemap.values())

    ballot_data = []

    for party, votes in votemap.items():
        count = int((votes / total_votes) * 100000)
        ranking = [f"{party} #{i + 1}" for i in range(seats)]
        ballot_data.append({"count": count, "ranking": ranking})

    trailing_zero_list = []
    for datum in ballot_data:
        manipulandum = str(datum["count"])
        trailing_zeroes = len(manipulandum) - len(manipulandum.rstrip('0'))
        trailing_zero_list.append(trailing_zeroes)

    least_trailing_zeroes = min(trailing_zero_list)

    ballot_data = [{**datum, "count": datum["count"] // 10**least_trailing_zeroes} for datum in ballot_data]

    with open(outfile, "w") as fp:
        json.dump(ballot_data, fp, indent=2)


if __name__ == "__main__":
    typer.run(main)
