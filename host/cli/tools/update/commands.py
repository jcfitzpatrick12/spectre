# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import typer
from typing import List

from spectre.receivers.factory import get_receiver
from spectre.json_config.CaptureConfigHandler import CaptureConfigHandler
from spectre.json_config.FitsConfigHandler import FitsConfigHandler
from spectre.utils import dict_helpers 
app = typer.Typer()

@app.command()
def capture_config(tag: str = typer.Option(..., "--tag", "-t", help=""),
                   params: List[str] = typer.Option(..., "--param", "-p", help="Pass arbitrary key-value pairs.", metavar="KEY=VALUE"),
) -> None:
    
    # extract the current capture config saved (which will be type cast!)
    capture_config_handler = CaptureConfigHandler(tag)
    capture_config = capture_config_handler.load_as_dict()

    # find the receiver and the mode of the capture config
    receiver_name = capture_config.get("receiver")
    mode = capture_config.get("mode")

    # and use them to instantiate a receiver
    receiver = get_receiver(receiver_name, mode)
    # fetch the corresponding template so we can type cast the params list
    template = receiver.get_template()
    # convert the params to update (passed in via --param arguments) into a string valued dict
    params_as_string_dict = dict_helpers.params_list_to_string_valued_dict(params)
    # type cast this dict via the template
    params_as_dict = dict_helpers.convert_types(params_as_string_dict, template)

    # update the capture config
    for key, value in params_as_dict.items():
        capture_config = dict_helpers.update_key_value(capture_config, key, value)

    # save the updated capture config
    receiver.save_capture_config(tag, capture_config, doublecheck_overwrite=False)
    typer.secho(f"The capture-config for tag \"{tag}\" has been updated.", fg=typer.colors.GREEN)
    raise typer.Exit()


@app.command()
def fits_config(tag: str = typer.Option(..., "--tag", "-t", help=""),
                   params: List[str] = typer.Option(..., "--param", "-p", help="Pass arbitrary key-value pairs.", metavar="KEY=VALUE"),
) -> None:
    fits_config_handler = FitsConfigHandler(tag)
    fits_config = fits_config_handler.load_as_dict()
    template = fits_config_handler.get_template()

    params_as_string_dict = dict_helpers.params_list_to_string_valued_dict(params)

    params_as_dict = dict_helpers.convert_types(params_as_string_dict, template)
    for key, value in params_as_string_dict.items():
        fits_config = dict_helpers.update_key_value(fits_config, key, value)
    
    fits_config_handler.save_dict_as_json(fits_config, doublecheck_overwrite=False)
    typer.secho(f"The fits-config for tag \"{tag}\" has been updated.", fg=typer.colors.GREEN)
    raise typer.Exit()