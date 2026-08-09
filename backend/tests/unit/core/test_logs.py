# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import os

import pytest

import spectre_server.core.config
import spectre_server.core.logs

_SERVER_FILE_NAME = "2025-01-31T00:00:00.000000Z_4242.log"
_SERVER_CONTENTS = "server contents"

_WORKER_FILE_NAME = "abcd1234_signal.log"
_WORKER_CONTENTS = "worker contents"


class TestGetLogFilePaths:
    def test_server(
        self,
    ) -> None:
        """The server log path is constructed correctly."""
        got = spectre_server.core.logs.get_server_log_file_path(
            "2025-01-31T00:00:00.000000Z", 123, "."
        )
        expected = "./2025-01-31T00:00:00.000000Z_123.log"
        assert got == expected

    def test_worker(
        self,
    ) -> None:
        """The worker log path is constructed correctly."""
        got = spectre_server.core.logs.get_worker_log_file_path(
            "2025-01-31T00:00:00.000000Z", "123", "."
        )
        expected = "./2025-01-31T00:00:00.000000Z_123.log"
        assert got == expected


class TestLog:
    def test_read(
        self,
        spectre_config_paths: spectre_server.core.config.Paths,
    ) -> None:
        """Check that we can read the contents of logs from the filesystem."""
        file_path = os.path.join(spectre_config_paths.get_logs_dir_path(), "sample.log")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("hello world")
        log = spectre_server.core.logs.Log(file_path)
        assert log.read() == "hello world"


@pytest.fixture
def logs(
    spectre_config_paths: spectre_server.core.config.Paths,
) -> None:
    """Write one server log and one worker log under the scoped directories."""
    server_path = os.path.join(
        spectre_config_paths.get_logs_dir_path(
            scope=spectre_server.core.logs.ProcessType.SERVER.value
        ),
        _SERVER_FILE_NAME,
    )
    worker_path = os.path.join(
        spectre_config_paths.get_logs_dir_path(
            scope=spectre_server.core.logs.ProcessType.WORKER.value
        ),
        _WORKER_FILE_NAME,
    )
    for path, contents in (
        (server_path, _SERVER_CONTENTS),
        (worker_path, _WORKER_CONTENTS),
    ):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(contents)


class TestLogs:
    def test_get_from_file_name_resolves_server_and_worker_logs(
        self,
        spectre_config_paths: spectre_server.core.config.Paths,
        logs: spectre_server.core.logs.Logs,
    ) -> None:
        """Check that we can read logs from their filename."""
        logs = spectre_server.core.logs.Logs(spectre_config_paths.get_logs_dir_path())
        assert logs.get_from_file_name(_SERVER_FILE_NAME).read() == _SERVER_CONTENTS
        assert logs.get_from_file_name(_WORKER_FILE_NAME).read() == _WORKER_CONTENTS

    @pytest.mark.parametrize(
        "scope, expected_file_name",
        [
            (spectre_server.core.logs.ProcessType.SERVER.value, _SERVER_FILE_NAME),
            (spectre_server.core.logs.ProcessType.WORKER.value, _WORKER_FILE_NAME),
        ],
    )
    def test_iterating_scoped_logs_returns_only_scoped_files(
        self,
        spectre_config_paths: spectre_server.core.config.Paths,
        logs: spectre_server.core.logs.Logs,
        scope: str,
        expected_file_name: str,
    ) -> None:
        """Iterating a scoped `Logs` should return only files under that scope."""
        logs = spectre_server.core.logs.Logs(
            spectre_config_paths.get_logs_dir_path(scope=scope)
        )
        file_names = [os.path.basename(log.file_path) for log in logs]
        assert file_names == [expected_file_name]
