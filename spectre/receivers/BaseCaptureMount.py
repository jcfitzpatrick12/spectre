# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

from abc import ABC, abstractmethod
from cfg import CONFIG

class BaseCaptureMount(ABC):
    def __init__(self):
        self.set_capture_methods()
        self.valid_modes = list(self.capture_methods.keys())
        pass


    @abstractmethod
    def set_capture_methods(self) -> None:
        pass


    def start(self, mode: str, capture_configs: list) -> None:
        capture_method = self.capture_methods.get(mode)
        if capture_method is None:
            raise ValueError(f"Invalid mode '{mode}'. Valid modes are: {self.valid_modes}")
        capture_method(capture_configs)
        return