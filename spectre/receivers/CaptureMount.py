from abc import ABC, abstractmethod

class CaptureMount(ABC):
    def __init__(self):
        self.set_capture_modes()
        self.valid_modes = list(self.capture_modes.keys())
        pass


    @abstractmethod
    def set_capture_modes(self,):
        pass


    def start(self, mode, capture_config):
        capture_method = self.capture_modes.get(mode)
        if capture_method is None:
            raise ValueError(f"Invalid mode '{mode}'. Valid modes are: {self.valid_modes}")
        capture_method(capture_config)
