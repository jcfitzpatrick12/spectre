# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
import tempfile

import spectre_server.core.config


@pytest.fixture
def spectre_config_paths():
    """Provide a temporary directory for Spectre file system data during each test."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env = {"SPECTRE_DATA_DIR_PATH": tmpdir}
        paths = spectre_server.core.config.Paths(env)
        yield paths
