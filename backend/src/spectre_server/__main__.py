# SPDX-FileCopyrightText: © 2024-2025 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

import flask

from .config import SPECTRE_BIND_HOST, SPECTRE_BIND_PORT
from .routes.configs import configs_blueprint
from .routes.recordings import recordings_blueprint
from .routes.batches import batches_blueprint
from .routes.receivers import receivers_blueprint
from .routes.logs import logs_blueprint

from .core.logs import configure_root_logger, ProcessType
from .core import recordings as core_recordings

configure_root_logger(ProcessType.USER)

_LOGGER = logging.getLogger(__name__)


def make_app() -> flask.Flask:
    # Initialise the persistence layer once, before any request handling.
    # `init_db` is idempotent so this is safe on hot reloads and worker
    # restarts. `mark_stale_as_failed` cleans up any recordings whose
    # supervisor was orphaned by a prior backend crash — their PIDs no longer
    # refer to live processes, so leaving them in a non-terminal state would
    # be a lie.
    core_recordings.init_db()
    reconciled = core_recordings.mark_stale_as_failed()
    if reconciled:
        _LOGGER.warning(
            "Reconciled %d stale recording(s) as failed on boot: %s",
            len(reconciled),
            reconciled,
        )

    app = flask.Flask(__name__)
    app.register_blueprint(configs_blueprint)
    app.register_blueprint(recordings_blueprint)
    app.register_blueprint(batches_blueprint)
    app.register_blueprint(logs_blueprint)
    app.register_blueprint(receivers_blueprint)

    return app


if __name__ == "__main__":
    app = make_app()
    app.run(host=SPECTRE_BIND_HOST, port=SPECTRE_BIND_PORT, debug=True)
