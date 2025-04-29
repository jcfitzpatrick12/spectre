# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typer import Typer, Option, Exit, secho
from typing import List

from ._safe_request import safe_request

create_typer = Typer(
    help = "Create resources."
)

def _secho_created_resource(
    resource_endpoint: str
) -> None:    
    secho(resource_endpoint, fg="green")


@create_typer.command(
    help = "Create a capture config."
)
def capture_config(
    tag: str = Option(None, 
                      "--tag", 
                      "-t", 
                      help="Unique identifier for the capture config."),
    base_file_name: str = Option(None,
                                 "-f",
                                 help="The base file name for the capture config."),
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
    if not (base_file_name is None) ^ (tag is None):
        raise ValueError("Specify either the tag or file name, not both.")
                                                                           
    base_file_name = base_file_name or f"{tag}.json"

    json = {
        "receiver_name": receiver_name,
        "receiver_mode": receiver_mode,
        "string_parameters": params,
        "force": force
    }
    jsend_dict = safe_request(f"spectre-data/configs/{base_file_name}", 
                              "PUT", 
                              json=json)
    resource_endpoint = jsend_dict["data"]
    _secho_created_resource(resource_endpoint)
    raise Exit()
        


@create_typer.command(
    help = "Create a plot of spectrogram data."
)
def plot(
    tags: list[str] = Option(..., 
                      "--tag", 
                      "-t", 
                      help="Specify one or more spectrograms to plot. The first tag specified will "
                           "determine which batch the plot will be saved under."),
    obs_date: str = Option(...,
                           "--obs-date",
                           help="The start date of the observation, in the format `%Y-%m-%d`."),
    start_time: str = Option(...,
                             "--start-time",
                             help="The start time of the observation (UTC), in the format `%H:%M:%S`."),
    end_time: str = Option(...,
                           "--end-time",
                           help = "The end time of the observation (UTC), in the format `%H:%M:%S`."),
    lower_freq: float = Option(None,
                             "--lower-freq",
                             help="The lower bound of the frequency range in Hz. If unspecified, the minimum frequency "
                                  "available in each spectrogram is used."),
    upper_freq: float = Option(None,
                               "--upper-freq",
                               help="The upper bound of the frequency range in Hz. If unspecified, the maximum frequency "
                                  "available in each spectrogram is used."),
    log_norm: bool = Option(False,
                            "--log-norm",
                            help="If specifed, normalises spectrograms to the 0-1 range on a logarithmic scale."),
    dBb: bool = Option(False,
                       "--dBb",
                       help="If specified, plots the spectrograms in decibels above the background."),
    vmin: float = Option(None,
                         "--vmin",
                         help="The minimum value for the colormap. Only applies if `dBb` is True."),
    vmax: float = Option(None,
                         "--vmax",
                         help="The minimum value for the colormap. Only applies if `dBb` is True."),
    figsize_x : int = Option(None,
                            "--figsize-x",
                            help="The horizontal size of the plot."),
    figsize_y: int = Option(None,
                            "--figsize-y",
                            help="The vertical size of the plot.")
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
    jsend_dict = safe_request(f"spectre-data/batches/plots/{primary_tag}", 
                              "PUT", 
                              json=json)
    resource_endpoint = jsend_dict["data"]
    _secho_created_resource(resource_endpoint)
    raise Exit()

    

