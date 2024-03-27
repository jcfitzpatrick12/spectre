## helper functions which convert params (input from CLI) into a validated capture config

def unpack(param: str) -> tuple:
    if '=' not in param or param.startswith('=') or param.endswith('='):
        raise ValueError(f'Invalid format: "{param}". Expected "KEY=VALUE".')
    return tuple(map(str.strip, param.split('=', 1)))


def params_to_raw_dict(params: list) -> dict:
    # unpack the config dict. Everything is string! The types are specified in the base_template configs
    raw_dict = {k: v for k, v in (unpack(param) for param in params)}
    # template = fetch.fetch_capture_config_template(re)
    return raw_dict


def convert_types(raw_dict: dict, template: dict) -> dict:
    config_dict = {}
    for key, string_value in raw_dict.items():          
        dynamic_type = template.get(key)
        if dynamic_type is None:
            raise ValueError(f"Dynamic type must be specified in the template. Received: {dynamic_type}.")
        try:
            config_dict[key] = dynamic_type(string_value)
        except ValueError as e:
            raise ValueError(f'Could not convert type for {key}. Received: {string_value} but expected {dynamic_type}.')
    return config_dict


def validate_keys(raw_dict: dict, template: dict) -> None:
    # self.get_template(mode).keys()
    template_keys = set(template.keys())
    raw_dict_keys = set(raw_dict.keys())

    missing_keys = template_keys - raw_dict_keys
    invalid_keys = raw_dict_keys - template_keys

    if missing_keys or invalid_keys:
        errors = []
        if missing_keys:
            errors.append(f"Missing keys: {', '.join(missing_keys)}. Pass in the missing keys via --param [KEY]=[VALUE].")
        if invalid_keys:
            errors.append(f"Invalid keys: {', '.join(invalid_keys)}.")
        raise KeyError("Key errors found! " + " ".join(errors))