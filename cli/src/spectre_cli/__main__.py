# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer

from spectre_cli.commands.create import create_typer
from spectre_cli.commands.get import get_typer
from spectre_cli.commands.delete import delete_typer
from spectre_cli.commands.update import update_typer
from spectre_cli.commands.test import test_typer
from spectre_cli.commands.record import record_typer


app = typer.Typer(
    help="Spectre: Process, Explore and Capture Transient Radio Emissions"
)
app.add_typer(create_typer, name="create")
app.add_typer(get_typer, name="get")
app.add_typer(delete_typer, name="delete")
app.add_typer(update_typer, name="update")
app.add_typer(test_typer, name="test")
app.add_typer(record_typer, name="record")
