from typer import Typer
import typer


app = Typer(name="rankedvoting")


@app.command()
def stv(ballot_file: str, seats: int = 1):
    from .stv import main

    main(ballot_file, seats)


@app.command()
def condorcet(ballot_file: str, diff: bool = False):
    from .condorcet import main

    main(ballot_file, diff)


@app.command()
def proportional(
    vote_map_file: str,
    seats: int = typer.Option(..., "--seats", "-s"),
    method: str = typer.Option("dhondt", "--method", "-m"),
):
    from .proportional import main

    main(vote_map_file, seats, method)


if __name__ == "__main__":
    app()
