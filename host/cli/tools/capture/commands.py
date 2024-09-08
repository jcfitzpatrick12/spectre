# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer
import os
from typing import List

from host.cli import __app_name__, __version__
from host.capture_session import processes
from host.tests.analytical import do_analytical_test
from cfg import CONFIG

from spectre.receivers.factory import get_receiver
from spectre.watchdog.Watcher import Watcher
from host.capture_session import session


app = typer.Typer()


@app.command()
def start_session(receiver_name: str = typer.Option(..., "--receiver", "-r", help="Specify the receiver name"),
                  mode: str = typer.Option(..., "--mode", "-m", help="Specify the mode for capture"),
                  tags: List[str] = typer.Option(..., "--tag", "-t", help="Specify the tags for the capture session."),
                  force_restart: bool = typer.Option(False, "--force_restart", help="If a subprocess stops, terminate all subprocesses and restart the capture session..")
                 ) -> None:

    session.start_session(receiver_name,
                          mode,
                          tags,
                          force_restart)
    return


@app.command()
def start(receiver_name: str = typer.Option(..., "--receiver", "-r", help="Specify the receiver name"),
          mode: str = typer.Option(..., "--mode", "-m", help="Specify the mode for capture"),
          tags: List[str] = typer.Option(..., "--tag", "-t", help="Specify the tags for the capture."),
          run_as_foreground_ps: bool = typer.Option(False, "--in-foreground", help="Specify whether to run as a foreground process."),
) -> None:
    session.start_capture(receiver_name,
                          mode,
                          tags,
                          run_as_foreground_ps)
    raise typer.Exit()

@app.command()
def start_watcher(tags: List[str] = typer.Option(..., "--tag", "-t", help="Specify the tags for the capture session."),,
                  run_as_foreground_ps: bool = typer.Option(False, "--in-foreground", help="Specify whether to run as a foreground process."),
) -> None:
    session.start_watcher(tags,
                          run_as_foreground_ps)
    raise typer.Exit()


@app.command()
def stop(
) -> None:
    processes.stop()
    raise typer.Exit()


@app.command()
def analytical_test(
    test_tag: str = typer.Option(..., "--tag", "-t", help="Tag for the analytical test."),
    show_slice_status: bool = typer.Option(False, "--show-slice-status", help="If partial success, print the times of the spectral slices which failed validation.")
) -> None: 
    do_analytical_test.main(test_tag, show_slice_status = show_slice_status)
    raise typer.Exit()

