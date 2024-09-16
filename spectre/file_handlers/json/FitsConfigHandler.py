# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import os

from spectre.file_handlers.json.SPECTREConfigHandler import SPECTREConfigHandler
from spectre.utils import dict_helpers

class FitsConfigHandler(SPECTREConfigHandler):
    def __init__(self, tag: str, **kwargs):
        super().__init__(tag, "fits", **kwargs)

    @classmethod
    def get_template(cls) -> dict:
        return {
            "ORIGIN": str,
            "TELESCOP": str,
            "INSTRUME": str,
            "OBJECT": str,
            "OBS_LAT": float,
            "OBS_LONG": float,
            "OBS_ALT": float
        }

    def save_params_as_fits_config(self, params: list[str]) -> None:
        # convert the user defined params to a raw_dict [key=string_value]
        string_valued_dict = dict_helpers.params_list_to_string_valued_dict(params)
        # fetch the fits config template
        template = self.get_template()
        # verify the keys of the raw dict against the template
        dict_helpers.validate_keys(string_valued_dict, template)
        # convert the raw dict string values to those defined in the template
        fits_config_as_dict = dict_helpers.convert_types(string_valued_dict, template)  
        # and finally, save the fits config as a json
        self.save_dict_as_json(fits_config_as_dict)
    

    def template_to_command(self, tag: str, as_string = False) -> str:
        command_as_list = ["spectre", "create", "fits-config", "-t", tag]
        template = self.get_template()
        for key, value in template.items():
            command_as_list += ["-p"]
            command_as_list += [f"{key}={value.__name__}"]
        if as_string:
            return " ".join(command_as_list)
        else:
            return command_as_list