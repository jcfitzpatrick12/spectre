import typer
import os

from host.cli import __app_name__, __version__
from cfg import CONFIG, callisto_stations
from spectre.utils import dir_helpers, datetime_helpers
from spectre.receivers.Receiver import Receiver
from spectre.receivers import get_mount
from spectre.chunks.Chunks import Chunks

app = typer.Typer()

@app.command()
def callisto_instrument_codes(

) -> None:
    for callisto_instrument_code in callisto_stations.instrument_codes:
        typer.secho(f"{callisto_instrument_code}")
    raise typer.Exit()

@app.command()
def chunks(
    tag: str = typer.Option(..., "--tag", "-t", help=""),
    ext: str = typer.Option(..., "--ext", "-e", help=""),
    year: int = typer.Option(None, "--year", "-y", help=""),
    month: int = typer.Option(None, "--month", "-m", help=""),
    day: int = typer.Option(None, "--day", "-d", help=""),
) -> None:
    chunks = Chunks(tag, 
                    year=year, 
                    month=month,
                    day=day)
    for chunk_start_time, chunk in chunks.dict.items():
        # Use getattr to dynamically get the attribute based on 'ext'
        attribute = getattr(chunk, ext, None)
        if attribute is None:
            typer.echo(f"No attribute '{ext}' found on chunk")
            continue
        if attribute.exists():
            print(f"{chunk_start_time}_{tag}.{ext}")
    typer.Exit()

@app.command()
def receivers(
) -> None:
    receiver_list = get_mount.list_all_receivers()
    for receiver_name in receiver_list:
        typer.secho(f"{receiver_name}")
    typer.Exit()


@app.command()
def modes(
    receiver_name: str = typer.Option(..., "--receiver", "-r", help="Specify the receiver name")
) -> None:
    receiver = Receiver(receiver_name)
    valid_modes = receiver.valid_modes
    
    for i, mode in enumerate(valid_modes):
        typer.secho(f"{mode}")
    raise typer.Exit()

@app.command()
def fits_configs(
) -> None:
    json_config_files = os.listdir(CONFIG.json_configs_dir)
    for json_config_file in json_config_files:
        if json_config_file.startswith("fits_config"):
            typer.secho(
                f'{json_config_file}',
            )
    raise typer.Exit()


@app.command()
def capture_configs(
) -> None:
    json_config_files = os.listdir(CONFIG.json_configs_dir)
    for json_config_file in json_config_files:
        if json_config_file.startswith("capture_config"):
            typer.secho(
                f'{json_config_file}',
            )
    raise typer.Exit()



@app.command()
def tags(
    tag_type: str = typer.Option(None, "--tag-type", help=""),
    year: int = typer.Option(None, "--year", "-y", help=""),
    month: int = typer.Option(None, "--month", "-m", help=""),
    day: int = typer.Option(None, "--day", "-d", help=""),
    
) -> None:
    chunks_dir = CONFIG.chunks_dir
    if (not year is None) or (not month is None) or (not day is None):
        # if the user specifies any of the date kwargs, call that method to append to the parent chunks directory
        chunks_dir = datetime_helpers.append_date_dir(CONFIG.chunks_dir, 
                                                        year=year, 
                                                        month=month, 
                                                        day=day)
    all_files = dir_helpers.list_all_files(chunks_dir)
    
    if tag_type not in [None, "native", "callisto"]:
        raise ValueError("Expected argument for --tag-type to be 'native' or 'callisto'.")

    tags = set()
    for file in all_files:
        file_name, _ = os.path.splitext(file)
        tag = file_name.split("_")[-1]
        if tag_type == "callisto" and "callisto" in tag:
            tags.add(tag)
        elif tag_type == "native" and "callisto" not in tag:
            tags.add(tag)
        elif tag_type is None:
            tags.add(tag)

    if len(tags) == 0:
        typer.secho("No tags found.")
    else:
        for tag in sorted(tags):
            typer.secho(f"{tag}")
    raise typer.Exit()

