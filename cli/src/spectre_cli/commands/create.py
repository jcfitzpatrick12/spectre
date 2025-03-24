# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typer import Typer, Option, Exit, secho
from typing import List

from ._safe_request import safe_request

create_typer = Typer(
    help = "Create resources."
)

def _secho_created_file(
    abs_path: str
) -> None:    
    secho(f"Created '{abs_path}'", fg="green")


@create_typer.command(
    help = "Create a capture config."
)
def capture_config(
    tag: str = Option(..., 
                      "--tag", 
                      "-t", 
                      help="Unique identifier for the capture config."),
    receiver_name: str = Option(..., 
                               "--receiver",
                               "-r", 
                               help="The name of the receiver."),
    receiver_mode: str = Option(..., 
                                "--mode", 
                                "-m", 
                                help="The operating mode for the receiver."),
    params: List[str] = Option([], 
                               "--param", 
                               "-p", 
                               help="Parameters as key-value pairs.", 
                               metavar="KEY=VALUE"),
    force: bool = Option(False, 
                         "--force", 
                         help="If a capture config already exists with the same tag, "
                              "overwrite it.", 
                         is_flag=True)
) -> None:
    json = {
        "receiver_name": receiver_name,
        "receiver_mode": receiver_mode,
        "string_parameters": params,
        "force": force
    }
    jsend_dict = safe_request(f"spectre-data/configs/{tag}", 
                              "PUT", 
                              json=json)
    abs_path = jsend_dict["data"]
    _secho_created_file(abs_path)
    raise Exit()
        


@create_typer.command(
    help = "Create a plot of spectrogram data."
)
def plot(
    tags: list[str] = Option(..., 
                      "--tag", 
                      "-t", 
                      help="Indicate which spectrograms to plot."),
    obs_date: str = Option(...,
                           "--obs-date",
                           help="The start date of the observation, in the format `%Y-%m-%d`."),
    start_time: str = Option(...,
                             "--start-time",
                             help="The start time of the observation, in the format `%H:%M:%S`."),
    end_time: str = Option(...,
                           "--end-time",
                           help = "The end time of the observation, in the format `%H:%M:%S`."),
    lower_freq: float = Option(None,
                             "--lower-freq",
                             help = "Defines the lower bound of the frequency range of the spectrograms, in Hz. "
                                    "If unspecified, the minimum frequency available for each spectrogram will be taken."),
    upper_freq: float = Option(None,
                               "--upper-freq",
                               help="Defines the upper bound of the frequency range of the spectrograms, in Hz. "
                                    "If unspecified, the maximum frequency available for each spectrogram will be taken."),
    log_norm: bool = Option(False,
                            "--log-norm",
                            help="If specifed, normalizes spectrograms to the 0-1 range on a logarithmic scale."),
    dBb: bool = Option(False,
                       "--dBb",
                       help="If specified, plots the spectrograms in decibels above the background."),
    vmin: float = Option(None,
                         "--vmin",
                         help="Minimum value for the colormap. Only applies if `dBb` is True."),
    vmax: float = Option(None,
                         "--vmax",
                         help="Minimum value for the colormap. Only applies if `dBb` is True."),
    figsize_x : float = Option(None,
                               "--figsize-x",
                               help="Indicate the horizontal size of the plot."),
    figsize_y: float = Option(None,
                              "--figsize-y",
                              help="Indicate the vertical size of the plot.")
) -> None:
    primary_tag, tags = tags[0], tags[1:]
    json = {
        "tags": tags,
        "obs_date": obs_date,
        "start_time": start_time,
        "end_time": end_time,
        "lower_freq": lower_freq,
        "upper_freq": upper_freq,
        "log_norm": log_norm,
        "dBb": dBb,
        "vmin": vmin,
        "vmax": vmax,
        "figsize_x": figsize_x,
        "figsize_y": figsize_y
    }
    jsend_dict = safe_request(f"spectre-data/batches/{primary_tag}", 
                              "PUT", 
                              json=json)
    abs_path = jsend_dict["data"]
    _secho_created_file(abs_path)
    raise Exit()

    

