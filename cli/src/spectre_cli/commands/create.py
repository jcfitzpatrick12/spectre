# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from typer import Typer, Option, Exit
from typing import List

from ._secho_resources import secho_new_resource
from ._utils import safe_request, get_config_file_name

create_typer = Typer(help="Create resources.")


@create_typer.command(help="Create a capture config.", deprecated=True)
def capture_config(
    receiver_name: str = Option(
        ..., "--receiver", "-r", help="The name of the receiver."
    ),
    receiver_mode: str = Option(
        ..., "--mode", "-m", help="The operating mode for the receiver."
    ),
    tag: str = Option(None, "--tag", "-t", help="The unique identifier."),
    file_name: str = Option(None, "-f", help="The file name.", metavar="<tag>.json"),
    params: List[str] = Option(
        [],
        "--param",
        "-p",
        help="Parameters as key-value pairs.",
        metavar="<key>=<value>",
    ),
    force: bool = Option(
        False,
        "--force",
        help="If specified, force the operation even if batch files exist with the same tag.",
    ),
    skip_validation: bool = Option(
        False,
        "--skip-validation",
        help="If specified, do not validate the parameters.",
    ),
) -> None:
    file_name = get_config_file_name(file_name, tag)

    json = {
        "receiver_name": receiver_name,
        "receiver_mode": receiver_mode,
        "string_parameters": params,
        "force": force,
        "validate": not skip_validation,
    }
    jsend_dict = safe_request(f"spectre-data/configs/{file_name}", "PUT", json=json)
    endpoint = jsend_dict["data"]
    secho_new_resource(endpoint)
    raise Exit()


@create_typer.command(help="Create a config.")
def config(
    receiver_name: str = Option(
        ..., "--receiver", "-r", help="The name of the receiver."
    ),
    receiver_mode: str = Option(
        ..., "--mode", "-m", help="The operating mode for the receiver."
    ),
    tag: str = Option(None, "--tag", "-t", help="The unique identifier."),
    file_name: str = Option(None, "-f", help="The file name.", metavar="<tag>.json"),
    params: List[str] = Option(
        [],
        "--param",
        "-p",
        help="Parameters as key-value pairs.",
        metavar="<key>=<value>",
    ),
    force: bool = Option(
        False,
        "--force",
        help="If specified, force the operation even if files exist with the same tag.",
    ),
    skip_validation: bool = Option(
        False,
        "--skip-validation",
        help="If specified, do not validate the parameters.",
    ),
) -> None:
    file_name = get_config_file_name(file_name, tag)

    json = {
        "receiver_name": receiver_name,
        "receiver_mode": receiver_mode,
        "string_parameters": params,
        "force": force,
        "validate": not skip_validation,
    }
    jsend_dict = safe_request(f"spectre-data/configs/{file_name}", "PUT", json=json)
    endpoint = jsend_dict["data"]
    secho_new_resource(endpoint)
    raise Exit()


@create_typer.command(help="Create a plot of spectrogram data.")
def plot(
    tags: list[str] = Option(
        ...,
        "--tag",
        "-t",
        help="The file tag. Specifying multiple tags yields a stacked plot over the same time frame.",
    ),
    obs_date: str = Option(
        ...,
        "--obs-date",
        help="The start date of the observation, in the format `%Y-%m-%d`.",
    ),
    start_time: str = Option(
        ...,
        "--start-time",
        help="The start time of the observation (UTC), in the format `%H:%M:%S`.",
    ),
    end_time: str = Option(
        ...,
        "--end-time",
        help="The end time of the observation (UTC), in the format `%H:%M:%S`.",
    ),
    lower_freq: float = Option(
        None,
        "--lower-freq",
        help="The lower bound of the frequency range in Hz. If unspecified, the minimum frequency "
        "available in each spectrogram is used.",
    ),
    upper_freq: float = Option(
        None,
        "--upper-freq",
        help="The upper bound of the frequency range in Hz. If unspecified, the maximum frequency "
        "available in each spectrogram is used.",
    ),
    log_norm: bool = Option(
        False,
        "--log-norm",
        help="If specified, normalise all values to the 0-1 range on a logarithmic scale.",
    ),
    dBb: bool = Option(
        False,
        "--dBb",
        help="If specified, use units of decibels above the background.",
    ),
    vmin: float = Option(
        None,
        "--vmin",
        help="The minimum value for the colormap. Only applies if `dBb` is specified.",
    ),
    vmax: float = Option(
        None,
        "--vmax",
        help="The maximum value for the colormap. Only applies if `dBb` is specified.",
    ),
    figsize_x: int = Option(
        None, "--figsize-x", help="The horizontal size of the plot."
    ),
    figsize_y: int = Option(None, "--figsize-y", help="The vertical size of the plot."),
) -> None:
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
        "figsize_y": figsize_y,
    }
    jsend_dict = safe_request(f"spectre-data/batches/plots", "PUT", json=json)
    endpoint = jsend_dict["data"]
    secho_new_resource(endpoint)
    raise Exit()
