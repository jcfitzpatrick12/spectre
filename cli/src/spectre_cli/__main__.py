# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer

from spectre_cli.commands.create   import create_typer
from spectre_cli.commands.get      import get_typer
from spectre_cli.commands.delete   import delete_typer
from spectre_cli.commands.start    import start_typer
from spectre_cli.commands.update   import update_typer
from spectre_cli.commands.download import download_typer
from spectre_cli.commands.test     import test_typer

app = typer.Typer(help = "SPECTRE: Process, Explore and Capture Transient Radio Emissions")

# Register subcommands
app.add_typer(create_typer  , name="create")
app.add_typer(get_typer     , name="get")
app.add_typer(delete_typer  , name="delete")
app.add_typer(start_typer   , name="start")
app.add_typer(update_typer  , name="update")
app.add_typer(download_typer, name="download")
app.add_typer(test_typer    , name="test")
