# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import base64
import pytest
import os
import tempfile

import spectre_server.core.io


@pytest.fixture
def tmpdir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class File(spectre_server.core.io.Base[str]):
    """A pseudo-concrete implementation of the abstract parent for testing purposes."""

    def read(self) -> str:
        raise NotImplementedError("Cannot instantiate abstract parent.")


EXTENSION = "txt"
BASE_FILE_NAME = "foo"


@pytest.fixture
def base_file(tmpdir: str) -> spectre_server.core.io.Base:
    """Fixture to provide an instance of File with a dummy path."""
    file_path = f"{tmpdir}/{BASE_FILE_NAME}.{EXTENSION}"
    return File(file_path)


class TestBase:
    def test_parent_dir_path(
        self, tmpdir: str, base_file: spectre_server.core.io.Base
    ) -> None:
        """Check that the parent directory path is correctly returned."""
        assert base_file.parent_dir_path == tmpdir

    def test_base_file_name(self, base_file: spectre_server.core.io.Base) -> None:
        """Check that the base file name is correctly returned."""
        assert base_file.base_file_name == BASE_FILE_NAME

    def test_extension(self, base_file: spectre_server.core.io.Base) -> None:
        """Check that the file extension is correctly returned."""
        assert base_file.extension == EXTENSION

    def test_file_name(self, base_file: spectre_server.core.io.Base) -> None:
        """Check that the full file name is correctly returned."""
        assert base_file.file_name == f"{BASE_FILE_NAME}.{EXTENSION}"

    def test_exists(self, base_file: spectre_server.core.io.Base) -> None:
        """Check that the file existence is correctly determined."""
        assert not base_file.exists
        with open(base_file.file_path, "w", encoding="utf-8") as f:
            f.write("foo")
        assert base_file.exists

    def test_delete(self, base_file: spectre_server.core.io.Base) -> None:
        """Check that the file is deleted correctly."""
        with open(base_file.file_path, "w", encoding="utf-8") as f:
            f.write("content")
        assert base_file.exists
        base_file.delete()
        assert not base_file.exists


class TestRead:
    def test_read_text(self, tmpdir: str) -> None:
        """Check that we can read files containing simple text."""
        file_path = f"{tmpdir}/test.txt"
        content = "Hello, world!"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        result = spectre_server.core.io.read_file(
            file_path, spectre_server.core.io.FileFormat.TEXT
        )

        assert result == content

    def test_read_json(self, tmpdir: str) -> None:
        """Check that we can read files in the JSON file format."""
        file_path = f"{tmpdir}/test.json"
        content = {"key": "value"}

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(content, f)

        result = spectre_server.core.io.read_file(
            file_path, spectre_server.core.io.FileFormat.JSON
        )

        assert result == content

    def test_read_png(self, tmpdir: str) -> None:
        """Check that we can read files in the PNG file format."""
        file_path = f"{tmpdir}/test.png"
        content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"

        with open(file_path, "wb") as f:
            f.write(content)

        result = spectre_server.core.io.read_file(
            file_path, spectre_server.core.io.FileFormat.PNG
        )

        assert result == base64.b64encode(content).decode("ascii")
