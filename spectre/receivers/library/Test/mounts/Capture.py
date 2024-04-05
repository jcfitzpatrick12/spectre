from spectre.receivers.CaptureMount import CaptureMount
from spectre.receivers.mount_register import register_capture_mount

@register_capture_mount("Test")
class Capture(CaptureMount):
    def __init__(self):
        super().__init__()


    def set_capture_methods(self) -> None:
        self.capture_methods = {
            "fixed": self.fixed,
        }

    def fixed(self, capture_config: dict) -> None:
        pass


