from abc import ABC, abstractmethod

class CaptureConfigMount(ABC):
    def __init__(self):
        self.set_templates()
        self.set_validators()
        
        # we impose that for any config detailed in templates, it must have a corresponding validator
        if self.templates.keys() != self.validators.keys():
            raise KeyError(f"Key mismatch between templates and validators for {self.receiver_name}!")

        self.valid_modes = list(self.templates.keys())
    

    @abstractmethod
    def set_validators(self):
        pass


    @abstractmethod
    def set_templates(self):
        pass


    def validate(self, capture_config: dict, mode: str) -> None:
        validator = self.get_validator(mode)
        validator(capture_config)
        return 


    def get_validator(self, mode: str):
        validator = self.validators.get(mode)
        if validator is None:
            raise ValueError(f"Invalid mode: {mode}, validator not found. Need one of {self.valid_modes}.")
        return validator
    

    def get_template(self, mode: str) -> dict:
        template = self.templates.get(mode)
        if template is None:
            raise ValueError(f"Invalid mode: {mode}, validator not found. Need one of {self.valid_modes}.")
        return template
    





    



