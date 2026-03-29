# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

"""File system path definitions."""

import os
import pathlib
from typing import Optional, Dict

DEFAULT_SPECTRE_DATA_DIR_PATH = pathlib.Path(os.curdir) / ".spectre_data"


class Paths:
    def __init__(self, env: Optional[Dict[str, str]] = None):
        """Manages file system paths for Spectre.

        :param env: A dictionary representing environment variables. Defaults to `os.environ`.
        """
        self._env = env or os.environ
        self.__make_dirs()

    def get_spectre_data_dir_path(self) -> str:
        """Get the base directory for Spectre data.

        :return: The path stored in the `SPECTRE_DATA_DIR_PATH` environment variable, or the default.
        """
        return str(
            pathlib.Path(
                self._env.get("SPECTRE_DATA_DIR_PATH", DEFAULT_SPECTRE_DATA_DIR_PATH)
            ).absolute()
        )

    def set_spectre_data_dir_path(self, spectre_data_dir_path: str) -> None:
        """Set the `SPECTRE_DATA_DIR_PATH` environment variable and create necessary directories.

        :param spectre_data_dir_path: The new base directory for Spectre data.
        """
        self._env["SPECTRE_DATA_DIR_PATH"] = spectre_data_dir_path
        self.__make_dirs()

    def __make_dirs(self) -> None:
        self.__mkdir(pathlib.Path(self.get_spectre_data_dir_path()))
        self.__mkdir(pathlib.Path(self.get_batches_dir_path()))
        self.__mkdir(pathlib.Path(self.get_logs_dir_path()))
        self.__mkdir(pathlib.Path(self.get_configs_dir_path()))

    def get_batches_dir_path(
        self,
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
    ) -> str:
        """Get the directory for batched data files, optionally with a date-based subdirectory."""
        return str(
            self.__get_date_based_dir_path(
                pathlib.Path(self.get_spectre_data_dir_path()) / "batches",
                year,
                month,
                day,
            )
        )

    def get_logs_dir_path(
        self,
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
    ) -> str:
        """Get the directory for log files, optionally with a date-based subdirectory."""
        return str(
            self.__get_date_based_dir_path(
                pathlib.Path(self.get_spectre_data_dir_path()) / "logs",
                year,
                month,
                day,
            )
        )

    def get_configs_dir_path(self) -> str:
        """Get the directory for configuration files."""
        return str(pathlib.Path(self.get_spectre_data_dir_path()) / "configs")

    def __get_date_based_dir_path(
        self,
        base_dir: pathlib.Path,
        year: Optional[int],
        month: Optional[int],
        day: Optional[int],
    ) -> pathlib.Path:
        """Append a date-based directory onto the base directory."""
        if day and not (year and month):
            raise ValueError("A day requires both a month and a year")
        if month and not year:
            raise ValueError("A month requires a year")

        date_components = []
        if year:
            date_components.append(f"{year:04}")
        if month:
            date_components.append(f"{month:02}")
        if day:
            date_components.append(f"{day:02}")

        return base_dir.joinpath(*date_components)

    def __mkdir(self, path: pathlib.Path) -> None:
        """Create a directory if it doesn't already exist."""
        path.mkdir(parents=True, exist_ok=True)


paths = Paths()
