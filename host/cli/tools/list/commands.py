# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer
from os import listdir, walk
from os.path import splitext

from host.cli import __app_name__, __version__

from spectre.receivers.factory import get_receiver
from spectre.receivers.receiver_register import list_all_receiver_names
from spectre.chunks import Chunks

from spectre.cfg import (
    JSON_CONFIGS_DIR_PATH,
    INSTRUMENT_CODES
)
from spectre.cfg import get_chunks_dir_path

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
    extensions: list[str] = typer.Option([], "--extension", "-e", help="")
) -> None:
    chunks = Chunks(tag, 
                    year=year, 
                    month=month,
                    day=day)
    
    for chunk in chunks:
        
        # if no extensions are specified, look for ALL defined extensions for that chunk
        if not extensions:
            extensions = chunk.get_extensions()

        for extension in extensions:
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
def specifications(
    receiver_name: str = typer.Option(..., "--receiver", "-r", help="Specify the receiver name")
) -> None:
    receiver = get_receiver(receiver_name)
    specifications = receiver.get_specifications()
    for k, v in specifications.items():
        typer.secho(f"{k}: {v}")
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
    year: int = typer.Option(None, "--year", "-y", help=""),
    month: int = typer.Option(None, "--month", "-m", help=""),
    day: int = typer.Option(None, "--day", "-d", help=""),
    
) -> None:
    chunks_dir_path = get_chunks_dir_path(year, month, day)
    chunk_files = [f for (_, _, files) in walk(chunks_dir_path) for f in files]
    tags = set()
    for chunk_file in chunk_files:
        chunk_base_name, _ = splitext(chunk_file)
        tag = chunk_base_name.split("_")[1]
        tags.add(tag)
    if len(tags) == 0:
        typer.secho("No tags found.")
    else:
        for tag in sorted(tags):
            typer.secho(f"{tag}")
    raise typer.Exit()

