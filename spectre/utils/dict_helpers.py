import ast

def unpack(param: str) -> tuple:
    if '=' not in param or param.startswith('=') or param.endswith('='):
        raise ValueError(f'Invalid format: "{param}". Expected "KEY=VALUE".')
    return tuple(map(str.strip, param.split('=', 1)))

# converts the params list where each element is of the form "KEY=VALUE" 
# into a dict {"key": "value" , ...}
# no type conversion is performed, all values in the output dict are string
def params_list_to_string_valued_dict(params: list) -> dict:
    return {k: v for k, v in (unpack(param) for param in params)}

def convert_types(string_valued_dict: dict, template: dict) -> dict:
    type_converted_dict = {}
    for key, string_value in string_valued_dict.items():          
        dynamic_type = template.get(key)
        if dynamic_type is None:
            raise ValueError(f"Dynamic type must be specified in the template. Received: {dynamic_type}.")
        try:
            if dynamic_type == bool:
                # need a specific implementation for boolean types
                type_converted_dict[key] = convert_to_bool(string_value)
            elif dynamic_type == dict:
                # need a specific implementation for dictionaries
                type_converted_dict[key] = ast.literal_eval(string_value)
            else:
                type_converted_dict[key] = dynamic_type(string_value)
        except ValueError as e:
            raise ValueError(f'Could not convert type for {key}. Received: {string_value} but expected {dynamic_type}.')
    return type_converted_dict


def convert_to_bool(value: str) -> bool:
    if value.lower() in ('true', '1', 't', 'y', 'yes'):
        return True
    elif value.lower() in ('false', '0', 'f', 'n', 'no'):
        return False
    else:
        raise ValueError(f"Cannot convert {value} to bool.")


def validate_keys(input_dict: dict, template: dict) -> None:
    template_keys = set(template.keys())
    keys_to_check = set(input_dict.keys())

    missing_keys = template_keys - keys_to_check
    invalid_keys = keys_to_check - template_keys

    if missing_keys or invalid_keys:
        errors = []
        if missing_keys:
            errors.append(f"Missing keys: {', '.join(missing_keys)}.")
        if invalid_keys:
            errors.append(f"Invalid keys: {', '.join(invalid_keys)}.")
        raise KeyError("Key errors found! " + " ".join(errors))
    

def validate_types(input_dict: dict, template: dict) -> None:
        # check the types match between the values of the capture config and the template
        for key, value in input_dict.items():
            expected_type = template.get(key)
            if expected_type is None:
                raise ValueError(f"Cannot have a type of value None, received {expected_type}.")
            if not isinstance(value, expected_type):
                raise TypeError(f"Expected {expected_type}, but received {value} which is of type {type(value)}.")