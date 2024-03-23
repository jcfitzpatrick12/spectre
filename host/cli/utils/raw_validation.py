def validate_raw_dict(raw_dict, template):
    check_keys_are_valid(raw_dict, template)
    check_missed_keys(raw_dict, template)
    check_values_are_populated(raw_dict)


def check_missed_keys(raw_dict, template):
    for key in template.keys():
        if key not in raw_dict.keys():
            raise KeyError(f'{key} is missing. Please pass in using --param {key}=VALUE')
    pass


def check_keys_are_valid(raw_dict, template):
    valid_keys = list(template.keys())
    for key in raw_dict.keys():
        if key not in valid_keys:
            raise KeyError(f'{key} is an undefined key. Need one of {valid_keys}')
    pass


def check_values_are_populated(raw_dict):
    for value in raw_dict.values():
        if value == None:
            raise ValueError(f"{value} cannot be None. Received {value}.")
    pass
