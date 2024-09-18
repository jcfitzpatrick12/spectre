# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer
from typing import List

from spectre.receivers.factory import get_receiver
from spectre.file_handlers.json.FitsConfigHandler import FitsConfigHandler
from spectre.file_handlers.json.CaptureConfigHandler import CaptureConfigHandler

app = typer.Typer()

@app.command()
def capture_config(tag: str = typer.Option(..., "--tag", "-t", help=""),
                   params: List[str] = typer.Option(..., "--param", "-p", help="Pass arbitrary key-value pairs.", metavar="KEY=VALUE"),
) -> None:
    
    # extract the current capture config saved (which will be type cast!)
    capture_config_handler = CaptureConfigHandler(tag)
    capture_config = capture_config_handler.read()

    # find the receiver and the mode of the capture config
    receiver_name = capture_config.get("receiver")
    mode = capture_config.get("mode")

    # and use them to instantiate a receiver
    receiver = get_receiver(receiver_name, mode)
    # fetch the corresponding template so we can type cast the params list
    template = receiver.get_template()
    # convert the params to update (passed in via --param arguments) into a string valued dict
    d = capture_config_handler.type_cast_params(params, template, ignore_keys=['receiver', 'mode', 'tag'])
    # update the key values as per the params dict
    capture_config.update(d)
    # save the updated capture config
    receiver.save_capture_config(tag, capture_config, doublecheck_overwrite=False)
    typer.secho(f"The capture-config for tag \"{tag}\" has been updated.", fg=typer.colors.GREEN)
    raise typer.Exit()


@app.command()
def fits_config(tag: str = typer.Option(..., "--tag", "-t", help=""),
                   params: List[str] = typer.Option(..., "--param", "-p", help="Pass arbitrary key-value pairs.", metavar="KEY=VALUE"),
) -> None:
    fits_config_handler = FitsConfigHandler(tag)
    fits_config = fits_config_handler.read()
    template = fits_config_handler.get_template()
    params_as_string_dict = dict_helpers.params_list_to_string_valued_dict(params)
    params_as_dict = dict_helpers.convert_types(params_as_string_dict, template)
    fits_config.update(params_as_dict)
    fits_config_handler.save(fits_config, doublecheck_overwrite=False)
    typer.secho(f"The fits-config for tag \"{tag}\" has been updated.", fg=typer.colors.GREEN)
    raise typer.Exit()