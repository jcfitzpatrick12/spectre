from cli.receivers.maps import receiver_templates, receiver_validators

# gets the config for a particular receiver name
def fetch_templates(receiver_name):
    try:
        return receiver_templates[receiver_name]
    except KeyError:
        valid_receiver_names = list(receiver_templates.keys())
        raise KeyError(f'{receiver_name} is not a valid receiver name. Need one of {valid_receiver_names}')
    

def fetch_validators(receiver_name):
    try:
        return receiver_validators[receiver_name]
    except KeyError:
        valid_receiver_names = list(receiver_validators.keys())
        raise KeyError(f'{receiver_name} is not a valid receiver name. Need one of {valid_receiver_names}')