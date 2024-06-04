import typer
from typing import List

from spectre.web_fetch.callisto import fetch_chunks

app = typer.Typer()

@app.command()
def callisto(
    station: str = typer.Option(..., "--station", "-s", help=""),
    year: int = typer.Option(None, "--year", "-y", help=""),
    month: int = typer.Option(None, "--month", "-m", help=""),
    day: int = typer.Option(None, "--day", "-d", help=""),
) -> None:
    fetch_chunks(station, year=year, month=month, day=day)
    raise typer.Exit()