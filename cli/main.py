# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import typer
from typing import Optional

from spectre_core.logging import configure_root_logger

from cli import APP_NAME, VERSION
from cli.commands.create import app as create_app
from cli.commands.list import app as list_app
from cli.commands.print import app as print_app
from cli.commands.delete import app as delete_app
from cli.commands.capture import app as capture_app
from cli.commands.update import app as update_app
from cli.commands.web_fetch import app as web_fetch_app
from cli.commands.test import app as test_app

app = typer.Typer()

# Register subcommands
app.add_typer(create_app, name="create")
app.add_typer(list_app, name="list")
app.add_typer(print_app, name="print")
app.add_typer(delete_app, name="delete")
app.add_typer(capture_app, name="capture")
app.add_typer(update_app, name="update")
app.add_typer(web_fetch_app, name="web-fetch")
app.add_typer(test_app, name="test")


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{APP_NAME} v{VERSION}")
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
    ),
    log: Optional[bool] = typer.Option(
        False,  # Default to False, becomes True when flag is used
        "--log",
        help="Generate a log for this session.",
        is_flag=True
    ),
    log_level: Optional[int] = typer.Option(
        logging.INFO,
        "--log-level",
        help="Set the logging level (e.g., 10 for DEBUG, 20 for INFO)."
    )
) -> None:
    if log:
        logs_handler = configure_root_logger("USER", log_level)
        typer.secho(f"Generating logs at {logs_handler.file_path}", fg=typer.colors.GREEN)

