from spectre.receivers.CaptureMount import CaptureMount
from spectre.receivers.mount_register import register_capture_mount


@register_capture_mount("RSP1A")
class Capture(CaptureMount):
    def __init__(self):
        super().__init__()


    def set_capture_methods(self) -> None:
        self.capture_methods = {
            "fixed": self.fixed,
            "sweeping": self.sweeping
        }


    def fixed(self, capture_config: dict) -> None:
        return


    def sweeping(self, capture_config: dict) -> None:
        return

