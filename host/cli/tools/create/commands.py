import typer
from typing import List

from cli import __app_name__, __version__
from cfg import CONFIG
from spectre.receivers.Receiver import Receiver
from spectre.cfg.json_config.FitsConfig import FitsConfig


app = typer.Typer()

@app.command()
def fits_config(tag: str = typer.Option(..., "--tag", "-t", help=""),
                params: List[str] = typer.Option([], "--param", "-p", help="Pass arbitrary key-value pairs.", metavar="KEY=VALUE")
) -> None:
    try:
        fits_config_instance = FitsConfig(tag, CONFIG.json_configs_dir)
        fits_config_instance.save_params_as_fits_config(params)

    except KeyError as e:
        typer.secho(
            f'Received {e}. Pass in appropriate keys using --param [KEY=VALUE].',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    finally:
        pass

    typer.secho(f"The fits config for tag \"{tag}\" has been created.", fg=typer.colors.GREEN)


@app.command()
def capture_config(tag: str = typer.Option(..., "--tag", "-t", help=""),
                   mode: str = typer.Option(..., "--mode", "-m", help=""),
                   receiver_name: str = typer.Option(..., "--receiver", "-r", help=""),
                   params: List[str] = typer.Option([], "--param", "-p", help="Pass arbitrary key-value pairs.", metavar="KEY=VALUE"),
) -> None:
    
    # # # # #save the params to file as a validated capture config
    try:
    # # instantiate the receiver specific capture config class 
        receiver = Receiver(receiver_name)
        receiver.set_mode(mode)
        receiver.save_params_as_capture_config(params, tag, CONFIG.json_configs_dir)

    except KeyError as e:
        typer.secho(
            f'Received {e}. Pass in appropriate keys using --param [KEY=VALUE].',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    

    finally:
        pass

    typer.secho(f"The capture config for tag \"{tag}\" has been created.", fg=typer.colors.GREEN)
    

        

    

