# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

import typer

log_level_option: int = typer.Option(
    logging.INFO,
    "--log-level",
    help="Set the logging level (e.g., 10 for DEBUG, 20 for INFO)."
)