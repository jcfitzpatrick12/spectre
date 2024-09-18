# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from spectre.file_handlers.json.SPECTREConfigHandler import SPECTREConfigHandler

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
        

    def save_params_as_fits_config(self, 
                                   params: list[str], 
                                   doublecheck_overwrite: bool = True
                                   ) -> None:
        d = self.type_cast_params(params, self.get_template())
        self.save(d, doublecheck_overwrite=doublecheck_overwrite)
        return