# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer
from os import listdir
from os.path import isfile, join, splitext

from host.cli import __app_name__, __version__

from spectre.utils import dir_helpers, datetime_helpers
from spectre.receivers.factory import get_receiver
from spectre.receivers.receiver_register import list_all_receiver_names
from spectre.file_handlers.chunks.Chunks import Chunks

from cfg import (
    CHUNKS_DIR_PATH,
    JSON_CONFIGS_DIR_PATH,
    INSTRUMENT_CODES
)

app = typer.Typer()

@app.command()
def callisto_instrument_codes(

) -> None:
    for callisto_instrument_code in INSTRUMENT_CODES:
        typer.secho(f"{callisto_instrument_code}")
    raise typer.Exit()

@app.command()
def chunks(
    tag: str = typer.Option(..., "--tag", "-t", help=""),
    year: int = typer.Option(None, "--year", "-y", help=""),
    month: int = typer.Option(None, "--month", "-m", help=""),
    day: int = typer.Option(None, "--day", "-d", help=""),
) -> None:
    chunks = Chunks(tag, 
                    year=year, 
                    month=month,
                    day=day)
    
    for chunk in chunks:
        for extension in chunk.get_extensions():
            if chunk.has_file(extension):
                chunk_file = chunk.get_file(extension)
                print(chunk_file.file_name)
                continue
    typer.Exit()


@app.command()
def receivers(
) -> None:
    receiver_list = list_all_receiver_names()
    for receiver_name in receiver_list:
        typer.secho(f"{receiver_name}")
    typer.Exit()


@app.command()
def modes(
    receiver_name: str = typer.Option(..., "--receiver", "-r", help="Specify the receiver name")
) -> None:
    receiver = get_receiver(receiver_name)
    valid_modes = receiver.valid_modes
    
    for i, mode in enumerate(valid_modes):
        typer.secho(f"{mode}")
    raise typer.Exit()


@app.command()
def fits_configs(
) -> None:
    json_config_files = listdir(JSON_CONFIGS_DIR_PATH)
    for json_config_file in json_config_files:
        if json_config_file.startswith("fits_config"):
            typer.secho(
                f'{json_config_file}',
            )
    raise typer.Exit()


@app.command()
def capture_configs(
) -> None:
    json_config_files = listdir(JSON_CONFIGS_DIR_PATH)
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
    chunks_dir = CHUNKS_DIR_PATH
    if (not year is None) or (not month is None) or (not day is None):
        # if the user specifies any of the date kwargs, call that method to append to the parent chunks directory
        chunks_dir = datetime_helpers.append_date_dir(CHUNKS_DIR_PATH, 
                                                        year=year, 
                                                        month=month, 
                                                        day=day)
    chunk_files = [f for f in listdir(chunks_dir) if isfile(join(chunks_dir, f))]
    print(chunk_files)
    exit()
    if tag_type not in [None, "native", "callisto"]:
        raise ValueError("Expected argument for --tag-type to be 'native' or 'callisto'.")

    tags = set()
    for chunk_file in chunk_files:
        chunk_base_name, _ = splitext(chunk_file)
        tag = chunk_base_name.split("_")[1]
        if tag_type == "callisto" and "callisto" in tag:
            tags.add(tag)
        elif tag_type == "native" and "callisto" not in tag:
            tags.add(tag)
        else:
            tags.add(tag)

    if len(tags) == 0:
        typer.secho("No tags found.")
    else:
        for tag in sorted(tags):
            typer.secho(f"{tag}")
    raise typer.Exit()

