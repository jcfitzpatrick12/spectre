from spectre.receivers.BaseCaptureMount import BaseCaptureMount
from spectre.receivers.mount_register import register_capture_mount

from spectre.receivers.library.RSP1A.gr import fixed


@register_capture_mount("RSP1A")
class CaptureMount(BaseCaptureMount):
    def __init__(self):
        super().__init__()


    def set_capture_methods(self) -> None:
        self.capture_methods = {
            "fixed": self.fixed,
        }


    def fixed(self, capture_configs: list) -> None:
        num_capture_configs = len(capture_configs)
        if num_capture_configs > 1:
            raise ValueError(f"Expected 1 capture config. Received {num_capture_configs}")
        # take the first (and now verified only) capture config in the list
        capture_config = capture_configs[0]
        fixed.main(capture_config)
        return


