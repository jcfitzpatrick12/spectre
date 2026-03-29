# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import json
import abc
import base64
import typing
import enum

from typing import Any, Optional, TypeVar, Generic

T = TypeVar("T")


class FileFormat(enum.Enum):
    JSON = "json"
    TEXT = "txt"
    PNG = "png"


class Base(abc.ABC, Generic[T]):
    def __init__(self, file_path: str) -> None:
        """An abstract interface to read a file of arbitrary format from the file system.

        :param file_path: The path to the file on the filesystem.
        """
        self._cache: Optional[T] = None
        self._file_path = file_path

    @abc.abstractmethod
    def read(self) -> T:
        """Read the contents of the file."""

    @property
    def file_path(self) -> str:
        """The path to the file on the filesystem."""
        return self._file_path

    @property
    def parent_dir_path(self) -> str:
        """Return the parent directory path for the file."""
        return os.path.dirname(self._file_path)

    @property
    def base_file_name(self) -> str:
        """Return the file name without the extension."""
        return os.path.splitext(os.path.basename(self._file_path))[0]

    @property
    def extension(self) -> Optional[str]:
        """Return the file extension (without the dot), or None if no extension exists."""
        _, ext = os.path.splitext(self._file_path)
        return ext.strip(".") if ext else None

    @property
    def file_name(self) -> str:
        """Return the full file name (base file name and extension)."""
        return os.path.basename(self._file_path)

    @property
    def exists(self) -> bool:
        """Check if the file exists in the filesystem."""
        return os.path.exists(self._file_path)

    def cached_read(self) -> T:
        """Read the file contents, caching the result for repeated calls.

        :return: The cached contents of the file.
        """
        if self._cache is None:
            self._cache = self.read()
        return self._cache

    def delete(self, ignore_if_missing: bool = False) -> None:
        """Delete the file from the filesystem.

        :param ignore_if_missing: If True, skips deletion if the file does not exist, defaults to False.
        :raises FileNotFoundError: If the file is missing and `ignore_if_missing` is False.
        """
        if not self.exists:
            if not ignore_if_missing:
                raise FileNotFoundError(f"{self.file_name} does not exist.")
        else:
            os.remove(self._file_path)


class _JsonFile(Base[dict[str, Any]]):
    def read(self) -> dict[str, Any]:
        with open(self._file_path, "r", encoding="utf-8") as f:
            return json.load(f)


class _TextFile(Base[str]):
    def read(self) -> str:
        with open(self._file_path, "r", encoding="utf-8") as f:
            return f.read()


class _PngFile(Base[str]):
    def read(self) -> str:
        with open(self.file_path, "rb") as f:
            encoded = base64.b64encode(f.read())
            return encoded.decode("ascii")


@typing.overload
def read_file(
    file_path: str, file_format: typing.Literal[FileFormat.JSON]
) -> dict[str, Any]: ...
@typing.overload
def read_file(file_path: str, file_format: typing.Literal[FileFormat.TEXT]) -> str: ...
@typing.overload
def read_file(file_path: str, file_format: typing.Literal[FileFormat.PNG]) -> str: ...


def read_file(file_path: str, file_format: FileFormat) -> typing.Any:
    """Read a file using the specified file format.

    :param file_path: The path to the file.
    :param file_format: The format of the file (FileFormat enum).
    :return: The contents of the file.
    :raises ValueError: If the file format is unsupported.
    """
    file: Base
    if file_format == FileFormat.JSON:
        file = _JsonFile(file_path)
    elif file_format == FileFormat.TEXT:
        file = _TextFile(file_path)
    elif file_format == FileFormat.PNG:
        file = _PngFile(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_format}")
    return file.read()
