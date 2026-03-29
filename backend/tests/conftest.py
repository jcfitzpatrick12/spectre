# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
import tempfile
import typing

import flask
import flask.testing

import spectre_server.core.config
from spectre_server.__main__ import make_app


@pytest.fixture
def spectre_config_paths():
    """Provide a temporary directory for Spectre file system data during each test."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env = {"SPECTRE_DATA_DIR_PATH": tmpdir}
        paths = spectre_server.core.config.Paths(env)
        yield paths


@pytest.fixture()
def app() -> typing.Iterator[flask.Flask]:
    app = make_app()
    app.config.update(
        {
            "TESTING": True,
        }
    )
    yield app


@pytest.fixture()
def client(app: flask.Flask) -> flask.testing.FlaskClient:
    return app.test_client()
