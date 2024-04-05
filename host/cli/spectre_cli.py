import typer
from typing import Optional

from cli import __app_name__, __version__
from cfg import CONFIG

from spectre.receivers.Receiver import Receiver

from cli.tools.create.commands import app as create_app
from cli.tools.list.commands import app as list_app
from cli.tools.print.commands import app as print_app
from cli.tools.delete.commands import app as delete_app
from cli.tools.capture.commands import app as capture_app


app = typer.Typer()

app.add_typer(create_app, name="create")
app.add_typer(list_app, name='list')
app.add_typer(print_app, name='print')
app.add_typer(delete_app, name='delete')
app.add_typer(capture_app, name='capture')


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


    


