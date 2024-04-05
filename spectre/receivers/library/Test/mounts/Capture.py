from spectre.receivers.CaptureMount import CaptureMount
from spectre.receivers.mount_register import register_capture_mount

from spectre.receivers.library.Test.gr import cosine_signal

@register_capture_mount("Test")
class Capture(CaptureMount):
    def __init__(self):
        super().__init__()


    def set_capture_methods(self) -> None:
        self.capture_methods = {
            "cosine_signal": self.cosine_signal,
        }

    def cosine_signal(self, capture_config: dict) -> None:
        cosine_signal.main(capture_config)
        return


