# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from logging import getLogger
_LOGGER = getLogger(__name__)

from typing import List

from spectre.receivers.factory import get_receiver
from spectre.exceptions import log_exceptions
from spectre.file_handlers.json.handlers import (
    FitsConfigHandler,
    CaptureConfigHandler
)


@log_exceptions(_LOGGER)
def capture_config(tag: str,
                   params: List[str]
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
    d = capture_config_handler.type_cast_params(params, 
                                                template, 
                                                validate_against_template=False, # don't validate against the template
                                                ignore_keys=['receiver', 'mode', 'tag'])
    # update the key values as per the params dict
    capture_config.update(d)
    # save the updated capture config
    receiver.save_capture_config(tag, capture_config, doublecheck_overwrite=False)


@log_exceptions(_LOGGER)
def fits_config(tag: str,
                params: List[str]
) -> None:
    fits_config_handler = FitsConfigHandler(tag)
    fits_config = fits_config_handler.read()
    template = fits_config_handler.get_template()
    d = fits_config_handler.type_cast_params(params,
                                             template,
                                             validate_against_template=False)
    fits_config.update(d)
    fits_config_handler.validate_against_template(fits_config, template)
    fits_config_handler.save(fits_config, doublecheck_overwrite=False)