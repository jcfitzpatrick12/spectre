import typer
from typing import Optional

from host.cli import __app_name__, __version__
from host.cfg import CONFIG
from host.gui.SPECTRECompanion import main as spectre_companion


from host.cli.tools.create.commands import app as create_app
from host.cli.tools.list.commands import app as list_app
from host.cli.tools.print.commands import app as print_app
from host.cli.tools.delete.commands import app as delete_app
from host.cli.tools.capture.commands import app as capture_app


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

@app.command()
def companion(
    tag: str = typer.Option(..., "--tag", "-t", help="Specify the tag on start up of the gui.")
) -> None:
    spectre_companion(tag)
    return


    


