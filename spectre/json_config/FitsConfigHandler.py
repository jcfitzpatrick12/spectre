import os

from spectre.json_config.JsonConfigHandler import JsonConfigHandler
from spectre.utils import dict_helpers

class FitsConfigHandler(JsonConfigHandler):
    def __init__(self, tag: str):
        super().__init__("fits", tag)


    def get_template(self,) -> dict:
        return {
            "ORIGIN": str,
            "TELESCOP": str,
            "INSTRUME": str,
            "OBJECT": str,
            "OBS_LAT": float,
            "OBS_LONG": float,
            "OBS_ALT": float
        }


    def set_template(self,) -> None:
        return self.template
    

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
    