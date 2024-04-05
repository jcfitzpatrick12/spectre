from abc import ABC, abstractmethod
from cfg import CONFIG



class CaptureMount(ABC):
    def __init__(self):
        self.set_capture_methods()
        self.valid_modes = list(self.capture_methods.keys())
        pass


    @abstractmethod
    def set_capture_methods(self) -> None:
        pass


    def start(self, mode: str, capture_config: dict) -> None:
        capture_method = self.capture_methods.get(mode)
        if capture_method is None:
            raise ValueError(f"Invalid mode '{mode}'. Valid modes are: {self.valid_modes}")
        capture_method(capture_config)
        return