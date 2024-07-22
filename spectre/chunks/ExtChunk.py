# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Any

from spectre.utils import datetime_helpers, file_helpers
from spectre.chunks.BaseChunk import BaseChunk
from cfg import CONFIG

class ExtChunk(ABC, BaseChunk):
    def __init__(self, chunk_start_time: str, tag: str, ext: str):
        super().__init__(chunk_start_time, tag)
        self.ext = ext
        self.file = f"{self.chunk_start_time}_{tag}.{self.ext}"


    @abstractmethod
    def read(self) -> Any:
        pass


    def get_path(self) -> str:
        return os.path.join(self.chunk_dir, f"{self.chunk_start_time}_{self.tag}{self.ext}")
    

    def exists(self) -> bool:
        return os.path.exists(self.get_path()) 


    def delete(self, doublecheck_delete = True, ignore_file_existance = True) -> None:
        if not self.exists():
            return
        else:
            if doublecheck_delete:
                file_helpers.doublecheck_delete(self.get_path())
            try:
                os.remove(self.get_path())
            except FileNotFoundError:
                if ignore_file_existance:
                    pass
                else:
                    raise
        return
    