import typer
from typing import Optional

from cli import __app_name__, __version__
from cfg import CONFIG

from spectre.receivers.Receiver import Receiver

from cli.tools.create.commands import app as create_app
from cli.tools.list.commands import app as list_app
from cli.tools.print.commands import app as print_app
from cli.tools.delete.commands import app as delete_app


app = typer.Typer()

app.add_typer(create_app, name="create")
app.add_typer(list_app, name='list')
app.add_typer(print_app, name='print')
app.add_typer(delete_app, name='delete')


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, 
        "--version", 
        "-v", 
        help="Show the application's version and exit.", 
        callback=_version_callback, 
        is_eager=True,
    )
) -> None:
    return

@app.command()
def capture(
    tag: str = typer.Option(None, "--tag", "-t", help=""),
    mode: str = typer.Option(None, "--mode", "-m", help=""),
    receiver_name: str = typer.Option(None, "--receiver", "-r", help=""),
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
    
    
    # tag is mandatory
    if not tag:
        typer.secho(
            f'You must specify the tag via --tag [requested tag]',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    

    try:
        receiver = Receiver(receiver_name)
        receiver.set_mode(mode)
        receiver.do_capture(tag, CONFIG.path_to_capture_configs)

    except Exception as e:
        typer.secho(
            f'Could not start capture, received: {e}',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    return

    


