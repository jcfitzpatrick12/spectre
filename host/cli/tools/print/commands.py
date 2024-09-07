# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer
import os

from host.cli import __app_name__, __version__
from cfg import CONFIG

from spectre.json_config.CaptureConfigHandler import CaptureConfigHandler
from spectre.json_config.FitsConfigHandler import FitsConfigHandler
from spectre.receivers.factory import get_receiver
from spectre.utils import file_helpers
from host.capture_scripts.capture_session import update_process_status

app = typer.Typer()

@app.command()
def cron_log() -> None:
    file_helpers.cat("/var/log/daily_capture.log")
    raise typer.Exit()


@app.command()
def process_log(
    pid: int = typer.Option(None, "--pid", help="Print the process log, or if specified, the specific logs for a subprocess")
) -> None:
    """
    Print the process log or the log for a specific subprocess if PID is provided.
    """
    # Update the statuses of subprocesses before printing
    update_process_status()

    if pid:
        # Print the log for the specific subprocess by PID
        file_helpers.cat(os.path.join(CONFIG.path_to_logs, f"subprocess_{pid}.log"))
    else:
        # Print the general process tracking log
        file_helpers.cat(CONFIG.path_to_processes_log)

    raise typer.Exit()


@app.command()
def fits_config_template(
    tag: str = typer.Option(None, "--tag", "-t", help=""),
    as_command: bool = typer.Option(False, "--as-command", help="")
) -> None:
    if as_command:
        if not tag:
            raise ValueError("If specifying --as-command, the tag must also be specified with --tag or -t.")
        fits_config_handler = FitsConfigHandler(tag)
        command_as_string = fits_config_handler.template_to_command(tag, as_string=True)
        typer.secho(command_as_string)
    else:
        template = FitsConfigHandler.get_template()
        for key, value in template.items():
            typer.secho(
                f"{key}: {value.__name__}"
            )
    typer.Exit()


@app.command()
def capture_config_template(
    receiver_name: str = typer.Option(..., "--receiver", "-r", help="Specify the receiver name"),
    mode: str = typer.Option(..., "--mode", "-m", help="Specify the mode for capture"),
    as_command: bool = typer.Option(False, "--as-command", help=""),
    tag: str = typer.Option(None, "--tag", "-t", help="")
) -> None:
    
    receiver = get_receiver(receiver_name, mode = mode)
    
    if as_command:
        if not tag:
            raise ValueError("If specifying --as-command, the tag must also be specified with --tag or -t.")
        command_as_string = receiver.template_to_command(tag, as_string=True)
        typer.secho(command_as_string)
    else:
        template = receiver.get_template()
        for key, value in template.items():
            typer.secho(
                f"{key}: {value.__name__}"
            )
    raise typer.Exit()


@app.command()
def fits_config(tag: str = typer.Option(..., "--tag", "-t", help=""),
) -> None:
    fits_config_handler = FitsConfigHandler(tag)
    config_dict = fits_config_handler.load_as_dict()
    for key, value in config_dict.items():
        typer.secho(
            f"{key}: {value}"
        )
    raise typer.Exit()

@app.command()
def capture_config(tag: str = typer.Option(..., "--tag", "-t", help=""),
) -> None:
    capture_config_handler = CaptureConfigHandler(tag)
    config_dict = capture_config_handler.load_as_dict()
    for key, value in config_dict.items():
        typer.secho(
            f"{key}: {value}"
        )
    raise typer.Exit()

    
