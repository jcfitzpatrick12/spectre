from cli.utils import json_helpers
    

def unpack(param):
    if '=' not in param or param.startswith('=') or param.endswith('='):
        raise ValueError(f'Invalid format: "{param}". Expected "KEY=VALUE".')
    return tuple(map(str.strip, param.split('=', 1)))


def params_to_raw_dict(params):
    # unpack the config dict. Everything is string! The types are specified in the base_template configs
    raw_dict = {k: v for k, v in (unpack(param) for param in params)}
    # template = fetch.fetch_capture_config_template(re)
    return raw_dict


def convert_types(raw_dict, template):
    config_dict = {}
    for key, string_value in raw_dict.items():          
        dynamic_type = template[key]
        try:
            config_dict[key] = dynamic_type(string_value)
        except ValueError as e:
            raise ValueError(f'Could not convert type for {key}. Received: {string_value} but expected {dynamic_type}.')
    return config_dict