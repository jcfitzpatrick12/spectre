# SPDX-FileCopyrightText: © 2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import spectre_server.services.configs as services


def test_is_config_locked_delegates_to_batch_lookup(monkeypatch) -> None:
    """A config is locked exactly when batches exist under its parsed tag."""
    monkeypatch.setattr(services, "_has_batches", lambda tag: tag == "locked")

    assert services.is_config_locked("locked.json") is True
    assert services.is_config_locked("unlocked.json") is False
