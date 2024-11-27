# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer

from cli import (
    PROCESS_TYPE_HELP,
    YEAR_HELP,
    MONTH_HELP,
    DAY_HELP,
    TAG_HELP,
    EXTENSIONS_HELP,
    RECEIVER_NAME_HELP
)

app = typer.Typer()

@app.command()
def callisto_instrument_codes(
) -> None:
    # for instrument_code in get.callisto_instrument_codes():
    #     typer.secho(instrument_code)
    raise typer.Exit()


@app.command()
def logs(process_type: str = typer.Option(None, "--process-type", help=PROCESS_TYPE_HELP),
         year: int = typer.Option(None, "--year", "-y", help=YEAR_HELP),
         month: int = typer.Option(None, "--month", "-m", help=MONTH_HELP),
         day: int = typer.Option(None, "--day", "-d", help=DAY_HELP)
) -> None:
    # for log_file_name in get.log_file_names(process_type, year, month, day):
    #     typer.secho(log_file_name)
    raise typer.Exit()


@app.command()
def chunk_files(
    tag: str = typer.Option(..., "--tag", "-t", help=TAG_HELP),
    year: int = typer.Option(None, "--year", "-y", help=YEAR_HELP),
    month: int = typer.Option(None, "--month", "-m", help=MONTH_HELP),
    day: int = typer.Option(None, "--day", "-d", help=DAY_HELP),
    extensions: list[str] = typer.Option(None, "--extension", "-e", help=EXTENSIONS_HELP)
) -> None:
    # for chunk_file_name in get.chunk_file_names(tag, year, month, day, extensions):
    #     typer.secho(chunk_file_name)
    raise typer.Exit()


@app.command()
def receivers(
) -> None:
    # for receiver_name in get.receiver_names():
    #     typer.secho(receiver_name)
    raise typer.Exit()

@app.command()
def modes(
    receiver_name: str = typer.Option(..., "--receiver", "-r", help=RECEIVER_NAME_HELP)
) -> None:
    # for mode in get.receiver_modes(receiver_name):
    #     typer.secho(mode)
    raise typer.Exit()


@app.command()
def specifications(
    receiver_name: str = typer.Option(..., "--receiver", "-r", help=RECEIVER_NAME_HELP)
) -> None:
    # specifications = get.receiver_specifications(receiver_name)
    # for k, v in specifications.items():
    #     typer.secho(f"{k}: {v}")
    raise typer.Exit()


@app.command()
def fits_configs(
) -> None:
    # for file_name in get.fits_config_file_names():
    #     typer.secho(file_name)
    raise typer.Exit()


@app.command()
def capture_configs(
) -> None:
    # for file_name in get.capture_config_names():
    #     typer.secho(file_name)
    raise typer.Exit()


@app.command()
def tags(
    year: int = typer.Option(None, "--year", "-y", help=YEAR_HELP),
    month: int = typer.Option(None, "--month", "-m", help=MONTH_HELP),
    day: int = typer.Option(None, "--day", "-d", help=DAY_HELP),
    
) -> None:
    # for tag in get.tags(year, month, day):
    #     typer.secho(tag)
    raise typer.Exit()

