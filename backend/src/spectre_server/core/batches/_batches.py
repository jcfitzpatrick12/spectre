# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import typing
import collections
import datetime

import spectre_server.core.config
import spectre_server.core.spectrograms
from ._base import Base, parse_batch_file_name

T = typing.TypeVar("T", bound=Base)


class Batches(typing.Generic[T]):
    def __init__(
        self,
        tag: str,
        batch_cls: typing.Type[T],
        batches_dir_path: typing.Optional[str] = None,
    ) -> None:
        """A simple interface to read batched filesystem data.

        :param batch_cls: The `Base` subclass used to read batch files under that tag.
        :param tag: The data tag.
        :param batches_dir_path: Optionally override the directory containing the batched files.
        """
        self.__batch_cls = batch_cls
        self.__tag = tag
        self.__batches_dir_path = (
            batches_dir_path or spectre_server.core.config.paths.get_batches_dir_path()
        )
        self.__batch_map: dict[str, T] = collections.OrderedDict()
        self.__update()

    def __update(self) -> None:
        """Perform a fresh search of all files with `tag` in the batch name."""
        self.__batch_map.clear()

        paths = []
        for root, _, files in os.walk(self.__batches_dir_path):
            for file in files:
                paths.append(os.path.join(root, file))

        for path in paths:
            start_time, tag, _ = parse_batch_file_name(os.path.basename(path))
            if not self.__tag is None and tag == self.__tag:
                self.__batch_map[start_time] = self.__batch_cls(
                    os.path.dirname(path), start_time, tag
                )

        self.__batch_map = collections.OrderedDict(sorted(self.__batch_map.items()))

    def __iter__(self) -> typing.Iterator[T]:
        yield from self.__batch_map.values()

    def __len__(self) -> int:
        return len(self.__batch_map)

    def __getitem__(self, start_time: str) -> T:
        """Get a batch by its start time string.

        :param start_time: The start time string in the format specified by TimeFormat.DATETIME.
        :return: The batch corresponding to the start time.
        :raises KeyError: If no batch exists for the given start time.
        """
        if start_time not in self.__batch_map:
            raise KeyError(f"No batch found for start time '{start_time}'")
        return self.__batch_map[start_time]

    def __validate_range(
        self, start_datetime: datetime.datetime, end_datetime: datetime.datetime
    ) -> None:
        if start_datetime == end_datetime:
            raise ValueError(
                f"The start and end time must be different. "
                f"Got start time {start_datetime}, "
                f"and end time {end_datetime}"
            )

        if start_datetime > end_datetime:
            raise ValueError(
                f"The start time must be less than the end time. "
                f"Got start time {start_datetime}, "
                f"and end time {end_datetime}"
            )

    def get_spectrogram(
        self, start_datetime: datetime.datetime, end_datetime: datetime.datetime
    ) -> spectre_server.core.spectrograms.Spectrogram:
        """
        Retrieve a spectrogram spanning the specified time range.

        :param start_datetime: The start time of the range (inclusive).
        :param end_datetime: The end time of the range (inclusive).
        :raises FileNotFoundError: If no spectrogram data is available within the specified time range.
        :raise ValueError: If the start time is not less than the end time.
        :return: A spectrogram created by stitching together data from all matching batches.
        """
        self.__validate_range(start_datetime, end_datetime)
        batches_in_range = self.get_batches_in_range(start_datetime, end_datetime)
        spectrograms = [
            batch.read_spectrogram()
            for batch in batches_in_range
            if batch.spectrogram_file.exists
        ]

        if not spectrograms:
            raise FileNotFoundError(
                f"No spectrogram data found for the time range {start_datetime} to {end_datetime}."
            )
        return spectre_server.core.spectrograms.time_chop(
            spectre_server.core.spectrograms.join_spectrograms(spectrograms),
            start_datetime,
            end_datetime,
        )

    def get_batches_in_range(
        self, start_datetime: datetime.datetime, end_datetime: datetime.datetime
    ) -> list[T]:
        """Get batches that overlap with the input time range.

        The end time of each batch is assumed to be upper bounded by the start time of the next,
        since they cannot overlap. The final batch is treated as ending at `datetime.max`
        since there is no batch after it to provide that upper bound.

        :param start_datetime: The start time of the range (inclusive).
        :param end_datetime: The end time of the range (inclusive).
        :raise ValueError: If the start time is not less than the end time.
        :return: A list of batches that fall within the specified time range.
        """
        self.__validate_range(start_datetime, end_datetime)
        filtered_batches = []
        batch_datetimes = [
            datetime.datetime.strptime(
                t, spectre_server.core.config.TimeFormat.DATETIME
            )
            for t in self.__batch_map.keys()
        ]
        for idx, batch in enumerate(self):
            this_start = batch_datetimes[idx]
            next_start = (
                batch_datetimes[idx + 1]
                if idx + 1 < len(batch_datetimes)
                else datetime.datetime.max
            )
            if start_datetime < next_start and this_start <= end_datetime:
                filtered_batches.append(batch)

        return filtered_batches
