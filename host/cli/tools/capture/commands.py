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


app = typer.Typer()

@app.command()
def start(receiver_name: str = typer.Option(..., "--receiver", "-r", help="Specify the receiver name"),
          mode: str = typer.Option(..., "--mode", "-m", help="Specify the mode for capture"),
          tags: List[str] = typer.Option(..., "--tag", "-t", help="Specify the tags for the capture session."),
          run_as_foreground_ps: bool = typer.Option(False, "--in-foreground", help="Specify whether to run as a foreground process."),
) -> None:

    if not os.path.exists(CONFIG.path_to_start_capture):
        raise FileNotFoundError(f"Could not find capture script: {CONFIG.path_to_start_capture}.")
    
    if run_as_foreground_ps:
        receiver = get_receiver(receiver_name, mode = mode)
        receiver.start_capture(tags)

    else:
        # build the command to start the capture session
        subprocess_command = [
            'python3', f'{CONFIG.path_to_start_capture}',
            '--receiver', receiver_name,
            '--mode', mode
        ]

        subprocess_command += ['--tag']
        for tag in tags:
            subprocess_command += [tag]

        capture_session.start(subprocess_command)
        raise typer.Exit()

@app.command()
def start_watcher(tag: str = typer.Option(..., "--tag", "-t", help="Tag for the capture session",),
                  run_as_foreground_ps: bool = typer.Option(False, "--in-foreground", help="Specify whether to run as a foreground process."),
) -> None:
    
    if not os.path.exists(CONFIG.path_to_start_watcher):
        raise FileNotFoundError(f"Could not find capture script: {CONFIG.path_to_start_watcher}.")
    
    if run_as_foreground_ps:

        if not os.path.exists(CONFIG.path_to_chunks_dir):
            os.mkdir(CONFIG.path_to_chunks_dir)

        watcher = Watcher(tag)
        watcher.start()

    else:
        # build the command to start the capture session
        subprocess_command = [
            'python3', f'{CONFIG.path_to_start_watcher}',
            '--tag', tag,
        ]
        processes.start(subprocess_command)
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

