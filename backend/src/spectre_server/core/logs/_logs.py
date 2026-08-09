# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import typing
import collections

import spectre_server.core.io
import spectre_server.core.config


class Log(spectre_server.core.io.Base):
    def __init__(self, file_path: str) -> None:
        super().__init__(file_path)

    def read(self) -> str:
        return spectre_server.core.io.read_file(
            self.file_path, spectre_server.core.io.FileFormat.TEXT
        )


class Logs:
    def __init__(self, logs_dir_path: typing.Optional[str] = None) -> None:
        self._logs_dir_path = (
            logs_dir_path or spectre_server.core.config.paths.get_logs_dir_path()
        )
        self._log_map: dict[str, Log] = collections.OrderedDict()
        self.__update()

    def __update(self) -> None:
        entries: list[tuple[str, str]] = []
        for root, _, files in os.walk(self._logs_dir_path):
            for file in files:
                entries.append((file, os.path.join(root, file)))
        entries.sort()
        self._log_map = collections.OrderedDict(
            (name, Log(path)) for name, path in entries
        )

    def __iter__(self) -> typing.Iterator[Log]:
        yield from self._log_map.values()

    def get_from_file_name(self, file_name: str) -> Log:
        file_name, _ = os.path.splitext(file_name)
        # tolerate callers who pass the extension in either form
        for key, log in self._log_map.items():
            if os.path.splitext(key)[0] == file_name:
                return log
        raise FileNotFoundError(f"Log not found with file name '{file_name}'")
