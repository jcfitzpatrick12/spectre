# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from spectre.receivers.BaseCaptureMount import BaseCaptureMount
from spectre.receivers.mount_register import register_capture_mount
from spectre.receivers.library.RSPduo.gr import tuner_1_fixed


@register_capture_mount("RSPduo")
class CaptureMount(BaseCaptureMount):
    def __init__(self):
        super().__init__()


    def set_capture_methods(self) -> None:
        self.capture_methods = {
            "tuner_1_fixed": self.tuner_1_fixed,
        }


    def tuner_1_fixed(self, capture_configs: list) -> None:
        num_capture_configs = len(capture_configs)
        if num_capture_configs > 1:
            raise ValueError(f"Expected 1 capture config. Received {num_capture_configs}")
        # take the first (and now verified only) capture config in the list
        capture_config = capture_configs[0]
        tuner_1_fixed.main(capture_config)
        return


