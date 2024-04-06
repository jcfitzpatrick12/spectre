import typer
from cli import __app_name__, __version__
from utils import capture_session  # Assume capture_session.py is the refactored module

app = typer.Typer()

@app.command()
def start(tag: str = typer.Option(..., "--tag", "-t", help="Tag for the capture session"),
          mode: str = typer.Option(..., "--mode", "-m", help="Mode for the capture"),
          receiver_name: str = typer.Option(..., "--receiver", "-r", help="Receiver name")
) -> None:
    # receiver_name is mandatory
    if not receiver_name:
        typer.secho(
            f'You must specify the receiver via --receiver [receiver name]',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    # mode is mandatory

    if not mode:
        typer.secho(
            f'You must specify the receiver mode via --mode [mode type]',
            fg=typer.colors.RED
        )
        raise typer.Exit(1)
    capture_session.start_capture(receiver_name, mode, tag)

    # tag is mandatory
    if not tag:
        typer.secho(
            f'You must specify the tag via --tag [requested tag]',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)


@app.command()
def stop(
) -> None:
    capture_session.stop_capture()

if __name__ == "__main__":
    app()
