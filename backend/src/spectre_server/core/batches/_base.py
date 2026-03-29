# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime
import typing
import functools
import abc
import dataclasses
import os

import spectre_server.core.io
import spectre_server.core.config
import spectre_server.core.spectrograms


def parse_batch_file_path(absolute_file_path: str) -> tuple[str, str, str, str]:
    """Parse a file path into the directory name, the start time, tag and extension."""
    return (
        os.path.dirname(absolute_file_path),
        *parse_batch_file_name(os.path.basename(absolute_file_path)),
    )


def parse_batch_file_name(file_name: str) -> tuple[str, str, str]:
    """Parse a file name into a start time, tag, and extension."""
    batch_name, extension = os.path.splitext(file_name)
    if batch_name.count("_") != 1:
        raise ValueError(f"Expected exactly one underscore in '{batch_name}'.")

    start_time, tag = batch_name.split("_", 1)
    return start_time, tag, extension.lstrip(".")


T = typing.TypeVar("T")


class BatchFile(spectre_server.core.io.Base[T]):
    def __init__(self, file_path: str) -> None:
        """An abstract base class for files belonging to a batch, identified by their file extension.

        Batch file names must conform to the following structure:

            `<start time>_<tag>.<extension>`

        The substring `<start time>_<tag>` is referred to as the batch name. Files with the same batch name
        belong to the same batch.

        :param file_path: The absolute path to the batch file.
        """
        super().__init__(file_path)
        self._start_time, self._tag, _ = parse_batch_file_name(self.file_name)

    @property
    def start_time(self) -> str:
        """The start time of the batch, up to seconds precision."""
        return self._start_time

    @property
    def tag(self) -> str:
        """The data tag."""
        return self._tag

    @functools.cached_property
    def start_datetime(self) -> datetime.datetime:
        """The start time of the batch."""
        return datetime.datetime.strptime(
            self.start_time, spectre_server.core.config.TimeFormat.DATETIME
        )


@dataclasses.dataclass(frozen=True)
class _Extension:
    PNG = "png"


class _PngFile(BatchFile[str]):
    """Stores an image in the PNG file format."""

    def read(self) -> str:
        return spectre_server.core.io.read_file(
            self.file_path, spectre_server.core.io.FileFormat.PNG
        )


class Base(abc.ABC):
    def __init__(self, batches_dir_path: str, start_time: str, tag: str) -> None:
        """An abstract base class representing a group of data files over a common time interval.

        All files in a batch share a base file name and differ only by their extension.
        Subclasses define the expected data for each file extension and
        provide an API for accessing their contents using `BatchFile` subclasses.

        Subclasses should expose `BatchFile` instances directly as attributes, which
        simplifies static typing. Additionally, they should call `add_file` in the constructor
        to formally register each `BatchFile`.

        :param batches_dir_path: The shared parent directory for each batch file.
        :param start_time: The start time of the batch.
        :param tag: The data tag.
        """
        self._batches_dir_path = batches_dir_path
        self._start_time = start_time
        self._tag: str = tag

        self._batch_files: dict[str, BatchFile] = {}

        self.add_file(_PngFile, _Extension.PNG)

    @property
    @abc.abstractmethod
    def spectrogram_file(
        self,
    ) -> BatchFile[spectre_server.core.spectrograms.Spectrogram]:
        """Indicate the file in the batch storing spectrogram data."""

    @property
    def start_time(self) -> str:
        """The start time of the batch, up to seconds precision."""
        return self._start_time

    @functools.cached_property
    def start_datetime(self) -> datetime.datetime:
        """The start time of the batch."""
        return datetime.datetime.strptime(
            self.start_time, spectre_server.core.config.TimeFormat.DATETIME
        )

    @property
    def tag(self) -> str:
        """The data tag."""
        return self._tag

    @property
    def name(self) -> str:
        """Return the base file name shared by all files in the batch,
        composed of the start time and the batch tag."""
        return f"{self._start_time}_{self._tag}"

    @property
    def extensions(self) -> list[str]:
        """All defined file extensions for the batch."""
        return list(self._batch_files.keys())

    @property
    def png_file(self) -> _PngFile:
        """The batch file corresponding to the `.png` extension."""
        return typing.cast(_PngFile, self.get_file(_Extension.PNG))

    def add_file(self, batch_file_cls: typing.Type[BatchFile], extension: str) -> None:
        """Add a batch file to the batch."""
        if extension in self._batch_files:
            raise ValueError(
                f"A file with extension '{extension}' is already registered."
            )
        self._batch_files[extension] = batch_file_cls(
            os.path.join(self._batches_dir_path, f"{self.name}.{extension}")
        )

    def get_file(self, extension: str) -> BatchFile:
        """Get a batch file from the batch, according to the file extension.

        :param extension: The file extension of the batch file.
        :raises NotImplementedError: If the extension is undefined for the batch.
        :return: The batch file registered under the input file extension.
        """
        if extension in self._batch_files:
            return self._batch_files[extension]
        else:
            raise NotImplementedError(
                f"A batch file with extension '{extension}' is not implemented for this batch."
            )

    def delete_file(self, extension: str) -> None:
        """Delete a file from the batch, according to the file extension.

        :param extension: The file extension of the batch file.
        :raises FileNotFoundError: If the batch file does not exist in the file system.
        """
        batch_file = self.get_file(extension)
        batch_file.delete()

    def has_file(self, extension: str) -> bool:
        """Determine the existance of a batch file in the file system.

        :param extension: The file extension of the batch file.
        :return: True if the batch file exists in the file system, False otherwise.
        """
        try:
            batch_file = self.get_file(extension)
            return batch_file.exists
        except FileNotFoundError:
            return False

    def read_spectrogram(self) -> spectre_server.core.spectrograms.Spectrogram:
        """Read and return the spectrogram data stored in the batch.

        :return: The spectrogram stored by the batch `spectrogram_file`.
        """
        return self.spectrogram_file.read()
