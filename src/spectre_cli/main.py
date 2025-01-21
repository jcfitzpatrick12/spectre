# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer

from spectre_cli.commands.create   import create_app
from spectre_cli.commands.get      import get_app
from spectre_cli.commands.delete   import delete_app
from spectre_cli.commands.start    import start_app
from spectre_cli.commands.update   import update_app
from spectre_cli.commands.download import download_app
from spectre_cli.commands.test     import test_app

app = typer.Typer(help = "SPECTRE: Process, Explore and Capture Transient Radio Emissions")

# Register subcommands
app.add_typer(create_app  , name="create")
app.add_typer(get_app     , name="get")
app.add_typer(delete_app  , name="delete")
app.add_typer(start_app   , name="start")
app.add_typer(update_app  , name="update")
app.add_typer(download_app, name="download")
app.add_typer(test_app    , name="test")
