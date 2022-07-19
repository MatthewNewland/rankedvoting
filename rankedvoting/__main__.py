from typer import Typer

app = Typer(name="rankedvoting")

from .stv import main as stv_main

app.command("stv")(stv_main)

from .condorcet import main as condorcet_main

app.command("condorcet")(condorcet_main)

from .proportional import main as proportional_main

app.command("proportional")(proportional_main)

from .btr_irv import main as btr_irv_main
app.command("btr-irv")(btr_irv_main)

app()
