from typer import Typer


app = Typer(name="rankedvoting")


@app.command()
def stv(ballot_file: str, seats: int = 1):
    from .stv import main
    main(ballot_file, seats)


@app.command()
def condorcet(ballot_file: str, diff: bool = False):
    from .condorcet import main
    main(ballot_file, diff)


if __name__ == "__main__":
    app()
