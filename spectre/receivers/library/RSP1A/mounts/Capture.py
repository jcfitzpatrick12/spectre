from spectre.receivers.CaptureMount import CaptureMount
from spectre.receivers.mount_register import register_capture_mount

from spectre.receivers.library.RSP1A.gr import dummy_fixed_capture, dummy_sweeping_capture

@register_capture_mount("RSP1A")
class Capture(CaptureMount):
    def __init__(self):
        super().__init__()


    def set_capture_modes(self) -> None:
        self.capture_modes = {
            "fixed": self.fixed,
            "sweeping": self.sweeping
        }


    def fixed(self, capture_config: dict) -> None:
        dummy_fixed_capture.main(capture_config)


    def sweeping(self, capture_config: dict) -> None:
        dummy_sweeping_capture.main(capture_config)

